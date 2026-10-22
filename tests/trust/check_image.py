#!/usr/bin/env python3
"""Check a local linux/amd64 image without building, pulling or deleting images.

CA files are copied from a never-started container, independently of runtime
checks. This matters when a container engine injects additional runtime roots.
Exit 0: selected checks passed; 1: affected chains accepted; 2: invalid or
inconclusive evidence. No result certifies clients that were not exercised.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import uuid

import chain_check


DIRECTORY = Path(__file__).resolve().parent
CA_ENV_KEYS = {
    "SSL_CERT_FILE", "SSL_CERT_DIR", "REQUESTS_CA_BUNDLE", "PIP_CERT",
    "AWS_CA_BUNDLE", "GRPC_DEFAULT_SSL_ROOTS_FILE_PATH", "CURL_CA_BUNDLE",
    "NODE_EXTRA_CA_CERTS", "NODE_OPTIONS",
}
FILE_ENV_KEYS = CA_ENV_KEYS - {"SSL_CERT_DIR", "NODE_OPTIONS"}
DEFAULT_CA_FILES = (
    "/etc/ssl/certs/ca-certificates.crt",
    "/etc/ssl/cert.pem",
    "/etc/pki/tls/certs/ca-bundle.crt",
    "/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem",
)
PYTHON_PACKAGES = {
    "stdlib": None, "requests": "requests", "httpx": "httpx",
    "botocore": "botocore", "grpc": "grpcio",
}
PYTHON_CLIENTS = set(PYTHON_PACKAGES)
EvidenceError = chain_check.EvidenceError


def execute(command, timeout=30):
    try:
        return subprocess.run(command, text=True, capture_output=True,
                              timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise EvidenceError(f"Command failed: {Path(command[0]).name}: {type(error).__name__}") from error


def require_success(result, operation):
    if result.returncode:
        raise EvidenceError(f"{operation} failed (exit {result.returncode}): {result.stderr.strip()[:1000]}")
    return result.stdout


def image_evidence(inspect):
    if not isinstance(inspect, list) or len(inspect) != 1:
        raise EvidenceError("Expected one local image inspection result")
    image = inspect[0]
    if image.get("Os") != "linux" or image.get("Architecture") != "amd64":
        raise EvidenceError("Only a local linux/amd64 image can be qualified")
    image_id = image.get("Id", "")
    if not re.fullmatch(r"sha256:[a-f0-9]{64}", image_id):
        raise EvidenceError("Image inspection did not return a content-addressed image ID")
    environment = {}
    for value in (image.get("Config") or {}).get("Env") or []:
        key, separator, content = value.partition("=")
        if separator and key in CA_ENV_KEYS:
            environment[key] = content
    return {
        "id": image_id,
        "repo_digests": image.get("RepoDigests") or [],
        "os": image["Os"],
        "architecture": image["Architecture"],
        "trust_environment": environment,
    }


def source_hashes(directory, runtime):
    names = ["chain_check.py", "check_image.py", "check_directories.py",
             "fixtures/manifest.json", "fixtures/roots.json"]
    names.extend("fixtures/" + name for name in chain_check.FIXTURES)
    if runtime != "none":
        names.append("python_probe.py" if runtime == "python" else "node_probe.js")
    if runtime == "python":
        names.append("librdkafka_probe.py")
    return {name: hashlib.sha256((directory / name).read_bytes()).hexdigest() for name in names}


def verify_source_hashes(directory, expected):
    for name, digest in expected.items():
        if hashlib.sha256((directory / name).read_bytes()).hexdigest() != digest:
            raise EvidenceError(f"Checker source changed during qualification: {name}")


def select_openssl(explicit):
    candidates = [explicit] if explicit else [
        "/opt/homebrew/opt/openssl@3/bin/openssl",
        "/usr/local/opt/openssl@3/bin/openssl",
        shutil.which("openssl"),
    ]
    for candidate in candidates:
        if not candidate or not Path(candidate).is_file():
            continue
        try:
            return candidate, chain_check.openssl_version(candidate)
        except EvidenceError:
            if explicit:
                raise
    raise EvidenceError("OpenSSL 3 with isolated-store verification options was not found")


def ca_candidates(environment):
    candidates = dict.fromkeys(DEFAULT_CA_FILES, False)
    for key in sorted(FILE_ENV_KEYS):
        value = environment.get(key)
        if value:
            if not value.startswith("/") or "\n" in value or "\x00" in value:
                raise EvidenceError(f"{key} must select an absolute container CA file")
            candidates[value] = True
    return candidates


def python_static_bundles(runtime):
    metadata = runtime["evidence"]["metadata"]
    packages = metadata["packages"]
    bundles = metadata["bundles"]
    result = []
    for package, bundle in (("certifi", "certifi"), ("pip", "pip._vendor.certifi")):
        if package not in packages:
            continue
        record = bundles.get(bundle, {})
        path = record.get("path", "")
        digest = record.get("sha256", "")
        if (not path.startswith("/") or "\n" in path or "\x00" in path
                or not re.fullmatch(r"[a-f0-9]{64}", digest)):
            raise EvidenceError(f"Installed {package} did not report a valid CA bundle path/hash")
        result.append((bundle, path, digest))
    return result


def runtime_classification(runtime, stdout, returncode):
    """Reject partial, duplicated, malformed or contradictory runtime evidence."""
    hosts = {name.removesuffix(".pem") for name in chain_check.FIXTURES}
    exposed = False
    inconclusive = False
    if runtime == "python":
        data = json.loads(stdout)
        if not isinstance(data, dict) or not isinstance(data.get("checks"), list):
            raise EvidenceError("Python probe did not return a checks object")
        checks = data["checks"]
        grouped = {}
        for row in checks:
            name = row.get("client")
            if name not in PYTHON_CLIENTS:
                raise EvidenceError("Python probe returned an unknown client")
            grouped.setdefault(name, []).append(row)
        skipped = data.get("skipped_clients", [])
        if (not isinstance(skipped, list) or len(skipped) != len(set(skipped))
                or "stdlib" not in grouped or set(grouped) & set(skipped)
                or set(grouped) | set(skipped) != PYTHON_CLIENTS):
            raise EvidenceError("Python client coverage is incomplete or contradictory")
        packages = data.get("metadata", {}).get("packages", {})
        if any(PYTHON_PACKAGES[client] in packages for client in skipped):
            raise EvidenceError("An installed Python client was skipped")
        for name, rows in grouped.items():
            positive_url = "https://pubsub.googleapis.com/" if name == "grpc" else "https://pypi.org/"
            expected = {positive_url: "accept"}
            expected.update({f"https://{host}/": "reject_issuer" for host in hosts})
            if len(rows) != 13 or {row.get("url") for row in rows} != set(expected):
                raise EvidenceError(f"Incomplete or duplicated Python checks: {name}")
            for row in rows:
                positive = expected[row["url"]] == "accept"
                if row.get("expected") != expected[row["url"]] or type(row.get("passed")) is not bool:
                    raise EvidenceError("Python check has an invalid expectation or verdict")
                accepted_transport = (
                    row.get("transport") == "grpc" and row.get("tls_established") is True
                    and isinstance(row.get("grpc_status"), str)
                ) if name == "grpc" else (
                    type(row.get("http_status")) is int and 200 <= row["http_status"] < 400
                )
                actual_pass = (
                    row.get("result") == "accepted" and accepted_transport
                ) if positive else (
                    row.get("result") == "issuer_rejected" and row.get("issuer_rejected") is True
                )
                if row["passed"] != actual_pass:
                    raise EvidenceError("Python verdict contradicts the recorded TLS result")
                exposed |= not positive and row.get("result") == "accepted"
                inconclusive |= not actual_pass and not (not positive and row.get("result") == "accepted")
        inconclusive |= bool(data.get("initialization_errors"))
        all_passed = not exposed and not inconclusive
        if type(data.get("passed")) is not bool or data["passed"] != all_passed:
            raise EvidenceError("Python overall verdict contradicts its checks")
    else:
        rows = [json.loads(line) for line in stdout.splitlines() if line.strip()]
        expected = hosts | {"dev.azure.com"}
        if len(rows) != 13 or {row.get("host") for row in rows} != expected:
            raise EvidenceError("Incomplete or duplicated Node checks")
        issuer_errors = {
            "CERT_REVOKED", "UNABLE_TO_GET_ISSUER_CERT_LOCALLY",
            "UNABLE_TO_VERIFY_LEAF_SIGNATURE", "SELF_SIGNED_CERT_IN_CHAIN",
        }
        for row in rows:
            positive = row["host"] == "dev.azure.com"
            actual_pass = row.get("result") == "TLS_ACCEPTED" if positive else row.get("result") in issuer_errors
            if type(row.get("passed")) is not bool or row["passed"] != actual_pass:
                raise EvidenceError("Node verdict contradicts the recorded TLS result")
            exposed |= not positive and row.get("result") == "TLS_ACCEPTED"
            inconclusive |= not actual_pass and not (not positive and row.get("result") == "TLS_ACCEPTED")
        all_passed = not exposed and not inconclusive
        data = {"checks": rows, "passed": all_passed}
    if returncode not in (0, 1, 2) or (returncode == 0) != all_passed:
        raise EvidenceError("Runtime process exit contradicts its qualification evidence")
    if returncode == 2:
        inconclusive = True
    return {"status": "error" if inconclusive else "exposed" if exposed else "passed", "evidence": data}


def librdkafka_classification(data, returncode, source_digest, binding_version):
    from librdkafka_probe import classify, fixture_certificates

    fixtures = fixture_certificates(DIRECTORY / "fixtures")
    checks = data.get("checks", [])
    if len(checks) != 13 or {row.get("host") for row in checks} != set(fixtures) | {"pypi.org"}:
        raise EvidenceError("Incomplete or duplicated librdkafka checks")
    library = data.get("library", {})
    if (data.get("source_sha256") != source_digest
            or library.get("python_binding_version") != binding_version
            or not library.get("path", "").startswith("/")
            or not re.fullmatch(r"[a-f0-9]{64}", library.get("sha256", ""))
            or not isinstance(library.get("version"), str)
            or type(library.get("version_number")) is not int
            or data.get("operations") != ["metadata"]):
        raise EvidenceError("Invalid librdkafka library/source provenance")
    statuses = []
    for row in checks:
        host = row["host"]
        positive = host == "pypi.org"
        if row.get("default_policy") != {
            "enable.ssl.certificate.verification": "true",
            "ssl.endpoint.identification.algorithm": "https",
        }:
            raise EvidenceError("librdkafka certificate or hostname verification was not preserved")
        status = classify(host, positive, row["verification_events"], row["logs"],
                          row["callback_errors"], fixtures.get(host))
        expected = "accept" if positive else "reject_issuer"
        passed = status == ("accepted" if positive else "issuer_rejected")
        if (row.get("status") != status or row.get("expected") != expected
                or type(row.get("passed")) is not bool or row["passed"] != passed):
            raise EvidenceError("librdkafka verdict contradicts its OpenSSL evidence")
        statuses.append(status)
    inconclusive = bool(data.get("errors")) or "inconclusive" in statuses
    exposed = "exposed" in statuses
    expected_status = "inconclusive" if inconclusive else "exposed" if exposed else "passed"
    expected_exit = 2 if inconclusive else 1 if exposed else 0
    if data.get("status") != expected_status or returncode != expected_exit:
        raise EvidenceError("librdkafka exit/status contradicts its checks")
    return {"status": "error" if inconclusive else expected_status, "evidence": data}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True)
    parser.add_argument("--output", "--output-json", "--outputJSON", dest="output", type=Path, required=True)
    parser.add_argument("--context", default="orbstack")
    parser.add_argument("--runtime", choices=("python", "node", "none"), default="none")
    parser.add_argument("--python-bin", default="python")
    parser.add_argument("--openssl")
    args = parser.parse_args()
    docker = ["docker", "--context", args.context]
    owned_containers = []
    invocation = uuid.uuid4().hex
    report = {
        "image_requested": args.image,
        "docker_context": args.context,
        "checks": [],
        "errors": [],
        "librdkafka": {"status": "not_checked"},
        "scope": {
            "image_filesystem": "never-started container; runtime-injected CA files are not image evidence",
            "hashed_ca_directory": "static default and configured directories; see directory_checks",
            "runtime": args.runtime,
            "live_negative_attribution": "Python and Node endpoint issuer rejection only; peer certificate fingerprints are not recorded",
            "pinned_chain_evidence": "Static store checks verify the exact pinned chains; librdkafka binds verification events to pinned certificate hashes when installed",
            "other_clients_and_explicit_custom_bundles": "not_checked",
        },
    }

    def create(extra):
        result = execute(docker + ["create", "--pull=never", "--platform", "linux/amd64",
                                   "--label", f"quixwork=trust-{invocation}"] + extra)
        identifier = require_success(result, "Create qualification container").strip()
        if not re.fullmatch(r"[a-f0-9]{64}", identifier):
            raise EvidenceError("Docker did not return a container ID")
        owned_containers.append(identifier)
        return identifier

    try:
        report["source_sha256"] = source_hashes(DIRECTORY, args.runtime)
        openssl, version = select_openssl(args.openssl)
        report["openssl"] = version
        check_args = SimpleNamespace(openssl=openssl, fixtures_dir=DIRECTORY / "fixtures")
        roots = chain_check.load_fixtures(check_args.fixtures_dir, openssl)
        inspected = execute(docker + ["image", "inspect", args.image])
        report["image"] = image_evidence(json.loads(require_success(inspected, "Inspect local image")))
        image_id = report["image"]["id"]
        with tempfile.TemporaryDirectory(prefix="quix-image-trust-") as temporary:
            directory = Path(temporary)
            control = directory / "published-roots.pem"
            control.write_text(roots)
            positive = [chain_check.verify_chain(check_args, check_args.fixtures_dir / name,
                                                "-CAfile", control) for name in chain_check.FIXTURES]
            if any(row["status"] != "accepts" for row in positive):
                raise EvidenceError("Published-root positive control did not accept all twelve pinned chains")
            report["positive_control"] = {"status": "passed", "results": positive}
            static = create(["--entrypoint", "/bin/true", image_id])
            report["static_extraction"] = {"container_started": False}
            missing = []
            by_hash = {}
            extraction_index = 0

            def extract_store(source, required, name="os_ca_file", runtime_digest=None):
                nonlocal extraction_index
                destination = directory / f"ca-{extraction_index}.pem"
                extraction_index += 1
                copied = execute(docker + ["cp", "-L", f"{static}:{source}", str(destination)])
                if copied.returncode:
                    absent = re.search(r"could not find the file|no such file or directory", copied.stderr, re.I)
                    if absent and not required:
                        missing.append(source)
                        return
                    require_success(copied, f"Extract CA file {source}")
                if not destination.is_file():
                    raise EvidenceError(f"CA path is not a regular image file: {source}")
                digest = hashlib.sha256(destination.read_bytes()).hexdigest()
                if digest in by_hash:
                    result = dict(by_hash[digest])
                    result["same_content_as"] = result["path"]
                else:
                    result = chain_check.check_store(check_args, destination)
                    result["path"] = source
                    by_hash[digest] = result
                result["path"] = source
                result["name"] = name
                if runtime_digest:
                    result["runtime_sha256"] = runtime_digest
                    result["runtime_content_matches_image"] = runtime_digest == digest
                report["checks"].append(result)

            for source, required in ca_candidates(report["image"]["trust_environment"]).items():
                extract_store(source, required)
            report["static_extraction"]["absent_optional_bundles"] = missing
            if not report["checks"]:
                raise EvidenceError("No CA file could be verified from the image filesystem")
            if args.runtime != "none":
                binary = args.python_bin if args.runtime == "python" else "node"
                script = "/quix-trust/python_probe.py" if args.runtime == "python" else "/quix-trust/node_probe.js"
                command = ["-B", script] if args.runtime == "python" else [script]
                runtime = create([
                    "--memory", "512m", "--cpus", "1", "--pids-limit", "128",
                    "--mount", f"type=bind,source={DIRECTORY},target=/quix-trust,readonly",
                    "--entrypoint", binary, image_id, *command,
                ])
                execution = execute(docker + ["start", "--attach", runtime], timeout=300)
                report["runtime"] = runtime_classification(args.runtime, execution.stdout, execution.returncode)
                report["runtime"]["stderr"] = execution.stderr[-4000:]
                report["runtime"]["exit_code"] = execution.returncode
                if args.runtime == "python":
                    for name, source, runtime_digest in python_static_bundles(report["runtime"]):
                        extract_store(source, True, name, runtime_digest)
                    packages = report["runtime"]["evidence"]["metadata"]["packages"]
                    if "confluent-kafka" in packages:
                        native = create([
                            "--memory", "512m", "--cpus", "1", "--pids-limit", "128",
                            "--mount", f"type=bind,source={DIRECTORY},target=/quix-trust,readonly",
                            "--entrypoint", args.python_bin, image_id,
                            "-B", "/quix-trust/librdkafka_probe.py",
                        ])
                        native_run = execute(docker + ["start", "--attach", native], timeout=180)
                        native_data = json.loads(native_run.stdout)
                        report["librdkafka"] = {"evidence": native_data, "exit_code": native_run.returncode}
                        report["librdkafka"].update(librdkafka_classification(
                            native_data, native_run.returncode,
                            report["source_sha256"]["librdkafka_probe.py"], packages["confluent-kafka"],
                        ))
                        report["librdkafka"]["stderr"] = native_run.stderr[-4000:]
                    else:
                        report["librdkafka"] = {"status": "not_installed"}
            else:
                report["runtime"] = {"status": "not_checked"}
            directory_output = directory / "directories.json"
            directory_check = execute([
                sys.executable, "-B", str(DIRECTORY / "check_directories.py"),
                "--image", image_id, "--context", args.context,
                "--output", str(directory_output),
                "--extraction-container", static,
            ], timeout=180)
            directories = json.loads(directory_output.read_text())
            if directories.get("image", {}).get("id") != image_id:
                raise EvidenceError("Directory checks refer to a different image")
            report["directory_checks"] = directories
            if directory_check.returncode not in (0, 1, 2):
                raise EvidenceError("Directory checker failed to complete")
            if directories.get("errors") or directory_check.returncode == 2:
                raise EvidenceError("Static directory checks are inconclusive: "
                                    + str(directories.get("errors")))
        verify_source_hashes(DIRECTORY, report["source_sha256"])
    except (EvidenceError, OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        report["errors"].append({"type": type(error).__name__, "detail": str(error)})
    finally:
        for identifier in reversed(owned_containers):
            try:
                cleanup = execute(docker + ["rm", "--force", "--volumes", identifier])
                require_success(cleanup, "Remove owned qualification container")
            except EvidenceError as error:
                report["errors"].append({"type": "CleanupError", "detail": str(error)})
    exposed = any(row.get("accepted", 0) for row in report["checks"])
    exposed |= any(row.get("accepted", 0) for row in
                   report.get("directory_checks", {}).get("checks", []))
    runtime_status = report.get("runtime", {}).get("status")
    native_status = report["librdkafka"].get("status")
    exposed |= runtime_status == "exposed" or native_status == "exposed"
    failed = bool(report["errors"]) or runtime_status == "error" or native_status == "error"
    exit_code = 2 if failed else 1 if exposed else 0
    report["status"] = "error" if failed else "exposed" if exposed else "passed_selected_checks"
    report["exit_code"] = exit_code
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"image": args.image, "status": report["status"], "evidence": str(args.output)}))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
