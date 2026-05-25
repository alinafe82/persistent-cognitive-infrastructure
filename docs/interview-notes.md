# Interview Notes

## 60-Second Explanation

Persistent Cognitive Infrastructure is a scaffold for an internal platform that keeps codebase
and operational facts accurate over time. It treats facts as claims with evidence, confidence,
and source authority, then schedules verification work when those claims decay, conflict, or
need reconciliation.

## Decisions I Can Defend

- Claims need evidence and invalidation rules; summaries alone are not reliable enough for
  engineering workflows.
- LLMs, if used, should be governed executors behind typed contracts rather than owners of
  system state.
- Contracts, schemas, and threat modeling came before feature breadth because the runtime has
  governance and data-boundary risks.

## Tradeoffs

The repo is broad and not a completed runtime. The upside is that it shows system boundaries,
contracts, and operational thinking. The risk is overclaiming, so the README now explicitly
states that this is a scaffold.

## Fixes Made During Portfolio Hardening

- Reduced keyword-heavy README language.
- Added a portfolio-oriented architecture summary.
- Added ADR and interview notes that state the scaffold boundary clearly.
- Verified control-plane runtime tests.

## Likely Questions

**Why not build this as a chatbot?**
A chatbot does not solve stale source authority. The core problem is maintaining verified
claims about systems, not adding a conversational surface.

**Why use an event and claim model?**
Events preserve change history, while claims make the current belief reviewable. Confidence and
evidence provide a path to reconciliation.

**What would you build next?**
Durable repositories, a GitHub connector, scheduler tests, and a small end-to-end workflow that
turns a repo event into a verified graph update.

**What does this show for Engineering Productivity?**
It shows platform-level thinking around internal knowledge systems, reliability of developer
tools, governance, and testable contracts.
