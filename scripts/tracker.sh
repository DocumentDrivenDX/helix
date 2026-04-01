#!/usr/bin/env bash
# Built-in HELIX bead tracker.
# Stores canonical issues in .helix/issues.jsonl — one JSON object per line.
# Requires: jq

# ── paths ──────────────────────────────────────────────────────────────
tracker_dir="${HELIX_TRACKER_DIR:-${target_root:-.}/.helix}"
tracker_file="${tracker_dir}/issues.jsonl"
beads_dir="${HELIX_BEADS_DIR:-${target_root:-.}/.beads}"
beads_file="${beads_dir}/issues.jsonl"
tracker_lock_dir="${tracker_dir}/issues.lock"
tracker_lock_timeout="${HELIX_TRACKER_LOCK_TIMEOUT:-10}"
tracker_lock_poll_interval="${HELIX_TRACKER_LOCK_POLL_INTERVAL:-0.05}"

tracker_init() {
  mkdir -p "$tracker_dir"
  touch "$tracker_file"
}

tracker_ensure() {
  if [[ ! -f "$tracker_file" ]]; then
    tracker_init
  fi
}

tracker_acquire_lock() {
  tracker_ensure

  local start now owner
  start="$(date +%s)"

  while ! mkdir "$tracker_lock_dir" 2>/dev/null; do
    now="$(date +%s)"
    if (( now - start >= tracker_lock_timeout )); then
      owner="unknown"
      if [[ -f "${tracker_lock_dir}/pid" ]]; then
        owner="$(cat "${tracker_lock_dir}/pid" 2>/dev/null || echo unknown)"
      fi
      echo "tracker: timed out waiting for tracker lock (owner: ${owner})" >&2
      return 1
    fi
    sleep "$tracker_lock_poll_interval"
  done

  printf '%s\n' "$$" > "${tracker_lock_dir}/pid"
  printf '%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "${tracker_lock_dir}/acquired_at"

  if [[ -n "${HELIX_TRACKER_TEST_HOLD_LOCK_SEC:-}" ]]; then
    sleep "${HELIX_TRACKER_TEST_HOLD_LOCK_SEC}"
  fi
}

tracker_release_lock() {
  if [[ -d "$tracker_lock_dir" ]]; then
    rm -rf "$tracker_lock_dir"
  fi
}

tracker_with_lock() {
  tracker_acquire_lock || return 1
  local status=0
  "$@" || status=$?
  tracker_release_lock
  return "$status"
}

# ── ID generation ──────────────────────────────────────────────────────
# Short hex hash: 8 chars from /dev/urandom
tracker_gen_id() {
  local prefix="${1:-hx}"
  printf '%s-%s' "$prefix" "$(head -c4 /dev/urandom | od -An -tx1 | tr -d ' \n')"
}

# ── low-level read/write ──────────────────────────────────────────────
# Read all issues as a JSON array
tracker_read_all() {
  tracker_ensure
  if [[ ! -s "$tracker_file" ]]; then
    printf '[]\n'
  else
    if ! jq -s '.' "$tracker_file"; then
      echo "tracker: malformed tracker state: $tracker_file" >&2
      return 1
    fi
  fi
}

# Write a JSON array back as JSONL (one object per line, sorted by id)
tracker_write_all() {
  local json="$1"
  local tmp
  tmp="$(mktemp "${tracker_dir}/issues.jsonl.tmp.XXXXXX")"
  printf '%s' "$json" | jq -c '.[] | .' > "$tmp"
  mv -f "$tmp" "$tracker_file"
}

tracker_write_jsonl_file() {
  local json="$1"
  local output_file="$2"
  local output_dir
  output_dir="$(dirname "$output_file")"
  mkdir -p "$output_dir"
  local tmp
  tmp="$(mktemp "${output_dir}/issues.jsonl.tmp.XXXXXX")"
  printf '%s' "$json" | jq -c '.[] | .' > "$tmp"
  mv -f "$tmp" "$output_file"
}

