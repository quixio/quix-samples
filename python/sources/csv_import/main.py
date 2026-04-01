import os
import csv
import io
import json
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from quixstreams import Application
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

BATCH_SIZE = int(os.environ.get("batch_size", "10000"))

# Store progress for active uploads: upload_id -> {status, rows_sent, percent, ...}
uploads = {}


@app.get("/", response_class=HTMLResponse)
async def index():
    with open(os.path.join("static", "index.html")) as f:
        return f.read()


@app.post("/upload")
async def upload_csv(request: Request):
    content_type = request.headers.get("content-type", "")
    if "multipart/form-data" not in content_type:
        return {"status": "error", "message": "Expected multipart/form-data"}

    # Client sends upload_id as query param so it can poll progress immediately
    upload_id = request.query_params.get("upload_id", str(uuid.uuid4()))
    content_length = int(request.headers.get("content-length", 0))

    uploads[upload_id] = {"status": "uploading", "rows_sent": 0, "percent": 0}

    topic_name = os.environ.get("output", "csv-data")
    quix_app = Application(
        consumer_group="csv-uploader",
        auto_create_topics=True,
    )
    topic = quix_app.topic(name=topic_name, value_serializer="json")

    buffer = ""
    headers = None
    key = None
    sent = 0
    batch = []
    bytes_received = 0
    filename = "upload"

    boundary = content_type.split("boundary=")[-1].strip()
    in_file = False
    past_headers = False
    producer = quix_app.get_producer()

    async for chunk in request.stream():
        bytes_received += len(chunk)
        text = chunk.decode("utf-8", errors="replace")

        if not in_file:
            if f"--{boundary}" in text:
                in_file = True
                if 'filename="' in text:
                    fn_start = text.index('filename="') + 10
                    fn_end = text.index('"', fn_start)
                    filename = text[fn_start:fn_end]
                    key = os.path.splitext(filename)[0]

                parts = text.split("\r\n\r\n", 1)
                if len(parts) > 1:
                    past_headers = True
                    text = parts[1]
                    if f"\r\n--{boundary}" in text:
                        text = text[:text.index(f"\r\n--{boundary}")]
                else:
                    continue
        else:
            if f"\r\n--{boundary}" in text:
                text = text[:text.index(f"\r\n--{boundary}")]

        if not past_headers:
            if "\r\n\r\n" in text:
                past_headers = True
                text = text.split("\r\n\r\n", 1)[1]
            else:
                continue

        buffer += text
        lines = buffer.split("\n")
        buffer = lines.pop()

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if headers is None:
                headers = [h.strip() for h in line.split(",")]
                continue

            reader = csv.reader(io.StringIO(line))
            try:
                values = next(reader)
            except StopIteration:
                continue

            if len(values) != len(headers):
                continue

            row = {}
            for h, v in zip(headers, values):
                try:
                    row[h] = float(v)
                except (ValueError, TypeError):
                    row[h] = v

            batch.append(row)

            if len(batch) >= BATCH_SIZE:
                for r in batch:
                    message = topic.serialize(key=key, value=r)
                    producer.produce(
                        topic=topic.name,
                        key=message.key,
                        value=message.value,
                    )
                producer.flush()
                sent += len(batch)
                batch = []
                pct = min(99, round(bytes_received / content_length * 100)) if content_length else 0
                uploads[upload_id] = {"status": "sending", "rows_sent": sent, "percent": pct}

    # Process remaining buffer
    if buffer.strip() and headers is not None:
        reader = csv.reader(io.StringIO(buffer.strip()))
        try:
            values = next(reader)
            if len(values) == len(headers):
                row = {}
                for h, v in zip(headers, values):
                    try:
                        row[h] = float(v)
                    except (ValueError, TypeError):
                        row[h] = v
                batch.append(row)
        except StopIteration:
            pass

    # Send remaining batch
    if batch:
        for r in batch:
            message = topic.serialize(key=key, value=r)
            producer.produce(
                topic=topic.name,
                key=message.key,
                value=message.value,
            )
        producer.flush()
        sent += len(batch)

    producer.flush()

    uploads[upload_id] = {
        "status": "done",
        "rows_sent": sent,
        "percent": 100,
        "topic": topic_name,
        "filename": filename,
    }

    return {"upload_id": upload_id, "status": "done", "rows_sent": sent, "topic": topic_name, "filename": filename}


@app.get("/progress/{upload_id}")
async def progress(upload_id: str):
    info = uploads.get(upload_id)
    if not info:
        return {"status": "unknown"}
    if info["status"] == "done":
        uploads.pop(upload_id, None)
    return info
