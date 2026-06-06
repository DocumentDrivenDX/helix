---
ddx:
  id: NET-001
  type: network-plan
  status: in-progress
  links: []
---

# Network Plan — production VPC

## Outstanding

- VPC peering CIDR conflict with shared-services account (blocks
  rollout to prod)
- Cloudflare zone provisioning pending finance approval (blocks
  external hostname assignment)

Both are blocking infra rollout.
