"""Scope a bound blob connection to the live user.

The storage gateway resolves the user from an S3 request whose access key is the
user id and whose secret is that user's token, then limits blob access to that
user's workspaces. This rewrites the platform-injected connection so the shared
``quixportal`` filesystem talks to the gateway as the live user.
"""

from __future__ import annotations

import json


def scope_connection_to_live_user(
    connection_json: str, user_id: str, token: str
) -> str:
    """Return the connection JSON with the S3 credentials set to the live user.

    Leaves non S3-compatible connections untouched.
    """
    connection = json.loads(connection_json)
    s3 = connection.get("S3Compatible")
    if not s3:
        return connection_json
    s3["AccessKeyId"] = user_id
    s3["SecretAccessKey"] = token
    return json.dumps(connection)
