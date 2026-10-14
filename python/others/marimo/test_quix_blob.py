"""Smallest check that the live-user credential swap keeps working."""

import json

from quix_blob import scope_connection_to_live_user

USER_ID = "3f2504e0-4f89-41d3-9a0c-0305e82c3301"
TOKEN = "live-user-token"

CONNECTION = json.dumps(
    {
        "Provider": "S3",
        "S3Compatible": {
            "BucketName": "quix-bucket",
            "AccessKeyId": "MINTED-KEY",
            "SecretAccessKey": "minted-secret",
            "ServiceUrl": "https://gateway.example",
        },
    }
)


def test_swaps_in_live_user_credentials():
    scoped = json.loads(
        scope_connection_to_live_user(CONNECTION, USER_ID, TOKEN)
    )
    assert scoped["S3Compatible"]["AccessKeyId"] == USER_ID
    assert scoped["S3Compatible"]["SecretAccessKey"] == TOKEN


def test_non_s3_connection_untouched():
    azure = json.dumps({"Provider": "Azure", "AzureBlobStorage": {"Key": "x"}})
    assert scope_connection_to_live_user(azure, USER_ID, TOKEN) == azure


if __name__ == "__main__":
    test_swaps_in_live_user_credentials()
    test_non_s3_connection_untouched()
    print("ok")
