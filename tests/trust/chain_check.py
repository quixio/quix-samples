#!/usr/bin/env python3
"""Verify public certificate chains against explicit stores without changing them.

Exit 0: required checks passed; 1: exposure/policy failure; 2: invalid evidence or
tool failure. Node checks establish the configured OS-store policy, not a TLS
handshake. An application/runtime TLS canary remains a separate rollout gate.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


AT_TIME = 1792584000
FIXTURES = tuple(sorted(
    f"{kind}-g3{branch}{suffix}-emudhra.we-have-a-problem.com.pem"
    for kind in ("dv", "ov", "ev")
    for branch in ("b", "c")
    for suffix in ("", "-aaa")
))
CERTIFICATE = re.compile(
    r"-----BEGIN CERTIFICATE-----\s+.+?\s+-----END CERTIFICATE-----", re.S
)
# Only failures that mean an otherwise valid fixture is not trusted. Expiry,
# hostname, signature, purpose and parsing failures must never count as passes.
UNTRUSTED_ERRORS = {2, 19, 20, 21, 27, 28}


class EvidenceError(Exception):
    pass


def run(command, data=None):
    try:
        return subprocess.run(command, input=data, text=True, capture_output=True,
                              timeout=30, check=False)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise EvidenceError(f"Cannot execute {Path(command[0]).name}: "
                            f"{type(error).__name__}") from error


def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise EvidenceError(f"Cannot read {path.name}: {type(error).__name__}") from error


def certificates(text, label, openssl):
    blocks = CERTIFICATE.findall(text)
    if (not blocks or len(blocks) != text.count("-----BEGIN CERTIFICATE-----")
            or len(blocks) != text.count("-----END CERTIFICATE-----")):
        raise EvidenceError(f"Missing or malformed certificate data in {label}")
    for index, block in enumerate(blocks, 1):
        result = run([openssl, "x509", "-noout"], block + "\n")
        if result.returncode:
            raise EvidenceError(f"Invalid certificate {index} in {label}")
    return len(blocks)


def openssl_version(executable):
    result = run([executable, "version"])
    if result.returncode or not re.match(r"^OpenSSL 3\.\d+\.\d+\b", result.stdout):
        raise EvidenceError("OpenSSL 3 is required; LibreSSL and other versions are unsupported")
    help_result = run([executable, "verify", "-help"])
    help_text = help_result.stdout + help_result.stderr
    if help_result.returncode or any(flag not in help_text for flag in
            ("-no-CAfile", "-no-CApath", "-no-CAstore", "-attime", "-verify_hostname")):
        raise EvidenceError("OpenSSL verify lacks the required isolated-store options")
    return result.stdout.strip()


def load_fixtures(directory, openssl):
    try:
        manifest = json.loads(read_text(directory / "manifest.json"))
        expected = set(FIXTURES) | {"roots.json"}
        if (manifest.get("schema_version") != 1
                or manifest.get("verification_time") != AT_TIME
                or set(manifest.get("files", {})) != expected):
            raise EvidenceError("Fixture manifest must contain the twelve expected chains and roots.json")
        for name, digest in manifest["files"].items():
            if not isinstance(digest, str) or not re.fullmatch(r"[a-f0-9]{64}", digest):
                raise EvidenceError("Invalid SHA-256 in fixture manifest")
            try:
                actual = hashlib.sha256((directory / name).read_bytes()).hexdigest()
            except OSError as error:
                raise EvidenceError(f"Missing fixture {name}") from error
            if actual != digest:
                raise EvidenceError(f"Fixture hash mismatch: {name}")
        roots = json.loads(read_text(directory / "roots.json"))
        if not isinstance(roots, list) or len(roots) != 4:
            raise EvidenceError("Positive control requires the four published roots")
        root_pems = []
        for root in roots:
            pem = root["pem"].replace("\\n", "\n")
            if certificates(pem, "positive-control root", openssl) != 1:
                raise EvidenceError("Each positive-control root must contain one certificate")
            root_pems.append(pem)
        for name in FIXTURES:
            certificates(read_text(directory / name), name, openssl)
        return "\n".join(root_pems)
    except (ValueError, KeyError, TypeError, AttributeError) as error:
        raise EvidenceError("Malformed fixture manifest or roots.json") from error


def verify_chain(args, fixture, store_flag, store):
    command = [args.openssl, "verify", "-no-CAfile", "-no-CApath", "-no-CAstore",
               "-purpose", "sslserver", "-verify_hostname", fixture.name[:-4],
               "-attime", str(AT_TIME), store_flag, str(store),
               "-untrusted", str(fixture), str(fixture)]
    result = run(command)
    if result.returncode == 0:
        return {"fixture": fixture.name, "status": "accepts", "verify_errors": []}
    output = result.stdout + result.stderr
    errors = [int(value) for value in re.findall(r"error (\d+) at \d+ depth lookup:", output)]
    if result.returncode != 2 or not errors or not set(errors) <= UNTRUSTED_ERRORS:
        raise EvidenceError(f"Unexpected verification failure for {fixture.name}; "
                            f"exit={result.returncode}, verify_errors={errors}")
    return {"fixture": fixture.name, "status": "rejects", "verify_errors": errors}


def check_store(args, path, directory=False):
    if directory:
        if not path.is_dir():
            raise EvidenceError("CA directory is missing or is not a directory")
        entries = sorted(p for p in path.iterdir() if re.fullmatch(r"[a-f0-9]{8}\.\d+", p.name))
        if not entries:
            raise EvidenceError("CA directory has no hashed certificate entries")
        for entry in entries:
            text = read_text(entry)
            if certificates(text, "CA directory entry " + entry.name, args.openssl) != 1:
                raise EvidenceError(f"CA directory entry {entry.name} must contain exactly one certificate")
            subject_hash = run([args.openssl, "x509", "-noout", "-subject_hash"], text)
            if (subject_hash.returncode or subject_hash.stdout.strip() != entry.name.split(".")[0]):
                raise EvidenceError(f"CA directory entry {entry.name} does not match its certificate subject hash")
        metadata = {"path": str(path), "hashed_entries": len(entries), "certificate_count": len(entries)}
    else:
        text = read_text(path)
        metadata = {"path": str(path), "certificate_count": certificates(text, "CA file", args.openssl),
                    "sha256": hashlib.sha256(text.encode()).hexdigest()}
    results = [verify_chain(args, args.fixtures_dir / name,
                           "-CApath" if directory else "-CAfile", path) for name in FIXTURES]
    accepted = sum(row["status"] == "accepts" for row in results)
    return {"name": "os_ca_directory" if directory else "os_ca_file",
            "status": "failed" if accepted else "passed", **metadata,
            "accepted": accepted, "rejected": len(results) - accepted, "results": results}
