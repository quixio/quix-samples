FROM python:3.11-slim

WORKDIR /app

# Install asyncua
RUN pip install --no-cache-dir asyncua

# Copy server script
COPY opcua_test_server.py .

# Expose OPC UA port
EXPOSE 4840

# Run the server
CMD ["python", "opcua_test_server.py"]
