# Claude Code install scenario
#
# Build: docker build -t helix-install-test:claude-code tests/install/claude-code/
# Run:   docker run --rm \
#          -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
#          -e TEST_FUNCTIONAL=1 \
#          -v /path/to/helix:/workspace/helix:ro \
#          helix-install-test:claude-code

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl git python3 python3-yaml \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI.
# Anthropic ships a self-installing tarball; the canonical install URL
# may change. Override with --build-arg CLAUDE_INSTALL_URL=<url> when needed.
ARG CLAUDE_INSTALL_URL="https://claude.ai/install.sh"
RUN curl -fsSL "$CLAUDE_INSTALL_URL" -o /tmp/install-claude.sh \
    && bash /tmp/install-claude.sh \
    || echo "WARN: claude installer failed at $CLAUDE_INSTALL_URL; provide the binary manually"

# Ensure the installed binary is on PATH for the runtime user.
ENV PATH="/root/.local/bin:/root/.local/share/claude/versions:$PATH"

COPY install.sh verify.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/install.sh /usr/local/bin/verify.sh

WORKDIR /workspace
CMD ["bash", "-c", "install.sh && verify.sh"]
