"""STOPPED source candidate: owner-confirmed selected-practice location CREATE.

This inert F2 descendant creates no role, Engine, deployment or runtime authority.
The protected tenant Engine/service factory and verified HTTP principal are trusted;
SQL parameters, GUCs, signatures and row locks do not authenticate hostile SQL.
Existing location SELECT is not tenant row isolation. Existing location RLS bits
remain unchanged; only the new command/audit/outbox tables are made FORCE RLS.
A location/site is not a validated room, calendar or proof of bookable capacity.
"""
from alembic import context, op
import sqlalchemy as sa

revision = "f3a4b5c6d7e8"
down_revision = "f2a3b4c5d6e7"
branch_labels = None
depends_on = None
OWNER = "raisa_local_location_functions"
TENANT = "raisa_local_tenant"
AUTH_ARGS = "p_account uuid,p_membership uuid,p_user uuid,p_practice uuid,p_role text,p_generation bigint,p_expiry timestamptz"
AUTH_TYPES = "uuid,uuid,uuid,uuid,text,bigint,timestamptz"
AUTH_CALL = "p_account,p_membership,p_user,p_practice,p_role,p_generation,p_expiry"
COMMAND_COLUMNS = (
    "id,practice_id,actor_account_id,actor_membership_id,actor_user_id,role,authority_generation,"
    "command_key,create_intent_id,draft_revision,request_intent_id,supersedes_command_id,"
    "predecessor_revision,started_new_intent,canonicalization_version,canonical_text,canonical_body,"
    "body_digest,prepared_at,expires_at,state,location_id,audit_event_id,outbox_event_id,committed_at"
)
AUDIT_COLUMNS = (
    "id,practice_id,command_id,location_id,actor_account_id,actor_membership_id,actor_user_id,"
    "event_code,body_digest,created_at"
)
OUTBOX_COLUMNS = (
    "id,practice_id,command_id,audit_event_id,location_id,actor_account_id,actor_membership_id,"
    "actor_user_id,correlation_id,event_type,schema_version,source_system,payload,published,created_at"
)
# Exact column ACLs; UPDATE(key) on authority relations exists only for row locks.
COLUMNS = {
    "accounts": ("id,is_active", "", "id"),
    "practice_memberships": ("id,account_id,practice_id,legacy_user_id,is_active,authority_generation", "", "id"),
    "users": ("id,practice_id,role,is_active,authority_generation", "", "id"),
    "practice_membership_roles": ("membership_id,role", "", "membership_id"),
    "practices": ("id", "", "id"),
    "practice_locations": ("id,practice_id,name,is_active", "id,practice_id,name,is_active", ""),
    "practice_location_create_commands": (COMMAND_COLUMNS, COMMAND_COLUMNS,
        "state,location_id,audit_event_id,outbox_event_id,committed_at"),
    "practice_location_create_audit": ("", AUDIT_COLUMNS, ""),
    "practice_location_create_outbox": ("", OUTBOX_COLUMNS, ""),
}
NEW_TABLES = ("practice_location_create_commands", "practice_location_create_audit", "practice_location_create_outbox")

