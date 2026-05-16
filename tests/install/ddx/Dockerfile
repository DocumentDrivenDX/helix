# DDx install scenario
#
# Builds a minimal Ubuntu image with the DDx CLI installed, then runs
# install.sh + verify.sh against a mounted HELIX source tree.
#
# Build: docker build -t helix-install-test:ddx tests/install/ddx/
# Run:   docker run --rm -v /path/to/helix:/workspace/helix:ro helix-install-test:ddx

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl git python3 python3-yaml jq \
    && rm -rf /var/lib/apt/lists/*

# Install DDx CLI.
# The DDx project does not yet publish a stable install URL; substitute
# whichever channel is current (GitHub releases binary, brew, npm, etc.).
# For now we expect the host to mount the binary OR build DDx and copy in.
# Override DDX_BIN at build time to point at a local binary:
#   docker build --build-arg DDX_BIN=/tmp/ddx -t helix-install-test:ddx .
ARG DDX_BIN=""
COPY ddx-bin* /usr/local/bin/
RUN if [[ -n "$DDX_BIN" && -f /usr/local/bin/ddx-bin ]]; then \
        mv /usr/local/bin/ddx-bin /usr/local/bin/ddx && chmod +x /usr/local/bin/ddx; \
    fi

# Fallback: if the host did not provide a binary, try the documented
# install (placeholder; replace with the canonical install URL when DDx
# publishes one).
RUN if [[ ! -x /usr/local/bin/ddx ]]; then \
        echo "WARNING: no ddx binary provided. The scenario will run only if you mount one at /usr/local/bin/ddx." >&2; \
    fi

COPY install.sh verify.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/install.sh /usr/local/bin/verify.sh

WORKDIR /workspace
CMD ["bash", "-c", "install.sh && verify.sh"]
