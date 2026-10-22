import hashlib
import json
from pathlib import Path
import ssl
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import urllib.error

from python_probe import fixture_hosts, grpc_client, rejection_reason


class RejectionReasonTests(unittest.TestCase):
    def test_wrapped_issuer_error_passes(self):
        ssl_error = ssl.SSLCertVerificationError("certificate verify failed")
        ssl_error.verify_code = 20
        error = urllib.error.URLError(ssl_error)
        self.assertTrue(rejection_reason(error)["issuer_rejected"])

    def test_wrapped_botocore_error_passes(self):
        error = RuntimeError("SSL validation failed")
        error.kwargs = {"error": ssl.SSLError("unable to get local issuer certificate")}
        self.assertTrue(rejection_reason(error)["issuer_rejected"])

    def test_other_verification_codes_do_not_pass(self):
        for code in (9, 10, 62):
            with self.subTest(code=code):
                error = ssl.SSLCertVerificationError("certificate verify failed")
                error.verify_code = code
                self.assertFalse(rejection_reason(error)["issuer_rejected"])

    def test_connection_and_other_certificate_errors_are_inconclusive(self):
        for message in (
            "timed out",
            "Name or service not known",
            "certificate has expired",
            "certificate is not yet valid",
            "Hostname mismatch",
            "certificate verify failed",
        ):
            with self.subTest(message=message):
                self.assertFalse(rejection_reason(RuntimeError(message))["issuer_rejected"])

    def test_expiration_does_not_pass_due_to_other_context_text(self):
        error = RuntimeError("unable to get local issuer certificate")
        error.__cause__ = ssl.SSLError("certificate has expired")
        self.assertFalse(rejection_reason(error)["issuer_rejected"])

    def test_cyclic_exception_context_terminates(self):
        error = RuntimeError("certificate revoked")
        error.__context__ = error
        self.assertTrue(rejection_reason(error)["issuer_rejected"])


class FixtureTests(unittest.TestCase):
    def test_requires_all_twelve_hash_verified_chains(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            files = {}
            for number in range(12):
                name = f"test-{number}-emudhra.we-have-a-problem.com.pem"
                content = f"fixture {number}".encode()
                (directory / name).write_bytes(content)
                files[name] = hashlib.sha256(content).hexdigest()
            (directory / "manifest.json").write_text(json.dumps({"files": files}))
            self.assertEqual(len(fixture_hosts(directory)), 12)
            (directory / next(iter(files))).write_text("tampered")
            with self.assertRaisesRegex(ValueError, "Invalid chain fixture"):
                fixture_hosts(directory)

    def test_rejects_incomplete_fixture_set(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            (directory / "manifest.json").write_text(json.dumps({"files": {}}))
            with self.assertRaisesRegex(ValueError, "Expected 12"):
                fixture_hosts(directory)


class GrpcProbeTests(unittest.TestCase):
    def fake_grpc(self, ready, message="method not implemented"):
        class RpcError(Exception):
            def code(self):
                return SimpleNamespace(name="UNIMPLEMENTED")

        class Channel:
            closed = False

            def subscribe(self, callback, try_to_connect):
                if ready:
                    callback("ready")

            def unary_unary(self, method):
                self.method = method

                def call(payload, timeout):
                    raise RpcError(message)

                return call

            def close(self):
                self.closed = True

        channel = Channel()
        module = SimpleNamespace(
            RpcError=RpcError, ChannelConnectivity=SimpleNamespace(READY="ready"),
            ssl_channel_credentials=lambda: "default-roots",
            secure_channel=lambda target, credentials: channel,
        )
        return module, channel

    def test_application_error_after_ready_proves_tls(self):
        grpc, channel = self.fake_grpc(True)
        with patch.dict("sys.modules", {"grpc": grpc}):
            outcome = grpc_client(1)("https://pubsub.googleapis.com/")
        self.assertEqual(outcome, {"transport": "grpc", "tls_established": True, "grpc_status": "UNIMPLEMENTED"})
        self.assertEqual(channel.method, "/grpc.health.v1.Health/Check")
        self.assertTrue(channel.closed)

    def test_status_without_ready_does_not_prove_tls(self):
        grpc, channel = self.fake_grpc(False)
        with patch.dict("sys.modules", {"grpc": grpc}):
            with self.assertRaises(grpc.RpcError):
                grpc_client(1)("https://pubsub.googleapis.com/")
        self.assertTrue(channel.closed)

    def test_issuer_rejection_is_preserved_for_classifier(self):
        grpc, channel = self.fake_grpc(False, "SSL certificate verify failed: unable to get local issuer certificate")
        with patch.dict("sys.modules", {"grpc": grpc}):
            with self.assertRaises(grpc.RpcError) as caught:
                grpc_client(1)("https://dv-g3b-emudhra.we-have-a-problem.com/")
        self.assertTrue(rejection_reason(caught.exception)["issuer_rejected"])
        self.assertTrue(channel.closed)


if __name__ == "__main__":
    unittest.main()