tracker_normalize_issue_array() {
  local issues_json="$1"
  local now
  now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

  printf '%s' "$issues_json" | jq --arg now "$now" '
    def default_execution_eligible:
      if (.labels | type) != "array" then false
      else
        ((.labels | index("phase:build")) != null) or
        ((.labels | index("phase:deploy")) != null) or
        ((.labels | index("phase:iterate")) != null)
      end;
    map({
      id:          (.id // "hx-unknown"),
      title:       (.title // "untitled"),
      type:        (.type // "task"),
      status:      (.status // "open"),
      priority:    (.priority // 2),
      labels:      (if (.labels | type) == "array" then .labels else [] end),
      parent:      (.parent // ""),
      "spec-id":   (.["spec-id"] // ""),
      description: (.description // ""),
      design:      (.design // ""),
      acceptance:  (.acceptance // ""),
      deps:        (if (.deps | type) == "array" then .deps else [] end),
      assignee:    (.assignee // ""),
      notes:       (.notes // ""),
      "execution-eligible":
                   (if .["execution-eligible"] == null then default_execution_eligible else .["execution-eligible"] end),
      "superseded-by": (.["superseded-by"] // ""),
      replaces:    (.replaces // ""),
      created:     (.created // $now),
      updated:     (.updated // $now)
    })
  '
}

# ── triage validation ──────────────────────────────────────────────────

# Validate issue fields before creation.
# Returns: 0=ok, 1=hard error (blocks creation), 2=warning (proceeds).
# Errors/warnings printed to stderr with [triage] prefix.
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
    *,phase:build,*|*,phase:deploy,*|*,phase:iterate,*|*,phase:design,*|*,phase:review,*) ;;
    *)
      printf '[triage] error: missing phase label (phase:build, phase:deploy, phase:iterate, phase:design, or phase:review)\n' >&2
      rc=1
      ;;
  esac

  # Hard: spec-id required for tasks
  if [[ "$type" == "task" ]] && [[ -z "$spec_id" ]]; then
    printf '[triage] error: tasks require --spec-id pointing to governing artifact\n' >&2
    rc=1
  fi

  # Hard: acceptance required for tasks and epics
  if [[ "$type" == "task" || "$type" == "epic" ]] && [[ -z "$acceptance" ]]; then
    printf '[triage] error: %s issues require --acceptance criteria\n' "$type" >&2
    rc=1
  fi

  # Hard: deps must reference existing issues
  if [[ -n "$deps" ]]; then
    local dep
    for dep in ${deps//,/ }; do
      if ! tracker_show "$dep" --json >/dev/null 2>&1; then
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
        printf '[triage] warning: consider adding a kind label (kind:build, kind:implementation, etc.)\n' >&2
        (( rc == 0 )) && rc=2
        ;;
    esac
  fi

  return "$rc"
}

# Validate issue fields before update.
# Only checks fields that are being changed.
tracker_validate_update() {
  local id="$1"
  shift
  local labels="" deps=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --labels)  labels="$2"; shift 2 ;;
      --deps)    deps="$2"; shift 2 ;;
      *)         shift 2 2>/dev/null || shift ;;
    esac
  done

  local rc=0

  # If labels are being changed, validate helix label is present
  if [[ -n "$labels" ]]; then
    case ",${labels}," in
      *,helix,*) ;;
      *)
        printf '[triage] error: cannot remove required "helix" label\n' >&2
        rc=1
        ;;
    esac
  fi

  # Validate dep references if deps are being changed
  if [[ -n "$deps" ]]; then
    local dep
    for dep in ${deps//,/ }; do
      if [[ "$dep" == "$id" ]]; then
        printf '[triage] error: circular dependency: %s depends on itself\n' "$id" >&2
        rc=1
      elif ! tracker_show "$dep" --json >/dev/null 2>&1; then
        printf '[triage] error: dependency %s does not exist\n' "$dep" >&2
        rc=1
      fi
    done
  fi

  return "$rc"
}

# ── create ─────────────────────────────────────────────────────────────
tracker_create_impl() {
  tracker_ensure
  need_cmd jq

  local title="" type="task" labels="" deps="" parent="" spec_id="" description="" design="" acceptance="" priority=2
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
      --silent)     shift ;; # compat: just suppress extra output
      -h|--help|help) tracker_usage; return 0 ;;
      *)            title="$1"; shift ;;
    esac
  done

  if [[ -z "$title" ]]; then
    echo "tracker: title required" >&2
    return 1
  fi

  # Triage validation (skip with HELIX_SKIP_TRIAGE=1 for internal ops)
  if [[ "${HELIX_SKIP_TRIAGE:-0}" != "1" ]]; then
    local _triage_rc=0
    tracker_validate_create "$type" "$labels" "$spec_id" "$acceptance" "$deps" || _triage_rc=$?
    if (( _triage_rc == 1 )); then
      printf '[triage] issue not created — fix the errors above\n' >&2
      return 1
    fi
    # rc=2 is advisory warning, proceed with creation
  fi

  local id
  id="$(tracker_gen_id hx)"

  local labels_json
  if [[ -n "$labels" ]]; then
    labels_json="$(printf '%s' "$labels" | jq -R 'split(",")')"
  else
    labels_json='[]'
  fi

  local deps_json
  if [[ -n "$deps" ]]; then
    deps_json="$(printf '%s' "$deps" | jq -R 'split(",")')"
  else
    deps_json='[]'
  fi

  if [[ -z "$execution_eligible" ]]; then
    case ",${labels}," in
      *,phase:build,*|*,phase:deploy,*|*,phase:iterate,*)
        execution_eligible="true"
        ;;
      *)
        execution_eligible="false"
        ;;
    esac
  fi

  case "$execution_eligible" in
    true|false)
      ;;
    *)
      echo "tracker: --execution-eligible must be true or false" >&2
      return 1
      ;;
  esac

  local now
  now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

  local obj
  obj="$(jq -n \
    --arg id "$id" \
    --arg title "$title" \
    --arg type "$type" \
    --arg status "open" \
    --argjson priority "$priority" \
    --argjson labels "$labels_json" \
    --argjson deps "$deps_json" \
    --arg parent "$parent" \
    --arg spec_id "$spec_id" \
    --arg description "$description" \
    --arg design "$design" \
    --arg acceptance "$acceptance" \
    --argjson execution_eligible "$execution_eligible" \
    --arg superseded_by "$superseded_by" \
    --arg replaces "$replaces" \
    --arg created "$now" \
    --arg updated "$now" \
    '{
      id: $id,
      title: $title,
      type: $type,
      status: $status,
      priority: $priority,
      labels: $labels,
      deps: $deps,
      parent: $parent,
      "spec-id": $spec_id,
      description: $description,
      design: $design,
      acceptance: $acceptance,
      assignee: "",
      notes: "",
      "execution-eligible": $execution_eligible,
      "superseded-by": $superseded_by,
      replaces: $replaces,
      created: $created,
      updated: $updated
    }'
  )"

  local all updated
  all="$(tracker_read_all)" || return 1
  updated="$(printf '%s' "$all" | jq --argjson obj "$obj" '. + [$obj]')"
  tracker_write_all "$updated"
  printf '%s\n' "$id"
}

tracker_create() {
  tracker_with_lock tracker_create_impl "$@"
}

# ── show ───────────────────────────────────────────────────────────────
tracker_show() {
  local id="$1"
  local json_flag=0
  [[ "${2:-}" == "--json" ]] && json_flag=1

  tracker_ensure
  local issue
  issue="$(jq -c "select(.id == \"$id\")" "$tracker_file" | head -1)"

  if [[ -z "$issue" ]]; then
    echo "tracker: issue not found: $id" >&2
    return 1
  fi

  if (( json_flag )); then
    printf '%s\n' "$issue" | jq '.'
  else
    printf '%s\n' "$issue" | jq -r '
      "[\(.status)] \(.id) (\(.type)) — \(.title)\n" +
      (if .description != "" then "  Description: \(.description)\n" else "" end) +
      (if .design != "" then "  Design: \(.design)\n" else "" end) +
      (if .acceptance != "" then "  Acceptance: \(.acceptance)\n" else "" end) +
      (if (.labels | length) > 0 then "  Labels: \(.labels | join(", "))\n" else "" end) +
      (if (.deps | length) > 0 then "  Deps: \(.deps | join(", "))\n" else "" end) +
      (if .parent != "" then "  Parent: \(.parent)\n" else "" end) +
      (if .["execution-eligible"] != null then "  Execution Eligible: \(.["execution-eligible"])\n" else "" end) +
      (if .["superseded-by"] != "" then "  Superseded By: \(.["superseded-by"])\n" else "" end) +
      (if .replaces != "" then "  Replaces: \(.replaces)\n" else "" end) +
      (if .assignee != "" then "  Assignee: \(.assignee)\n" else "" end) +
      (if .["spec-id"] != "" then "  Spec: \(.["spec-id"])\n" else "" end)
    '
  fi
}

# ── update ─────────────────────────────────────────────────────────────
tracker_update_impl() {
  tracker_ensure
  need_cmd jq

  local id="$1"; shift
  local updates=()
  local claim=0

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --status)      updates+=(".status = \"$2\""); shift 2 ;;
      --title)       updates+=(".title = \"$2\""); shift 2 ;;
      --assignee)    updates+=(".assignee = \"$2\""); shift 2 ;;
      --spec-id)     updates+=(".[\"spec-id\"] = \"$2\""); shift 2 ;;
      --parent)      updates+=(".parent = \"$2\""); shift 2 ;;
      --description) updates+=(".description = \"$2\""); shift 2 ;;
      --design)      updates+=(".design = \"$2\""); shift 2 ;;
      --acceptance)  updates+=(".acceptance = \"$2\""); shift 2 ;;
      --notes)       updates+=(".notes = \"$2\""); shift 2 ;;
      --priority)    updates+=(".priority = $2"); shift 2 ;;
      --execution-eligible)
        case "$2" in
          true|false)
            updates+=(".[\"execution-eligible\"] = $2")
            ;;
          *)
            echo "tracker: --execution-eligible must be true or false" >&2
            return 1
            ;;
        esac
        shift 2
        ;;
      --superseded-by) updates+=(".[\"superseded-by\"] = \"$2\""); shift 2 ;;
      --replaces)    updates+=(".replaces = \"$2\""); shift 2 ;;
      --labels)
        local lj
        lj="$(printf '%s' "$2" | jq -R 'split(",")')"
        updates+=(".labels = $lj")
        shift 2
        ;;
      --deps)
        local dj
        dj="$(printf '%s' "$2" | jq -R 'if length == 0 then [] else split(",") end')"
        updates+=(".deps = $dj")
        shift 2
        ;;
      --claim)
        updates+=(".status = \"in_progress\"" ".assignee = \"helix\"")
        shift
        ;;
      -h|--help|help) tracker_usage; return 0 ;;
      *)
        echo "tracker: unknown update flag: $1" >&2
        return 1
        ;;
    esac
  done

  if [[ ${#updates[@]} -eq 0 ]]; then
    echo "tracker: nothing to update" >&2
    return 1
  fi

  local now
  now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  updates+=(".updated = \"$now\"")

  # Build the jq update expression
  local expr
  expr="$(IFS='|'; echo "${updates[*]}")"

  local all
  all="$(tracker_read_all)" || return 1
  local found
  found="$(printf '%s' "$all" | jq "[.[] | select(.id == \"$id\")] | length")"

  if [[ "$found" == "0" ]]; then
    echo "tracker: issue not found: $id" >&2
    return 1
  fi

  local updated
  updated="$(printf '%s' "$all" | jq "[.[] | if .id == \"$id\" then $expr else . end]")"
  tracker_write_all "$updated"
}

tracker_update() {
  tracker_with_lock tracker_update_impl "$@"
}

# ── close ──────────────────────────────────────────────────────────────
tracker_close() {
  local id="$1"
  tracker_with_lock tracker_update_impl "$id" --status closed
}

# ── list ───────────────────────────────────────────────────────────────
tracker_list() {
  tracker_ensure
  need_cmd jq

  local status_filter="" label_filter="" json_flag=0
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --status) status_filter="$2"; shift 2 ;;
      --label)  label_filter="$2"; shift 2 ;;
      --json)   json_flag=1; shift ;;
      *)        shift ;;
    esac
  done

  local all
  all="$(tracker_read_all)" || return 1

  local filtered="$all"
  if [[ -n "$status_filter" ]]; then
    filtered="$(printf '%s' "$filtered" | jq "[.[] | select(.status == \"$status_filter\")]")"
  fi
  if [[ -n "$label_filter" ]]; then
    filtered="$(printf '%s' "$filtered" | jq "[.[] | select(.labels | index(\"$label_filter\"))]")"
  fi

  if (( json_flag )); then
    printf '%s\n' "$filtered" | jq '.'
  else
    printf '%s\n' "$filtered" | jq -r '.[] | "[\(.status)] \(.id) — \(.title)"'
  fi
}

# ── ready ──────────────────────────────────────────────────────────────
# Returns issues that are open and have all deps satisfied (all deps closed)
tracker_ready() {
  tracker_ensure
  need_cmd jq

  local json_flag=0
  local execution_only=0
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --json) json_flag=1; shift ;;
      --execution) execution_only=1; shift ;;
      *) shift ;;
    esac
  done

  local all
  all="$(tracker_read_all)" || return 1

  local ready
  ready="$(printf '%s' "$all" | jq '
    def default_execution_eligible:
      if (.labels | type) != "array" then false
      else
        ((.labels | index("phase:build")) != null) or
        ((.labels | index("phase:deploy")) != null) or
        ((.labels | index("phase:iterate")) != null)
      end;
    . as $all |
    [.[] | select(
      .status == "open" and
      '"$(if (( execution_only )); then printf '((if .["execution-eligible"] == null then default_execution_eligible else .["execution-eligible"] end) == true) and ((.["superseded-by"] // "") == "") and'; else printf 'true and'; fi)"'
      (
        (.deps | length) == 0 or
        (
          .deps as $deps |
          [$all[] | select(.id == ($deps[])) | .status] |
          all(. == "closed")
        )
      )
    )]
  ')"

  if (( json_flag )); then
    printf '%s\n' "$ready"
  else
    printf '%s\n' "$ready" | jq -r '.[] | "[\(.status)] \(.id) — \(.title)"'
  fi
}

# ── blocked ────────────────────────────────────────────────────────────
tracker_blocked() {
  tracker_ensure
  need_cmd jq

  local json_flag=0
  [[ "${1:-}" == "--json" ]] && json_flag=1

  local all
  all="$(tracker_read_all)" || return 1

  local blocked
  blocked="$(printf '%s' "$all" | jq '
    . as $all |
    [.[] | select(
      .status == "open" and
      (.deps | length) > 0 and
      (
        .deps as $deps |
        [$all[] | select(.id == ($deps[])) | .status] |
        any(. != "closed")
      )
    )]
  ')"

  if (( json_flag )); then
    printf '%s\n' "$blocked"
  else
    printf '%s\n' "$blocked" | jq -r '.[] | "[\(.status)] \(.id) — \(.title)"'
  fi
}

# ── dep ────────────────────────────────────────────────────────────────
tracker_dep_impl() {
  local subcmd="$1"; shift

  case "$subcmd" in
    add)
      local child="$1" parent="$2"
      local all
      all="$(tracker_read_all)" || return 1
      local updated
      updated="$(printf '%s' "$all" | jq "[.[] | if .id == \"$child\" then .deps += [\"$parent\"] | .deps |= unique else . end]")"
      tracker_write_all "$updated"
      ;;
    remove)
      local child="$1" parent="$2"
      local all
      all="$(tracker_read_all)" || return 1
      local updated
      updated="$(printf '%s' "$all" | jq "[.[] | if .id == \"$child\" then .deps -= [\"$parent\"] else . end]")"
      tracker_write_all "$updated"
      ;;
    tree)
      local id="$1"
      tracker_ensure
      local all
      all="$(tracker_read_all)" || return 1
      printf '%s\n' "$all" | jq -r --arg id "$id" '
        . as $all |
        .[] | select(.id == $id) |
        "\(.id) — \(.title)",
        (.deps[] as $d | $all[] | select(.id == $d) | "  └─ [\(.status)] \(.id) — \(.title)")
      '
      ;;
    *)
      echo "tracker: unknown dep subcommand: $subcmd" >&2
      return 1
      ;;
  esac
}

