# AUTHORITY_MATRIX — Human-Agent Decision Ownership

> **Version:** 1.0  
> **Status:** Active  
> **Authority:** Charter §4.0, Playbook §4  
> **Last Updated:** 2026-01-04

---

## 1. Purpose

This document provides the **definitive reference** for who owns decisions versus who executes them within the Human-Agent collaboration model.

**Obsidian is the authoritative system.** No external system may override decisions recorded in the vault.

---

## 2. Governing Principles

| Principle | Statement |
|-----------|-----------|
| Human Authority | Humans own all strategic, sensitive, and final decisions |
| Agent Execution | Agents own all mechanical, structural, and automation tasks |
| No Overlap | Each decision type has exactly one owner |
| Explicit Delegation | Agent authority is granted, not assumed |
| Escalation Required | Ambiguity escalates to Human |
| Obsidian Authority | Vault state is the source of truth |

---

## 3. Decision Authority Matrix

### 3.1 Strategic Decisions (Human Only)

| Decision Area | Decision Type | Human Authority | Agent Authority |
|---------------|---------------|-----------------|-----------------|
| **Strategy** | Product vision | OWNER | None |
| **Strategy** | Roadmap direction | OWNER | Suggest only |
| **Strategy** | Market positioning | OWNER | None |
| **Strategy** | Business model | OWNER | None |
| **Priority** | Epic priority (P0-P3) | OWNER | None |
| **Priority** | Sprint scope | OWNER | Recommend |
| **Priority** | Release content | OWNER | None |
| **Priority** | Resource allocation | OWNER | None |
| **Scope** | Feature inclusion | OWNER | None |
| **Scope** | Scope changes | OWNER | Flag only |
| **Scope** | MVP definition | OWNER | None |
| **Scope** | Cut decisions | OWNER | None |
| **Budget** | Tool purchases | OWNER | Cost analysis |
| **Budget** | Infrastructure spend | OWNER | Cost analysis |
| **Budget** | Third-party services | OWNER | Cost analysis |
| **Risk** | Risk acceptance | OWNER | Risk identification |
| **Risk** | Security exceptions | OWNER | None |
| **Risk** | Compliance decisions | OWNER | Audit only |

### 3.2 Technical Decisions (Shared — Human Approves, Agent Drafts)

| Decision Area | Decision Type | Human Authority | Agent Authority |
|---------------|---------------|-----------------|-----------------|
| **Architecture** | System design | APPROVE | DRAFT, PROPOSE |
| **Architecture** | Service boundaries | APPROVE | DRAFT, PROPOSE |
| **Architecture** | Data models | APPROVE | DRAFT, PROPOSE |
| **Architecture** | Integration patterns | APPROVE | DRAFT, PROPOSE |
| **Technology** | Language/framework | APPROVE | RECOMMEND |
| **Technology** | Database choice | APPROVE | RECOMMEND |
| **Technology** | Third-party APIs | APPROVE | EVALUATE |
| **Quality** | Coverage thresholds | DEFINE | ENFORCE |
| **Quality** | Complexity limits | DEFINE | ENFORCE |
| **Quality** | Security standards | DEFINE | ENFORCE |
| **Acceptance** | Story acceptance criteria | DEFINE | VERIFY |
| **Acceptance** | Definition of Done | DEFINE | APPLY |
| **Acceptance** | Release criteria | DEFINE | CHECK |

### 3.3 Execution Decisions (Agent Authority)

| Decision Area | Decision Type | Human Authority | Agent Authority |
|---------------|---------------|-----------------|-----------------|
| **Implementation** | Code structure | None | OWNER |
| **Implementation** | Function design | None | OWNER |
| **Implementation** | Variable naming | None | OWNER |
| **Implementation** | Algorithm choice | None | OWNER (within constraints) |
| **Testing** | Test structure | None | OWNER |
| **Testing** | Test data | None | OWNER |
| **Testing** | Mock strategy | None | OWNER |
| **Documentation** | Format/layout | None | OWNER |
| **Documentation** | Technical accuracy | REVIEW | OWNER |
| **Documentation** | API docs generation | None | OWNER |
| **Automation** | CI/CD pipeline steps | None | OWNER |
| **Automation** | Script implementation | None | OWNER |
| **Automation** | Index regeneration | None | OWNER |
| **Metadata** | YAML frontmatter | None | OWNER |
| **Metadata** | Status transitions | None | OWNER (within workflow) |
| **Metadata** | Timestamps/IDs | None | OWNER |
| **Indexing** | INDEX.md content | None | OWNER |
| **Indexing** | Dashboard queries | None | OWNER |
| **Indexing** | Report generation | None | OWNER |

