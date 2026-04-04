#!/usr/bin/env bash
# HELIX tracker — thin delegation layer over ddx bead.
#
# Provides tracker_* shell functions that scripts/helix calls.
# Storage, locking, deps, import/export are all handled by ddx bead.
# HELIX adds: triage validation, execution-eligible derivation, field mapping.
#
# Requires: ddx (on PATH), jq

# ── ddx bead configuration ────────────────────────────────────────────
tracker_dir="${HELIX_TRACKER_DIR:-${target_root:-.}/.ddx}"
tracker_file="${tracker_dir}/beads.jsonl"  # ddx bead canonical file
export DDX_BEAD_DIR="$tracker_dir"
# Per-project prefix: defaults to "hx", configurable via .helix/config or env
export DDX_BEAD_PREFIX="${HELIX_BEAD_PREFIX:-hx}"

tracker_init() {
  ddx bead init 2>/dev/null
}

tracker_ensure() {
  if [[ ! -f "$tracker_file" ]]; then
    tracker_init
  fi
}

# ── ID generation (delegate to ddx) ──────────────────────────────────
tracker_gen_id() {
  local prefix="${1:-hx}"
  printf '%s-%s' "$prefix" "$(head -c4 /dev/urandom | od -An -tx1 | tr -d ' \n')"
}

# ── triage validation (HELIX-specific) ────────────────────────────────
tracker_validate_create() {
  local type="$1" labels="$2" spec_id="$3" acceptance="$4" deps="$5"
  local rc=0

  # Hard: helix label required
  case ",${labels}," in
    *,helix,*) ;;
    *)
      printf '[triage] error: missing required label "helix"\n' >&2
      rc=1
      ;;
  esac

  # Hard: at least one phase label
  case ",${labels}," in
    *,phase:frame,*|*,phase:design,*|*,phase:test,*|*,phase:build,*|*,phase:deploy,*|*,phase:iterate,*|*,phase:review,*) ;;
    *)
      printf '[triage] error: missing phase label\n' >&2
      rc=1
      ;;
  esac

  # Hard: spec-id required for tasks
  if [[ "$type" == "task" ]] && [[ -z "$spec_id" ]]; then
    printf '[triage] error: tasks require --spec-id\n' >&2
    rc=1
  fi

  # Hard: acceptance required for tasks and epics
  if [[ "$type" == "task" || "$type" == "epic" ]] && [[ -z "$acceptance" ]]; then
    printf '[triage] error: %s issues require --acceptance\n' "$type" >&2
    rc=1
  fi

  # Hard: deps must reference existing issues
  if [[ -n "$deps" ]]; then
    local dep
    for dep in ${deps//,/ }; do
      if ! ddx bead show "$dep" --json >/dev/null 2>&1; then
        printf '[triage] error: dependency %s does not exist\n' "$dep" >&2
        rc=1
      fi
    done
  fi

  # Advisory: kind label
  if (( rc == 0 )); then
    case ",${labels}," in
      *,kind:*) ;;
      *)
        printf '[triage] warning: consider adding a kind label\n' >&2
        (( rc == 0 )) && rc=2
        ;;
    esac
  fi

  return "$rc"
}

