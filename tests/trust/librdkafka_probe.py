#!/usr/bin/env python3
"""Observe exact librdkafka OpenSSL decisions using its public C API.

The verifier callback returns 1 iff the original x509_error is zero. It never
modifies that error, supplies roots, changes hostname policy, or overrides a
failed verification. Only metadata requests are sent; no credentials/messages.

API and implementation reviewed at the tested librdkafka release:
https://github.com/confluentinc/librdkafka/blob/v2.12.1/src/rdkafka.h
https://github.com/confluentinc/librdkafka/blob/v2.12.1/src/rdkafka_ssl.c
"""

from __future__ import annotations

import argparse
import ctypes as C
import hashlib
import importlib.metadata
import json
from pathlib import Path
import ssl
import sys
import threading
import time

from chain_check import CERTIFICATE, FIXTURES


ISSUER_ERRORS = {2, 18, 19, 20, 21, 23, 27, 28}
VERIFY_CALLBACK = C.CFUNCTYPE(
    C.c_int, C.c_void_p, C.c_char_p, C.c_int32, C.POINTER(C.c_int),
    C.c_int, C.c_void_p, C.c_size_t, C.c_void_p, C.c_size_t, C.c_void_p,
)
LOG_CALLBACK = C.CFUNCTYPE(None, C.c_void_p, C.c_int, C.c_char_p, C.c_char_p)


def original_verdict(code):
    return int(code == 0)


