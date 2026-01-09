# HUMAN_PRODUCT_OWNER — Role Definition

> **Version:** 1.0  
> **Status:** Active  
> **Authority:** Charter §4.0, §4.1, §4.2  
> **Last Updated:** 2026-01-04

---

## 1. Purpose

The Human Product Owner is the **sole authority** for strategic, sensitive, and final decisions across the Agile Delivery System.

This role embodies both the Non-Technical PM and Technical PM authorities (per Charter §4.0 Dual-PM Model). From the system perspective, these are treated as two distinct decision entities with equal authority.

This document governs the Human side of the Human-Agent collaboration model within the Obsidian-based delivery system.

---

## 2. Responsibilities

### 2.1 Strategic Authority (MUST)

| Responsibility | Scope |
|----------------|-------|
| Product vision and roadmap | Define what gets built and why |
| Scope approval | Accept or reject feature requests |
| Priority decisions | Set P0/P1/P2/P3 levels for all work items |
| Budget authority | Approve paid tools, infrastructure costs |
| Risk acceptance | Accept or reject identified risks |
| Release approval | Final Go/No-Go for production releases |
| Timeline commitments | Set deadlines and negotiate scope |

### 2.2 Governance Authority (MUST)

| Responsibility | Scope |
|----------------|-------|
| Agent activation | Approve new Agent types (Charter §11.7) |
| Role definition | Define or modify Agent responsibilities |
| Escalation resolution | Resolve blocked or conflicting work |
| Charter amendments | Approve changes to governance documents |
| Exception approval | Override automation rules when justified |

### 2.3 Validation Authority (MUST)

| Responsibility | Scope |
|----------------|-------|
| Acceptance criteria | Approve or reject story completion |
| Quality gates | Set thresholds for code quality |
| Architecture decisions | Approve ADRs |
| Security posture | Accept or reject security recommendations |

---

## 3. Explicit Non-Responsibilities

The Human Product Owner **MUST NOT**:

| Non-Responsibility | Reason |
|--------------------|--------|
| Write production code | Execution is Agent domain |
| Perform mechanical edits | Structural maintenance is Agent domain |
| Generate reports | Report generation is Agent domain |
| Update INDEX.md | Auto-generated file |
| Manage metadata | YAML frontmatter is Agent domain |
| Execute CLI commands | Automation is Agent domain |
| Create routine issues | Issue templating is Agent domain |
| Format documents | Structural formatting is Agent domain |

---

## 4. Authority Boundaries

### 4.1 Decisions Reserved for Human (MUST NOT delegate)

- Product direction
- Budget allocation
- Hiring/team changes
- Legal/compliance decisions
- Customer commitments
- Scope changes to approved work
- Risk acceptance for security issues
- Exception to governance rules

### 4.2 Decisions Delegated to Agents (MUST delegate)

- Code implementation details
- File structure organization
- Test coverage strategy (within thresholds)
- Documentation formatting
- CI/CD pipeline execution
- Index regeneration
- Status transitions (within workflow)
- Report generation

### 4.3 Shared Decisions (Human decides, Agent executes)

| Decision Type | Human Role | Agent Role |
|---------------|------------|------------|
| Architecture | Approve ADR | Draft ADR, implement |
| Sprint planning | Set priorities | Assign capacity |
| Release | Approve release | Execute deployment |
| Quality | Set thresholds | Enforce checks |

---

## 5. Interaction Model with Obsidian

### 5.1 Obsidian as Source of Truth

Obsidian vault (`cm-workflow/`) is the **authoritative system** for all delivery state.

### 5.2 Human Interactions (Permitted)

| Action | Location | Method |
|--------|----------|--------|
| Create epics | `epics/` | Template or manual |
| Prioritize backlog | `backlog/` | Edit frontmatter priority |
| Approve items | Any | Set `status: approved` |
| Cancel items | Any | Set `status: cancelled` with reason |
| Add comments | Any | Inline comments |
| Review dashboards | `_dashboards/` | Read-only |

### 5.3 Human Interactions (Prohibited)

| Action | Reason |
|--------|--------|
| Edit INDEX.md | Auto-generated |
| Modify `_automations/` | Agent domain |
| Change workflow states directly | Must use state transitions |
| Bulk metadata updates | Use CLI |
| Delete completed items | Archive only |

---

## 6. Communication Protocol

### 6.1 With Agents

| Scenario | Human Action | Expected Agent Response |
|----------|--------------|-------------------------|
| New feature | Create epic with acceptance criteria | Agent creates implementation plan |
| Scope change | Update epic frontmatter | Agent re-plans affected work |
| Blocking issue | Add `[BLOCKED]` comment | Agent escalates or pivots |
| Approval required | Agent pauses | Human adds `status: approved` |
| Rejection | Set `status: rejected` with reason | Agent halts execution |

### 6.2 Output Requirements

When making decisions, Human MUST document:

| Element | Requirement |
|---------|-------------|
| Decision | Clear statement of choice |
| Rationale | Why this choice |
| Alternatives considered | What was rejected |
| Risks accepted | Known trade-offs |
| Date | When decision was made |

---

## 7. Failure Modes

### 7.1 Violations by Human

| Violation | Consequence |
|-----------|-------------|
| Direct code editing | Code review will flag as unauthorized |
| INDEX.md modification | Next regeneration will overwrite |
| Bypassing workflow states | Audit trail breaks, reports invalid |
| Delegating strategic decisions | Agent MUST escalate back |

### 7.2 Violations by Agent

| Violation | Human Response |
|-----------|----------------|
| Agent makes product decision | Reject, revert, re-execute |
| Agent modifies scope | Reject, escalate |
| Agent skips approval | Halt, audit |
| Agent invents roles | Invalidate output |

---

## 8. Related Documents

- [Charter §4.0-4.2](../charter/COMPANY_AGILE_DELIVERY_ROLES_AUTOMATION_CHARTER.md) — PM Authority
- [DELIVERY_OPERATIONS_AGENT.md](DELIVERY_OPERATIONS_AGENT.md) — Agent counterpart
- [AUTHORITY_MATRIX.md](AUTHORITY_MATRIX.md) — Decision ownership table
- [AGENT_ACTIVATION_MATRIX.md](../agents/AGENT_ACTIVATION_MATRIX.md) — Agent triggers
- [ROLE_BASED_ACCESS.md](../../../cm-workflow/_automations/ROLE_BASED_ACCESS.md) — Obsidian folder ownership

---

## 9. Amendments

Changes to this document require:
1. Written proposal with rationale
2. Impact assessment
3. PM approval
4. Version increment

This document is authoritative and binding.