SCHEMA_SQL = """
CREATE TABLE public.practice_location_create_commands (
 id uuid PRIMARY KEY,
 practice_id uuid NOT NULL REFERENCES public.practices(id),
 actor_account_id uuid NOT NULL REFERENCES public.accounts(id),
 actor_membership_id uuid NOT NULL REFERENCES public.practice_memberships(id),
 actor_user_id uuid NOT NULL,
 role text NOT NULL CHECK (role='PracticeOwner'),
 authority_generation bigint NOT NULL CHECK (authority_generation>=1),
 command_key uuid NOT NULL,
 create_intent_id uuid NOT NULL,
 draft_revision bigint NOT NULL CHECK (draft_revision>=1),
 request_intent_id uuid,
 supersedes_command_id uuid,
 predecessor_revision bigint,
 started_new_intent boolean NOT NULL,
 canonicalization_version text NOT NULL CHECK (canonicalization_version='practice_location.create.body.v1'),
 canonical_text text NOT NULL,
 canonical_body jsonb NOT NULL,
 body_digest text NOT NULL CHECK (body_digest ~ '^[0-9a-f]{64}$'),
 prepared_at timestamptz NOT NULL,
 expires_at timestamptz NOT NULL CHECK (expires_at>prepared_at),
 state text NOT NULL CHECK (state IN ('prepared','superseded','committed')),
 location_id uuid,
 audit_event_id uuid,
 outbox_event_id uuid,
 committed_at timestamptz,
 CONSTRAINT uq_practice_location_create_key UNIQUE(practice_id,actor_membership_id,command_key),
 CONSTRAINT uq_practice_location_create_revision UNIQUE(practice_id,actor_membership_id,create_intent_id,draft_revision),
 CONSTRAINT uq_practice_location_create_practice UNIQUE(practice_id,id),
 CONSTRAINT fk_practice_location_create_user FOREIGN KEY(practice_id,actor_user_id) REFERENCES public.users(practice_id,id),
 CONSTRAINT fk_practice_location_create_resource FOREIGN KEY(practice_id,location_id)
   REFERENCES public.practice_locations(practice_id,id),
 CONSTRAINT fk_practice_location_create_predecessor FOREIGN KEY(practice_id,supersedes_command_id)
   REFERENCES public.practice_location_create_commands(practice_id,id),
 CONSTRAINT ck_practice_location_create_context CHECK (
   (started_new_intent AND draft_revision=1 AND request_intent_id IS NULL
     AND supersedes_command_id IS NULL AND predecessor_revision IS NULL)
   OR (NOT started_new_intent AND request_intent_id IS NOT NULL AND request_intent_id=create_intent_id
     AND supersedes_command_id IS NOT NULL AND predecessor_revision IS NOT NULL AND predecessor_revision>=1
     AND draft_revision=predecessor_revision+1)),
 CONSTRAINT ck_practice_location_create_terminal CHECK (
   (state='committed' AND location_id IS NOT NULL AND audit_event_id IS NOT NULL
     AND outbox_event_id IS NOT NULL AND committed_at IS NOT NULL)
   OR (state IN ('prepared','superseded') AND location_id IS NULL AND audit_event_id IS NULL
     AND outbox_event_id IS NULL AND committed_at IS NULL)),
 CONSTRAINT ck_practice_location_create_body CHECK (canonical_body=canonical_text::jsonb
   AND body_digest=pg_catalog.encode(pg_catalog.sha256(pg_catalog.convert_to(canonical_text,'UTF8')),'hex'))
);
CREATE UNIQUE INDEX uq_practice_location_create_prepared ON public.practice_location_create_commands
 (practice_id,actor_membership_id,create_intent_id) WHERE state='prepared';
CREATE UNIQUE INDEX uq_practice_location_create_committed ON public.practice_location_create_commands
 (practice_id,actor_membership_id,create_intent_id) WHERE state='committed';
CREATE UNIQUE INDEX uq_practice_location_create_successor ON public.practice_location_create_commands(supersedes_command_id)
 WHERE supersedes_command_id IS NOT NULL;
CREATE INDEX ix_practice_location_create_resource ON public.practice_location_create_commands(practice_id,location_id);
CREATE INDEX ix_practice_location_create_account ON public.practice_location_create_commands(actor_account_id);
CREATE INDEX ix_practice_location_create_user ON public.practice_location_create_commands(practice_id,actor_user_id);
CREATE TABLE public.practice_location_create_audit (
 id uuid PRIMARY KEY,
 practice_id uuid NOT NULL REFERENCES public.practices(id),
 command_id uuid NOT NULL,
 location_id uuid NOT NULL,
 actor_account_id uuid NOT NULL REFERENCES public.accounts(id),
 actor_membership_id uuid NOT NULL REFERENCES public.practice_memberships(id),
 actor_user_id uuid NOT NULL,
 event_code text NOT NULL CHECK (event_code='location_created'),
 body_digest text NOT NULL CHECK (body_digest ~ '^[0-9a-f]{64}$'),
 created_at timestamptz NOT NULL,
 CONSTRAINT uq_practice_location_create_audit_command UNIQUE(practice_id,command_id),
 CONSTRAINT uq_practice_location_create_audit_practice UNIQUE(practice_id,id),
 CONSTRAINT fk_practice_location_create_audit_command FOREIGN KEY(practice_id,command_id)
   REFERENCES public.practice_location_create_commands(practice_id,id),
 CONSTRAINT fk_practice_location_create_audit_resource FOREIGN KEY(practice_id,location_id)
   REFERENCES public.practice_locations(practice_id,id),
 CONSTRAINT fk_practice_location_create_audit_user FOREIGN KEY(practice_id,actor_user_id)
   REFERENCES public.users(practice_id,id)
);
CREATE TABLE public.practice_location_create_outbox (
 id uuid PRIMARY KEY,
 practice_id uuid NOT NULL REFERENCES public.practices(id),
 command_id uuid NOT NULL,
 audit_event_id uuid NOT NULL,
 location_id uuid NOT NULL,
 actor_account_id uuid NOT NULL REFERENCES public.accounts(id),
 actor_membership_id uuid NOT NULL REFERENCES public.practice_memberships(id),
 actor_user_id uuid NOT NULL,
 correlation_id uuid NOT NULL,
 event_type text NOT NULL CHECK (event_type='practice.location_created'),
 schema_version text NOT NULL CHECK (schema_version='practice.location_created.v1'),
 source_system text NOT NULL CHECK (source_system='emr4-practice-administration'),
 payload jsonb NOT NULL,
 published boolean NOT NULL CHECK (published=false),
 created_at timestamptz NOT NULL,
 CONSTRAINT uq_practice_location_create_outbox_command UNIQUE(practice_id,command_id),
 CONSTRAINT uq_practice_location_create_outbox_audit UNIQUE(practice_id,audit_event_id),
 CONSTRAINT uq_practice_location_create_outbox_practice UNIQUE(practice_id,id),
 CONSTRAINT fk_practice_location_create_outbox_command FOREIGN KEY(practice_id,command_id)
   REFERENCES public.practice_location_create_commands(practice_id,id),
 CONSTRAINT fk_practice_location_create_outbox_audit FOREIGN KEY(practice_id,audit_event_id)
   REFERENCES public.practice_location_create_audit(practice_id,id),
 CONSTRAINT fk_practice_location_create_outbox_resource FOREIGN KEY(practice_id,location_id)
   REFERENCES public.practice_locations(practice_id,id),
 CONSTRAINT fk_practice_location_create_outbox_user FOREIGN KEY(practice_id,actor_user_id)
   REFERENCES public.users(practice_id,id)
);
ALTER TABLE public.practice_location_create_commands ADD CONSTRAINT fk_practice_location_create_audit
 FOREIGN KEY(practice_id,audit_event_id) REFERENCES public.practice_location_create_audit(practice_id,id);
ALTER TABLE public.practice_location_create_commands ADD CONSTRAINT fk_practice_location_create_outbox
 FOREIGN KEY(practice_id,outbox_event_id) REFERENCES public.practice_location_create_outbox(practice_id,id);
CREATE INDEX ix_practice_location_create_audit_resource ON public.practice_location_create_audit(practice_id,location_id);
CREATE INDEX ix_practice_location_create_audit_member ON public.practice_location_create_audit(actor_membership_id);
CREATE INDEX ix_practice_location_create_audit_user ON public.practice_location_create_audit(practice_id,actor_user_id);
CREATE INDEX ix_practice_location_create_outbox_resource ON public.practice_location_create_outbox(practice_id,location_id);
CREATE INDEX ix_practice_location_create_outbox_member ON public.practice_location_create_outbox(actor_membership_id);
CREATE INDEX ix_practice_location_create_outbox_user ON public.practice_location_create_outbox(practice_id,actor_user_id);
"""

GUARD = """
  IF session_user<>'raisa_local_tenant' OR current_user<>'raisa_local_location_functions'
     OR (SELECT count(*) FROM pg_catalog.pg_roles r WHERE r.rolname IN
       ('raisa_local_tenant','raisa_local_location_functions'))<>2
     OR EXISTS (SELECT 1 FROM pg_catalog.pg_roles r WHERE r.rolname IN
       ('raisa_local_tenant','raisa_local_location_functions') AND
       (r.rolsuper OR r.rolbypassrls OR r.rolinherit OR r.rolcreaterole OR r.rolcreatedb
        OR r.rolreplication OR r.rolcanlogin<>(r.rolname='raisa_local_tenant')))
     OR EXISTS (SELECT 1 FROM pg_catalog.pg_auth_members e JOIN pg_catalog.pg_roles r
       ON r.oid=e.member OR r.oid=e.roleid WHERE r.rolname IN
       ('raisa_local_tenant','raisa_local_location_functions'))
     OR pg_catalog.has_schema_privilege('raisa_local_location_functions','public','CREATE')
     OR pg_catalog.has_schema_privilege('raisa_local_tenant','public','CREATE')
     OR pg_catalog.has_column_privilege('raisa_local_location_functions','public.accounts','password_hash','SELECT')
     OR pg_catalog.has_column_privilege('raisa_local_location_functions','public.users','password_hash','SELECT')
  THEN RAISE EXCEPTION 'location authority denied' USING ERRCODE='42501'; END IF;
"""

