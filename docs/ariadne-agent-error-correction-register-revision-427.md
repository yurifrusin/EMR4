# Ariadne agent error and correction register — revision 427

Date: 2026-08-18

Status: accepted correction update

Reasoning level: high

Revision 427 preserves accepted revision 426 and adds AER-0497. The one
admitted occupied rc.7 worker terminaled with exit 1 in under one second while
the stock headless profile applied its HMR service. That service requires Node
`--expose-internals`; the package-declared CLI launcher did not supply it.

The custom runner, Harness session and provider boundary were never reached.
The isolated broker recorded only its ready event, the worker worktree remained
clean and the disposable home root contained only preset/profile material with
no session root. The attempt is consumed without retry or resume.

The canonical register contains 497 bounded incidents, all corrected or
explicitly contained and none open.
