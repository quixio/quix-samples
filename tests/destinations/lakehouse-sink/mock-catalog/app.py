"""
Mock REST Catalog Service for Testing

This service mimics an Iceberg REST Catalog to verify that the QuixLake sink
correctly calls the catalog endpoints with proper data.

It logs all requests and stores them for verification.
"""
from flask import Flask, request, jsonify
import json
import logging
from datetime import datetime

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# In-memory storage for tracking calls
catalog_state = {
    'tables': {},
    'requests': [],
    'manifest_files': []
}


def log_request(endpoint, method, data=None):
    """Log an incoming request for verification"""
    request_info = {
        'timestamp': datetime.utcnow().isoformat(),
        'endpoint': endpoint,
        'method': method,
        'data': data
    }
    catalog_state['requests'].append(request_info)
    logger.info(f"{method} {endpoint}")
    if data:
        logger.info(f"  Data: {json.dumps(data, indent=2)}")


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200


@app.route('/namespaces/<namespace>/tables/<table>', methods=['GET'])
def get_table(namespace, table):
    """Get table metadata"""
    log_request(f'/namespaces/{namespace}/tables/{table}', 'GET')

    table_key = f"{namespace}.{table}"

    if table_key in catalog_state['tables']:
        logger.info(f"  → Table exists: {table_key}")
        return jsonify(catalog_state['tables'][table_key]), 200
    else:
        logger.info(f"  → Table not found: {table_key}")
        return jsonify({'error': 'Table not found'}), 404


@app.route('/namespaces/<namespace>/tables/<table>', methods=['PUT'])
def create_table(namespace, table):
    """Create a new table"""
    data = request.get_json()
    log_request(f'/namespaces/{namespace}/tables/{table}', 'PUT', data)

    table_key = f"{namespace}.{table}"

    # Store the table metadata
    catalog_state['tables'][table_key] = {
        'name': table,
        'namespace': namespace,
        'location': data.get('location'),
        'partition_spec': data.get('partition_spec', []),
        'properties': data.get('properties', {}),
        'created_at': datetime.utcnow().isoformat()
    }

    logger.info(f"  → Table created: {table_key}")
    logger.info(f"  → Location: {data.get('location')}")
    logger.info(f"  → Partitions: {data.get('partition_spec', [])}")

    return jsonify(catalog_state['tables'][table_key]), 201


@app.route('/namespaces/<namespace>/tables/<table>/manifest/add-files', methods=['POST'])
def add_files_to_manifest(namespace, table):
    """Add files to table manifest"""
    data = request.get_json()
    log_request(f'/namespaces/{namespace}/tables/{table}/manifest/add-files', 'POST', data)

    table_key = f"{namespace}.{table}"
    files = data.get('files', [])

    # Store file registrations
    for file_info in files:
        file_entry = {
            'table': table_key,
            'file_path': file_info.get('file_path'),
            'file_size': file_info.get('file_size'),
            'row_count': file_info.get('row_count'),
            'partition_values': file_info.get('partition_values', {}),
            'registered_at': datetime.utcnow().isoformat()
        }
        catalog_state['manifest_files'].append(file_entry)

    logger.info(f"  → Registered {len(files)} file(s) for table {table_key}")
    for i, file_info in enumerate(files[:3]):  # Log first 3 files
        logger.info(f"    File {i+1}: {file_info.get('file_path')}")
        logger.info(f"      Size: {file_info.get('file_size')} bytes")
        logger.info(f"      Rows: {file_info.get('row_count')}")
        logger.info(f"      Partitions: {file_info.get('partition_values', {})}")

    if len(files) > 3:
        logger.info(f"    ... and {len(files) - 3} more file(s)")

    return jsonify({'success': True, 'files_added': len(files)}), 200


@app.route('/catalog/state', methods=['GET'])
def get_catalog_state():
    """Get the current catalog state (for testing/debugging)"""
    return jsonify({
        'tables': catalog_state['tables'],
        'total_requests': len(catalog_state['requests']),
        'total_files': len(catalog_state['manifest_files']),
        'recent_requests': catalog_state['requests'][-10:]  # Last 10 requests
    }), 200


@app.route('/catalog/verify', methods=['GET'])
def verify_catalog():
    """Verify catalog received expected calls"""
    table_count = len(catalog_state['tables'])
    file_count = len(catalog_state['manifest_files'])
    request_count = len(catalog_state['requests'])

    # Check if we received table creation requests
    table_creation_requests = [r for r in catalog_state['requests'] if r['method'] == 'PUT' and '/tables/' in r['endpoint']]

    # Check if we received file registration requests
    file_registration_requests = [r for r in catalog_state['requests'] if 'manifest/add-files' in r['endpoint']]

    verification = {
        'success': True,
        'tables_created': table_count,
        'files_registered': file_count,
        'total_requests': request_count,
        'table_creation_calls': len(table_creation_requests),
        'file_registration_calls': len(file_registration_requests),
        'issues': []
    }

    # Validate we got expected calls
    if table_count == 0:
        verification['success'] = False
        verification['issues'].append('No tables were created')

    if file_count == 0:
        verification['success'] = False
        verification['issues'].append('No files were registered')

    # Log verification results
    logger.info("="*60)
    logger.info("CATALOG VERIFICATION RESULTS")
    logger.info("="*60)
    logger.info(f"Tables created: {table_count}")
    logger.info(f"Files registered: {file_count}")
    logger.info(f"Total requests: {request_count}")
    logger.info(f"Table creation calls: {len(table_creation_requests)}")
    logger.info(f"File registration calls: {len(file_registration_requests)}")

    if verification['success']:
        logger.info("✓ Catalog verification PASSED")
    else:
        logger.info("✗ Catalog verification FAILED")
        for issue in verification['issues']:
            logger.info(f"  - {issue}")

    logger.info("="*60)

    return jsonify(verification), 200 if verification['success'] else 400


if __name__ == '__main__':
    logger.info("Starting Mock REST Catalog...")
    logger.info("Listening on port 5001")
    app.run(host='0.0.0.0', port=5001, debug=False)