tracker_dep() {
  case "${1:-}" in
    add|remove)
      tracker_with_lock tracker_dep_impl "$@"
      ;;
    *)
      tracker_dep_impl "$@"
      ;;
  esac
}

# ── status (health check) ─────────────────────────────────────────────
tracker_status() {
  tracker_ensure
  need_cmd jq

  local json_flag=0
  [[ "${1:-}" == "--json" ]] && json_flag=1

  local all
  all="$(tracker_read_all)" || return 1

  if (( json_flag )); then
    printf '%s' "$all" | jq '{
      total: length,
      open: [.[] | select(.status == "open")] | length,
      in_progress: [.[] | select(.status == "in_progress")] | length,
      closed: [.[] | select(.status == "closed")] | length
    }'
  else
    local total open ip closed
    total="$(printf '%s' "$all" | jq 'length')"
    open="$(printf '%s' "$all" | jq '[.[] | select(.status == "open")] | length')"
    ip="$(printf '%s' "$all" | jq '[.[] | select(.status == "in_progress")] | length')"
    closed="$(printf '%s' "$all" | jq '[.[] | select(.status == "closed")] | length')"
    printf 'tracker: %s issues (%s open, %s in-progress, %s closed)\n' "$total" "$open" "$ip" "$closed"
  fi
}

