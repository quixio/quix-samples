import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import chain_check
from check_image import (
    EvidenceError,
    ca_candidates,
    image_evidence,
    librdkafka_classification,
    python_static_bundles,
    runtime_classification,
    verify_source_hashes,
)


def python_evidence():
    checks = [{
        "client": "stdlib", "url": "https://pypi.org/", "expected": "accept",
        "result": "accepted", "http_status": 200, "passed": True,
    }]
    checks.extend({
        "client": "stdlib", "url": "https://" + name[:-4] + "/",
        "expected": "reject_issuer", "result": "issuer_rejected",
        "issuer_rejected": True, "passed": True,
    } for name in chain_check.FIXTURES)
    return {
        "checks": checks, "passed": True,
        "skipped_clients": ["requests", "httpx", "botocore", "grpc"],
        "initialization_errors": [], "metadata": {"packages": {}},
    }


def node_evidence():
    rows = [{"node": "v22.23.4", "host": "dev.azure.com", "passed": True, "result": "TLS_ACCEPTED"}]
    rows.extend({
        "node": "v22.23.4", "host": name[:-4], "passed": True,
        "result": "UNABLE_TO_GET_ISSUER_CERT_LOCALLY",
    } for name in chain_check.FIXTURES)
    return rows


def json_lines(rows):
    return "\n".join(json.dumps(row) for row in rows)


class RuntimeEvidenceTests(unittest.TestCase):
    def test_complete_python_evidence_passes(self):
        result = runtime_classification("python", json.dumps(python_evidence()), 0)
        self.assertEqual(result["status"], "passed")

    def test_accepted_python_chain_is_exposure(self):
        data = python_evidence()
        data["checks"][1].update(result="accepted", http_status=200, passed=False, issuer_rejected=False)
        data["passed"] = False
        self.assertEqual(runtime_classification("python", json.dumps(data), 1)["status"], "exposed")

    def test_python_timeout_is_inconclusive(self):
        data = python_evidence()
        data["checks"][1].update(result="inconclusive", passed=False, issuer_rejected=False)
        data["passed"] = False
        self.assertEqual(runtime_classification("python", json.dumps(data), 1)["status"], "error")

    def test_missing_or_duplicated_python_chain_is_rejected(self):
        for duplicate in (False, True):
            with self.subTest(duplicate=duplicate):
                data = python_evidence()
                data["checks"].pop()
                if duplicate:
                    data["checks"].append(copy.deepcopy(data["checks"][1]))
                with self.assertRaises(EvidenceError):
                    runtime_classification("python", json.dumps(data), 0)

    def test_installed_python_client_cannot_be_skipped(self):
        data = python_evidence()
        data["metadata"]["packages"]["requests"] = "2.32.5"
        with self.assertRaisesRegex(EvidenceError, "installed"):
            runtime_classification("python", json.dumps(data), 0)

    def test_installed_grpc_cannot_be_skipped(self):
        data = python_evidence()
        data["metadata"]["packages"]["grpcio"] = "1.84.1"
        with self.assertRaisesRegex(EvidenceError, "installed"):
            runtime_classification("python", json.dumps(data), 0)

    def test_grpc_requires_authenticated_transport_evidence(self):
        data = python_evidence()
        grpc_checks = copy.deepcopy(data["checks"])
        for row in grpc_checks:
            row["client"] = "grpc"
        positive = grpc_checks[0]
        positive.pop("http_status")
        positive.update(url="https://pubsub.googleapis.com/", transport="grpc",
                        tls_established=True, grpc_status="UNIMPLEMENTED")
        data["checks"].extend(grpc_checks)
        data["skipped_clients"].remove("grpc")
        self.assertEqual(runtime_classification("python", json.dumps(data), 0)["status"], "passed")
        positive["tls_established"] = False
        with self.assertRaisesRegex(EvidenceError, "contradicts"):
            runtime_classification("python", json.dumps(data), 0)

    def test_python_return_code_must_match_evidence(self):
        with self.assertRaisesRegex(EvidenceError, "exit"):
            runtime_classification("python", json.dumps(python_evidence()), 1)

    def test_python_check_verdict_must_match_result(self):
        data = python_evidence()
        data["checks"][1]["result"] = "inconclusive"
        with self.assertRaisesRegex(EvidenceError, "contradicts"):
            runtime_classification("python", json.dumps(data), 0)

    def test_python_bool_verdict_is_strict(self):
        data = python_evidence()
        data["checks"][1]["passed"] = "true"
        with self.assertRaises(EvidenceError):
            runtime_classification("python", json.dumps(data), 0)

    def test_complete_node_evidence_passes(self):
        self.assertEqual(runtime_classification("node", json_lines(node_evidence()), 0)["status"], "passed")

    def test_node_expiry_is_not_a_successful_rejection(self):
        rows = node_evidence()
        rows[1].update(result="CERT_HAS_EXPIRED", passed=False)
        self.assertEqual(runtime_classification("node", json_lines(rows), 1)["status"], "error")

    def test_node_accepted_chain_is_exposure(self):
        rows = node_evidence()
        rows[1].update(result="TLS_ACCEPTED", passed=False)
        self.assertEqual(runtime_classification("node", json_lines(rows), 1)["status"], "exposed")

    def test_node_missing_positive_control_is_rejected(self):
        with self.assertRaises(EvidenceError):
            runtime_classification("node", json_lines(node_evidence()[1:]), 0)


