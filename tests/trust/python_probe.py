#!/usr/bin/env python3
"""Exercise installed Python TLS clients without credentials or package downloads.

Exit codes: 0 = all applicable checks passed, 1 = failed/inconclusive TLS check,
2 = invalid fixtures or an installed client could not be initialized. Environment
variables selecting the image's CA stores are deliberately preserved.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import re
import ssl
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request


# Expiration, hostname mismatch and general connection errors do not demonstrate
# distrust of a compromised issuer.
ISSUER_VERIFY_CODES = {2, 18, 19, 20, 21, 23, 27, 28}
ISSUER_ERRORS = re.compile(
    r"unable to get (?:local )?issuer certificate|"
    r"unable to verify (?:the )?(?:first certificate|leaf signature)|"
    r"self[- ]signed certificate|certificate (?:revoked|untrusted|rejected)",
    re.IGNORECASE,
)
OTHER_CERT_ERRORS = re.compile(
    r"certificate has expired|certificate is not yet valid|"
    r"hostname mismatch|IP address mismatch|doesn't match|does not match",
    re.IGNORECASE,
)
CA_ENVIRONMENT = (
    "SSL_CERT_FILE",
    "SSL_CERT_DIR",
    "REQUESTS_CA_BUNDLE",
    "PIP_CERT",
    "AWS_CA_BUNDLE",
    "GRPC_DEFAULT_SSL_ROOTS_FILE_PATH",
)
GRPC_POSITIVE_URL = "https://pubsub.googleapis.com/"


def rejection_reason(error: BaseException) -> dict:
    """Unwrap SSL exceptions retained differently by each supported client."""
    pending = [error]
    seen = set()
    codes = set()
    messages = []
    while pending:
        value = pending.pop()
        if id(value) in seen:
            continue
        seen.add(id(value))
        if isinstance(value, BaseException):
            messages.append(str(value))
            code = getattr(value, "verify_code", None)
            if isinstance(code, int):
                codes.add(code)
            pending.extend(value.args)
            pending.extend(
                getattr(value, key, None)
                for key in ("__cause__", "__context__", "reason", "kwargs")
            )
        elif isinstance(value, dict):
            pending.extend(value.values())
        elif isinstance(value, (tuple, list)):
            pending.extend(value)
        elif isinstance(value, str):
            messages.append(value)
    details = " | ".join(dict.fromkeys(messages))
    if codes:
        rejected = bool(codes) and codes <= ISSUER_VERIFY_CODES
    else:
        rejected = bool(ISSUER_ERRORS.search(details)) and not bool(
            OTHER_CERT_ERRORS.search(details)
        )
    return {
        "issuer_rejected": rejected,
        "verify_codes": sorted(codes),
        "error_type": type(error).__name__,
        "detail": details[:2000],
    }


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def stdlib_client(timeout: float):
    opener = urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=ssl.create_default_context()),
        NoRedirect(),
    )

    def get(url):
        request = urllib.request.Request(url, headers={"User-Agent": "quix-trust-probe"})
        try:
            with opener.open(request, timeout=timeout) as response:
                return response.status
        except urllib.error.HTTPError as error:
            # Even HTTP errors or redirects establish that the TLS handshake
            # succeeded; do not follow a redirect and test a different issuer.
            error.close()
            return error.code

    return get


def requests_client(timeout: float):
    import requests

    def get(url):
        with requests.get(url, timeout=timeout, allow_redirects=False, stream=True) as response:
            return response.status_code

    return get


def httpx_client(timeout: float):
    import httpx

    def get(url):
        with httpx.stream("GET", url, timeout=timeout, follow_redirects=False) as response:
            return response.status_code

    return get


def botocore_client(timeout: float):
    from botocore.awsrequest import AWSRequest
    from botocore.httpsession import URLLib3Session
    from botocore.session import Session

    # This is the same CA setting resolution used to create SDK endpoints; no
    # service client, credential provider or request signing is invoked.
    bundle = Session().get_config_variable("ca_bundle")

    def get(url):
        session = URLLib3Session(verify=bundle or True, timeout=timeout)
        try:
            request = AWSRequest(method="GET", url=url).prepare()
            response = session.send(request)
            try:
                return response.status_code
            finally:
                response.raw.close()
        finally:
            session.close()

    return get


def grpc_client(timeout: float):
    import grpc

    def get(url):
        target = urllib.parse.urlsplit(url)
        if target.scheme != "https" or not target.hostname or target.username or target.password:
            raise ValueError("gRPC probe requires an HTTPS hostname without credentials")
        ready = threading.Event()
        # Default credentials retain gRPC's configured root-file behavior. No
        # access token, client certificate or application metadata is attached.
        channel = grpc.secure_channel(
            f"{target.hostname}:{target.port or 443}", grpc.ssl_channel_credentials(),
        )

        def state_changed(state):
            if state == grpc.ChannelConnectivity.READY:
                ready.set()

        channel.subscribe(state_changed, try_to_connect=True)
        try:
            status = "OK"
            try:
                channel.unary_unary("/grpc.health.v1.Health/Check")(b"", timeout=timeout)
            except grpc.RpcError as error:
                # A valid TLS/HTTP2 transport can return UNIMPLEMENTED for a
                # health service it does not expose. Status codes alone cannot
                # prove TLS: require the channel's authenticated READY state.
                if not ready.wait(0.2):
                    raise
                status = error.code().name
            if not ready.wait(0.2):
                raise RuntimeError("gRPC transport did not report authenticated readiness")
            return {"transport": "grpc", "tls_established": True, "grpc_status": status}
        finally:
            channel.close()

    return get


def bundle_record(path):
    if not path:
        return None
    result = {"path": str(path)}
    candidate = Path(path)
    if candidate.is_file():
        result["sha256"] = hashlib.sha256(candidate.read_bytes()).hexdigest()
    else:
        result["exists"] = candidate.exists()
    return result


def metadata():
    result = {
        "python": sys.version,
        "openssl": ssl.OPENSSL_VERSION,
        "default_verify_paths": ssl.get_default_verify_paths()._asdict(),
        "ca_environment": {key: os.environ.get(key) for key in CA_ENVIRONMENT},
        "packages": {},
        "bundles": {"os": bundle_record("/etc/ssl/certs/ca-certificates.crt")},
    }
    for package in ("pip", "certifi", "requests", "httpx", "botocore", "grpcio", "pyarrow", "confluent-kafka"):
        try:
            result["packages"][package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            pass
    for module in ("certifi", "pip._vendor.certifi"):
        try:
            imported = __import__(module, fromlist=["where"])
        except ModuleNotFoundError:
            continue
        result["bundles"][module] = bundle_record(imported.where())
        result["packages"][module] = getattr(imported, "__version__", "unknown")
    if importlib.util.find_spec("botocore"):
        import botocore

        result["bundles"]["botocore.embedded"] = bundle_record(Path(botocore.__file__).with_name("cacert.pem"))
        from botocore.session import Session

        result["bundles"]["botocore.configured"] = bundle_record(Session().get_config_variable("ca_bundle"))
    result["bundles"]["grpc.configured"] = bundle_record(os.environ.get("GRPC_DEFAULT_SSL_ROOTS_FILE_PATH"))
    return result


def fixture_hosts(directory: Path):
    manifest = json.loads((directory / "manifest.json").read_text())
    hosts = []
    for name, digest in manifest["files"].items():
        if not name.endswith("-emudhra.we-have-a-problem.com.pem"):
            continue
        if Path(name).name != name or hashlib.sha256((directory / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Invalid chain fixture: {name}")
        hosts.append(name.removesuffix(".pem"))
    if len(hosts) != 12:
        raise ValueError(f"Expected 12 pinned chain fixtures, found {len(hosts)}")
    return sorted(hosts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", type=Path, default=Path(__file__).with_name("fixtures"))
    parser.add_argument("--positive-url", default="https://pypi.org/")
    parser.add_argument("--timeout", type=float, default=10)
    args = parser.parse_args()
    result = {"checks": [], "skipped_clients": [], "initialization_errors": []}
    try:
        if not args.positive_url.startswith("https://") or args.timeout <= 0:
            raise ValueError("A HTTPS positive URL and positive timeout are required")
        hosts = fixture_hosts(args.fixtures)
        result["metadata"] = metadata()
    except Exception as error:
        result["initialization_errors"].append({"error_type": type(error).__name__, "detail": str(error)})
        print(json.dumps(result, indent=2))
        return 2
    factories = {
        "stdlib": stdlib_client,
        "requests": requests_client,
        "httpx": httpx_client,
        "botocore": botocore_client,
        "grpc": grpc_client,
    }
    for name, factory in factories.items():
        if name != "stdlib" and importlib.util.find_spec(name) is None:
            result["skipped_clients"].append(name)
            continue
        try:
            get = factory(args.timeout)
        except Exception as error:
            result["initialization_errors"].append({"client": name, "error_type": type(error).__name__, "detail": str(error)})
            continue
        positive_url = GRPC_POSITIVE_URL if name == "grpc" else args.positive_url
        targets = [(positive_url, True)] + [(f"https://{host}/", False) for host in hosts]
        for url, positive in targets:
            check = {"client": name, "url": url, "expected": "accept" if positive else "reject_issuer"}
            try:
                outcome = get(url)
                if isinstance(outcome, dict):
                    check.update(outcome)
                    check["passed"] = positive and outcome.get("tls_established") is True
                else:
                    check.update({"http_status": outcome, "passed": positive and 200 <= outcome < 400})
                check["result"] = "accepted"
            except Exception as error:
                rejection = rejection_reason(error)
                check.update(rejection)
                check["passed"] = not positive and rejection["issuer_rejected"]
                check["result"] = "issuer_rejected" if rejection["issuer_rejected"] else "inconclusive"
            result["checks"].append(check)
    result["passed"] = bool(result["checks"]) and all(check["passed"] for check in result["checks"]) and not result["initialization_errors"]
    print(json.dumps(result, indent=2))
    if result["initialization_errors"]:
        return 2
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
