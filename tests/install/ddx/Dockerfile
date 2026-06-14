# DDx install scenario
#
# Builds a minimal Ubuntu image with the DDx CLI installed, then runs
# install.sh + verify.sh against a mounted HELIX source tree.
#
# Build: docker build -t helix-install-test:ddx tests/install/ddx/
# Run:   docker run --rm -v /path/to/helix:/workspace/helix:ro helix-install-test:ddx

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/root/.local/bin:/usr/local/bin:${PATH}"
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl git python3 python3-yaml jq \
    && rm -rf /var/lib/apt/lists/*

# Install DDx CLI.
RUN curl -fsSL https://raw.githubusercontent.com/DocumentDrivenDX/ddx/main/install.sh | bash \
    && command -v ddx \
    && ddx version

COPY install.sh verify.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/install.sh /usr/local/bin/verify.sh

WORKDIR /workspace
CMD ["bash", "-c", "install.sh && verify.sh"]
