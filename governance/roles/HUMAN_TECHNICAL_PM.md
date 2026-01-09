# HUMAN_TECHNICAL_PM — Role Definition

> **Version:** 1.0  
> **Status:** Active  
> **Authority:** Charter §4.2  
> **Role Type:** Human — Technical Decision Authority  
> **Last Updated:** 2026-01-04

---

## 1. Purpose

The Technical Product Manager is the **technical decision authority** within the Product Management Department. This role bridges engineering reality with product intent, ensuring technical decisions support business goals while maintaining system integrity, security, and scalability.

Per Charter §4.0 (Dual-PM Model), this role operates alongside the Non-Technical PM with equal authority in their respective domains.

---

## 2. Responsibilities

### 2.1 Technical Authority (MUST)

| Responsibility | Scope |
|----------------|-------|
| Architecture decisions | Approve ADRs, system design |
| Technology stack | Select languages, frameworks, tools |
| API design | Approve interface contracts |
| Data models | Approve database schemas |
| Scalability planning | Set performance/capacity targets |
| Security posture | Accept security recommendations |
| Technical debt | Prioritize tech debt remediation |

### 2.2 Governance Authority (MUST)

| Responsibility | Scope |
|----------------|-------|
| Quality gates | Define code quality thresholds |
| CI/CD pipeline | Approve pipeline configuration |
| Release criteria | Define technical release requirements |
| Agent orchestration | Direct Agent execution order |
| Review standards | Set code review requirements |

### 2.3 Validation Authority (MUST)

| Responsibility | Scope |
|----------------|-------|
| Technical acceptance | Approve technical story completion |
| Architecture review | Validate architectural compliance |
| Code review escalation | Final authority on code disputes |
| Security review | Accept security agent findings |
| Performance review | Accept performance benchmarks |

---

## 3. Explicit Non-Responsibilities (MUST NOT)

| Non-Responsibility | Reason |
|--------------------|--------|
| Business scope decisions | Non-Technical PM domain |
| Budget final approval | Non-Technical PM domain |
| Customer commitments | Non-Technical PM domain |
| Market/positioning | Non-Technical PM domain |
| Write production code | Agent domain (delegated) |
| Execute CI/CD | DevOps Agent domain (delegated) |
| Generate reports | Agent domain (delegated) |
| Create Obsidian tasks | Agent domain (delegated) |
| Update task status | Agent domain (delegated) |
| Write test cases | QA Agent domain (delegated) |
| Create documentation | Technical Writer Agent domain (delegated) |

> **CRITICAL:** Human roles are STRATEGIC, not MECHANICAL. All execution tasks are delegated to appropriate Agents.

---

## 4. Obsidian Workflow Interactions

### 4.1 Read Permissions

| Folder | Permitted | Purpose |
|--------|-----------|---------|
| `backlog/` | ✅ YES | Technical planning |
| `sprints/` | ✅ YES | Sprint oversight |
| `epics/` | ✅ YES | Product understanding |
| `plans/` | ✅ YES | Planning |
| `reviews/` | ✅ YES | Quality oversight |
| `meetings/` | ✅ YES | Technical discussions |
| `_dashboards/` | ✅ YES | Health metrics |
| `_diagrams/` | ✅ YES | Architecture understanding |
| `_governance/` | ✅ YES | Governance oversight |

### 4.2 Write Permissions

| Folder | Permitted | Conditions |
|--------|-----------|------------|
| `backlog/` | ✅ WRITE | Technical tasks, bugs |
| `sprints/` | ✅ APPROVE | Sprint scope/capacity |
| `epics/` | ✅ WRITE | Technical epics |
| `plans/` | ✅ WRITE | Technical plans |
| `reviews/` | ✅ WRITE | Technical reviews |
| `meetings/` | ✅ WRITE | Technical meetings |
| `_dashboards/` | ❌ NO | DevOps Agent domain |
| `_diagrams/` | ❌ NO | Architect Agent domain |
| `_governance/` | ✅ APPROVE | Technical policies |

### 4.3 Decision Authority

