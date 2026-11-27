# Source this to run Python from the repository's shell scripts. All Python here runs through uv,
# in the environment pyproject.toml and uv.lock define.
HELIX_UV_PROJECT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if ! command -v uv >/dev/null 2>&1; then
  echo "error: uv is required to run this repository's Python (https://docs.astral.sh/uv/)" >&2
  exit 2
fi

uvpy() { uv run --quiet --locked --project "$HELIX_UV_PROJECT" python "$@"; }
