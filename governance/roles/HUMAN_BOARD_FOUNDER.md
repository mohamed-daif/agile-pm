# HUMAN_BOARD_FOUNDER — Role Definition

> **Version:** 1.0  
> **Status:** Active  
> **Authority:** Charter §3  
> **Role Type:** Human — Ultimate Authority  
> **Last Updated:** 2026-01-04

---

## 1. Purpose

The Board/Founder represents the **ultimate authority** within the organization, responsible for company vision, strategic direction, and final arbitration of all governance matters. This role exists above the day-to-day Product Management structure and intervenes only when escalation reaches the highest level.

---

## 2. Responsibilities

### 2.1 Strategic Authority (MUST)

| Responsibility | Scope |
|----------------|-------|
| Company vision | Define long-term organizational direction |
| Major investments | Approve significant capital expenditure |
| Strategic partnerships | Authorize external partnerships |
| Organizational structure | Define company hierarchy |
| Charter authority | Ultimate authority over governance charter |

### 2.2 Governance Authority (MUST)

| Responsibility | Scope |
|----------------|-------|
| Charter amendments | Final approval for charter changes |
| Role creation | Approve new Human/Agent role definitions |
| Exception authority | Override any governance rule with justification |
| Conflict resolution | Final arbiter when PM authority is insufficient |
| Audit authority | Commission governance audits |

### 2.3 Validation Authority (MUST)

| Responsibility | Scope |
|----------------|-------|
| Major release approval | Go/No-Go for critical releases |
| Risk acceptance (critical) | Accept risks beyond PM authority |
| Legal/compliance final | Ultimate compliance decisions |
| External commitments | Authorize customer/partner commitments |

---

## 3. Explicit Non-Responsibilities (MUST NOT)

| Non-Responsibility | Reason |
|--------------------|--------|
| Day-to-day product decisions | Delegated to PM Department (§4) |
| Sprint-level planning | Operational concern for PM/Agents |
| Technical implementation | Agent domain |
| Code review | Technical PM and Agent domain |
| Routine approvals | Delegated to appropriate PM |
| Direct Agent interaction | Communicate through PM layer |

---

## 4. Obsidian Workflow Interactions

### 4.1 Read Permissions

| Folder | Permitted | Purpose |
|--------|-----------|---------|
| `backlog/` | ✅ YES | Strategic oversight |
| `sprints/` | ✅ YES | Progress monitoring |
| `epics/` | ✅ YES | Product direction oversight |
| `plans/` | ✅ YES | Planning oversight |
| `reviews/` | ✅ YES | Quality oversight |
| `meetings/` | ✅ YES | Communication oversight |
| `_dashboards/` | ✅ YES | Health metrics |
| `_diagrams/` | ✅ YES | Architecture oversight |
| `_governance/` | ✅ YES | Governance oversight |

### 4.2 Write Permissions

| Folder | Permitted | Conditions |
|--------|-----------|------------|
| `backlog/` | ❌ NO | Delegate to PM |
| `sprints/` | ❌ NO | Delegate to PM |
| `epics/` | ✅ APPROVE | Strategic initiatives only |
| `plans/` | ✅ APPROVE | Major plans requiring Board approval |
| `reviews/` | ❌ NO | Delegate to PM |
| `meetings/` | ❌ NO | Delegate to PM |
| `_dashboards/` | ❌ NO | Read-only oversight |
| `_governance/` | ✅ APPROVE | Charter amendments only |

### 4.3 Decision Authority

| Decision Type | Authority Level | Notes |
|---------------|-----------------|-------|
| Company direction | 👑 ULTIMATE | No override possible |
| Charter changes | 👑 ULTIMATE | Final approval required |
| Major budget | 👑 ULTIMATE | Above PM threshold |
| Critical risk | 👑 ULTIMATE | Risks affecting company viability |
| Product strategy | ✅ APPROVE | Normally delegated to PM |
| Technical decisions | 🔍 REVIEW | Normally delegated to Tech PM |

---

## 5. Agent Delegation Model

| Task Type | Delegate To | Human Retains |
|-----------|-------------|---------------|
| Product execution | Non-Technical PM | Strategic oversight |
| Technical execution | Technical PM | Architecture oversight |
| All Agent work | PM Department | Governance oversight |
| Reporting | PM Department | Summary review |

---

## 6. Coordination with Other Roles

| Role | Relationship | Interaction |
|------|--------------|-------------|
| Non-Technical PM | Delegates to | Strategic direction, budget limits |
| Technical PM | Delegates to | Technical vision, architecture limits |
| All Agents | No direct contact | Through PM intermediary |

---

## 7. Escalation Triggers

| Condition | Action |
|-----------|--------|
| PM conflict unresolved | Final arbitration required |
| Budget exceeds PM authority | Board approval required |
| Legal/compliance risk | Board review required |
| Charter violation | Board intervention |
| Existential business risk | Board decision |

---

## 8. Communication Protocol

### 8.1 With PM Department

| Scenario | Board Action | Expected Response |
|----------|--------------|-------------------|
| Strategic pivot | Issue directive | PM creates implementation plan |
| Budget constraint | Set limits | PM operates within limits |
| Governance concern | Raise issue | PM investigates and reports |
| Escalation received | Review and decide | PM executes decision |

### 8.2 Output Requirements

When making decisions, this role MUST document:

| Element | Requirement |
|---------|-------------|
| Decision | Clear statement of choice |
| Rationale | Business/strategic reasoning |
| Scope | What is affected |
| Delegation | Who executes |
| Date | When decision was made |

---

## 9. Related Documents

- [Charter §3](../charter/COMPANY_AGILE_DELIVERY_ROLES_AUTOMATION_CHARTER.md)
- [AUTHORITY_MATRIX.md](AUTHORITY_MATRIX.md)
- [HUMAN_PRODUCT_OWNER.md](HUMAN_PRODUCT_OWNER.md)
- [HUMAN_NON_TECHNICAL_PM.md](HUMAN_NON_TECHNICAL_PM.md)
- [HUMAN_TECHNICAL_PM.md](HUMAN_TECHNICAL_PM.md)

---

## 10. Amendments

Changes to this document require:
1. Board self-amendment or
2. Unanimous PM recommendation with Board approval

This document is authoritative and binding.
