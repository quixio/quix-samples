import os
import requests

def main():
    host = os.getenv("CSV_SOURCE_HOST", "csv-source")
    port = int(os.getenv("CSV_SOURCE_PORT", "80"))
    csv_path = "/tests/test_data.csv"

    base_url = f"http://{host}:{port}"

    print(f"Uploading {csv_path} to {base_url}/upload")

    with open(csv_path, "rb") as f:
        response = requests.post(
            f"{base_url}/upload",
            files={"file": ("test_data.csv", f, "text/csv")},
        )

    if response.status_code != 200:
        print(f"FAILED: HTTP {response.status_code} - {response.text}")
        exit(1)

    result = response.json()
    print(f"Upload response: {result}")

    rows_sent = result.get("rows_sent", 0)
    if rows_sent < 1:
        print(f"FAILED: Expected rows_sent > 0, got {rows_sent}")
        exit(1)

    print(f"Successfully uploaded CSV with {rows_sent} rows")
    exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
