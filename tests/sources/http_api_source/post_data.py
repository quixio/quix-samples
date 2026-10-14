import os
import requests
import time

def main():
    http_host = os.getenv("HTTP_API_HOST", "http-api-source")
    http_port = int(os.getenv("HTTP_API_PORT", "80"))
    message_count = int(os.getenv("TEST_MESSAGE_COUNT", "3"))

    base_url = f"http://{http_host}:{http_port}"

    print(f"Posting {message_count} test messages to HTTP API at {base_url}")

    # Post 2 messages without key
    for i in range(2):
        data = {
            "id": i,
            "message": f"test_message_{i}",
            "timestamp": int(time.time() * 1000)
        }

        url = f"{base_url}/data/"
        print(f"POST {url} -> {data}")

        response = requests.post(url, json=data)

        if response.status_code != 200:
            print(f"FAILED: HTTP {response.status_code}")
            exit(1)

        time.sleep(0.1)

    # Post 1 message with key
    data = {
        "id": 2,
        "message": "test_message_2",
        "timestamp": int(time.time() * 1000)
    }

    url = f"{base_url}/data/custom_key"
    print(f"POST {url} -> {data}")

    response = requests.post(url, json=data)

    if response.status_code != 200:
        print(f"FAILED: HTTP {response.status_code}")
        exit(1)

    print(f"Successfully posted {message_count} messages via HTTP")
    exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
