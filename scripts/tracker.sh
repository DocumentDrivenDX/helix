#!/usr/bin/env bash
# Built-in JSONL issue tracker for HELIX.
# Stores issues in .helix/issues.jsonl — one JSON object per line.
# Requires: jq

# ── paths ──────────────────────────────────────────────────────────────
tracker_dir="${HELIX_TRACKER_DIR:-${target_root:-.}/.helix}"
tracker_file="${tracker_dir}/issues.jsonl"

tracker_init() {
  mkdir -p "$tracker_dir"
  touch "$tracker_file"
}

tracker_ensure() {
  if [[ ! -f "$tracker_file" ]]; then
    tracker_init
  fi
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
    jq -s '.' "$tracker_file"
  fi
}

# Write a JSON array back as JSONL (one object per line, sorted by id)
tracker_write_all() {
  local json="$1"
  printf '%s' "$json" | jq -c '.[] | .' > "${tracker_file}.tmp"
  mv "${tracker_file}.tmp" "$tracker_file"
}

# Append a single issue (JSON object) to the file
tracker_append() {
  local obj="$1"
  printf '%s\n' "$obj" >> "$tracker_file"
}

# ── create ─────────────────────────────────────────────────────────────
tracker_create() {
  tracker_ensure
  need_cmd jq

  local title="" type="task" labels="" parent="" spec_id="" description="" design="" acceptance="" priority=2
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --type)       type="$2"; shift 2 ;;
      --labels)     labels="$2"; shift 2 ;;
      --parent)     parent="$2"; shift 2 ;;
      --spec-id)    spec_id="$2"; shift 2 ;;
      --description) description="$2"; shift 2 ;;
      --design)     design="$2"; shift 2 ;;
      --acceptance) acceptance="$2"; shift 2 ;;
      --priority)   priority="$2"; shift 2 ;;
      --silent)     shift ;; # compat: just suppress extra output
      *)            title="$1"; shift ;;
    esac
  done

  if [[ -z "$title" ]]; then
    echo "tracker: title required" >&2
    return 1
  fi

  local id
  id="$(tracker_gen_id hx)"

  local labels_json
  if [[ -n "$labels" ]]; then
    labels_json="$(printf '%s' "$labels" | jq -R 'split(",")')"
  else
    labels_json='[]'
  fi

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
    --arg parent "$parent" \
    --arg spec_id "$spec_id" \
    --arg description "$description" \
    --arg design "$design" \
    --arg acceptance "$acceptance" \
    --arg created "$now" \
    --arg updated "$now" \
    '{
      id: $id,
      title: $title,
      type: $type,
      status: $status,
      priority: $priority,
      labels: $labels,
      parent: $parent,
      "spec-id": $spec_id,
      description: $description,
      design: $design,
      acceptance: $acceptance,
      deps: [],
      assignee: "",
      notes: "",
      created: $created,
      updated: $updated
    }'
  )"

  tracker_append "$obj"
  printf '%s\n' "$id"
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
      (if .assignee != "" then "  Assignee: \(.assignee)\n" else "" end) +
      (if .["spec-id"] != "" then "  Spec: \(.["spec-id"])\n" else "" end)
    '
  fi
}

# ── update ─────────────────────────────────────────────────────────────
tracker_update() {
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
      --description) updates+=(".description = \"$2\""); shift 2 ;;
      --design)      updates+=(".design = \"$2\""); shift 2 ;;
      --acceptance)  updates+=(".acceptance = \"$2\""); shift 2 ;;
      --notes)       updates+=(".notes = \"$2\""); shift 2 ;;
      --priority)    updates+=(".priority = $2"); shift 2 ;;
      --labels)
        local lj
        lj="$(printf '%s' "$2" | jq -R 'split(",")')"
        updates+=(".labels = $lj")
        shift 2
        ;;
      --claim)
        updates+=(".status = \"in_progress\"" ".assignee = \"helix\"")
        shift
        ;;
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
  all="$(tracker_read_all)"
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

# ── close ──────────────────────────────────────────────────────────────
tracker_close() {
  local id="$1"
  tracker_update "$id" --status closed
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
  all="$(tracker_read_all)"

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
  [[ "${1:-}" == "--json" ]] && json_flag=1

  local all
  all="$(tracker_read_all)"

  local ready
  ready="$(printf '%s' "$all" | jq '
    . as $all |
    [.[] | select(
      .status == "open" and
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
  all="$(tracker_read_all)"

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
tracker_dep() {
  local subcmd="$1"; shift

  case "$subcmd" in
    add)
      local child="$1" parent="$2"
      local all
      all="$(tracker_read_all)"
      local updated
      updated="$(printf '%s' "$all" | jq "[.[] | if .id == \"$child\" then .deps += [\"$parent\"] | .deps |= unique else . end]")"
      tracker_write_all "$updated"
      ;;
    remove)
      local child="$1" parent="$2"
      local all
      all="$(tracker_read_all)"
      local updated
      updated="$(printf '%s' "$all" | jq "[.[] | if .id == \"$child\" then .deps -= [\"$parent\"] else . end]")"
      tracker_write_all "$updated"
      ;;
    tree)
      local id="$1"
      tracker_ensure
      local all
      all="$(tracker_read_all)"
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

# ── status (health check) ─────────────────────────────────────────────
tracker_status() {
  tracker_ensure
  need_cmd jq

  local json_flag=0
  [[ "${1:-}" == "--json" ]] && json_flag=1

  local all
  all="$(tracker_read_all)"

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

# ── CLI dispatch (when called as `helix tracker <cmd>`) ────────────────
tracker_dispatch() {
  local cmd="${1:-status}"; shift || true

  case "$cmd" in
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
    *)
      echo "tracker: unknown command: $cmd" >&2
      echo "tracker: commands: init create show update close list ready blocked dep status" >&2
      return 1
      ;;
  esac
}