AUTHORITY_BODY = """
DECLARE account_row record; member_row record; user_row record; actual_role text;
BEGIN
""" + GUARD + """
  IF p_account IS NULL OR p_membership IS NULL OR p_user IS NULL OR p_practice IS NULL
     OR p_role IS DISTINCT FROM 'PracticeOwner' OR p_generation IS NULL OR p_generation<1
     OR p_expiry IS NULL OR pg_catalog.clock_timestamp()>=p_expiry
  THEN RAISE EXCEPTION 'location authority denied' USING ERRCODE='42501'; END IF;
  PERFORM pg_catalog.set_config('app.current_practice_id',p_practice::text,true);
  PERFORM pg_catalog.set_config('practice_location.account_id',p_account::text,true);
  PERFORM pg_catalog.set_config('practice_location.membership_id',p_membership::text,true);
  PERFORM pg_catalog.set_config('practice_location.user_id',p_user::text,true);
  SELECT a.id,a.is_active INTO account_row FROM public.accounts a
    WHERE a.id=p_account FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'location authority denied' USING ERRCODE='42501'; END IF;
  SELECT m.id,m.account_id,m.practice_id,m.legacy_user_id,m.is_active,m.authority_generation
    INTO member_row FROM public.practice_memberships m
    WHERE m.id=p_membership AND m.account_id=p_account AND m.practice_id=p_practice
      AND m.legacy_user_id=p_user FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'location authority denied' USING ERRCODE='42501'; END IF;
  SELECT u.id,u.practice_id,u.role,u.is_active,u.authority_generation INTO user_row
    FROM public.users u WHERE u.id=p_user AND u.practice_id=p_practice FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'location authority denied' USING ERRCODE='42501'; END IF;
  SELECT r.role INTO actual_role FROM public.practice_membership_roles r
    WHERE r.membership_id=p_membership FOR UPDATE;
  IF NOT FOUND OR account_row.is_active IS DISTINCT FROM true
     OR member_row.account_id IS DISTINCT FROM p_account OR member_row.legacy_user_id IS DISTINCT FROM p_user
     OR member_row.practice_id IS DISTINCT FROM p_practice OR member_row.is_active IS DISTINCT FROM true
     OR user_row.practice_id IS DISTINCT FROM p_practice OR user_row.is_active IS DISTINCT FROM true
     OR user_row.role::text IS DISTINCT FROM p_role OR actual_role IS DISTINCT FROM p_role
     OR user_row.authority_generation IS DISTINCT FROM p_generation
     OR member_row.authority_generation IS DISTINCT FROM p_generation
     OR pg_catalog.clock_timestamp()>=p_expiry
  THEN RAISE EXCEPTION 'location authority denied' USING ERRCODE='42501'; END IF;
  -- One selected-Practice lock, in UPDATE mode from the outset. No SHARE upgrade.
  PERFORM p.id FROM public.practices p WHERE p.id=p_practice FOR UPDATE;
  IF NOT FOUND OR pg_catalog.clock_timestamp()>=p_expiry
  THEN RAISE EXCEPTION 'location authority denied' USING ERRCODE='42501'; END IF;
END;
"""

LOCK_COMMANDS_BODY = """
BEGIN
  PERFORM c.id FROM public.practice_location_create_commands c
    WHERE c.practice_id=p_practice AND c.actor_membership_id=p_membership
      AND (c.command_key=p_key OR c.create_intent_id=p_intent)
    ORDER BY c.create_intent_id,c.draft_revision,c.id FOR UPDATE;
END;
"""

W1_BODY = """
DECLARE answer text;
BEGIN
  SELECT pg_catalog.string_agg(pg_catalog.chr(n),'' ORDER BY n) INTO answer FROM
    (VALUES (9),(10),(11),(12),(13),(28),(29),(30),(31),(32),(133),(160),(5760),
      (8192),(8193),(8194),(8195),(8196),(8197),(8198),(8199),(8200),(8201),(8202),
      (8232),(8233),(8239),(8287),(12288)) AS w(n);
  RETURN answer;
END;
"""

CANONICAL_BODY = """
DECLARE name_value text;
BEGIN
  name_value:=pg_catalog.btrim(p_name,location_api._w1());
  IF p_name IS NULL OR pg_catalog.char_length(name_value) NOT BETWEEN 1 AND 255
     OR EXISTS (SELECT 1 FROM pg_catalog.generate_series(1,pg_catalog.char_length(name_value)) AS c(n)
       WHERE pg_catalog.ascii(pg_catalog.substr(name_value,n,1))<32
         OR pg_catalog.ascii(pg_catalog.substr(name_value,n,1))=127)
  THEN RAISE EXCEPTION 'location body invalid' USING ERRCODE='22023'; END IF;
  -- UTF8 text rejects invalid encodings and NUL. No Unicode/name matching or
  -- normalization beyond the shared fixed W1 trim set is performed.
  RETURN '{"name":'||pg_catalog.to_json(name_value)::text||'}';
END;
"""

RECEIPT_BODY = """
BEGIN
  IF c.state<>'committed' THEN RAISE EXCEPTION 'location command conflict' USING ERRCODE='P0001'; END IF;
  RETURN pg_catalog.jsonb_build_object('schema_version','practice_location.create.receipt.v1',
    'command_id',c.id,'command_key',c.command_key,'create_intent_id',c.create_intent_id,
    'draft_revision',c.draft_revision,'practice_id',c.practice_id,'location_id',c.location_id,
    'actor_account_id',c.actor_account_id,'actor_membership_id',c.actor_membership_id,
    'actor_user_id',c.actor_user_id,'role',c.role,'authority_generation',c.authority_generation,
    'body_digest',c.body_digest,'audit_event_id',c.audit_event_id,'outbox_event_id',c.outbox_event_id,
    'committed_at',pg_catalog.to_char(c.committed_at AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"'));
END;
"""

