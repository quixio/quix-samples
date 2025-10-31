import os
from elasticsearch import Elasticsearch

def main():
    # Elasticsearch connection details
    url = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
    index = os.getenv("ELASTICSEARCH_INDEX", "test_index")
    expected_count = int(os.getenv("TEST_MESSAGE_COUNT", "1"))

    print(f"Connecting to Elasticsearch at {url}")

    # Connect to Elasticsearch
    es = Elasticsearch([url])

    max_attempts = 5
    hits = []
    for attempt in range(max_attempts):
        try:
            # Refresh index to make documents searchable
            es.indices.refresh(index=index)

            # Search for all documents (ES 8.x API)
            result = es.search(index=index, query={"match_all": {}}, size=100)
            hits = result['hits']['hits']

            print(f"Query attempt {attempt + 1}: Found {len(hits)} documents")

            if len(hits) >= expected_count:
                break
            elif attempt < max_attempts - 1:
                print(f"Waiting for more documents... (expected at least {expected_count})")
                import time
                time.sleep(3)
        except Exception as e:
            if attempt < max_attempts - 1:
                print(f"Query attempt {attempt + 1} failed: {e}. Retrying...")
                import time
                time.sleep(3)
            else:
                raise

    actual_count = len(hits)
    print(f"Found {actual_count} documents in Elasticsearch index '{index}'")

    if actual_count < expected_count:
        print(f"FAILED: Expected at least {expected_count} documents, got {actual_count}")
        exit(1)

    docs_to_check = min(len(hits), 3)
    for i in range(docs_to_check):
        doc = hits[i]['_source']
        print(f"Document {i}: {doc}")

        # Check required fields
        if 'id' not in doc:
            print(f"FAILED: Document {i} missing 'id' field")
            exit(1)
        if 'name' not in doc:
            print(f"FAILED: Document {i} missing 'name' field")
            exit(1)
        if 'value' not in doc:
            print(f"FAILED: Document {i} missing 'value' field")
            exit(1)
        if 'time' not in doc:
            print(f"FAILED: Document {i} missing 'time' field (added by transformation)")
            exit(1)

    print(f"Success: Verified {actual_count} documents with correct structure in Elasticsearch")
    exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
