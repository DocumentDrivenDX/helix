# API Contract: [Contract Name] [FEAT-XXX]

**Contract ID**: API-XXX
**Type**: [REST | GraphQL | CLI | Library]

## CLI Interface (if applicable)

### Command: [command-name]
**Purpose**: [What this command does]
**Usage**: `$ [program] [command] [options]`

**Options**:
- `--option1, -o` : [Description]

**Input**: Format: [JSON|Text|File], Schema: [structure]
**Output**: Format: [JSON|Text], Schema: [structure]

**Exit Codes**:
- `0`: Success
- `1`: General error
- `2`: [Specific error]

**Examples**:
```bash
$ [program] [command] --option value
[Expected output]
```

## REST API (if applicable)

### Base URL
```
[protocol]://[host]:[port]/api/v1
```

### GET /[resource]
**Purpose**: [What this endpoint does]
**Authentication**: [Required|Optional|None]

**Request**:
```http
GET /[resource]?param1=value HTTP/1.1
Authorization: Bearer [token]
```

**Success (200)**:
```json
{ "field1": "value", "field2": 123 }
```

**Error (4xx/5xx)**:
```json
{ "error": "Error message", "code": "ERROR_CODE", "details": {} }
```

## Library API (if applicable)

### Function: `functionName`
```[language]
function functionName(param1: Type, param2: Type): ReturnType
```
- `param1`: [Description, constraints]
- **Returns**: [Description]
- **Throws**: `ErrorType`: When [condition]

## Data Contracts

### Input Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": { "field1": { "type": "string" } },
  "required": ["field1"]
}
```

### Error Response Format
```json
{
  "error": { "code": "ERROR_CODE", "message": "Human readable message", "details": {} }
}
```

## Validation

### Test Scenarios
1. **Happy Path**: [Expected behavior with valid input]
2. **Error/Edge Cases**: [Invalid input, boundary conditions, error reporting]
