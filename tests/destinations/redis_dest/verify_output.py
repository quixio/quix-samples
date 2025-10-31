import redis
import json
import sys
import time

def main():
    r = redis.Redis(host='redis', port=6379, decode_responses=True)

    expected_count = 1
    max_attempts = 20
    found_count = 0

    print("Checking Redis for stored keys with retry...")

    # Retry logic with polling
    for attempt in range(max_attempts):
        found_count = 0

        # Check for keys with the expected prefix (check up to 5 possible keys)
        for i in range(5):
            key = f"test:msg_{i}"
            value = r.get(key)

            if value:
                found_count += 1
                print(f"Found key '{key}': {value}")

                # Verify it's valid JSON
                try:
                    data = json.loads(value)
                    if 'id' not in data:
                        print(f"ERROR: Key '{key}' missing 'id' field")
                        sys.exit(1)
                except json.JSONDecodeError:
                    print(f"ERROR: Key '{key}' contains invalid JSON")
                    sys.exit(1)

        if found_count >= expected_count:
            print(f"Success: Found {found_count} keys in Redis")
            sys.exit(0)

        print(f"Attempt {attempt + 1}/{max_attempts}: Found {found_count} keys, waiting...")
        time.sleep(2)

    print(f"FAILED: Only found {found_count} keys after {max_attempts} attempts")
    sys.exit(1)

if __name__ == "__main__":
    main()