---

## 4. Workflow State Ownership

| State Transition | Who Initiates | Who Executes |
|------------------|---------------|--------------|
| New → Backlog | Human | Agent |
| Backlog → Ready | Human (approves) | Agent |
| Ready → In Progress | Agent | Agent |
| In Progress → Review | Agent | Agent |
| Review → Done | Human (accepts) | Agent |
| Any → Blocked | Either | Agent (records) |
| Any → Cancelled | Human | Agent (executes) |

---

## 5. Artifact Ownership

### 5.1 Human-Owned Artifacts

| Artifact | Location | Human Action | Agent Action |
|----------|----------|--------------|--------------|
| Epics | `epics/` | Create, prioritize | Format, index |
| Stories | `backlog/stories/` | Create, approve | Template, track |
| Acceptance Criteria | Frontmatter | Define | Verify |
| ADRs | `adr/` | Approve | Draft, format |
| Risk Registers | `docs/` | Accept risks | Identify, document |
| Budget Documents | N/A | Maintain | Analyze |

### 5.2 Agent-Owned Artifacts

| Artifact | Location | Human Action | Agent Action |
|----------|----------|--------------|--------------|
| Tasks | `backlog/tasks/` | None | Create, manage |
| Bugs | `backlog/bugs/` | None | Create, triage |
| INDEX.md | Root | None | Generate |
| Dashboards | `_dashboards/` | View | Generate |
| Reports | `reports/` | Review | Generate |
| Test files | Various | Review | Create, maintain |
| CI configs | `.github/workflows/` | Approve changes | Implement |

### 5.3 Shared Artifacts

| Artifact | Location | Human Action | Agent Action |
|----------|----------|--------------|--------------|
| Sprint Plans | `sprints/` | Approve scope | Create, track |
| Release Notes | `releases/` | Approve | Draft |
| CHANGELOG | Root | Review | Update |
| Documentation | `docs/` | Review | Write |

---

## 6. Obsidian Authority Declaration

### 6.1 Source of Truth

The Obsidian vault at `cm-workflow/` is the **authoritative system** for:

- All work items (epics, stories, tasks, bugs)
- All status and priority assignments
- All sprint and release planning
- All team assignments
- All decision records

### 6.2 External System Rules

| External System | Relationship | Conflict Resolution |
|-----------------|--------------|---------------------|
| GitHub Issues | Sync target | Obsidian wins |
| GitHub PRs | Reference | Linked, not duplicated |
| Notion | Optional mirror | Obsidian wins |
| CI/CD | Execution | Obsidian defines state |
| Jira | Not used | N/A |

### 6.3 Conflict Resolution

If conflict between systems:
1. Obsidian state is authoritative
2. External system state is overwritten
3. Conflict logged for audit
4. Human notified if strategic decision affected

---

## 7. Escalation Protocol

### 7.1 Agent-to-Human Escalation

| Trigger | Agent Action | Human Response |
|---------|--------------|----------------|
| Scope ambiguity | Flag, propose options | Choose option |
| Priority conflict | Report conflict | Resolve priority |
| Blocked dependency | Mark blocked, pivot | Unblock or re-scope |
| Security concern | Halt, report | Accept risk or reject |
| Budget implication | Report cost | Approve or deny |
| Governance violation | Halt, report | Investigate, decide |

### 7.2 Escalation Format

```markdown
**ESCALATION**
- **Issue:** [Description]
- **Options:**
  1. [Option A] — [Impact]
  2. [Option B] — [Impact]
- **Recommendation:** [Agent's suggestion]
- **Awaiting:** Human decision
```

---

## 8. Validation Rules

### 8.1 Human Decision Validation

| Decision | Validation | Enforced By |
|----------|------------|-------------|
| Priority set | P0-P3 only | Schema |
| Status transition | Workflow states only | Automation |
| Approval | `status: approved` exists | Agent check |
| Cancellation | Reason provided | Schema |

### 8.2 Agent Execution Validation

| Execution | Validation | Enforced By |
|-----------|------------|-------------|
| Code change | Plan exists | Playbook §4 |
| Status change | Within workflow | Automation |
| Role switch | Declared | Matrix §5 |
| Output format | Schema compliant | Agent self-check |