# ── import/export ──────────────────────────────────────────────────────
tracker_import_impl() {
  need_cmd jq

  local from="auto" file_path=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --from) from="$2"; shift 2 ;;
      --file) file_path="$2"; shift 2 ;;
      *)      file_path="$1"; shift ;;
    esac
  done

  local source="" source_label=""
  local issues="[]"

  case "$from" in
    auto)
      if command -v bd >/dev/null 2>&1 && [[ -d "$beads_dir" ]]; then
        if issues="$(bd list --json 2>/dev/null)" && [[ -n "$issues" ]] && [[ "$(printf '%s' "$issues" | jq 'length')" -gt 0 ]]; then
          source="bd"
          source_label="bd (live Dolt database)"
        fi
      fi

      if [[ -z "$source" ]] && command -v br >/dev/null 2>&1; then
        if issues="$(br list --json 2>/dev/null)" && [[ -n "$issues" ]] && [[ "$(printf '%s' "$issues" | jq 'length')" -gt 0 ]]; then
          source="br"
          source_label="br (live SQLite database)"
        fi
      fi

      if [[ -z "$source" ]]; then
        local import_jsonl="${file_path:-$beads_file}"
        if [[ -f "$import_jsonl" ]] && [[ -s "$import_jsonl" ]]; then
          issues="$(jq -s '.' "$import_jsonl" 2>/dev/null || echo '[]')"
          if [[ "$(printf '%s' "$issues" | jq 'length')" -gt 0 ]]; then
            source="jsonl"
            source_label="${import_jsonl} (beads JSONL)"
          fi
        fi
      fi
      ;;
    bd)
      if ! command -v bd >/dev/null 2>&1; then
        echo "tracker: bd is not installed" >&2
        return 1
      fi
      issues="$(bd list --json 2>/dev/null || echo '[]')"
      source="bd"
      source_label="bd (live Dolt database)"
      ;;
    br)
      if ! command -v br >/dev/null 2>&1; then
        echo "tracker: br is not installed" >&2
        return 1
      fi
      issues="$(br list --json 2>/dev/null || echo '[]')"
      source="br"
      source_label="br (live SQLite database)"
      ;;
    jsonl|beads-jsonl)
      local import_jsonl="${file_path:-$beads_file}"
      if [[ ! -f "$import_jsonl" ]] || [[ ! -s "$import_jsonl" ]]; then
        echo "tracker: no beads JSONL found at ${import_jsonl}" >&2
        return 1
      fi
      issues="$(jq -s '.' "$import_jsonl" 2>/dev/null || echo '[]')"
      source="jsonl"
      source_label="${import_jsonl} (beads JSONL)"
      ;;
    *)
      echo "tracker: unknown import source: $from" >&2
      return 1
      ;;
  esac

  if [[ -z "$source" ]]; then
    echo "tracker: no beads data found (tried bd, br, ${beads_file})" >&2
    return 1
  fi

  local count
  count="$(printf '%s' "$issues" | jq 'length')"
  printf 'tracker: found %s issues from %s\n' "$count" "$source_label" >&2

  # Check for existing tracker data
  tracker_ensure
  local existing
  existing="$(tracker_read_all)" || return 1
  local existing_count
  existing_count="$(printf '%s' "$existing" | jq 'length')"

  if (( existing_count > 0 )); then
    printf 'tracker: WARNING — .helix/issues.jsonl already has %s issues\n' "$existing_count" >&2
    printf 'tracker: migration will APPEND, not replace. Duplicates may result.\n' >&2
    printf 'tracker: to start fresh, remove .helix/issues.jsonl first.\n' >&2
  fi

  local normalized
  normalized="$(tracker_normalize_issue_array "$issues")"

  local merged
  merged="$({
    printf '%s\n' "$existing"
    printf '%s\n' "$normalized"
  } | jq -s '.[0] + .[1]')"
  tracker_write_all "$merged"

  local migrated
  migrated="$(printf '%s' "$normalized" | jq 'length')"
  printf 'tracker: imported %s beads to .helix/issues.jsonl\n' "$migrated" >&2
  printf 'tracker: source: %s\n' "$source_label" >&2
  printf 'tracker: verify with: helix tracker status\n' >&2
}

