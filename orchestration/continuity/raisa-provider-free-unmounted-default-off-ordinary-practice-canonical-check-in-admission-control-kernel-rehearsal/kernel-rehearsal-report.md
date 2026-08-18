# Provider-free unmounted check-in admission-control kernel rehearsal report

Status: `passed`

Source HEAD: `249609a7f0c7131cff376aef315e1ff7742b44d7`

Source bindings: 7

Named scenarios: 63

Evaluator scenarios: 17

Record transition matrix: 25

Command scenarios: 18

Hostile contract mutations: 341

Hostile escapes: 0

Canonical active ordinary records: 0

Ordinary admission releases: 0

Only the authored-synthetic lane may release admission. The kill switch
dominates both lanes, executable transitions never produce active,
withdrawal is disable-only, unknown commit releases no success, and the
Ariadne/DeepSeek shared clock remains shadow-only.
