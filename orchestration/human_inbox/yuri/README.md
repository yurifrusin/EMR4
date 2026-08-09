# Yuri Tranche Mailbox

This is Yuri's durable, repository-local mailbox for EMR4 tranche closeouts.
It prevents progress summaries from being stranded in transient conversation
history and complements, without replacing, the authoritative acceptance,
evidence and handover documents.

For every completed tranche, the Conductor writes one Markdown message here
before the task-branch closeout commit and publication. Files use the stable
name `YYYY-MM-DD--<tranche-slug>.md`; a corrected message receives an explicit
`--revision-N` suffix and does not overwrite its predecessor.

Every message contains:

1. the tranche identity, outcome, exact task-branch result and evidence links;
2. a plain-language account of what became possible;
3. a technical account of the implemented or proven boundary;
4. issues exposed, resolved or still open;
5. what remains deliberately closed;
6. where the work fits in the overall Raisa architecture and direction; and
7. the planned next tranche, its purpose, boundary and whether Yuri's attention
   is genuinely required.

Mailbox delivery is a reporting obligation, not an authority source or a
permission gate. The live `AGENTS.md`, active accepted plan, protected-evidence
rules and exact Git/evidence state remain authoritative. Messages contain no
patient, clinical, product-derived, credential or protected-evidence content.

Use [`TRANCHE-CLOSEOUT-TEMPLATE.md`](TRANCHE-CLOSEOUT-TEMPLATE.md) for new
messages.
