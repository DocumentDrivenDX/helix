# Data Design

## Conceptual Data Model

```mermaid
erDiagram
    %% [Define entities with attributes and relationships]
```

### Entity Descriptions

#### Entity: [Name]
- **Purpose**: [What this entity represents]
- **Key Attributes**: [Most important fields]
- **Business Rules**: [Rules governing this entity]
- **Volume**: [Expected records] | **Growth**: [Rate]

## Logical Data Model

### Table: [table_name]
```sql
CREATE TABLE table_name (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- [columns with types and constraints]
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_table_field ON table_name(field);
```

### Relationships

| From | To | Type | Cardinality | On Delete |
|------|-----|------|-------------|-----------|
| [Entity1] | [Entity2] | [1:N, N:M] | [Required/Optional] | [CASCADE/RESTRICT/SET NULL] |

## Data Patterns

### Audit Trail
```sql
-- [Audit log table and trigger implementation]
```

### Soft Deletes
```sql
-- [deleted_at column, active views, soft delete function]
```

### Versioning (if needed)
- **Approach**: [Temporal tables | Version tables | Event sourcing]

## Access Patterns

### Common Queries
```sql
-- [Key query with index support notes]
```

### Caching Strategy

| Data Type | Cache Level | TTL | Invalidation |
|-----------|------------|-----|--------------|
| [Type] | [App/CDN/Redis] | [Duration] | [Strategy] |

## Validation Rules

| Entity.Field | Rules | Error Message |
|--------------|-------|---------------|
| [Field] | [Constraints] | [Message] |

## Migration Strategy

- **Tooling**: [Migration framework]
- **Approach**: [Versioned migrations with rollback]
- **Data backfill**: [Strategy for existing data]

## Data Security

| Data Type | Classification | Protection |
|-----------|---------------|------------|
| [Type] | [Public/Internal/Confidential/Restricted] | [Controls] |

- **Encryption at rest**: [Strategy]
- **Encryption in transit**: [Strategy]
- **Data retention**: [Policy]
