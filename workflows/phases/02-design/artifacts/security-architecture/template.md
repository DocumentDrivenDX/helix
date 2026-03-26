# Security Architecture

## Summary

| Aspect | Decision |
|--------|----------|
| Security Approach | [Overview] |
| Key Principles | [Primary principles] |
| Critical Controls | [Most important controls] |

## Security Principles

### Defense in Depth
- **Network**: [Firewalls, segmentation, IDS]
- **Application**: [Input validation, auth, output encoding]
- **Data**: [Encryption, access controls, DLP]

### Least Privilege
- **Users**: [RBAC, just-in-time access]
- **Services**: [Service accounts, API permissions, resource isolation]
- **Admin**: [Privileged access management]

## Security Architecture Diagram

```
[Network zones: Internet -> WAF -> DMZ -> App Tier -> Data Tier]
[Show security boundaries and controls at each layer]
```

## Authentication & Authorization

### Authentication
- **Identity Provider**: [Provider, protocol, features]
- **MFA**: [Methods, when required]
- **Sessions**: [Storage, timeouts, security attributes]

### Authorization
```
Role Hierarchy:
[Define roles and inheritance]

Permission Model: Resource.Action.Scope
[Define with examples]
```

## Data Protection

| Classification | Description | Controls |
|----------------|-------------|----------|
| [Public/Internal/Confidential/Restricted] | [Description] | [Controls] |

### Encryption
- **At Rest**: [Database, files, backups -- algorithms and key management]
- **In Transit**: [External TLS, internal mTLS, DB connections]
- **Key Management**: [Storage, rotation, recovery]

## Application Security

- **Input Validation**: [Server-side, rules, sanitization]
- **API Security**: [Auth, rate limiting, schema validation]
- **Session Security**: [CSRF, XSS prevention, CSP]

## Monitoring & Incident Response

### Logging
- **Security Events**: [Auth, authz, security events]
- **Audit Trail**: [Admin actions, config changes]
- **Storage**: [Centralized, retention, SIEM integration]

### Alerting
- [Alert conditions and escalation]

### Incident Response
1. **Detection**: [Automated + manual reporting]
2. **Containment**: [Isolation procedures]
3. **Recovery**: [Restoration, monitoring for recurrence]

## Threat Mitigation Mapping

| Threat ID | Threat | Control | Implementation | Verification |
|-----------|--------|---------|----------------|--------------|
| [From threat model] | [Description] | [Control] | [How] | [How verified] |

## Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| [Risk] | H/M/L | H/M/L | [Strategy] |
