# Provider-free durability parse/catalogue input-namespace rebind

Date: 2026-08-10

Status: characterization and distinct exact reproduction passed

Renderer `2.0.18` at accepted source
`f64f3cd7ad8577953c51c66309151cb288440acb` regenerated the inert durability
artifact with SHA-256
`sha256:8756f315a3f1112551550141c1fff83d047ff24103b357e97ddb17b0c805e470`
and 1,448,546 bytes. The 421-statement and six-phase populations are
unchanged. Logical body contract, schema objects, privileges and the frozen
behavior scenarios are unchanged; only body-program input parameter spellings
use the new `cf_arg_` physical namespace.

One fresh networkless, tmpfs-backed, pull-never PostgreSQL 16 characterization
attempt `a8eab7307b3f1913a8d5d992` admitted and rolled back the exact artifact,
installed it atomically, collected all fixed catalogue queries, removed its
owned container and independently verified absence. Against the preceding
binding-RLS exact proof, exactly the `functions` digest changed, as expected
from PostgreSQL's catalogue record of argument names. All other fourteen bound
catalogue digests, including function ACLs, RLS policies, relations and
triggers, remain byte-identical.

The characterization evidence SHA-256 is
`75700e214ac4b155602fe584f1fd0cbbe64c86426c51f449ae31a0e22b867971`.
Its fifteen fixed digests are rebound under exact contract SHA-256
`e783fedb13785672cad84c76984f39ec6ec0b7bb3787ca9b33fb61db1f59fc68`.
A distinct exact-digest attempt `5edadc6475cfe1fc633eb8ff` then reproduced all
fifteen bound digests, the atomic rollback/install lifecycle and verified
cleanup in a different owned container. Its immutable evidence SHA-256 is
`0ec5fb64d9b431e313067e2f550e052d947fecdc8dffa98809df44adb711a528`.
The behavior contract may now be rebound to this accepted parse source; another
behavior attempt remains closed until that six-parent rebind, a complete
deterministic packet and a fresh exact-head independent veto all pass.

No migration, operational database, source/watcher/listener/feed,
patient/product data, provider, application, command, deployment, release,
Pages or protected-ref authority is opened.
