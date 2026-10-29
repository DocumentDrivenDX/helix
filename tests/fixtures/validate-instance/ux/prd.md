---
ddx:
  id: prd
  type: prd
  authoring:
    home: repo
---

# Product Requirements Document

## Summary

DepositMatch helps reconciliation leads match bank deposits to invoices.

## Problem and Goals

Reconciliation takes too long and errors are found late.

## Users and Scope

### Primary Persona: Maya

**Role**: Reconciliation lead
**Goals**: Reconcile every client by Friday
**Pain Points**: Client exports change format without notice

### User Segments

| User | Context | Needs | Evidence | Confidence | Status |
|------|---------|-------|----------|------------|--------|
| Reconciliation lead | Desktop, 12 to 20 clients a week | Trust imported rows | Research plan `pilot-reviewer-interviews` | medium | validated |

### User Needs

| Need | Importance | Evidence | Confidence | Status |
|------|------------|----------|------------|--------|
| Trust imported rows | high | Research plan `pilot-reviewer-interviews` | medium | validated |
| Tell the client which rows failed | medium | none | low | assumed |

## Requirements

### Must Have (P0)

1. Import bank and invoice CSV files for a client.

## Functional Requirements

Import CSV files with saved column mappings.

## Acceptance Test Sketches

Upload two CSV files and reach the import summary.

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Client formats drift | Medium | Saved mappings flag renamed columns |

## Success Criteria

A reviewer can import a representative bank CSV and invoice CSV and reach the
import summary without support.
