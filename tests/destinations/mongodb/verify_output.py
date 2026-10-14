import os
from pymongo import MongoClient

def main():
    # MongoDB connection details
    host = "mongodb"
    port = 27017
    username = "admin"
    password = "password"
    db_name = "testdb"
    collection_name = "testcollection"
    expected_count = 1

    print(f"Connecting to MongoDB at {host}:{port}")

    # Connect to MongoDB
    client = MongoClient(
        host=host,
        port=port,
        username=username,
        password=password
    )

    db = client[db_name]
    collection = db[collection_name]

    # Count documents
    actual_count = collection.count_documents({})
    print(f"Found {actual_count} documents in MongoDB collection '{collection_name}'")

    if actual_count < expected_count:
        print(f"FAILED: Expected at least {expected_count} documents, got {actual_count}")
        exit(1)

    # Verify document structure
    for i, doc in enumerate(collection.find()):
        print(f"Document {i}: id={doc.get('id')}, name={doc.get('name')}, value={doc.get('value')}")

        # Check that required fields exist
        if 'id' not in doc:
            print(f"FAILED: Document {i} missing 'id' field")
            exit(1)
        if 'name' not in doc:
            print(f"FAILED: Document {i} missing 'name' field")
            exit(1)
        if 'value' not in doc:
            print(f"FAILED: Document {i} missing 'value' field")
            exit(1)

    print(f"Success: Verified {actual_count} documents with correct structure in MongoDB")
    client.close()
    exit(0)

if __name__ == "__main__":
    main()
