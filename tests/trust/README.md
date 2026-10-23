# Sample image trust qualification

The [catalog](catalog.json) covers **76 catalog entries and 80 Dockerfile definitions** on `release/v5`: 74 sample Dockerfiles, two managed entries without Dockerfiles, two utility Dockerfiles, and four test Dockerfiles. The PostgreSQL CDC fixture uses `Dockerfile.postgres` and is included. Ten repositories referenced by `project-templates.json` are tracked separately.

Every catalog qualification starts as `pending`. A digest pin, package version, successful build, or passing OS bundle check alone does not establish that an application rejects the [disclosed eMudhra chains](https://emudhra.we-have-a-problem.com/). Owner routes identify maintainers or publishing repositories; they do not assign a named person.

## Build and check

Use a builder whose registry client rejects the affected chains before fetching base images. Fixing trust inside a Dockerfile does not protect downloads performed by a vulnerable Docker daemon or BuildKit instance.

Build locally for `linux/amd64`, using the same context, Dockerfile, build arguments, and target stage as the cluster builder. A sample copied into its own repository normally uses the sample directory as its context; preserve any actual `MAINAPPPATH` setting. Qualify dependency-download stages as well as the final runtime.

For example, from the samples repository root:

```sh
docker build --platform linux/amd64 \
  -f python/sources/demo_data/dockerfile \
  -t quix-trust-demo-data:local python/sources/demo_data

python3 tests/trust/check_image.py \
  --context "$(docker context show)" \
  --image quix-trust-demo-data:local --runtime python \
  --output /tmp/quix-trust-demo-data.json
```

`check_image.py` requires local Python and OpenSSL 3. It never builds or pulls images. It extracts PEM bundles and default/configured hashed CA directories from a **never-started container**, then optionally runs the installed Python or Node clients with the image's trust environment intact. This separates baked image contents from CA certificates injected by the container engine at startup. The directory helper reuses the parent's extraction container, so the parent retains cleanup responsibility if the helper times out. Standalone directory checks create and remove their own container.

- `--runtime python` exercises the standard library and applicable installed requests, httpx, botocore and gRPC clients. Use `--python-bin` for a specific virtual environment.
- When `confluent-kafka` is installed, the checker also exercises the exact loaded librdkafka shared library. Its verification callback records the original OpenSSL verdict without accepting rejected certificates; the probe makes credential-free metadata requests and sends no Kafka messages.
- `--runtime node` exercises the installed Node executable.
- `--runtime none` checks the selected PEM files and hashed CA directories only. It does not qualify the application.
- Java and .NET probes are in `JavaTlsProbe.java`, `Java8TlsProbe.java` and `dotnet/`. Run them with each relevant image's actual runtime; they are not invoked by `check_image.py`.

For Java 8, compile `Java8TlsProbe.java` with `javac --release 8 -d /tmp/quix-java-probe tests/trust/Java8TlsProbe.java`, mount that output directory read-only at `/probe`, and invoke the image's Java binary with `-cp /probe Java8TlsProbe positive https://pypi.org/`. Run it again with `negative` and the twelve fixture URLs. The probe preserves default trust and hostname verification, records the observed peer certificate SHA-256 hashes, and treats date or unrelated failures as inconclusive. Compare each negative leaf hash with its pinned fixture before treating the live rejection as evidence for that certificate.

The current live gRPC negative checks are inconclusive: the disclosure endpoints close the HTTP/2 connection before the client exposes certificate-verification evidence. Offline bundle rejection plus a successful legitimate gRPC connection provides partial coverage only; do not mark gRPC qualified from those checks.

The twelve public certificate fixtures and their hashes are pinned in `fixtures/manifest.json`. Offline verification uses a fixed valid time and published-root positive controls. Live checks require legitimate TLS connections to succeed and the disclosure endpoints to be rejected for issuer-trust errors. Timeouts, expiry, hostname failures, missing tools, and initialization errors are inconclusive, not successful mitigation.

The .NET probe records `peerSha256` while preserving the platform's validation result. Compare every negative peer hash with the corresponding fixture's leaf certificate before counting it as pinned-chain runtime evidence.

Python, Node, Java and other live probes without recorded peer-certificate fingerprints demonstrate endpoint rejection only. They cannot distinguish the pinned affected chain from an unrelated untrusted certificate presented at the same hostname. Their live results provide partial coverage and must not be described as exact pinned-chain runtime proof. Static store checks verify the exact pinned chains; the librdkafka callback additionally binds native verification events to the pinned certificate hashes.

Exit codes are **0** for the selected checks passing, **1** for exposed trust, and **2** for invalid or inconclusive evidence. Inspect the recorded scope before interpreting a result. Preserve source revision, base and output digests, architecture, tested clients, checker hashes, and functional-test results outside the source tree.

Checker unit tests:

```sh
python3 -m unittest discover -s tests/trust -p 'test_*.py'
```

## Coverage limits and remaining work

The qualified sample Dockerfiles use readable version tags plus SHA-256 digests.
The digest selects the image; the tag describes the intended version. The
[base-image lock](base-images.lock.json) records the exact base resolutions from
stage 1 amd64 builds and hashes of their build provenance. Pinning preserves
those base inputs; it does not fix vulnerable image contents, authenticate a
publisher, freeze package repositories, or make the entire build reproducible.

Deploy the digest-aware Build service before switching the samples release.
Its pinned-image cache verifies and consumes the original manifest/index digest;
if mirroring fails, the original pinned upstream reference remains in place.
It never substitutes a mutable tag for a requested digest. Existing tag-only
projects retain their tag-cache behavior, including their configured offline
fallback. No global cache purge is required.

Update a base digest through a reviewed change and rerun trust and application
checks. Security fixes published under the same tag are deliberately not picked
up until the pin is refreshed. Run `python3 -m unittest discover -s tests/trust`
to check that Dockerfiles, inventory and lock agree. InfluxDB3 remains excluded
until its image can be accessed and qualified; pinning an unknown image would
not close that gap.

Existing copied projects must apply the Dockerfile and dependency updates,
rebuild and redeploy. A library update or cache refresh alone does not update
their source or running images. To roll back pinned sample source, drain queued
builds first and restore the stage 1 source; retain the digest-aware builder
until no pinned builds remain. Do not roll back corrected CA stores.

| Area | Required follow-up |
|---|---|
| Additional CA paths | Default and configured hashed directories are included in the checker; application-specific paths still require separate assessment. |
| MinIO, Prometheus, Pushgateway | Verify the actual binaries with the configured CA file and isolated directory. Existing standard PEM bundles are replaced; the checker audits default/configured directories, while custom application stores need separate evidence. |
| MongoDB | Qualify both native `mongod` and the embedded Node runtime in `mongosh`; confirm the selected `NODE_OPTIONS` is supported. |
| Other vendor services and native SDKs | Exercise the actual relevant TLS clients, including database utilities, plugins and libraries. A Python or OpenSSL probe cannot stand in for a different implementation. |
| InfluxDB3 | Remains unmodified pending image access and assessment of Rust/webpki and Python plugin trust. |
| MATLAB and Simulink | The bundled JVM trust store is rebuilt from corrected OS anchors and requires native JVM validation. Oracle Java 8u202 remains for runtime compatibility; its broader obsolete-runtime risks, MathWorks native HTTP clients, and compiled-wheel provenance require separate assessment. |
| Quix prebuilt images | Wrapper changes require local validation; publisher builds and embedded clients still need their own evidence. |
| Managed services | Remediate `Quix.DataLake.Sink` and `Quix.DynamicConfiguration` in their publishing repositories, then update the deployed images. |
| Kafka Connect and external templates | Qualify selected connector plugins and the ten separate template repositories. |

Explicit custom CA files, mounted certificates, environment overrides, and packages installed later can change effective trust. An unresolved item remains open exposure or unknown status; it does not count as a qualified sample.

After qualification, rebuild applicable Instant Deploy artifacts and plan a controlled cluster rollout. Existing copied samples and deployments are separate rollout targets. Keep the `main` follow-up separate from this `release/v5` work.

## Platform rollout

Qualify the library service's source-fetching trust as well as the build service
and Docker daemon. A corrected Dockerfile cannot protect an earlier repository
or base-image download performed by an affected client.

Check clone depth and per-item commit references before changing a library URL
or branch. A shallow recovery clone can attribute every item to the branch head
and enqueue a full library rebuild, even when only one sample changed. Preserve
history where practical and allow capacity for the actual rebuild set. Do not
assume a small Git diff implies a small build queue.

Drain existing library builds before switching the source reference, and keep
that reference stable until the new builds finish. The current build request
captures Dockerfile content when queued but downloads the sample ZIP from the
library service when executed. Changing served content while requests are queued
can mix revisions. Verify the served commit, downloaded content and published
image before promotion.

Use fresh version tags and verify the matching base-cache entries before
invalidating anything. The registry mirror, Docker build layers and published
library artifacts are separate caches. Refresh only entries proven stale; keep
existing deployment images for rollback and qualify any rollback's trust status.
An unavailable upstream can leave a previously cached base in use, so confirm
the resulting image rather than treating a successful build as proof of repair.

## Maintaining the inventory

Inventory all tracked `library.json` files and case-insensitive `Dockerfile*` filenames, including build stages and test fixtures. Keep `catalog.json` synchronized when image references or catalog entries change. Record evidence before changing an entry's qualification state, and retain explicit gap IDs for any untested runtime or independently selected trust store.