def fixture_certificates(directory):
    manifest = json.loads((directory / "manifest.json").read_text())
    if set(manifest.get("files", {})) != set(FIXTURES) | {"roots.json"}:
        raise ValueError("Exactly twelve pinned chains and roots.json are required")
    result = {}
    for name, digest in manifest["files"].items():
        data = (directory / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError(f"Fixture hash mismatch: {name}")
        if name not in FIXTURES:
            continue
        pems = CERTIFICATE.findall(data.decode())
        if not pems:
            raise ValueError(f"Missing certificate chain: {name}")
        hashes = [hashlib.sha256(ssl.PEM_cert_to_DER_cert(pem)).hexdigest() for pem in pems]
        result[name[:-4]] = {"leaf_sha256": hashes[0], "chain_sha256": hashes}
    return result


def loaded_library():
    import confluent_kafka

    paths = set()
    for line in Path("/proc/self/maps").read_text().splitlines():
        fields = line.split(maxsplit=5)
        if len(fields) != 6 or not fields[5].startswith("/"):
            continue
        path = Path(fields[5])
        if path.name.startswith("librdkafka") and not path.name.startswith("librdkafka++") and ".so" in path.name:
            paths.add(path)
    if len(paths) != 1:
        raise RuntimeError("Could not identify exactly one librdkafka shared library loaded by confluent_kafka")
    path = paths.pop()
    library = C.CDLL(str(path))
    library.rd_kafka_version_str.restype = C.c_char_p
    library.rd_kafka_version.restype = C.c_int
    version = library.rd_kafka_version_str().decode()
    number = library.rd_kafka_version()
    if (version, number) != confluent_kafka.libversion():
        raise RuntimeError("Loaded librdkafka does not match the Python binding's version")
    return library, {
        "path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "version": version, "version_number": number,
        "python_binding_version": importlib.metadata.version("confluent-kafka"),
    }


def bind_api(lib):
    signatures = {
        "rd_kafka_conf_new": (C.c_void_p, []),
        "rd_kafka_conf_destroy": (None, [C.c_void_p]),
        "rd_kafka_conf_set": (C.c_int, [C.c_void_p, C.c_char_p, C.c_char_p, C.c_void_p, C.c_size_t]),
        "rd_kafka_conf_get": (C.c_int, [C.c_void_p, C.c_char_p, C.c_void_p, C.POINTER(C.c_size_t)]),
        "rd_kafka_conf_set_ssl_cert_verify_cb": (C.c_int, [C.c_void_p, VERIFY_CALLBACK]),
        "rd_kafka_conf_set_log_cb": (None, [C.c_void_p, LOG_CALLBACK]),
        "rd_kafka_new": (C.c_void_p, [C.c_int, C.c_void_p, C.c_void_p, C.c_size_t]),
        "rd_kafka_metadata": (C.c_int, [C.c_void_p, C.c_int, C.c_void_p, C.POINTER(C.c_void_p), C.c_int]),
        "rd_kafka_metadata_destroy": (None, [C.c_void_p]),
        "rd_kafka_destroy": (None, [C.c_void_p]),
    }
    for name, (restype, argtypes) in signatures.items():
        function = getattr(lib, name)
        function.restype = restype
        function.argtypes = argtypes


def classify(host, positive, certificates, logs, callback_errors, fixture):
    verified = any(row["facility"] == "SSLVERIFY" and row["message"].endswith("Broker SSL certificate verified") for row in logs)
    hostname_checked = any(row["facility"] == "ENDPOINT" and row["message"].endswith("Enabled endpoint identification using hostname " + host) for row in logs)
    codes = {row["x509_error"] for row in certificates}
    nonzero = codes - {0}
    invalid_broker = any(row["broker"] not in (host, host + ":443") for row in certificates)
    if callback_errors or not certificates or invalid_broker or not hostname_checked:
        return "inconclusive"
    if positive:
        return "accepted" if verified and codes == {0} else "inconclusive"
    if verified:
        leaf_matches = any(row["depth"] == 0 and row["sha256"] == fixture["leaf_sha256"] for row in certificates)
        return "exposed" if leaf_matches else "inconclusive"
    failures = [row for row in certificates if row["x509_error"] != 0]
    if nonzero and nonzero <= ISSUER_ERRORS and all(row["sha256"] in fixture["chain_sha256"] for row in failures):
        return "issuer_rejected"
    return "inconclusive"


def probe(lib, host, positive, fixture, timeout):
    certificates = []
    logs = []
    callback_errors = []
    decisive = threading.Event()

    @VERIFY_CALLBACK
    def verify(rk, broker, broker_id, error_pointer, depth, der, length, message, capacity, opaque):
        try:
            code = error_pointer[0]
            if not der or not 0 < length < 1024 * 1024:
                raise ValueError("Invalid DER certificate callback data")
            certificates.append({
                "broker": broker.decode(), "depth": depth, "x509_error": code,
                "sha256": hashlib.sha256(C.string_at(der, length)).hexdigest(),
            })
            if code:
                explanation = f"Preserving OpenSSL verification failure {code}".encode()
                if message and capacity:
                    value = explanation[:capacity - 1] + b"\0"
                    C.memmove(message, value, len(value))
                decisive.set()
            # Deliberately never assign through error_pointer or accept an
            # OpenSSL failure. This preserves the API's original decision.
            return original_verdict(code)
        except Exception as error:
            callback_errors.append({"type": type(error).__name__, "detail": str(error)})
            decisive.set()
            return 0

    @LOG_CALLBACK
    def log(rk, level, facility, message):
        try:
            name = facility.decode()
            if name in {"OPENSSL", "CACERTS", "ENDPOINT", "SSLVERIFY", "SSLCERTVRFY"}:
                logs.append({"facility": name, "message": message.decode(errors="replace")})
                if name == "SSLVERIFY":
                    decisive.set()
        except Exception as error:
            callback_errors.append({"type": type(error).__name__, "detail": str(error)})
            decisive.set()

    conf = lib.rd_kafka_conf_new()
    if not conf:
        raise RuntimeError("Cannot allocate librdkafka configuration")
    client = None
    defaults = {}
    metadata_results = []
    try:
        for key, expected in (("enable.ssl.certificate.verification", "true"), ("ssl.endpoint.identification.algorithm", "https")):
            value = C.create_string_buffer(4096)
            size = C.c_size_t(len(value))
            if lib.rd_kafka_conf_get(conf, key.encode(), value, C.byref(size)) != 0:
                raise RuntimeError(f"Cannot verify default policy {key}")
            defaults[key] = value.value.decode()
            if defaults[key] != expected:
                raise RuntimeError(f"Default certificate policy is not the expected secure value: {key}")
        error = C.create_string_buffer(4096)
        settings = {
            "bootstrap.servers": host + ":443", "security.protocol": "ssl",
            "debug": "security", "socket.timeout.ms": str(int(timeout * 1000)),
            "socket.connection.setup.timeout.ms": str(int(timeout * 1000)),
            "reconnect.backoff.ms": "10000", "reconnect.backoff.max.ms": "10000",
        }
        for key, value in settings.items():
            if lib.rd_kafka_conf_set(conf, key.encode(), value.encode(), error, len(error)) != 0:
                raise RuntimeError(f"Cannot set {key}: {error.value.decode()}")
        if lib.rd_kafka_conf_set_ssl_cert_verify_cb(conf, verify) != 0:
            raise RuntimeError("The installed librdkafka does not support the verifier callback")
        lib.rd_kafka_conf_set_log_cb(conf, log)
        client = lib.rd_kafka_new(0, conf, error, len(error))
        if not client:
            raise RuntimeError(f"Cannot create metadata client: {error.value.decode()}")
        conf = None  # Ownership transfers only after successful rd_kafka_new.
        deadline = time.monotonic() + timeout
        while not decisive.is_set() and time.monotonic() < deadline:
            metadata = C.c_void_p()
            remaining_ms = max(1, min(1000, int((deadline - time.monotonic()) * 1000)))
            result = lib.rd_kafka_metadata(client, 0, None, C.byref(metadata), remaining_ms)
            metadata_results.append(result)
            if metadata:
                lib.rd_kafka_metadata_destroy(metadata)
    finally:
        if client:
            lib.rd_kafka_destroy(client)
        if conf:
            lib.rd_kafka_conf_destroy(conf)
    status = classify(host, positive, certificates, logs, callback_errors, fixture)
    return {
        "host": host, "expected": "accept" if positive else "reject_issuer",
        "status": status, "passed": status == ("accepted" if positive else "issuer_rejected"),
        "default_policy": defaults, "verification_events": certificates,
        "logs": logs, "callback_errors": callback_errors, "metadata_results": metadata_results,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", type=Path, default=Path(__file__).with_name("fixtures"))
    parser.add_argument("--timeout", type=float, default=5)
    args = parser.parse_args()
    report = {
        "checks": [], "errors": [], "operations": ["metadata"],
        "verification_callback": "Observe x509_error; return 1 only when it is 0; never modify the error or roots",
        "api_sources": [
            "https://github.com/confluentinc/librdkafka/blob/v2.12.1/src/rdkafka.h",
            "https://github.com/confluentinc/librdkafka/blob/v2.12.1/src/rdkafka_ssl.c",
        ],
    }
    try:
        if not 1 <= args.timeout <= 15:
            raise ValueError("Per-host timeout must be between 1 and 15 seconds")
        fixtures = fixture_certificates(args.fixtures)
        lib, report["library"] = loaded_library()
        bind_api(lib)
        report["source_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        report["checks"].append(probe(lib, "pypi.org", True, None, args.timeout))
        for host, fixture in sorted(fixtures.items()):
            report["checks"].append(probe(lib, host, False, fixture, args.timeout))
    except Exception as error:
        report["errors"].append({"type": type(error).__name__, "detail": str(error)})
    exposed = any(row["status"] == "exposed" for row in report["checks"])
    inconclusive = bool(report["errors"]) or len(report["checks"]) != 13 or any(row["status"] == "inconclusive" for row in report["checks"])
    report["status"] = "inconclusive" if inconclusive else "exposed" if exposed else "passed"
    print(json.dumps(report, indent=2))
    return 2 if inconclusive else 1 if exposed else 0


if __name__ == "__main__":
    sys.exit(main())
