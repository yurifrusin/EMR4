# Ariadne agent-error register revision 2

Date: 2026-08-03

Status: corrected before worker dispatch

The fifth-pair orchestrator initially omitted three configured-but-unselected
adapter entries and the configured DeepSeek worker-slot inventory from its
otherwise complete five-source runtime packet. The deterministic preflight
failed closed with `worker_dispatch_permitted: false`; no worker had been
started and no product candidate changed.

The failure receipt remains preserved. The corrected packet explicitly lists
every configured adapter and required worker-slot inventory, and a distinct
second receipt passed before either fifth-pair worker was dispatched.

This is recorded as `AER-0008`, an observed low-severity orchestrator output
contract error. The prevention control is to derive every pre-dispatch adapter
and worker-slot entry from the configured harness inventory and mark unselected
resources explicitly rather than omitting them. It is not evidence about model
quality or causation.