| Decision Type | Authority Level | Notes |
|---------------|-----------------|-------|
| Architecture | ✅ OWNER | Final technical authority |
| Technology choice | ✅ OWNER | Within budget constraints |
| Quality standards | ✅ OWNER | Define thresholds |
| Security acceptance | ✅ OWNER | Accept risk or remediate |
| Release criteria | ✅ OWNER | Technical readiness |
| Product scope | 🔍 REVIEW | Non-Tech PM decides |
| Budget allocation | 🔍 REVIEW | Non-Tech PM decides |

---

## 5. Agent Delegation Model

| Task Type | Delegate To | Human Retains |
|-----------|-------------|---------------|
| Architecture drafts | Architect Agent | Approval |
| Implementation | Engineer Agents | Code review oversight |
| Testing | QA Agent | Quality gate approval |
| Security audit | Security Agent | Risk acceptance |
| Deployment | DevOps Agent | Release approval |
| Documentation | Technical Writer Agent | Accuracy review |

---

## 6. Coordination with Other Roles

| Role | Relationship | Interaction |
|------|--------------|-------------|
| Board/Founder | Reports to | Strategic alignment |
| Non-Technical PM | Peer (Dual-PM) | Business/technical translation |
| Architect Agent | Delegates to | Architecture execution |
| All Executor Agents | Directs | Technical orchestration |
| All Reviewer Agents | Receives from | Quality validation |

---

## 7. Escalation Triggers

| Condition | Action |
|-----------|--------|
| Architecture dispute | Technical PM decision required |
| Quality gate failure | Technical PM decision on release |
| Security vulnerability | Technical PM risk acceptance |
| Performance regression | Technical PM remediation decision |
| Cross-Agent conflict | Technical PM arbitration |
| Technical debt critical | Technical PM prioritization |

---

## 8. Communication Protocol

### 8.1 With Non-Technical PM

| Scenario | Technical PM Action | Expected Response |
|----------|-------------------|-------------------|
| Business request | Provide technical feasibility | Business priority decision |
| Technical risk | Translate to business impact | Risk acceptance decision |
| Timeline estimate | Provide detailed breakdown | Scope negotiation |
| Architecture decision | Present options with trade-offs | Budget/scope approval |

### 8.2 With Agents

| Scenario | Technical PM Action | Expected Response |
|----------|-------------------|-------------------|
| Implementation start | Provide requirements, constraints | Agent execution plan |
| Review escalation | Make final decision | Agent implements decision |
| Blocked work | Remove blocker or re-prioritize | Agent continues |
| Quality concern | Set remediation priority | Agent executes fix |

### 8.3 Output Requirements

When making decisions, this role MUST document:

| Element | Requirement |
|---------|-------------|
| Decision | Clear technical statement |
| Rationale | Technical reasoning |
| Alternatives | What was considered/rejected |
| Trade-offs | Performance, security, maintainability |
| Impact | Systems affected |
| Date | When decision was made |

---

## 9. Technical Domains

### 9.1 Domains Requiring Technical PM Approval

- System architecture changes
- Database schema changes
- API contract changes
- Third-party service integration
- Security configuration changes
- Performance optimization strategy
- Deployment strategy changes
- Technology stack changes

### 9.2 Domains Delegated to Agents

- Implementation details within approved architecture
- Test case design
- Documentation format
- Code style (within defined standards)
- CI pipeline execution
- Routine deployments (within release criteria)

---

## 10. Related Documents

- [Charter §4.2](../charter/COMPANY_AGILE_DELIVERY_ROLES_AUTOMATION_CHARTER.md)
- [AUTHORITY_MATRIX.md](AUTHORITY_MATRIX.md)
- [HUMAN_PRODUCT_OWNER.md](HUMAN_PRODUCT_OWNER.md)
- [HUMAN_NON_TECHNICAL_PM.md](HUMAN_NON_TECHNICAL_PM.md)
- [ARCHITECT_AGENT.md](ARCHITECT_AGENT.md)
- [DELIVERY_OPERATIONS_AGENT.md](DELIVERY_OPERATIONS_AGENT.md)

---

## 11. Amendments

Changes to this document require:
1. Written proposal with rationale
2. Impact assessment
3. Both PM approval (per Dual-PM Model)
4. Version increment

This document is authoritative and binding.
