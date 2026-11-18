from pathlib import Path
import unittest

from librdkafka_probe import classify, fixture_certificates, original_verdict


HOST = "dv-g3b-emudhra.we-have-a-problem.com"
FIXTURE = {"leaf_sha256": "leaf", "chain_sha256": ["leaf", "intermediate"]}


def logs(host=HOST, verified=False):
    result = [{"facility": "ENDPOINT", "message": "Enabled endpoint identification using hostname " + host}]
    if verified:
        result.append({"facility": "SSLVERIFY", "message": "Broker SSL certificate verified"})
    return result


def event(code=20, digest="intermediate", depth=1, host=HOST):
    return {"broker": host + ":443", "depth": depth, "x509_error": code, "sha256": digest}


class NativeVerifierTests(unittest.TestCase):
    def test_callback_preserves_every_nonzero_error(self):
        for code in range(-1, 101):
            with self.subTest(code=code):
                self.assertEqual(original_verdict(code), 1 if code == 0 else 0)

    def test_positive_requires_final_tls_and_hostname_success(self):
        self.assertEqual(classify("pypi.org", True, [event(0, host="pypi.org")], logs("pypi.org", True), [], None), "accepted")
        self.assertEqual(classify("pypi.org", True, [event(0, host="pypi.org")], logs("pypi.org", False), [], None), "inconclusive")

    def test_exact_issuer_error_and_fixture_match_pass(self):
        self.assertEqual(classify(HOST, False, [event()], logs(), [], FIXTURE), "issuer_rejected")

    def test_expiry_hostname_and_generic_failure_do_not_pass(self):
        for code in (0, 9, 10, 62):
            with self.subTest(code=code):
                self.assertEqual(classify(HOST, False, [event(code)], logs(), [], FIXTURE), "inconclusive")

    def test_unrelated_certificate_or_broker_does_not_pass(self):
        for record in (event(digest="unrelated"), event(host="different.example")):
            self.assertEqual(classify(HOST, False, [record], logs(), [], FIXTURE), "inconclusive")

    def test_missing_hostname_or_callback_failure_does_not_pass(self):
        self.assertEqual(classify(HOST, False, [event()], [], [], FIXTURE), "inconclusive")
        self.assertEqual(classify(HOST, False, [event()], logs(), ["error"], FIXTURE), "inconclusive")

    def test_accepted_fixture_leaf_is_exposure(self):
        self.assertEqual(classify(HOST, False, [event(0, "leaf", 0)], logs(verified=True), [], FIXTURE), "exposed")
        self.assertEqual(classify(HOST, False, [event(0, "changed-leaf", 0)], logs(verified=True), [], FIXTURE), "inconclusive")

    def test_all_checked_in_fixtures_are_hash_verified(self):
        fixtures = fixture_certificates(Path(__file__).with_name("fixtures"))
        self.assertEqual(len(fixtures), 12)
        self.assertTrue(all(value["leaf_sha256"] in value["chain_sha256"] for value in fixtures.values()))


if __name__ == "__main__":
    unittest.main()