DRAFT_BODY = """
BEGIN
  RETURN pg_catalog.jsonb_build_object('state','prepared','draft',pg_catalog.jsonb_build_object(
    'command_id',c.id,'command_key',c.command_key,'create_intent_id',c.create_intent_id,
    'draft_revision',c.draft_revision,'canonicalization_version',c.canonicalization_version,
    'body',c.canonical_body,'body_digest',c.body_digest,
    'role',c.role,'authority_generation',c.authority_generation,
    'expires_at',pg_catalog.to_char(c.expires_at AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"')));
END;
"""

PREPARE_BODY = """
DECLARE prior public.practice_location_create_commands%ROWTYPE; head public.practice_location_create_commands%ROWTYPE;
        fresh public.practice_location_create_commands%ROWTYPE; instant timestamptz; canonical text;
        fresh_intent uuid; next_revision bigint; answer jsonb; prior_found boolean;
BEGIN
  PERFORM location_api._authority(""" + AUTH_CALL + """);
  IF p_key IS NULL OR p_new IS NULL OR p_canonical IS NULL OR p_digest IS NULL
     OR (p_new AND (p_intent IS NOT NULL OR p_predecessor IS NOT NULL OR p_revision IS NOT NULL))
     OR (NOT p_new AND (p_intent IS NULL OR p_predecessor IS NULL OR p_revision IS NULL
       OR p_revision NOT BETWEEN 1 AND 9223372036854775806))
  THEN RAISE EXCEPTION 'location body invalid' USING ERRCODE='22023'; END IF;
  canonical:=location_api._canonical(p_name);
  IF p_canonical IS DISTINCT FROM canonical
     OR p_digest IS DISTINCT FROM pg_catalog.encode(pg_catalog.sha256(pg_catalog.convert_to(canonical,'UTF8')),'hex')
  THEN RAISE EXCEPTION 'location body invalid' USING ERRCODE='22023'; END IF;
  PERFORM location_api._lock_commands(p_practice,p_membership,p_key,p_intent);
  SELECT c.* INTO prior FROM public.practice_location_create_commands c
    WHERE c.practice_id=p_practice AND c.actor_membership_id=p_membership AND c.command_key=p_key;
  prior_found:=FOUND;
  instant:=pg_catalog.clock_timestamp();
  IF instant>=p_expiry THEN RAISE EXCEPTION 'location authority denied' USING ERRCODE='42501'; END IF;
  IF prior_found THEN
    IF prior.actor_account_id IS DISTINCT FROM p_account OR prior.actor_user_id IS DISTINCT FROM p_user
       OR prior.canonicalization_version IS DISTINCT FROM 'practice_location.create.body.v1'
       OR prior.canonical_text IS DISTINCT FROM canonical OR prior.canonical_body IS DISTINCT FROM canonical::jsonb
       OR prior.body_digest IS DISTINCT FROM p_digest OR prior.started_new_intent IS DISTINCT FROM p_new
       OR prior.request_intent_id IS DISTINCT FROM p_intent OR prior.supersedes_command_id IS DISTINCT FROM p_predecessor
       OR prior.predecessor_revision IS DISTINCT FROM p_revision
    THEN RAISE EXCEPTION 'location command conflict' USING ERRCODE='P0001'; END IF;
    IF prior.state='committed' THEN
      answer:=pg_catalog.jsonb_build_object('state','committed','receipt',location_api._receipt(prior));
    ELSE
      IF prior.state<>'prepared' OR prior.role IS DISTINCT FROM p_role
         OR prior.authority_generation IS DISTINCT FROM p_generation OR instant>=prior.expires_at
      THEN RAISE EXCEPTION 'location command conflict' USING ERRCODE='P0001'; END IF;
      answer:=location_api._draft(prior);
    END IF;
    IF pg_catalog.clock_timestamp()>=p_expiry
    THEN RAISE EXCEPTION 'location authority denied' USING ERRCODE='42501'; END IF;
    IF prior.state='prepared' AND pg_catalog.clock_timestamp()>=prior.expires_at
    THEN RAISE EXCEPTION 'location command conflict' USING ERRCODE='P0001'; END IF;
    RETURN answer;
  END IF;
  IF p_new THEN
    fresh_intent:=pg_catalog.gen_random_uuid(); next_revision:=1;
  ELSE
    SELECT c.* INTO head FROM public.practice_location_create_commands c
      WHERE c.practice_id=p_practice AND c.actor_membership_id=p_membership AND c.create_intent_id=p_intent
      ORDER BY c.draft_revision DESC,c.id DESC LIMIT 1;
    IF NOT FOUND OR head.actor_account_id IS DISTINCT FROM p_account OR head.actor_user_id IS DISTINCT FROM p_user
       OR head.state<>'prepared' OR head.id IS DISTINCT FROM p_predecessor OR head.draft_revision IS DISTINCT FROM p_revision
       OR EXISTS (SELECT 1 FROM public.practice_location_create_commands c WHERE c.practice_id=p_practice
         AND c.actor_membership_id=p_membership AND c.create_intent_id=p_intent AND c.state='committed')
    THEN RAISE EXCEPTION 'location command conflict' USING ERRCODE='P0001'; END IF;
    -- A new current-authority revision can correct an expired draft; its old
    -- capability is superseded, never revived or silently confirmed.
    UPDATE public.practice_location_create_commands SET state='superseded'
      WHERE id=head.id AND practice_id=p_practice AND state='prepared';
    fresh_intent:=p_intent; next_revision:=head.draft_revision+1;
  END IF;
  instant:=pg_catalog.clock_timestamp();
  IF instant>=p_expiry THEN RAISE EXCEPTION 'location authority denied' USING ERRCODE='42501'; END IF;
  INSERT INTO public.practice_location_create_commands(id,practice_id,actor_account_id,actor_membership_id,actor_user_id,
    role,authority_generation,command_key,create_intent_id,draft_revision,request_intent_id,supersedes_command_id,
    predecessor_revision,started_new_intent,canonicalization_version,canonical_text,canonical_body,body_digest,
    prepared_at,expires_at,state,location_id,audit_event_id,outbox_event_id,committed_at)
    VALUES(pg_catalog.gen_random_uuid(),p_practice,p_account,p_membership,p_user,p_role,p_generation,p_key,
      fresh_intent,next_revision,p_intent,p_predecessor,p_revision,p_new,'practice_location.create.body.v1',canonical,
      canonical::jsonb,p_digest,instant,instant+interval '300 seconds','prepared',NULL,NULL,NULL,NULL)
    ON CONFLICT (practice_id,actor_membership_id,command_key) DO NOTHING RETURNING * INTO fresh;
  IF NOT FOUND THEN RAISE EXCEPTION 'location command conflict' USING ERRCODE='P0001'; END IF;
  answer:=location_api._draft(fresh);
  instant:=pg_catalog.clock_timestamp();
  IF instant>=p_expiry THEN RAISE EXCEPTION 'location authority denied' USING ERRCODE='42501'; END IF;
  IF instant>=fresh.expires_at THEN RAISE EXCEPTION 'location command conflict' USING ERRCODE='P0001'; END IF;
  RETURN answer;
END;
"""

