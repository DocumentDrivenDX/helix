# Metric Definition Prompt

Create one reusable metric definition.

## Storage Location

`docs/helix/06-iterate/metrics/<name>.yaml` -- one file per metric, filename matches the `name` field.

## Produced Output
- A YAML metric definition file

## Prompt

Define the metric as the authoritative source for ratchets, dashboards, experiments, and monitoring.

Keep the definition minimal: required fields are `name`, `description`, `unit`, `direction`, and `command`. Add `output_pattern`, `tolerance`, and `labels` only when needed.

The command must be deterministic, repeatable, and free of side effects or external service dependencies. Prefer `METRIC <name>=<value>` output unless an `output_pattern` is required.

Use the template at `workflows/phases/06-iterate/artifacts/metric-definition/template.md`.

## Consumers

| Consumer | How it references the definition |
|----------|--------------------------------|
| Ratchet floor fixture | `metric:` field pointing to the YAML file |
| Monitoring setup | Reads name, unit, labels |
| Metrics dashboard | Reads units and direction |
| Experiment session | Reads command, direction, tolerance |

## Completion Criteria
- [ ] All required fields populated
- [ ] Command is deterministic and repeatable
- [ ] Filename matches the `name` field
