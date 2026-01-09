# HUMAN_NON_TECHNICAL_PM — Role Definition

> **Version:** 1.0  
> **Status:** Active  
> **Authority:** Charter §4.1  
> **Role Type:** Human — Strategic & Business Authority  
> **Last Updated:** 2026-01-04

---

## 1. Purpose

The Non-Technical Product Manager is the **business and strategic decision authority** within the Product Management Department. This role ensures product decisions align with business goals without requiring technical/coding knowledge. All technical complexity must be translated into business impact by Agents and Technical PM.

Per Charter §4.0 (Dual-PM Model), this role operates alongside the Technical PM with equal authority in their respective domains.

---

## 2. Responsibilities

### 2.1 Strategic Authority (MUST)

| Responsibility | Scope |
|----------------|-------|
| Product vision | Define what gets built and why |
| Market positioning | Ensure product-market fit |
| Scope decisions | Accept/reject feature requests |
| Priority setting | Set P0/P1/P2/P3 for all work items |
| Budget authority | Approve paid tools, infrastructure costs |
| Timeline commitments | Set deadlines, negotiate scope trade-offs |
| Customer commitments | Authorize external promises |

### 2.2 Governance Authority (MUST)

| Responsibility | Scope |
|----------------|-------|
| Agent activation | Approve new Agent types |
| Role scoping | Define/modify Agent responsibilities |
| Escalation resolution | Resolve blocked or conflicting work |
| Exception approval | Override automation rules when justified |
| Resource allocation | Assign capacity priorities |

### 2.3 Validation Authority (MUST)

| Responsibility | Scope |
|----------------|-------|
| Story acceptance | Approve/reject story completion |
| Release Go/No-Go | Final decision for production releases |
| Business risk acceptance | Accept identified business risks |
| Quality thresholds | Set business-impacting quality standards |

---

## 3. Explicit Non-Responsibilities (MUST NOT)

| Non-Responsibility | Reason |
|--------------------|--------|
| Write or review code | Technical domain |
| Receive code snippets | Must get business-language translations |
| Technical architecture decisions | Delegated to Technical PM |
| Database/API design | Technical domain |
| CI/CD configuration | DevOps Agent domain |
| Technical debt prioritization | Technical PM domain |
| Security implementation | Security Agent domain |

---

## 4. Obsidian Workflow Interactions

### 4.1 Read Permissions

| Folder | Permitted | Purpose |
|--------|-----------|---------|
| `backlog/` | ✅ YES | Understand work queue |
| `sprints/` | ✅ YES | Monitor progress |
| `epics/` | ✅ YES | Product direction |
| `plans/` | ✅ YES | Planning oversight |
| `reviews/` | ✅ YES | Quality oversight |
| `meetings/` | ✅ YES | Stakeholder communication |
| `_dashboards/` | ✅ YES | Health metrics |
| `_diagrams/` | ❌ NO | Technical detail (use summaries) |
| `_governance/` | ✅ YES | Governance oversight |

### 4.2 Write Permissions

| Folder | Permitted | Conditions |
|--------|-----------|------------|
| `backlog/` | ❌ NO | Request via Agent |
| `sprints/` | ❌ NO | Approve via Tech PM |
| `epics/` | ✅ CREATE/APPROVE | Business epics, acceptance criteria |
| `plans/` | ✅ APPROVE | Business plans |
| `reviews/` | ❌ NO | Receive summaries |
| `meetings/` | ✅ WRITE | Stakeholder meetings |
| `_dashboards/` | ❌ NO | Read-only |
| `_governance/` | ✅ APPROVE | Policy changes |

### 4.3 Decision Authority

| Decision Type | Authority Level | Notes |
|---------------|-----------------|-------|
| Product scope | ✅ OWNER | Final authority |
| Product priority | ✅ OWNER | Final authority |
| Budget allocation | ✅ OWNER | Within Board limits |
| Business risk | ✅ OWNER | Final authority |
| Technical direction | 🔍 REVIEW | Delegate to Tech PM |
| Architecture | 🔍 REVIEW | Delegate to Tech PM |
| Release timing | ✅ OWNER | Business decision |

---

## 5. Agent Delegation Model

| Task Type | Delegate To | Human Retains |
|-----------|-------------|---------------|
| Technical planning | Technical PM | Business approval |
| Implementation | Engineer Agents | None (via Tech PM) |
| Documentation | Technical Writer Agent | Review (business clarity) |
| Testing | QA Agent | None (via Tech PM) |
| Reporting | All Agents | Summary review |

---

## 6. Coordination with Other Roles

| Role | Relationship | Interaction |
|------|--------------|-------------|
| Board/Founder | Reports to | Strategic direction, budget limits |
| Technical PM | Peer (Dual-PM) | Technical translation, shared decisions |
| Technical Writer Agent | Receives from | Business-language reports |
| All Executor Agents | No direct contact | Through Technical PM |

---

## 7. Escalation Triggers

| Condition | Action |
|-----------|--------|
| Scope change request | Non-Tech PM decision required |
| Budget overrun | Non-Tech PM approval required |
| Timeline slip | Non-Tech PM decision on scope/timeline trade-off |
| Customer commitment | Non-Tech PM approval required |
| Cross-team conflict | Non-Tech PM arbitration |

---

## 8. Communication Protocol

### 8.1 With Technical PM

| Scenario | Non-Tech PM Action | Expected Response |
|----------|-------------------|-------------------|
| New feature request | Define business value | Tech PM provides technical plan |
| Scope question | Define acceptance criteria | Tech PM clarifies implementation |
| Risk concern | Ask for business impact | Tech PM translates technical risk |
| Timeline question | Request estimate | Tech PM provides breakdown |

### 8.2 With Agents (via Technical Writer)

| Scenario | Non-Tech PM Action | Expected Response |
|----------|-------------------|-------------------|
| Status request | Ask for summary | Business-language report |
| Decision needed | Request options | Pros/cons in business terms |
| Approval needed | Review summary | Clear recommendation |

### 8.3 Output Requirements

When making decisions, this role MUST document:

| Element | Requirement |
|---------|-------------|
| Decision | Clear statement of choice |
| Business rationale | Why this choice benefits business |
| Alternatives | What was considered/rejected |
| Customer impact | How this affects users |
| Date | When decision was made |

---

## 9. Translation Requirements

All communication TO this role MUST:
- Use business language, not technical jargon
- Express impact in terms of: time, cost, risk, customer value
- Avoid code snippets, API details, architecture diagrams
- Provide clear recommendations with trade-offs

---

## 10. Related Documents

- [Charter §4.1](../charter/COMPANY_AGILE_DELIVERY_ROLES_AUTOMATION_CHARTER.md)
- [AUTHORITY_MATRIX.md](AUTHORITY_MATRIX.md)
- [HUMAN_PRODUCT_OWNER.md](HUMAN_PRODUCT_OWNER.md)
- [HUMAN_TECHNICAL_PM.md](HUMAN_TECHNICAL_PM.md)
- [TECHNICAL_WRITER_AGENT.md](TECHNICAL_WRITER_AGENT.md)

---

## 11. Amendments

Changes to this document require:
1. Written proposal with rationale
2. Impact assessment
3. Both PM approval (per Dual-PM Model)
4. Version increment

This document is authoritative and binding.