CONFIRM_BODY = """
DECLARE c public.practice_location_create_commands%ROWTYPE; instant timestamptz; canonical text;
        fresh_location uuid; fresh_audit uuid; fresh_outbox uuid; answer jsonb;
BEGIN
  PERFORM location_api._authority(""" + AUTH_CALL + """);
  IF p_key IS NULL OR p_command IS NULL OR p_intent IS NULL OR p_revision IS NULL OR p_revision<1
     OR p_digest IS NULL OR p_original_role IS DISTINCT FROM 'PracticeOwner'
     OR p_original_generation IS NULL OR p_original_generation<1 OR p_draft_expiry IS NULL
     OR p_confirmed IS DISTINCT FROM true
  THEN RAISE EXCEPTION 'location command conflict' USING ERRCODE='P0001'; END IF;
  PERFORM location_api._lock_commands(p_practice,p_membership,p_key,p_intent);
  SELECT x.* INTO c FROM public.practice_location_create_commands x
    WHERE x.practice_id=p_practice AND x.actor_membership_id=p_membership AND x.command_key=p_key;
  IF NOT FOUND OR c.actor_account_id IS DISTINCT FROM p_account OR c.actor_user_id IS DISTINCT FROM p_user
     OR c.id IS DISTINCT FROM p_command OR c.create_intent_id IS DISTINCT FROM p_intent
     OR c.draft_revision IS DISTINCT FROM p_revision OR c.body_digest IS DISTINCT FROM p_digest
     OR c.role IS DISTINCT FROM p_original_role OR c.authority_generation IS DISTINCT FROM p_original_generation
     OR c.expires_at IS DISTINCT FROM p_draft_expiry
  THEN RAISE EXCEPTION 'location command conflict' USING ERRCODE='P0001'; END IF;
  instant:=pg_catalog.clock_timestamp();
  IF instant>=p_expiry THEN RAISE EXCEPTION 'location authority denied' USING ERRCODE='42501'; END IF;
  -- Fresh same-identity authority is required for every call. The exact already
  -- committed tuple preserves its original generation/expiry; this is read-only
  -- replay, before the stricter uncommitted new-effect predicates below.
  IF c.state='committed' THEN RETURN location_api._receipt(c); END IF;
  IF c.state<>'prepared' OR c.role IS DISTINCT FROM p_role OR c.authority_generation IS DISTINCT FROM p_generation
     OR instant>=c.expires_at OR c.canonicalization_version IS DISTINCT FROM 'practice_location.create.body.v1'
     OR EXISTS (SELECT 1 FROM public.practice_location_create_commands x WHERE x.practice_id=p_practice
       AND x.actor_membership_id=p_membership AND x.create_intent_id=c.create_intent_id
       AND (x.draft_revision>c.draft_revision OR x.state='committed'))
  THEN RAISE EXCEPTION 'location command conflict' USING ERRCODE='P0001'; END IF;
  canonical:=location_api._canonical(c.canonical_body->>'name');
  IF c.canonical_text IS DISTINCT FROM canonical OR c.canonical_body IS DISTINCT FROM canonical::jsonb
     OR c.body_digest IS DISTINCT FROM pg_catalog.encode(pg_catalog.sha256(pg_catalog.convert_to(canonical,'UTF8')),'hex')
  THEN RAISE EXCEPTION 'location command conflict' USING ERRCODE='P0001'; END IF;
  instant:=pg_catalog.clock_timestamp();
  IF instant>=p_expiry THEN RAISE EXCEPTION 'location authority denied' USING ERRCODE='42501'; END IF;
  IF instant>=c.expires_at THEN RAISE EXCEPTION 'location command conflict' USING ERRCODE='P0001'; END IF;
  fresh_location:=pg_catalog.gen_random_uuid(); fresh_audit:=pg_catalog.gen_random_uuid();
  fresh_outbox:=pg_catalog.gen_random_uuid();
  -- No reuse by name or assumed table default: each explicit new command owns
  -- its own UUID. This writes a location/site, not room/capacity/calendar truth.
  INSERT INTO public.practice_locations(id,practice_id,name,is_active)
    VALUES(fresh_location,p_practice,c.canonical_body->>'name',true);
  INSERT INTO public.practice_location_create_audit(id,practice_id,command_id,location_id,
      actor_account_id,actor_membership_id,actor_user_id,event_code,body_digest,created_at)
    VALUES(fresh_audit,p_practice,c.id,fresh_location,p_account,p_membership,p_user,
      'location_created',c.body_digest,instant);
  INSERT INTO public.practice_location_create_outbox(id,practice_id,command_id,audit_event_id,location_id,
      actor_account_id,actor_membership_id,actor_user_id,correlation_id,event_type,schema_version,
      source_system,payload,published,created_at)
    VALUES(fresh_outbox,p_practice,c.id,fresh_audit,fresh_location,p_account,p_membership,p_user,
      c.command_key,'practice.location_created','practice.location_created.v1',
      'emr4-practice-administration',pg_catalog.jsonb_build_object('location_id',fresh_location,
        'body_digest',c.body_digest,'reason_codes',pg_catalog.jsonb_build_array('location_created')),
      false,instant);
  UPDATE public.practice_location_create_commands SET state='committed',location_id=fresh_location,
    audit_event_id=fresh_audit,outbox_event_id=fresh_outbox,committed_at=instant
    WHERE id=c.id AND practice_id=p_practice AND actor_membership_id=p_membership AND state='prepared'
    RETURNING * INTO c;
  IF NOT FOUND THEN RAISE EXCEPTION 'location command conflict' USING ERRCODE='P0001'; END IF;
  answer:=location_api._receipt(c);
  -- Any expiry after insert/update/FK/trigger waits raises inside the same
  -- transaction, rolling back location, command terminal state, audit and outbox.
  instant:=pg_catalog.clock_timestamp();
  IF instant>=p_expiry THEN RAISE EXCEPTION 'location authority denied' USING ERRCODE='42501'; END IF;
  IF instant>=c.expires_at THEN RAISE EXCEPTION 'location command conflict' USING ERRCODE='P0001'; END IF;
  RETURN answer;
END;
"""

