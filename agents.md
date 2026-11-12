# Shared agent project workspace

Keep each agent's code, tests, fixtures, outputs, and agent-specific documentation
inside its own directory. The existing Alert Triage POC is in `triage_agent/`;
read its README and scoped instructions before changing that agent.

For a future enrichment agent, review `triage_agent/INDICATOR_CONTRACT.md` and
`triage_agent/CODE_REVIEW_2026-11-06.md` (including Appendix C) before designing
the handoff. Enrichment sources, permissions, and schema changes require an
explicit design; do not assume review recommendations are approved work.

Preserve existing agent behavior and published-source snapshots when working on
another agent. Keep credentials out of code, generated reports, and documentation.
