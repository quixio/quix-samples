FROM python:3.11.17-slim-trixie@sha256:b7a9e5f6a93d6d4a31f129bbd4bdee69efccb6ded0fb230d78aafaf37af98377

ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt \
    SSL_CERT_DIR=/etc/ssl/certs \
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
    PIP_CERT=/etc/ssl/certs/ca-certificates.crt \
    AWS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
    GRPC_DEFAULT_SSL_ROOTS_FILE_PATH=/etc/ssl/certs/ca-certificates.crt

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && dpkg --compare-versions "$(dpkg-query -W -f='${Version}' ca-certificates)" ge '20250419+deb13u1' \
    && rm -rf /var/lib/apt/lists/* \
    && python -c 'import os, shutil; from pip._vendor import certifi; src = "/etc/ssl/certs/ca-certificates.crt"; dst = certifi.where(); os.path.samefile(src, dst) or shutil.copyfile(src, dst)' \
    && python -m pip install --no-cache-dir \
        --cert /etc/ssl/certs/ca-certificates.crt pip==26.2.2 certifi==2026.10.19

WORKDIR /tests

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["pytest", "-v", "--tb=short"]