READBACK_BODY = """
DECLARE c public.practice_location_create_commands%ROWTYPE; resource_row record;
        expected jsonb; current_facts jsonb; read_status text; answer jsonb;
BEGIN
  PERFORM location_api._authority(""" + AUTH_CALL + """);
  IF p_key IS NULL THEN RAISE EXCEPTION 'location body invalid' USING ERRCODE='22023'; END IF;
  PERFORM location_api._lock_commands(p_practice,p_membership,p_key,NULL);
  SELECT x.* INTO c FROM public.practice_location_create_commands x
    WHERE x.practice_id=p_practice AND x.actor_membership_id=p_membership AND x.command_key=p_key
      AND x.state='committed';
  IF NOT FOUND OR c.actor_account_id IS DISTINCT FROM p_account OR c.actor_user_id IS DISTINCT FROM p_user
  THEN RAISE EXCEPTION 'location receipt not found' USING ERRCODE='P0002'; END IF;
  expected:=pg_catalog.jsonb_build_object('name',c.canonical_body->>'name','is_active',true);
  SELECT p.id,p.practice_id,p.name,p.is_active INTO resource_row FROM public.practice_locations p
    WHERE p.id=c.location_id AND p.practice_id=p_practice;
  IF NOT FOUND THEN
    read_status:='missing'; current_facts:=NULL;
  ELSE
    current_facts:=pg_catalog.jsonb_build_object('id',resource_row.id,'practice_id',resource_row.practice_id,
      'name',resource_row.name,'is_active',resource_row.is_active);
    IF resource_row.name IS NOT DISTINCT FROM c.canonical_body->>'name'
       AND resource_row.is_active IS NOT DISTINCT FROM true
    THEN read_status:='matches_created'; ELSE read_status:='diverged'; END IF;
  END IF;
  -- Immutable original receipt and newly observed current facts remain separate.
  answer:=pg_catalog.jsonb_build_object('receipt',location_api._receipt(c),
    'readback',pg_catalog.jsonb_build_object('status',read_status,'expected',expected,'current',current_facts));
  IF pg_catalog.clock_timestamp()>=p_expiry
  THEN RAISE EXCEPTION 'location authority denied' USING ERRCODE='42501'; END IF;
  RETURN answer;
END;
"""

COMMAND_TRANSITION_BODY = """
BEGIN
  IF OLD.state IS DISTINCT FROM 'prepared' OR NEW.state NOT IN ('superseded','committed')
  THEN RAISE EXCEPTION 'location command immutable' USING ERRCODE='P0001'; END IF;
  RETURN NEW;
END;
"""

FUNCTIONS = (
    ("_authority", AUTH_ARGS, AUTH_TYPES, "void", AUTHORITY_BODY, False),
    ("_lock_commands", "p_practice uuid,p_membership uuid,p_key uuid,p_intent uuid", "uuid,uuid,uuid,uuid", "void", LOCK_COMMANDS_BODY, False),
    ("_w1", "", "", "text", W1_BODY, False),
    ("_canonical", "p_name text", "text", "text", CANONICAL_BODY, False),
    ("_receipt", "c public.practice_location_create_commands", "public.practice_location_create_commands", "jsonb", RECEIPT_BODY, False),
    ("_draft", "c public.practice_location_create_commands", "public.practice_location_create_commands", "jsonb", DRAFT_BODY, False),
    ("_command_transition", "", "", "trigger", COMMAND_TRANSITION_BODY, False),
    ("prepare_create", AUTH_ARGS+",p_key uuid,p_name text,p_canonical text,p_digest text,p_new boolean,p_intent uuid,p_predecessor uuid,p_revision bigint",
        AUTH_TYPES+",uuid,text,text,text,boolean,uuid,uuid,bigint", "jsonb", PREPARE_BODY, True),
    ("confirm_create", AUTH_ARGS+",p_key uuid,p_command uuid,p_intent uuid,p_revision bigint,p_digest text,p_original_role text,p_original_generation bigint,p_draft_expiry timestamptz,p_confirmed boolean",
        AUTH_TYPES+",uuid,uuid,uuid,bigint,text,text,bigint,timestamptz,boolean", "jsonb", CONFIRM_BODY, True),
    ("read_create_receipt", AUTH_ARGS+",p_key uuid", AUTH_TYPES+",uuid", "jsonb", READBACK_BODY, True),
)


def _columns(connection, table):
    return connection.execute(sa.text("""
      SELECT a.attname FROM pg_catalog.pg_attribute a
      WHERE a.attrelid=pg_catalog.to_regclass(:table) AND a.attnum>0 AND NOT a.attisdropped
      ORDER BY a.attnum
    """), {"table": "public."+table}).scalars().all()