# ── create ────────────────────────────────────────────────────────────
tracker_create() {
  local title="" type="task" labels="" deps="" parent="" spec_id=""
  local description="" design="" acceptance="" priority=2
  local execution_eligible="" superseded_by="" replaces=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --type)       type="$2"; shift 2 ;;
      --labels)     labels="$2"; shift 2 ;;
      --deps)       deps="$2"; shift 2 ;;
      --parent)     parent="$2"; shift 2 ;;
      --spec-id)    spec_id="$2"; shift 2 ;;
      --description) description="$2"; shift 2 ;;
      --design)     design="$2"; shift 2 ;;
      --acceptance) acceptance="$2"; shift 2 ;;
      --priority)   priority="$2"; shift 2 ;;
      --execution-eligible) execution_eligible="$2"; shift 2 ;;
      --superseded-by) superseded_by="$2"; shift 2 ;;
      --replaces)   replaces="$2"; shift 2 ;;
      --silent)     shift ;;
      -h|--help|help)
        echo "Usage: helix tracker create <title> [options]"
        echo ""
        echo "Options:"
        echo "  --type TYPE            Issue type (task, epic, bug, chore)"
        echo "  --labels L1,L2         Comma-separated labels"
        echo "  --deps ID1,ID2         Comma-separated dependency IDs"
        echo "  --parent ID            Parent issue ID"
        echo "  --spec-id ID           Governing artifact reference"
        echo "  --description TEXT      Issue description"
        echo "  --acceptance TEXT       Acceptance criteria"
        echo "  --priority N            Priority (0=highest, 4=lowest, default 2)"
        echo "  --execution-eligible T  true or false"
        echo "  --superseded-by ID     Replacement issue ID"
        echo "  --replaces ID          Issue this replaces"
        return 0
        ;;
      *)            title="$1"; shift ;;
    esac
  done

  if [[ -z "$title" ]]; then
    echo "tracker: title required" >&2
    return 1
  fi

  # Triage validation
  if [[ "${HELIX_SKIP_TRIAGE:-0}" != "1" ]]; then
    local _triage_rc=0
    tracker_validate_create "$type" "$labels" "$spec_id" "$acceptance" "$deps" || _triage_rc=$?
    if (( _triage_rc == 1 )); then
      printf '[triage] issue not created — fix the errors above\n' >&2
      return 1
    fi
  fi

  # Derive execution-eligible from phase labels if not set
  if [[ -z "$execution_eligible" ]]; then
    case ",${labels}," in
      *,phase:build,*|*,phase:deploy,*|*,phase:iterate,*)
        execution_eligible="true" ;;
      *)
        execution_eligible="false" ;;
    esac
  fi

  # Build ddx bead create command
  local -a cmd=(ddx bead create "$title" --type "$type" --priority "$priority")
  [[ -n "$labels" ]]      && cmd+=(--labels "$labels")
  [[ -n "$parent" ]]      && cmd+=(--parent "$parent")
  [[ -n "$description" ]] && cmd+=(--description "$description")
  [[ -n "$acceptance" ]]  && cmd+=(--acceptance "$acceptance")

  # HELIX-specific fields go into --set
  [[ -n "$spec_id" ]]     && cmd+=(--set "spec-id=$spec_id")
  [[ -n "$design" ]]      && cmd+=(--set "design=$design")
  [[ -n "$execution_eligible" ]] && cmd+=(--set "execution-eligible=$execution_eligible")
  [[ -n "$superseded_by" ]] && cmd+=(--set "superseded-by=$superseded_by")
  [[ -n "$replaces" ]]    && cmd+=(--set "replaces=$replaces")

  # Add deps
  local id
  id="$("${cmd[@]}" 2>&1)" || { echo "$id" >&2; return 1; }

  # Wire dependencies
  if [[ -n "$deps" ]]; then
    local dep
    for dep in ${deps//,/ }; do
      ddx bead dep add "$id" "$dep" 2>/dev/null || true
    done
  fi

  printf '%s\n' "$id"
}

# ── show ──────────────────────────────────────────────────────────────
tracker_show() {
  local id="$1"
  local json_flag=0
  [[ "${2:-}" == "--json" ]] && json_flag=1

  local raw
  raw="$(ddx bead show "$id" --json 2>/dev/null)" || {
    echo "tracker: issue not found: $id" >&2
    return 1
  }

  if (( json_flag )); then
    printf '%s' "$raw"
  else
    printf '%s\n' "$raw" | jq -r '
      "[" + .status + "] " + .id + " (" + .issue_type + ") — " + .title,
      (if .description != "" then "  Description: " + .description else empty end),
      (if .acceptance != "" then "  Acceptance: " + .acceptance else empty end),
      (if (.labels | length) > 0 then "  Labels: " + (.labels | join(", ")) else empty end),
      (if (.dependencies | length) > 0 then "  Deps: " + ([.dependencies[].depends_on_id] | join(", ")) else empty end),
      (if .parent != "" then "  Parent: " + .parent else empty end),
      (if .["execution-eligible"] then "  Execution Eligible: true" else empty end),
      (if .["spec-id"] != "" then "  Spec: " + .["spec-id"] else empty end)
    '
  fi
}

