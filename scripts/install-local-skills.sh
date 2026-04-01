#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
project_skills_dir="$repo_root/.agents/skills"
agents_skills_dir="${AGENTS_HOME:-$HOME/.agents}/skills"
claude_skills_dir="${CLAUDE_HOME:-$HOME/.claude}/skills"
local_bin_dir="$HOME/.local/bin"

mkdir -p "$agents_skills_dir" "$claude_skills_dir" "$local_bin_dir"

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
  install_link "$src" "$agents_skills_dir/$name"
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
  local name dir
  for name in "${names[@]}"; do
    for dir in "$agents_skills_dir" "$claude_skills_dir"; do
      local target="$dir/$name"
      # Only remove if it's a symlink (don't delete user-defined skills)
      if [[ -L "$target" ]]; then
        rm -f "$target"
      fi
    done
  done
}

remove_obsolete_native_links() {
  local codex_skills_dir="${CODEX_HOME:-$HOME/.codex}/skills"
  local names=(
    helix-run
    helix-implement
    helix-check
    helix-align
    helix-backfill
    helix-plan
    helix-polish
    helix-next
    helix-review
    helix-experiment
  )
  local name
  for name in "${names[@]}"; do
    local target="$codex_skills_dir/$name"
    if [[ -L "$target" ]]; then
      rm -f "$target"
    fi
  done
}

remove_noncanonical_links
remove_obsolete_native_links

install_pair "helix-run" "$project_skills_dir/helix-run"
install_pair "helix-implement" "$project_skills_dir/helix-implement"
install_pair "helix-check" "$project_skills_dir/helix-check"
install_pair "helix-align" "$project_skills_dir/helix-align"
install_pair "helix-backfill" "$project_skills_dir/helix-backfill"
install_pair "helix-plan" "$project_skills_dir/helix-plan"
install_pair "helix-polish" "$project_skills_dir/helix-polish"
install_pair "helix-next" "$project_skills_dir/helix-next"
install_pair "helix-review" "$project_skills_dir/helix-review"
install_pair "helix-experiment" "$project_skills_dir/helix-experiment"

echo "Installed skills into:"
echo "  Agents: $agents_skills_dir"
echo "  Claude: $claude_skills_dir"

chmod +x "$repo_root/scripts/helix"
install_helix_cli

echo "Installed HELIX CLI into:"
echo "  $local_bin_dir/helix"
