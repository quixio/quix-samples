import redis
import sys
import time

def main():
    r = redis.Redis(host='redis', port=6379, decode_responses=True)

    expected_count = 1
    max_attempts = 20
    found_count = 0

    print("Checking Redis for stored TimeSeries keys with retry...")

    for attempt in range(max_attempts):
        found_count = 0

        # The app stores keys as {prefix}:{key}:{m}
        # Test data uses key=sensor_0..2, m=temperature
        for i in range(3):
            key = f"test:sensor_{i}:temperature"
            try:
                info = r.ts().info(key)
                if info:
                    found_count += 1
                    last = r.ts().get(key)
                    print(f"Found TimeSeries key '{key}': last={last}")
            except redis.exceptions.ResponseError:
                pass

        if found_count >= expected_count:
            print(f"Success: Found {found_count} TimeSeries keys in Redis")
            sys.exit(0)

        print(f"Attempt {attempt + 1}/{max_attempts}: Found {found_count} keys, waiting...")
        time.sleep(2)

    print(f"FAILED: Only found {found_count} keys after {max_attempts} attempts")
    sys.exit(1)

if __name__ == "__main__":
    main()