# ── update ────────────────────────────────────────────────────────────
tracker_update() {
  local id="$1"
  shift

  local -a cmd=(ddx bead update "$id")
  local claim=0 unclaim=0 deps_to_add=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --title)      cmd+=(--title "$2"); shift 2 ;;
      --status)     cmd+=(--status "$2"); shift 2 ;;
      --priority)   cmd+=(--priority "$2"); shift 2 ;;
      --labels)     cmd+=(--labels "$2"); shift 2 ;;
      --acceptance) cmd+=(--acceptance "$2"); shift 2 ;;
      --assignee)   cmd+=(--assignee "$2"); shift 2 ;;
      --notes)      cmd+=(--set "notes=$2"); shift 2 ;;
      --claim)      claim=1; shift ;;
      --unclaim)    unclaim=1; shift ;;
      --spec-id)    cmd+=(--set "spec-id=$2"); shift 2 ;;
      --design)     cmd+=(--set "design=$2"); shift 2 ;;
      --deps)       deps_to_add="$2"; shift 2 ;;
      --execution-eligible) cmd+=(--set "execution-eligible=$2"); shift 2 ;;
      --superseded-by)      cmd+=(--set "superseded-by=$2"); shift 2 ;;
      --replaces)           cmd+=(--set "replaces=$2"); shift 2 ;;
      --parent)     cmd+=(--parent "$2"); shift 2 ;;
      *)            shift ;;
    esac
  done

  if (( claim )); then
    ddx bead update "$id" --status in_progress --assignee helix --set "claimed-at=$(date -u +%Y-%m-%dT%H:%M:%SZ)" --set "claimed-pid=$$" 2>/dev/null
    return $?
  fi

  if (( unclaim )); then
    ddx bead update "$id" --unclaim 2>/dev/null
    return $?
  fi

  "${cmd[@]}" 2>/dev/null || return $?

  # Wire deps after the main update
  if [[ -n "$deps_to_add" ]]; then
    local dep
    for dep in ${deps_to_add//,/ }; do
      ddx bead dep add "$id" "$dep" 2>/dev/null || true
    done
  fi
}

# ── close ─────────────────────────────────────────────────────────────
tracker_close() {
  ddx bead close "$1" 2>/dev/null
}

# ── list ──────────────────────────────────────────────────────────────
tracker_list() {
  local -a cmd=(ddx bead list)
  local json_flag=0

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --status) cmd+=(--status "$2"); shift 2 ;;
      --label)  cmd+=(--label "$2"); shift 2 ;;
      --json)   json_flag=1; cmd+=(--json); shift ;;
      *)        shift ;;
    esac
  done

  local output
  output="$("${cmd[@]}" 2>/dev/null)" || return $?

  if (( json_flag )); then
    printf '%s' "$output"
  else
    printf '%s\n' "$output"
  fi
}

# ── ready ─────────────────────────────────────────────────────────────
tracker_ready() {
  local -a cmd=(ddx bead ready)
  local json_flag=0 execution=0

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --json)      json_flag=1; shift ;;
      --execution) execution=1; shift ;;
      *)           shift ;;
    esac
  done

  (( execution )) && cmd+=(--execution)
  cmd+=(--json)

  local output
  output="$("${cmd[@]}" 2>/dev/null)" || return $?

  if (( json_flag )); then
    printf '%s' "$output"
  else
    # Exit 0 if items, 1 if empty (used by run loop)
    local count
    count="$(printf '%s' "$output" | jq 'length')"
    if (( count == 0 )); then
      return 1
    fi
    printf '%s' "$output" | jq -r '.[] | .id + "  " + .title'
  fi
}

# ── blocked ───────────────────────────────────────────────────────────
tracker_blocked() {
  local -a cmd=(ddx bead blocked --json)
  local json_flag=0
  [[ "${1:-}" == "--json" ]] && json_flag=1

  local output
  output="$("${cmd[@]}" 2>/dev/null)" || return $?

  if (( json_flag )); then
    printf '%s' "$output"
  else
    printf '%s' "$output" | jq -r '.[] | .id + "  " + .title + "  deps: " + ([.dependencies[].depends_on_id] | join(", "))'
  fi
}

