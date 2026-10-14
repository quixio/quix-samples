
def assert_messages_match(actual_messages, expected_messages):
    """
    Assert that actual messages match expected messages.
    Messages are grouped by key and order is verified within each key.

    Args:
        actual_messages: List of messages from Application.run()
        expected_messages: List of expected message dicts with '_key', 'start', 'end', 'value'
    """
    # Assert we got the expected number of messages
    assert len(actual_messages) == len(expected_messages), \
        f"Expected {len(expected_messages)} messages, got {len(actual_messages)}"

    print(f"\n✓ Received {len(actual_messages)} messages")

    # Group actual messages by key
    actual_by_key = {}
    for msg in actual_messages:
        key = msg["_key"].decode('utf-8') if isinstance(msg["_key"], bytes) else msg["_key"]
        if key not in actual_by_key:
            actual_by_key[key] = []
        actual_by_key[key].append(msg)

    # Group expected messages by key
    expected_by_key = {}
    for msg in expected_messages:
        key = msg["_key"]
        if key not in expected_by_key:
            expected_by_key[key] = []
        expected_by_key[key].append(msg)

    # Assert same keys exist
    assert set(actual_by_key.keys()) == set(expected_by_key.keys()), \
        f"Key mismatch: expected keys {set(expected_by_key.keys())}, got {set(actual_by_key.keys())}"

    # Verify messages for each key in order
    for key in sorted(expected_by_key.keys()):
        actual_msgs = actual_by_key[key]
        expected_msgs = expected_by_key[key]

        print(f"\n--- Verifying messages for key: {key} ---")

        assert len(actual_msgs) == len(expected_msgs), \
            f"Key '{key}': expected {len(expected_msgs)} messages, got {len(actual_msgs)}"

        for i, (actual, expected) in enumerate(zip(actual_msgs, expected_msgs)):
            print(f"\nMessage {i + 1} for key '{key}':")
            print(f"  Expected: start={expected['start']}, end={expected['end']}, value={expected['value']}")
            print(f"  Actual:   start={actual['start']}, end={actual['end']}, value={actual['value']}")

            assert actual["start"] == expected["start"], \
                f"Key '{key}' message {i+1}: start mismatch - expected {expected['start']}, got {actual['start']}"
            assert actual["end"] == expected["end"], \
                f"Key '{key}' message {i+1}: end mismatch - expected {expected['end']}, got {actual['end']}"
            assert actual["value"] == expected["value"], \
                f"Key '{key}' message {i+1}: value mismatch - expected {expected['value']}, got {actual['value']}"

            print(f"  ✓ Match!")

    print(f"\n✓ All assertions passed!")
    print(f"✓ All {len(expected_messages)} messages matched expected output across {len(expected_by_key)} keys")