class ImageAndSourceTests(unittest.TestCase):
    def test_installed_python_bundles_require_static_paths(self):
        runtime = {"evidence": {"metadata": {
            "packages": {"certifi": "2026.10.19", "pip": "26.2.2"},
            "bundles": {
                "certifi": {"path": "/python/certifi/cacert.pem", "sha256": "a" * 64},
                "pip._vendor.certifi": {"path": "/python/pip/_vendor/certifi/cacert.pem", "sha256": "b" * 64},
            },
        }}}
        self.assertEqual(len(python_static_bundles(runtime)), 2)
        del runtime["evidence"]["metadata"]["bundles"]["pip._vendor.certifi"]
        with self.assertRaisesRegex(EvidenceError, "Installed pip"):
            python_static_bundles(runtime)

    def test_only_allowlisted_image_environment_is_saved(self):
        inspected = [{
            "Id": "sha256:" + "a" * 64, "Os": "linux", "Architecture": "amd64",
            "RepoDigests": ["example@sha256:" + "b" * 64],
            "Config": {"Env": ["SECRET_TOKEN=do-not-save", "SSL_CERT_FILE=/fixed.pem"]},
        }]
        result = image_evidence(inspected)
        self.assertEqual(result["trust_environment"], {"SSL_CERT_FILE": "/fixed.pem"})
        self.assertNotIn("do-not-save", json.dumps(result))
        inspected[0]["Architecture"] = "arm64"
        with self.assertRaisesRegex(EvidenceError, "amd64"):
            image_evidence(inspected)

    def test_explicit_ca_file_is_required_and_must_be_absolute(self):
        self.assertTrue(ca_candidates({"SSL_CERT_FILE": "/fixed.pem"})["/fixed.pem"])
        with self.assertRaises(EvidenceError):
            ca_candidates({"SSL_CERT_FILE": "relative.pem"})

    def test_source_mutation_is_detected(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            path = directory / "probe.py"
            path.write_bytes(b"original source")
            expected = {"probe.py": hashlib.sha256(path.read_bytes()).hexdigest()}
            verify_source_hashes(directory, expected)
            path.write_bytes(b"modified source")
            with self.assertRaisesRegex(EvidenceError, "changed"):
                verify_source_hashes(directory, expected)


class LibrdkafkaEvidenceTests(unittest.TestCase):
    def evidence(self):
        from librdkafka_probe import fixture_certificates

        fixtures = fixture_certificates(Path(__file__).with_name("fixtures"))
        checks = []
        for host in ["pypi.org", *fixtures]:
            positive = host == "pypi.org"
            logs = [{"facility": "ENDPOINT", "message": "Enabled endpoint identification using hostname " + host}]
            if positive:
                logs.append({"facility": "SSLVERIFY", "message": "Broker SSL certificate verified"})
            checks.append({
                "host": host, "expected": "accept" if positive else "reject_issuer",
                "status": "accepted" if positive else "issuer_rejected", "passed": True,
                "default_policy": {"enable.ssl.certificate.verification": "true", "ssl.endpoint.identification.algorithm": "https"},
                "verification_events": [{
                    "broker": host + ":443", "depth": 1, "x509_error": 0 if positive else 20,
                    "sha256": "positive" if positive else fixtures[host]["chain_sha256"][1],
                }],
                "logs": logs, "callback_errors": [],
            })
        return {
            "checks": checks, "errors": [], "status": "passed", "operations": ["metadata"],
            "source_sha256": "a" * 64,
            "library": {"path": "/package/librdkafka.so", "sha256": "b" * 64,
                        "version": "2.12.1", "version_number": 34341375, "python_binding_version": "2.12.1"},
        }

    def test_complete_native_evidence_passes(self):
        self.assertEqual(librdkafka_classification(self.evidence(), 0, "a" * 64, "2.12.1")["status"], "passed")

    def test_modified_verification_policy_is_rejected(self):
        data = self.evidence()
        data["checks"][1]["default_policy"]["ssl.endpoint.identification.algorithm"] = "none"
        with self.assertRaisesRegex(EvidenceError, "preserved"):
            librdkafka_classification(data, 0, "a" * 64, "2.12.1")

    def test_native_source_and_exit_must_match_evidence(self):
        with self.assertRaisesRegex(EvidenceError, "provenance"):
            librdkafka_classification(self.evidence(), 0, "c" * 64, "2.12.1")
        with self.assertRaisesRegex(EvidenceError, "exit/status"):
            librdkafka_classification(self.evidence(), 1, "a" * 64, "2.12.1")

    def test_expiration_cannot_be_reported_as_issuer_rejection(self):
        data = self.evidence()
        data["checks"][1]["verification_events"][0]["x509_error"] = 10
        with self.assertRaisesRegex(EvidenceError, "contradicts"):
            librdkafka_classification(data, 0, "a" * 64, "2.12.1")


if __name__ == "__main__":
    unittest.main()
