import os
import requests
import hmac
import hashlib
import json
import time

def compute_signature(payload_bytes, secret):
    """Compute HMAC-SHA1 signature like Segment does"""
    secret_bytes = bytearray(secret, "utf-8")
    return hmac.new(secret_bytes, payload_bytes, hashlib.sha1).hexdigest()

def main():
    webhook_host = os.getenv("WEBHOOK_HOST", "segment-webhook")
    webhook_port = int(os.getenv("WEBHOOK_PORT", "80"))
    shared_secret = os.getenv("SHARED_SECRET", "test_secret_key_123")
    message_count = int(os.getenv("TEST_MESSAGE_COUNT", "3"))

    base_url = f"http://{webhook_host}:{webhook_port}"

    print(f"Sending {message_count} webhook requests to {base_url}/webhook")

    for i in range(message_count):
        # Create Segment-like event payload
        payload = {
            "type": "track",
            "event": "Test Event",
            "userId": f"user_{i}",
            "properties": {
                "test_id": i,
                "message": f"test_message_{i}"
            },
            "timestamp": int(time.time() * 1000)
        }

        payload_json = json.dumps(payload)
        payload_bytes = payload_json.encode('utf-8')

        # Compute HMAC signature
        signature = compute_signature(payload_bytes, shared_secret)

        url = f"{base_url}/webhook"
        headers = {
            "Content-Type": "application/json",
            "x-signature": signature
        }

        print(f"POST {url} with signature {signature[:10]}... -> {payload}")

        response = requests.post(url, data=payload_bytes, headers=headers)

        if response.status_code != 200:
            print(f"FAILED: Expected HTTP 200, got {response.status_code}")
            print(f"Response: {response.text}")
            exit(1)

        time.sleep(0.1)

    print(f"Successfully sent {message_count} webhook requests")

    # Test invalid signature
    print("\nTesting invalid signature (should return 401)...")
    payload = {"type": "test", "invalid": True}
    payload_bytes = json.dumps(payload).encode('utf-8')

    url = f"{base_url}/webhook"
    headers = {
        "Content-Type": "application/json",
        "x-signature": "invalid_signature"
    }

    response = requests.post(url, data=payload_bytes, headers=headers)

    if response.status_code == 401:
        print("✓ Invalid signature correctly rejected with 401")
    else:
        print(f"WARNING: Expected 401 for invalid signature, got {response.status_code}")

    exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
