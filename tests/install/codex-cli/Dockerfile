# OpenAI Codex CLI install scenario
#
# Build: docker build -t helix-install-test:codex-cli tests/install/codex-cli/
# Run:   docker run --rm \
#          -e OPENAI_API_KEY=$OPENAI_API_KEY \
#          -e TEST_FUNCTIONAL=1 \
#          -v /path/to/helix:/workspace/helix:ro \
#          helix-install-test:codex-cli

FROM node:22-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl git python3 python3-yaml \
    && rm -rf /var/lib/apt/lists/*

# Install OpenAI Codex CLI.
# Replace with the canonical install URL when openai/codex publishes one.
# Common candidates:
#   npm install -g @openai/codex
#   curl -fsSL https://codex.openai.com/install.sh | sh
RUN npm install -g @openai/codex 2>/dev/null \
    || echo "WARN: npm install @openai/codex failed; provide binary at /usr/local/bin/codex"

COPY install.sh verify.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/install.sh /usr/local/bin/verify.sh

WORKDIR /workspace
CMD ["bash", "-c", "install.sh && verify.sh"]
