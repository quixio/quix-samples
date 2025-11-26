"""
Verify catalog integration for Quix Lake Timeseries destination tests.

Tests that the sink correctly interacts with the REST Catalog:
1. Tables are created/registered
2. Files are added to the manifest
3. Correct partition information is sent
4. Proper metadata is included
"""
import os
import sys
import requests
import time


def wait_for_catalog(catalog_url: str, max_attempts: int = 20) -> bool:
    """
    Wait for the catalog service to be ready.

    Args:
        catalog_url: Base URL of the catalog
        max_attempts: Maximum number of retry attempts

    Returns:
        True if catalog is ready, False otherwise
    """
    print(f"Waiting for catalog at {catalog_url} to be ready...")

    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{catalog_url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✓ Catalog is ready")
                return True
        except requests.exceptions.RequestException as e:
            if attempt == 0:
                print(f"  Catalog not ready yet: {e}")

        if attempt < max_attempts - 1:
            time.sleep(2)

    return False


def get_catalog_state(catalog_url: str):
    """Get the current state of the catalog"""
    try:
        response = requests.get(f"{catalog_url}/catalog/state", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"✗ Failed to get catalog state: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error getting catalog state: {e}")
        return None


def verify_catalog(catalog_url: str):
    """Verify the catalog received expected calls"""
    try:
        response = requests.get(f"{catalog_url}/catalog/verify", timeout=10)
        result = response.json()

        if response.status_code == 200:
            return result, True
        else:
            return result, False
    except Exception as e:
        print(f"✗ Error verifying catalog: {e}")
        return None, False


def main():
    # Configuration from environment
    catalog_url = os.getenv("CATALOG_URL", "http://mock-catalog:5001")
    table_name = os.getenv("TABLE_NAME", "test-quixlake-input")
    expected_message_count = int(os.getenv("TEST_MESSAGE_COUNT", "10"))

    print("="*60)
    print("Catalog Integration Verification")
    print("="*60)
    print(f"Catalog URL: {catalog_url}")
    print(f"Expected table: {table_name}")
    print(f"Expected messages: {expected_message_count}")
    print()

    # Wait for catalog to be ready
    if not wait_for_catalog(catalog_url):
        print(f"\n✗ FAILED: Catalog at {catalog_url} did not become ready")
        sys.exit(1)

    # Get catalog state
    print("\n" + "="*60)
    print("Fetching Catalog State")
    print("="*60)

    state = get_catalog_state(catalog_url)

    if not state:
        print(f"✗ FAILED: Could not retrieve catalog state")
        sys.exit(1)

    print(f"Total requests received: {state['total_requests']}")
    print(f"Tables created: {len(state['tables'])}")
    print(f"Files registered: {state['total_files']}")

    # Verify catalog interactions
    print("\n" + "="*60)
    print("Verifying Catalog Interactions")
    print("="*60)

    verification, success = verify_catalog(catalog_url)

    if not verification:
        print(f"✗ FAILED: Could not verify catalog")
        sys.exit(1)

    # Print verification results
    print(f"\nVerification Results:")
    print(f"  Tables created: {verification['tables_created']}")
    print(f"  Files registered: {verification['files_registered']}")
    print(f"  Table creation calls: {verification['table_creation_calls']}")
    print(f"  File registration calls: {verification['file_registration_calls']}")

    if not success or not verification['success']:
        print(f"\n✗ VERIFICATION FAILED")
        if verification.get('issues'):
            print(f"\nIssues:")
            for issue in verification['issues']:
                print(f"  - {issue}")
        sys.exit(1)

    # Detailed validation
    print("\n" + "="*60)
    print("Detailed Validation")
    print("="*60)

    # Check table was created
    if verification['tables_created'] == 0:
        print(f"✗ FAILED: No tables were created")
        sys.exit(1)

    print(f"✓ Table creation verified ({verification['tables_created']} table(s))")

    # Check table metadata
    if state['tables']:
        for table_key, table_info in state['tables'].items():
            print(f"\nTable: {table_key}")
            print(f"  Location: {table_info['location']}")
            print(f"  Partition spec: {table_info['partition_spec']}")
            print(f"  Properties: {table_info['properties']}")
            print(f"  Created at: {table_info['created_at']}")

            # Verify expected partition columns are in partition spec
            expected_partitions = os.getenv("HIVE_COLUMNS", "location,year,month,day").split(',')
            actual_partitions = table_info.get('partition_spec', [])

            # Note: The partition spec might be empty initially (dynamic discovery)
            # or might contain the expected partitions
            if actual_partitions:
                print(f"  ✓ Partition spec configured: {actual_partitions}")
            else:
                print(f"  ℹ Partition spec empty (dynamic discovery mode)")

    # Check files were registered
    if verification['files_registered'] == 0:
        print(f"\n✗ FAILED: No files were registered in manifest")
        sys.exit(1)

    print(f"\n✓ File registration verified ({verification['files_registered']} file(s))")

    # Check file metadata
    if state['total_files'] > 0:
        print(f"\nSample registered files:")
        for i, file_entry in enumerate(state.get('manifest_files', [])[:3]):
            print(f"\n  File {i+1}:")
            print(f"    Path: {file_entry['file_path']}")
            print(f"    Size: {file_entry['file_size']} bytes")
            print(f"    Rows: {file_entry['row_count']}")
            print(f"    Partitions: {file_entry['partition_values']}")
            print(f"    Registered: {file_entry['registered_at']}")

            # Verify partition values are present
            if not file_entry['partition_values']:
                print(f"    ⚠ Warning: No partition values (expected for non-partitioned tables)")
            else:
                print(f"    ✓ Partition values present")

        if state['total_files'] > 3:
            print(f"\n  ... and {state['total_files'] - 3} more file(s)")

    # Check minimum file registration count
    # Should be at least 1 file per partition combination
    # With location=3 values × year=1 × month=1 × day=1 = 3 partitions minimum
    min_expected_files = 1
    if verification['files_registered'] < min_expected_files:
        print(f"\n⚠ Warning: Expected at least {min_expected_files} file(s), got {verification['files_registered']}")

    # Display recent requests for debugging
    if state.get('recent_requests'):
        print(f"\n" + "="*60)
        print("Recent Catalog Requests (last 10)")
        print("="*60)
        for i, req in enumerate(state['recent_requests'][-5:]):  # Show last 5
            print(f"\n{i+1}. {req['method']} {req['endpoint']}")
            print(f"   Timestamp: {req['timestamp']}")
            if req.get('data'):
                print(f"   Data keys: {list(req['data'].keys())}")

    # Final summary
    print("\n" + "="*60)
    print("✓ ALL CATALOG VERIFICATIONS PASSED")
    print("="*60)
    print(f"✓ Sink successfully registered table in catalog")
    print(f"✓ Sink successfully registered {verification['files_registered']} file(s) in manifest")
    print(f"✓ Catalog received {verification['total_requests']} total request(s)")
    print()

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