# ── dep ───────────────────────────────────────────────────────────────
tracker_dep() {
  local subcmd="$1"
  shift

  case "$subcmd" in
    add)    ddx bead dep add "$@" 2>/dev/null ;;
    remove) ddx bead dep remove "$@" 2>/dev/null ;;
    tree)   ddx bead dep tree "$@" 2>/dev/null ;;
    *)      echo "tracker: dep $subcmd: unknown subcommand" >&2; return 1 ;;
  esac
}

# ── status ────────────────────────────────────────────────────────────
tracker_status() {
  local json_flag=0
  [[ "${1:-}" == "--json" ]] && json_flag=1

  if (( json_flag )); then
    ddx bead status --json 2>/dev/null
  else
    ddx bead status 2>/dev/null
  fi
}

# ── import / export / migrate ─────────────────────────────────────────
tracker_import() {
  local from="auto" file_path=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --from) from="$2"; shift 2 ;;
      --file) file_path="$2"; shift 2 ;;
      *)      file_path="$1"; shift ;;
    esac
  done

  # Warn if existing data present
  local existing_count
  existing_count="$(ddx bead list --json 2>/dev/null | jq 'length' 2>/dev/null || echo 0)"
  if (( existing_count > 0 )); then
    printf 'WARNING: tracker already has %d issues; import will merge (not replace)\n' "$existing_count" >&2
  fi

  local -a cmd=(ddx bead import --from "$from")
  [[ -n "$file_path" ]] && cmd+=("$file_path")
  "${cmd[@]}" 2>&1
}

tracker_export() {
  local file_path="" stdout=0
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --stdout) stdout=1; shift ;;
      --file)   file_path="$2"; shift 2 ;;
      *)        file_path="$1"; shift ;;
    esac
  done

  if (( stdout )); then
    ddx bead export --stdout 2>/dev/null
  elif [[ -n "$file_path" ]]; then
    ddx bead export "$file_path" 2>/dev/null
  else
    ddx bead export --stdout 2>/dev/null
  fi
}

tracker_migrate() {
  tracker_import "$@"
}

# ── read/write (low-level, for fingerprinting) ────────────────────────
tracker_read_all() {
  ddx bead list --json 2>/dev/null
}

# ── fingerprint (used by run loop for drift detection) ────────────────
tracker_issue_fingerprint() {
  local id="$1"
  tracker_show "$id" --json 2>/dev/null | jq -r '
    [.title, .status, (.labels | sort | join(",")), .parent, .["spec-id"]] | join("|")
  ' | md5sum | cut -d' ' -f1
}

# ── dispatch (called by helix CLI main) ───────────────────────────────
tracker_dispatch() {
  local subcmd="${1:-}"
  shift 2>/dev/null || true

  case "$subcmd" in
    init)     tracker_init ;;
    create)   tracker_create "$@" ;;
    show)     tracker_show "$@" ;;
    update)   tracker_update "$@" ;;
    close)    tracker_close "$@" ;;
    list)     tracker_list "$@" ;;
    ready)    tracker_ready "$@" ;;
    blocked)  tracker_blocked "$@" ;;
    dep)      tracker_dep "$@" ;;
    status)   tracker_status "$@" ;;
    import)   tracker_import "$@" ;;
    export)   tracker_export "$@" ;;
    migrate)  tracker_migrate "$@" ;;
    help|-h|--help|"")
      echo "Usage: helix tracker <command>"
      echo ""
      echo "Canonical storage is .ddx/beads.jsonl (delegated to ddx bead)"
      echo ""
      echo "Commands:"
      echo "  helix tracker init                    Initialize tracker"
      echo "  helix tracker create <title> [opts]   Create issue"
      echo "  helix tracker show <id> [--json]      Show issue"
      echo "  helix tracker update <id> [opts]      Update issue"
      echo "  helix tracker close <id>              Close issue"
      echo "  helix tracker list [--status S]       List issues"
      echo "  helix tracker ready [--execution]     Ready queue"
      echo "  helix tracker blocked                 Blocked issues"
      echo "  helix tracker dep add|remove|tree     Dependencies"
      echo "  helix tracker status [--json]         Queue health"
      echo "  helix tracker import [--from S]       Import beads"
      echo "  helix tracker export [file]           Export beads"
      ;;
    *)
      echo "tracker: unknown command: $subcmd" >&2
      return 1
      ;;
  esac
}

tracker_usage() {
  tracker_dispatch help
}
