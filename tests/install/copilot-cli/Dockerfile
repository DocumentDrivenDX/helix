# GitHub Copilot CLI install scenario
#
# Build: docker build -t helix-install-test:copilot-cli tests/install/copilot-cli/
# Run:   docker run --rm \
#          -e GH_TOKEN=$GH_TOKEN \
#          -e TEST_FUNCTIONAL=1 \
#          -v /path/to/helix:/workspace/helix:ro \
#          helix-install-test:copilot-cli

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install gh CLI per https://github.com/cli/cli/blob/trunk/docs/install_linux.md
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl git python3 python3-yaml gnupg \
    && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
        | gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
        > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update && apt-get install -y --no-install-recommends gh \
    && rm -rf /var/lib/apt/lists/*

COPY install.sh verify.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/install.sh /usr/local/bin/verify.sh

WORKDIR /workspace
CMD ["bash", "-c", "install.sh && verify.sh"]