def _assert_roles(connection, *, final=False):
    rows = connection.execute(sa.text("""
      SELECT rolname,rolcanlogin,rolsuper,rolbypassrls,rolinherit,rolcreaterole,rolcreatedb,rolreplication
      FROM pg_catalog.pg_roles WHERE rolname IN ('raisa_local_location_functions','raisa_local_tenant')
      ORDER BY rolname
    """)).all()
    if [tuple(r) for r in rows] != [
        (OWNER, False, False, False, False, False, False, False),
        (TENANT, True, False, False, False, False, False, False)]:
        raise RuntimeError("location restricted roles unavailable")
    if connection.execute(sa.text("""
      SELECT EXISTS (SELECT 1 FROM pg_catalog.pg_auth_members e JOIN pg_catalog.pg_roles r
        ON r.oid=e.member OR r.oid=e.roleid WHERE r.rolname IN
        ('raisa_local_location_functions','raisa_local_tenant'))
      OR pg_catalog.has_schema_privilege('raisa_local_location_functions','public','CREATE')
      OR pg_catalog.has_schema_privilege('raisa_local_tenant','public','CREATE')
    """)).scalar_one():
        raise RuntimeError("location role membership/schema boundary unavailable")
    for table, sets in COLUMNS.items():
        if not final and table in NEW_TABLES:
            continue
        columns = _columns(connection, table)
        if not columns:
            raise RuntimeError("location relation missing")
        if connection.execute(sa.text("""
          SELECT c.relowner=r.oid FROM pg_catalog.pg_class c
          JOIN pg_catalog.pg_roles r ON r.rolname=:role
          WHERE c.oid=pg_catalog.to_regclass(:table)
        """), {"role": OWNER, "table": "public."+table}).scalar_one():
            raise RuntimeError("location function owner must not own public tables")
        for privilege, names in zip(("SELECT", "INSERT", "UPDATE"), sets):
            requested = set(names.split(",")) if names else set()
            if final and not requested.issubset(columns):
                raise RuntimeError("location exact column matrix unavailable")
            for column in columns:
                actual = connection.execute(sa.text("""
                  SELECT pg_catalog.has_column_privilege(:role,:table,:column,:privilege)
                """), {"role": OWNER, "table": "public."+table,
                         "column": column, "privilege": privilege}).scalar_one()
                if actual != (final and column in requested):
                    raise RuntimeError("location owner exact column ACL mismatch")
        for privilege in ("DELETE", "TRUNCATE", "REFERENCES", "TRIGGER"):
            if connection.execute(sa.text("SELECT pg_catalog.has_table_privilege(:role,:table,:privilege)"),
                {"role": OWNER, "table": "public."+table, "privilege": privilege}).scalar_one():
                raise RuntimeError("location owner excess table ACL")
        # Column REFERENCES is independent of table REFERENCES.
        for column in columns:
            if connection.execute(sa.text("SELECT pg_catalog.has_column_privilege(:role,:table,:column,'REFERENCES')"),
                {"role": OWNER, "table": "public."+table, "column": column}).scalar_one():
                raise RuntimeError("location owner excess column REFERENCES")


def _assert_location_contract(connection):
    # Exact selected-source physical contract, not a live DB assertion made by
    # this stopped file. The location table has no version or name uniqueness.
    if connection.execute(sa.text("SHOW server_encoding")).scalar_one() != "UTF8":
        raise RuntimeError("location canonical bytes require UTF8")
    rows = connection.execute(sa.text("""
      SELECT a.attname,pg_catalog.format_type(a.atttypid,a.atttypmod),a.attnotnull,
        a.attgenerated,a.attidentity,d.adbin IS NULL
      FROM pg_catalog.pg_attribute a LEFT JOIN pg_catalog.pg_attrdef d
        ON d.adrelid=a.attrelid AND d.adnum=a.attnum
      WHERE a.attrelid='public.practice_locations'::regclass
        AND a.attnum>0 AND NOT a.attisdropped ORDER BY a.attname
    """)).all()
    if [tuple(r) for r in rows] != [
        ("address_line1", "character varying(255)", False, "", "", True),
        ("address_postcode", "character varying(10)", False, "", "", True),
        ("address_state", "character varying(10)", False, "", "", True),
        ("address_suburb", "character varying(100)", False, "", "", True),
        ("id", "uuid", True, "", "", True),
        ("is_active", "boolean", False, "", "", True),
        ("name", "character varying(255)", True, "", "", True),
        ("phone", "character varying(20)", False, "", "", True),
        ("practice_id", "uuid", True, "", "", True),
        ("waiting_rooms", "jsonb", False, "", "", True)]:
        raise RuntimeError("location physical field/default contract unavailable")
    key_ok = connection.execute(sa.text("""
      SELECT count(*)=1 FROM pg_catalog.pg_constraint c
      WHERE c.conrelid='public.practice_locations'::regclass
        AND c.conname='uq_practice_locations_practice_id_id' AND c.contype='u'
        AND c.convalidated AND NOT c.condeferrable
        AND (SELECT pg_catalog.array_agg(a.attname::text ORDER BY k.ord)
          FROM pg_catalog.unnest(c.conkey) WITH ORDINALITY AS k(num,ord)
          JOIN pg_catalog.pg_attribute a ON a.attrelid=c.conrelid AND a.attnum=k.num)
            =ARRAY['practice_id','id']::text[]
    """)).scalar_one()
    if key_ok is not True:
        raise RuntimeError("existing location composite key unavailable")
    if tuple(connection.execute(sa.text("""
      SELECT relrowsecurity,relforcerowsecurity FROM pg_catalog.pg_class
      WHERE oid='public.practice_locations'::regclass
    """)).one()) != (False, False):
        raise RuntimeError("selected location RLS bits changed; separate mapping required")
    if connection.execute(sa.text("""
      SELECT EXISTS (SELECT 1 FROM pg_catalog.pg_trigger t
        WHERE t.tgrelid='public.practice_locations'::regclass AND NOT t.tgisinternal AND t.tgenabled<>'D')
    """)).scalar_one():
        raise RuntimeError("location trigger closure requires separate review")


