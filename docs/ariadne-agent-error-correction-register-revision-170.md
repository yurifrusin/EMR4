# Ariadne agent error and correction register — revision 170

Date: 2026-08-10

Revision 170 adds corrected incident `AER-0196`. Before dispatching the
generation-lock parse review, Sol inferred a forty-character baseline from the
displayed short commit rather than copying `git rev-parse`. The packet's diff
range therefore named a nonexistent object. The error was caught before any
model or database call; the wrong value is preserved in a fail-closed receipt,
the packet now uses exact Git output, and a fresh distinct orchestrator receipt
is required before dispatch.

This recurrence reinforces the existing rule from `AER-0192`: never expand a
short object ID. Every full Git binding must be copied from `git rev-parse` and
resolved before it enters a packet, contract or receipt.