---

## 9. Audit Trail Requirements

| Event Type | Recorded By | Location |
|------------|-------------|----------|
| Human decision | Human | Frontmatter, comments |
| Agent execution | Agent | Git commit, report |
| Status transition | Agent | Frontmatter history |
| Role switch | Agent | Execution output |
| Escalation | Agent | Plan/review document |
| Approval | Human | Frontmatter |

---

## 10. Approval Boundaries (ADR-007)

### 10.1 Artifacts Requiring Human Approval

All generated artifacts that impact project direction, security, or architecture MUST include explicit approval checkboxes.

| Artifact Type | Approval Authority | Checkbox Required |
|---------------|-------------------|-------------------|
| ADR (Architecture Decision Record) | Technical Lead | ✅ Yes |
| Sprint Plan | PM | ✅ Yes |
| Task Definition | PM | ✅ Yes |
| Execution Plan | PM | ✅ Yes |
| Review Document | Stakeholder | ✅ Yes |
| Security Change | Security Lead | ✅ Yes |
| Infrastructure Change | DevOps Lead | ✅ Yes |
| Code Implementation | PR Reviewer | ❌ No (PR process) |

### 10.2 Approval Checkbox Format

```markdown
## Approval

| Role | Status | Date | Approver |
|------|--------|------|----------|
| {Required Role} | [ ] Pending / [x] Approved | YYYY-MM-DD | @{username} |
```

### 10.3 Agent Execution Rules

1. **NEVER execute** tasks without `[x] Approved` checkbox
2. **MUST verify** approval exists before starting work
3. **MUST include** approval section in all generated artifacts
4. **MUST block** on missing approvals and notify user

### 10.4 Approval Bypass Conditions

Approval MAY be bypassed ONLY for:
- Emergency security fixes (with mandatory post-hoc approval)
- CI/CD pipeline failures (automated recovery)
- Documentation-only changes

All bypasses MUST be documented with `BYPASS: {reason}` in commit message.

---

## 11. Related Documents

- [HUMAN_PRODUCT_OWNER.md](HUMAN_PRODUCT_OWNER.md) — Human role definition
- [DELIVERY_OPERATIONS_AGENT.md](DELIVERY_OPERATIONS_AGENT.md) — Agent role definition
- [Charter §4.0](../charter/COMPANY_AGILE_DELIVERY_ROLES_AUTOMATION_CHARTER.md) — Dual-PM Model
- [AGENT_ACTIVATION_MATRIX.md](../agents/AGENT_ACTIVATION_MATRIX.md) — Trigger conditions
- [WORKFLOW_STATES.md](../../../cm-workflow/_automations/WORKFLOW_STATES.md) — State definitions

---

## 12. Agile Consultant Advisory Authority

The Agile Software Development Consultant Agent (§13) has **advisory authority** across all domains:

| Domain | Advisory Scope | Authority Level |
|--------|----------------|-----------------|
| Sprint Quality | Artifact completeness verification | ADVISE |
| Agile Practices | Best practice recommendations | ADVISE |
| Multi-Role Coordination | Executor-Reviewer pairing validation | VALIDATE |
| Meeting Quality | Output packaging standards | ADVISE + TEMPLATE |
| Arabic Translations | Dual-output completeness | VALIDATE |
| Definition of Done | DoD compliance checking | VERIFY |

**Key Constraint:** Advisory authority only — no execution or approval rights.

---

## 13. Summary Table

| Domain | Human Owns | Agent Owns | Consultant Advises |
|--------|------------|------------|-------------------|
| Strategy | Vision, roadmap, scope | None | None |
| Priority | Epic/story priority | Task ordering | None |
| Status | Approval, rejection | Transitions | Compliance |
| Metadata | Acceptance criteria | YAML, timestamps | Quality |
| Automation | Policy definition | Execution | Best practices |
| Indexing | None | Full ownership | None |
| Acceptance | Final sign-off | Verification | DoD compliance |
| Agile Process | None | Execution | Quality advisory |
| Multi-Role | None | Role switching | Pairing validation |
| Translations | Approval | Generation | Completeness |

---

## 13. Amendments

Changes to this document require:
1. Written proposal with rationale
2. Impact assessment
3. Human PM approval
4. Version increment

This document is authoritative and binding.