def _assert_tenant_and_surface(connection):
    for table in ("practice_locations", *NEW_TABLES):
        for column in _columns(connection, table):
            privileges = ("INSERT", "UPDATE", "REFERENCES")
            if table in NEW_TABLES:
                privileges = ("SELECT", *privileges)
            for privilege in privileges:
                actual = connection.execute(sa.text(
                    "SELECT pg_catalog.has_column_privilege(:role,:table,:column,:privilege)"
                ), {"role": TENANT, "table": "public."+table,
                    "column": column, "privilege": privilege}).scalar_one()
                # Existing tenant SELECT is preserved; no direct location write
                # or new command-table access is admitted by this migration.
                if actual:
                    raise RuntimeError("location tenant direct-write/table ACL mismatch")
        for privilege in ("DELETE", "TRUNCATE", "TRIGGER", "REFERENCES"):
            if connection.execute(sa.text("SELECT pg_catalog.has_table_privilege(:role,:table,:privilege)"),
                {"role": TENANT, "table": "public."+table, "privilege": privilege}).scalar_one():
                raise RuntimeError("location tenant excess direct-table ACL")
    for table in NEW_TABLES:
        if tuple(connection.execute(sa.text("""
          SELECT relrowsecurity,relforcerowsecurity FROM pg_catalog.pg_class
          WHERE oid=pg_catalog.to_regclass(:table)
        """), {"table": "public."+table}).one()) != (True, True):
            raise RuntimeError("location command RLS unavailable")
    for name, args, types, returns, body, public in FUNCTIONS:
        signature = "location_api."+name+"("+types+")"
        row = connection.execute(sa.text("""
          SELECT p.prosecdef,p.proconfig,r.rolname,
            pg_catalog.has_function_privilege(:tenant,p.oid,'EXECUTE'),
            EXISTS (SELECT 1 FROM pg_catalog.aclexplode(COALESCE(p.proacl,
              pg_catalog.acldefault('f',p.proowner))) a
              WHERE a.grantee=0 OR a.is_grantable OR
                (a.grantee<>p.proowner AND a.grantee<>(SELECT oid FROM pg_catalog.pg_roles WHERE rolname=:tenant)))
          FROM pg_catalog.pg_proc p JOIN pg_catalog.pg_roles r ON r.oid=p.proowner
          WHERE p.oid=pg_catalog.to_regprocedure(:signature)
        """), {"signature": signature, "tenant": TENANT}).one()
        if tuple(row) != (True, ["search_path=pg_catalog"], OWNER, public, False):
            raise RuntimeError("location function owner/search-path/ACL mismatch")
    row = connection.execute(sa.text("""
      SELECT r.rolname,pg_catalog.has_schema_privilege(:tenant,n.oid,'USAGE'),
        pg_catalog.has_schema_privilege(:tenant,n.oid,'CREATE'),
        EXISTS (SELECT 1 FROM pg_catalog.aclexplode(COALESCE(n.nspacl,
          pg_catalog.acldefault('n',n.nspowner))) a WHERE a.grantee=0)
      FROM pg_catalog.pg_namespace n JOIN pg_catalog.pg_roles r ON r.oid=n.nspowner
      WHERE n.nspname='location_api'
    """), {"tenant": TENANT}).one()
    if tuple(row) != (OWNER, True, False, False):
        raise RuntimeError("location schema ACL mismatch")


def upgrade():
    if context.is_offline_mode() or not op.get_bind().in_transaction():
        raise RuntimeError("location migration requires an owned online transaction")
    connection = op.get_bind()
    if connection.execute(sa.text("SHOW transaction_isolation")).scalar_one() != "read committed":
        raise RuntimeError("location migration requires read committed isolation")
    _assert_roles(connection)
    op.execute("LOCK TABLE public.practice_locations IN SHARE ROW EXCLUSIVE MODE")
    _assert_location_contract(connection)
    op.execute("CREATE SCHEMA location_api AUTHORIZATION raisa_local_location_functions")
    op.execute("REVOKE ALL ON SCHEMA location_api FROM PUBLIC")
    op.execute("GRANT USAGE ON SCHEMA location_api TO raisa_local_tenant")
    op.execute("GRANT USAGE ON SCHEMA public TO raisa_local_location_functions")
    op.execute(SCHEMA_SQL)
    # Existing relation RLS enable/force bits and unrelated policies are preserved.
    for table in NEW_TABLES:
        op.execute(f"REVOKE ALL ON public.{table} FROM PUBLIC,raisa_local_tenant")
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE public.{table} FORCE ROW LEVEL SECURITY")
    for table, sets in COLUMNS.items():
        for privilege, columns in zip(("SELECT", "INSERT", "UPDATE"), sets):
            if columns:
                op.execute(f"GRANT {privilege}({columns}) ON public.{table} TO {OWNER}")
    practice = "NULLIF(pg_catalog.current_setting('app.current_practice_id',true),'')::uuid"
    account = "NULLIF(pg_catalog.current_setting('practice_location.account_id',true),'')::uuid"
    member = "NULLIF(pg_catalog.current_setting('practice_location.membership_id',true),'')::uuid"
    user = "NULLIF(pg_catalog.current_setting('practice_location.user_id',true),'')::uuid"
    actor = "practice_id="+practice+" AND actor_account_id="+account+" AND actor_membership_id="+member+" AND actor_user_id="+user
    predicates = {
        "accounts": "id="+account,
        "practice_memberships": "id="+member+" AND practice_id="+practice+" AND account_id="+account+" AND legacy_user_id="+user,
        "users": "id="+user+" AND practice_id="+practice,
        "practice_membership_roles": "membership_id="+member+" AND EXISTS (SELECT 1 FROM public.practice_memberships m WHERE m.id=membership_id AND m.practice_id="+practice+")",
        "practices": "id="+practice,
        "practice_location_create_commands": actor,
        "practice_location_create_audit": actor,
        "practice_location_create_outbox": actor,
    }
    for table, predicate in predicates.items():
        read, insert, update = COLUMNS[table]
        if read:
            op.execute(f"CREATE POLICY practice_location_create_read ON public.{table} FOR SELECT TO {OWNER} USING ({predicate})")
        if insert:
            op.execute(f"CREATE POLICY practice_location_create_insert ON public.{table} FOR INSERT TO {OWNER} WITH CHECK ({predicate})")
        if update:
            op.execute(f"CREATE POLICY practice_location_create_lock_or_finish ON public.{table} FOR UPDATE TO {OWNER} USING ({predicate}) WITH CHECK ({predicate})")
    for name, args, types, returns, body, public in FUNCTIONS:
        op.execute(f"CREATE FUNCTION location_api.{name}({args}) RETURNS {returns} LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $location$\n{body}\n$location$")
        signature = f"location_api.{name}({types})"
        op.execute(f"ALTER FUNCTION {signature} OWNER TO {OWNER}")
        op.execute(f"REVOKE ALL ON FUNCTION {signature} FROM PUBLIC,raisa_local_tenant")
        if public:
            op.execute(f"GRANT EXECUTE ON FUNCTION {signature} TO {TENANT}")
    op.execute("CREATE TRIGGER practice_location_create_terminal BEFORE UPDATE ON public.practice_location_create_commands "
               "FOR EACH ROW EXECUTE FUNCTION location_api._command_transition()")
    _assert_roles(connection, final=True)
    _assert_tenant_and_surface(connection)
    _assert_location_contract(connection)


def downgrade():
    raise RuntimeError("location source has no admitted destructive downgrade")
