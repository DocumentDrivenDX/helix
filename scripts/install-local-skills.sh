#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
codex_skills_dir="${CODEX_HOME:-$HOME/.codex}/skills"
claude_skills_dir="${CLAUDE_HOME:-$HOME/.claude}/skills"
local_bin_dir="$HOME/.local/bin"

mkdir -p "$codex_skills_dir" "$claude_skills_dir" "$local_bin_dir"

install_link() {
  local src="$1"
  local dest="$2"

  if [[ -L "$dest" ]]; then
    ln -sfn "$src" "$dest"
    return
  fi

  if [[ -e "$dest" ]]; then
    echo "skip existing non-symlink: $dest" >&2
    return
  fi

  ln -s "$src" "$dest"
}

install_pair() {
  local name="$1"
  local src="$2"
  install_link "$src" "$codex_skills_dir/$name"
  install_link "$src" "$claude_skills_dir/$name"
}

install_helix_cli() {
  local dest="$local_bin_dir/helix"

  cat >"$dest" <<EOF
#!/usr/bin/env bash
exec bash "$repo_root/scripts/helix" "\$@"
EOF

  chmod +x "$dest"
}

remove_noncanonical_links() {
  local names=(
    helix-workflow
    helix-alignment-review
    plan-workflow
    polish-workflow
    experiment-workflow
    execute
    grind
    handoff
    review
    triage
    plan
    polish
    experiment
  )
  local name
  for name in "${names[@]}"; do
    rm -f "$codex_skills_dir/$name" "$claude_skills_dir/$name"
  done
}

remove_noncanonical_links

install_pair "helix-run" "$repo_root/skills/helix"
install_pair "helix-implement" "$repo_root/skills/execute"
install_pair "helix-check" "$repo_root/skills/check"
install_pair "helix-align" "$repo_root/skills/helix-alignment-review"
install_pair "helix-backfill" "$repo_root/skills/backfill"
install_pair "helix-plan" "$repo_root/skills/plan"
install_pair "helix-polish" "$repo_root/skills/polish"
install_pair "helix-next" "$repo_root/skills/next"
install_pair "helix-review" "$repo_root/skills/review"
install_pair "helix-spawn" "$repo_root/skills/spawn"
install_pair "helix-experiment" "$repo_root/skills/experiment"

echo "Installed skills into:"
echo "  Codex:  $codex_skills_dir"
echo "  Claude: $claude_skills_dir"

chmod +x "$repo_root/scripts/helix"
install_helix_cli

echo "Installed HELIX CLI into:"
echo "  $local_bin_dir/helix"