tracker_import() {
  tracker_with_lock tracker_import_impl "$@"
}

tracker_export_impl() {
  tracker_ensure
  need_cmd jq

  local to="jsonl" file_path="" stdout_flag=0
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --to)     to="$2"; shift 2 ;;
      --file)   file_path="$2"; shift 2 ;;
      --stdout) stdout_flag=1; shift ;;
      *)        file_path="$1"; shift ;;
    esac
  done

  case "$to" in
    jsonl|beads-jsonl|auto)
      ;;
    *)
      echo "tracker: unsupported export target in simple file-backed mode: $to" >&2
      echo "tracker: export beads as JSONL and import them into bd/br separately" >&2
      return 1
      ;;
  esac

  local all
  all="$(tracker_read_all)" || return 1

  if (( stdout_flag )); then
    printf '%s\n' "$all" | jq -c '.[]'
    return 0
  fi

  local output_jsonl="${file_path:-$beads_file}"
  tracker_write_jsonl_file "$all" "$output_jsonl"
  printf '%s\n' "$output_jsonl"
}

tracker_export() {
  tracker_with_lock tracker_export_impl "$@"
}

tracker_migrate() {
  tracker_import "$@"
}

tracker_usage() {
  cat <<EOF
Usage:
  helix tracker init
  helix tracker create "Title" [--type TYPE] [--labels a,b] [--deps id1,id2] [--parent ID] [--spec-id REF] [--description TEXT] [--design TEXT] [--acceptance TEXT] [--execution-eligible true|false] [--superseded-by ID] [--replaces ID]
  helix tracker show <id> [--json]
  helix tracker update <id> [--status S] [--title T] [--assignee A] [--priority N] [--labels a,b] [--description TEXT] [--design TEXT] [--acceptance TEXT] [--notes TEXT] [--claim] [--execution-eligible true|false] [--superseded-by ID] [--replaces ID]
  helix tracker close <id>
  helix tracker list [--status S] [--label L] [--json]
  helix tracker ready [--json] [--execution]
  helix tracker blocked [--json]
  helix tracker dep add <child> <parent>
  helix tracker dep remove <child> <parent>
  helix tracker dep tree <id>
  helix tracker status [--json]
  helix tracker import [--from auto|bd|br|jsonl] [--file PATH]
  helix tracker export [--to jsonl] [--file PATH] [--stdout]
  helix tracker migrate [args...]
  helix tracker help

Notes:
  Canonical storage is .helix/issues.jsonl.
  Export writes bead-compatible JSONL.
  Migrate is a compatibility alias for import.
EOF
}

# ── CLI dispatch (when called as `helix tracker <cmd>`) ────────────────
tracker_dispatch() {
  local cmd="${1:-status}"; shift || true

  case "$cmd" in
    help|--help|-h) tracker_usage ;;
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
    *)
      echo "tracker: unknown command: $cmd" >&2
      tracker_usage >&2
      return 1
      ;;
  esac
}
