# Runbook Generation Prompt

Create a concise, service-specific runbook.

## Storage Location

`docs/helix/05-deploy/runbook.md`

## Key Sections

- Keep the runbook executable during an incident.
- Include only the commands, checks, and escalation paths needed to operate this service.
- Cover deployment, rollback, monitoring, troubleshooting, maintenance, recovery, and security response.
- Omit generic system-administration filler.

## Completion Criteria

- [ ] Procedures are command-level and service-specific
- [ ] Monitoring and escalation paths are explicit
- [ ] Recovery and rollback steps are present
