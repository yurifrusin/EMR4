"""STOPPED/default-off owner-confirmed FIRST weekly window, F3 descendant.

No existing calendar columns/defaults/constraints/RLS bits are changed. Existing
calendar SELECT is not tenant row isolation. The protected tenant Engine,
verified HTTP service and separately provisioned restricted NOLOGIN function role
are prerequisites. SQL arguments/GUCs do not authenticate hostile SQL callers.
No role is created here. Only new command/audit/outbox tables become FORCE RLS.
No booking-capacity, runtime, publication or destructive downgrade is admitted.
"""
from alembic import context, op
import sqlalchemy as sa

revision = "f4a5b6c7d8e9"
down_revision = "f3a4b5c6d7e8"
branch_labels = None
depends_on = None
OWNER = "raisa_local_weekly_window_functions"
TENANT = "raisa_local_tenant"
AUTH_ARGS = "p_account uuid,p_membership uuid,p_user uuid,p_practice uuid,p_role text,p_generation bigint,p_expiry timestamptz"
AUTH_TYPES = "uuid,uuid,uuid,uuid,text,bigint,timestamptz"
COMMAND_COLUMNS = (
    "id,practice_id,actor_account_id,actor_membership_id,actor_user_id,role,authority_generation,command_key,"
    "practitioner_id,location_id,canonicalization_version,canonical_text,canonical_body,body_digest,context_digest,"
    "prepared_at,expires_at,state,schedule_id,audit_event_id,outbox_event_id,committed_at")
AUDIT_COLUMNS = ("id,practice_id,command_id,schedule_id,practitioner_id,location_id,actor_account_id,"
                 "actor_membership_id,actor_user_id,event_code,body_digest,context_digest,created_at")
OUTBOX_COLUMNS = ("id,practice_id,command_id,audit_event_id,schedule_id,practitioner_id,location_id,actor_account_id,"
                  "actor_membership_id,actor_user_id,correlation_id,event_type,schema_version,source_system,payload,published,created_at")
COLUMNS = {
    "accounts": ("id,is_active", "", "id"),
    "practice_memberships": ("id,account_id,practice_id,legacy_user_id,is_active,authority_generation", "", "id"),
    "users": ("id,practice_id,role,is_active,authority_generation", "", "id"),
    "practice_membership_roles": ("membership_id,role", "", "membership_id"),
    "practices": ("id,timezone", "", "id"),
    "practitioners": ("id,practice_id,is_active,aggregate_version", "", "id"),
    "practice_locations": ("id,practice_id,is_active", "", "id"),
    "practitioner_create_commands": ("id,practice_id,actor_account_id,actor_membership_id,actor_user_id,command_key,practitioner_id,state", "", ""),
    "practice_location_create_commands": ("id,practice_id,actor_account_id,actor_membership_id,actor_user_id,command_key,location_id,state", "", ""),
    "practitioner_schedules": ("id,practitioner_id,location_id,day_of_week,start_time,end_time,slot_duration_minutes",
                              "id,practitioner_id,location_id,day_of_week,start_time,end_time,slot_duration_minutes", ""),
    "schedule_overrides": ("id,practitioner_id", "", ""),
    "practitioner_first_weekly_window_commands": (COMMAND_COLUMNS, COMMAND_COLUMNS, "state,schedule_id,audit_event_id,outbox_event_id,committed_at"),
    "practitioner_first_weekly_window_audit": ("", AUDIT_COLUMNS, ""),
    "practitioner_first_weekly_window_outbox": ("", OUTBOX_COLUMNS, ""),
}
NEW_TABLES = ("practitioner_first_weekly_window_commands", "practitioner_first_weekly_window_audit", "practitioner_first_weekly_window_outbox")

SCHEMA_SQL = """
CREATE TABLE public.practitioner_first_weekly_window_commands (
 id uuid PRIMARY KEY, practice_id uuid NOT NULL REFERENCES public.practices(id),
 actor_account_id uuid NOT NULL REFERENCES public.accounts(id),
 actor_membership_id uuid NOT NULL REFERENCES public.practice_memberships(id), actor_user_id uuid NOT NULL,
 role text NOT NULL CHECK (role='PracticeOwner'), authority_generation bigint NOT NULL CHECK (authority_generation>=1),
 command_key uuid NOT NULL, practitioner_id uuid NOT NULL, location_id uuid NOT NULL,
 canonicalization_version text NOT NULL CHECK (canonicalization_version='practitioner.first_weekly_window.body.v1'),
 canonical_text text NOT NULL, canonical_body jsonb NOT NULL,
 body_digest text NOT NULL CHECK (body_digest ~ '^[0-9a-f]{64}$'),
 context_digest text NOT NULL CHECK (context_digest ~ '^[0-9a-f]{64}$'),
 prepared_at timestamptz NOT NULL, expires_at timestamptz NOT NULL CHECK (expires_at>prepared_at),
 state text NOT NULL CHECK (state IN ('prepared','committed')),
 schedule_id uuid REFERENCES public.practitioner_schedules(id), audit_event_id uuid, outbox_event_id uuid, committed_at timestamptz,
 CONSTRAINT uq_first_weekly_key UNIQUE(practice_id,actor_membership_id,command_key),
 CONSTRAINT uq_first_weekly_command_practice UNIQUE(practice_id,id),
 CONSTRAINT fk_first_weekly_actor FOREIGN KEY(practice_id,actor_user_id) REFERENCES public.users(practice_id,id),
 CONSTRAINT fk_first_weekly_practitioner FOREIGN KEY(practice_id,practitioner_id) REFERENCES public.practitioners(practice_id,id),
 CONSTRAINT fk_first_weekly_location FOREIGN KEY(practice_id,location_id) REFERENCES public.practice_locations(practice_id,id),
 CONSTRAINT ck_first_weekly_terminal CHECK (
   (state='committed' AND schedule_id IS NOT NULL AND audit_event_id IS NOT NULL AND outbox_event_id IS NOT NULL AND committed_at IS NOT NULL)
   OR (state='prepared' AND schedule_id IS NULL AND audit_event_id IS NULL AND outbox_event_id IS NULL AND committed_at IS NULL)),
 CONSTRAINT ck_first_weekly_body CHECK (canonical_body=canonical_text::jsonb AND
   body_digest=pg_catalog.encode(pg_catalog.sha256(pg_catalog.convert_to(canonical_text,'UTF8')),'hex'))
);
CREATE UNIQUE INDEX uq_first_weekly_committed_practitioner ON public.practitioner_first_weekly_window_commands(practice_id,practitioner_id) WHERE state='committed';
CREATE TABLE public.practitioner_first_weekly_window_audit (
 id uuid PRIMARY KEY, practice_id uuid NOT NULL REFERENCES public.practices(id), command_id uuid NOT NULL,
 schedule_id uuid NOT NULL REFERENCES public.practitioner_schedules(id), practitioner_id uuid NOT NULL, location_id uuid NOT NULL,
 actor_account_id uuid NOT NULL REFERENCES public.accounts(id), actor_membership_id uuid NOT NULL REFERENCES public.practice_memberships(id), actor_user_id uuid NOT NULL,
 event_code text NOT NULL CHECK(event_code='first_weekly_window_created'), body_digest text NOT NULL, context_digest text NOT NULL,
 created_at timestamptz NOT NULL,
 CONSTRAINT uq_first_weekly_audit_command UNIQUE(practice_id,command_id), CONSTRAINT uq_first_weekly_audit_practice UNIQUE(practice_id,id),
 FOREIGN KEY(practice_id,command_id) REFERENCES public.practitioner_first_weekly_window_commands(practice_id,id),
 FOREIGN KEY(practice_id,actor_user_id) REFERENCES public.users(practice_id,id),
 FOREIGN KEY(practice_id,practitioner_id) REFERENCES public.practitioners(practice_id,id),
 FOREIGN KEY(practice_id,location_id) REFERENCES public.practice_locations(practice_id,id)
);
CREATE TABLE public.practitioner_first_weekly_window_outbox (
 id uuid PRIMARY KEY, practice_id uuid NOT NULL REFERENCES public.practices(id), command_id uuid NOT NULL, audit_event_id uuid NOT NULL,
 schedule_id uuid NOT NULL REFERENCES public.practitioner_schedules(id), practitioner_id uuid NOT NULL, location_id uuid NOT NULL,
 actor_account_id uuid NOT NULL REFERENCES public.accounts(id), actor_membership_id uuid NOT NULL REFERENCES public.practice_memberships(id), actor_user_id uuid NOT NULL,
 correlation_id uuid NOT NULL, event_type text NOT NULL CHECK(event_type='practitioner.first_weekly_window_created'),
 schema_version text NOT NULL CHECK(schema_version='practitioner.first_weekly_window_created.v1'),
 source_system text NOT NULL CHECK(source_system='emr4-practice-administration'), payload jsonb NOT NULL,
 published boolean NOT NULL CHECK(published=false), created_at timestamptz NOT NULL,
 CONSTRAINT uq_first_weekly_outbox_command UNIQUE(practice_id,command_id), CONSTRAINT uq_first_weekly_outbox_audit UNIQUE(practice_id,audit_event_id),
 CONSTRAINT uq_first_weekly_outbox_practice UNIQUE(practice_id,id),
 FOREIGN KEY(practice_id,command_id) REFERENCES public.practitioner_first_weekly_window_commands(practice_id,id),
 FOREIGN KEY(practice_id,audit_event_id) REFERENCES public.practitioner_first_weekly_window_audit(practice_id,id),
 FOREIGN KEY(practice_id,actor_user_id) REFERENCES public.users(practice_id,id),
 FOREIGN KEY(practice_id,practitioner_id) REFERENCES public.practitioners(practice_id,id),
 FOREIGN KEY(practice_id,location_id) REFERENCES public.practice_locations(practice_id,id)
);
ALTER TABLE public.practitioner_first_weekly_window_commands ADD CONSTRAINT fk_first_weekly_audit FOREIGN KEY(practice_id,audit_event_id) REFERENCES public.practitioner_first_weekly_window_audit(practice_id,id);
ALTER TABLE public.practitioner_first_weekly_window_commands ADD CONSTRAINT fk_first_weekly_outbox FOREIGN KEY(practice_id,outbox_event_id) REFERENCES public.practitioner_first_weekly_window_outbox(practice_id,id);
"""

GUARD = """
  IF session_user<>'raisa_local_tenant' OR current_user<>'raisa_local_weekly_window_functions'
     OR (SELECT count(*) FROM pg_catalog.pg_roles r WHERE r.rolname IN
       ('raisa_local_tenant','raisa_local_weekly_window_functions'))<>2
     OR EXISTS (SELECT 1 FROM pg_catalog.pg_roles r WHERE r.rolname IN
       ('raisa_local_tenant','raisa_local_weekly_window_functions') AND
       (r.rolsuper OR r.rolbypassrls OR r.rolinherit OR r.rolcreaterole OR r.rolcreatedb
        OR r.rolreplication OR r.rolcanlogin<>(r.rolname='raisa_local_tenant')))
     OR EXISTS (SELECT 1 FROM pg_catalog.pg_auth_members e JOIN pg_catalog.pg_roles r
       ON r.oid=e.member OR r.oid=e.roleid WHERE r.rolname IN
       ('raisa_local_tenant','raisa_local_weekly_window_functions'))
     OR pg_catalog.has_schema_privilege('raisa_local_weekly_window_functions','public','CREATE')
     OR pg_catalog.has_schema_privilege('raisa_local_tenant','public','CREATE')
     OR pg_catalog.has_column_privilege('raisa_local_weekly_window_functions','public.accounts','password_hash','SELECT')
     OR pg_catalog.has_column_privilege('raisa_local_weekly_window_functions','public.users','password_hash','SELECT')
  THEN RAISE EXCEPTION 'first weekly window authority denied' USING ERRCODE='42501'; END IF;
"""

AUTHORITY_BODY = """
DECLARE account_row record; member_row record; user_row record; actual_role text;
BEGIN
""" + GUARD + """
  IF p_account IS NULL OR p_membership IS NULL OR p_user IS NULL OR p_practice IS NULL
     OR p_role IS DISTINCT FROM 'PracticeOwner' OR p_generation IS NULL OR p_generation<1
     OR p_expiry IS NULL OR pg_catalog.clock_timestamp()>=p_expiry
  THEN RAISE EXCEPTION 'first weekly window authority denied' USING ERRCODE='42501'; END IF;
  PERFORM pg_catalog.set_config('app.current_practice_id',p_practice::text,true);
  PERFORM pg_catalog.set_config('first_weekly_window.account_id',p_account::text,true);
  PERFORM pg_catalog.set_config('first_weekly_window.membership_id',p_membership::text,true);
  PERFORM pg_catalog.set_config('first_weekly_window.user_id',p_user::text,true);
  SELECT a.id,a.is_active INTO account_row FROM public.accounts a
    WHERE a.id=p_account FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'first weekly window authority denied' USING ERRCODE='42501'; END IF;
  SELECT m.id,m.account_id,m.practice_id,m.legacy_user_id,m.is_active,m.authority_generation
    INTO member_row FROM public.practice_memberships m
    WHERE m.id=p_membership AND m.account_id=p_account AND m.practice_id=p_practice
      AND m.legacy_user_id=p_user FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'first weekly window authority denied' USING ERRCODE='42501'; END IF;
  SELECT u.id,u.practice_id,u.role,u.is_active,u.authority_generation INTO user_row
    FROM public.users u WHERE u.id=p_user AND u.practice_id=p_practice FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'first weekly window authority denied' USING ERRCODE='42501'; END IF;
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
  THEN RAISE EXCEPTION 'first weekly window authority denied' USING ERRCODE='42501'; END IF;
  -- One selected-Practice lock, in UPDATE mode from the outset. No SHARE upgrade.
  PERFORM p.id FROM public.practices p WHERE p.id=p_practice FOR UPDATE;
  IF NOT FOUND OR pg_catalog.clock_timestamp()>=p_expiry
  THEN RAISE EXCEPTION 'first weekly window authority denied' USING ERRCODE='42501'; END IF;
END;
"""

BODY_BODY = """
DECLARE b jsonb; k text; expected text; width integer;
BEGIN
 IF p_canonical IS NULL OR p_digest IS NULL OR p_digest !~ '^[0-9a-f]{64}$'
   OR p_digest<>pg_catalog.encode(pg_catalog.sha256(pg_catalog.convert_to(p_canonical,'UTF8')),'hex')
 THEN RAISE EXCEPTION 'invalid window body' USING ERRCODE='22023'; END IF;
 BEGIN b:=p_canonical::jsonb;
 EXCEPTION WHEN invalid_text_representation THEN RAISE EXCEPTION 'invalid window body' USING ERRCODE='22023'; END;
 IF pg_catalog.jsonb_typeof(b)<>'object' OR (SELECT pg_catalog.array_agg(x ORDER BY x) FROM pg_catalog.jsonb_object_keys(b) x)
   IS DISTINCT FROM ARRAY['end_time','location_id','practice_timezone','practitioner_create_command_id','practitioner_create_command_key','practitioner_id','slot_duration_minutes','start_time','weekday']::text[]
 THEN RAISE EXCEPTION 'invalid window body' USING ERRCODE='22023'; END IF;
 FOREACH k IN ARRAY ARRAY['location_id','practitioner_id','practitioner_create_command_id','practitioner_create_command_key'] LOOP
   IF pg_catalog.jsonb_typeof(b->k)<>'string' OR (b->>k) !~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
   THEN RAISE EXCEPTION 'invalid window identity' USING ERRCODE='22023'; END IF;
 END LOOP;
 IF pg_catalog.jsonb_typeof(b->'weekday')<>'number' OR (b->>'weekday') !~ '^[0-6]$'
   OR pg_catalog.jsonb_typeof(b->'slot_duration_minutes')<>'number' OR (b->>'slot_duration_minutes') !~ '^[1-9][0-9]{0,3}$'
   OR pg_catalog.jsonb_typeof(b->'start_time')<>'string' OR (b->>'start_time') !~ '^([01][0-9]|2[0-3]):[0-5][0-9]$'
   OR pg_catalog.jsonb_typeof(b->'end_time')<>'string' OR (b->>'end_time') !~ '^([01][0-9]|2[0-3]):[0-5][0-9]$'
   OR pg_catalog.jsonb_typeof(b->'practice_timezone')<>'string' OR (b->>'practice_timezone') !~ '^[A-Za-z0-9._+/-]{1,50}$'
 THEN RAISE EXCEPTION 'invalid window values' USING ERRCODE='22023'; END IF;
 IF (b->>'slot_duration_minutes')::integer>1440 THEN RAISE EXCEPTION 'invalid grid' USING ERRCODE='22023'; END IF;
 width := (EXTRACT(EPOCH FROM ((b->>'end_time')::time-(b->>'start_time')::time))/60)::integer;
 IF width<=0 OR (b->>'slot_duration_minutes')::integer>width
   OR NOT EXISTS(SELECT 1 FROM pg_catalog.pg_timezone_names z WHERE z.name=b->>'practice_timezone')
 THEN RAISE EXCEPTION 'invalid window interval or zone' USING ERRCODE='22023'; END IF;
 expected:='{"end_time":'||(b->'end_time')::text||',"location_id":'||(b->'location_id')::text
   ||',"practice_timezone":'||(b->'practice_timezone')::text
   ||',"practitioner_create_command_id":'||(b->'practitioner_create_command_id')::text
   ||',"practitioner_create_command_key":'||(b->'practitioner_create_command_key')::text
   ||',"practitioner_id":'||(b->'practitioner_id')::text
   ||',"slot_duration_minutes":'||(b->'slot_duration_minutes')::text
   ||',"start_time":'||(b->'start_time')::text||',"weekday":'||(b->'weekday')::text||'}';
 IF p_canonical<>expected THEN RAISE EXCEPTION 'noncanonical window body' USING ERRCODE='22023'; END IF;
 RETURN b;
END;
"""

CONTEXT_BODY = """
DECLARE pr record; loc record; created record; zone text; bits record;
BEGIN
 SELECT p.id,p.practice_id,p.is_active,p.aggregate_version INTO pr FROM public.practitioners p
   WHERE p.id=(p_body->>'practitioner_id')::uuid AND p.practice_id=p_practice FOR UPDATE;
 IF NOT FOUND OR pr.is_active IS DISTINCT FROM true OR pr.aggregate_version IS NULL OR pr.aggregate_version<0
 THEN RAISE EXCEPTION 'window practitioner stale' USING ERRCODE='P0001'; END IF;
 SELECT c.id,c.practitioner_id INTO created FROM public.practitioner_create_commands c
   WHERE c.id=(p_body->>'practitioner_create_command_id')::uuid
     AND c.command_key=(p_body->>'practitioner_create_command_key')::uuid AND c.practice_id=p_practice
     AND c.practitioner_id=pr.id AND c.state='committed' AND c.actor_account_id=p_account
     AND c.actor_membership_id=p_membership AND c.actor_user_id=p_user;
 IF NOT FOUND THEN RAISE EXCEPTION 'exact practitioner create receipt required' USING ERRCODE='42501'; END IF;
 SELECT l.id,l.is_active INTO loc FROM public.practice_locations l
   WHERE l.id=(p_body->>'location_id')::uuid AND l.practice_id=p_practice FOR UPDATE;
 IF NOT FOUND OR loc.is_active IS DISTINCT FROM true THEN RAISE EXCEPTION 'window location stale' USING ERRCODE='P0001'; END IF;
 SELECT p.timezone INTO zone FROM public.practices p WHERE p.id=p_practice;
 IF zone IS DISTINCT FROM p_body->>'practice_timezone'
   OR NOT EXISTS(SELECT 1 FROM pg_catalog.pg_timezone_names z WHERE z.name=zone)
 THEN RAISE EXCEPTION 'window practice zone stale' USING ERRCODE='P0001'; END IF;
 -- Existing calendars have no practice column. Never infer an empty calendar
 -- through unknown RLS filtering or an unreviewed active trigger.
 IF EXISTS(SELECT 1 FROM pg_catalog.pg_class c WHERE c.oid IN ('public.practitioner_schedules'::regclass,'public.schedule_overrides'::regclass)
     AND (c.relrowsecurity OR c.relforcerowsecurity))
   OR EXISTS(SELECT 1 FROM pg_catalog.pg_trigger t WHERE t.tgrelid IN ('public.practitioner_schedules'::regclass,'public.schedule_overrides'::regclass)
     AND NOT t.tgisinternal AND t.tgenabled<>'D')
 THEN RAISE EXCEPTION 'unmapped calendar storage boundary' USING ERRCODE='42501'; END IF;
 IF EXISTS(SELECT 1 FROM public.practitioner_schedules s WHERE s.practitioner_id=pr.id)
   OR EXISTS(SELECT 1 FROM public.schedule_overrides o WHERE o.practitioner_id=pr.id)
   OR EXISTS(SELECT 1 FROM public.practitioner_first_weekly_window_commands c
     WHERE c.practice_id=p_practice AND c.practitioner_id=pr.id AND c.state='committed')
 THEN RAISE EXCEPTION 'first window requires empty calendar' USING ERRCODE='P0001'; END IF;
 RETURN pg_catalog.encode(pg_catalog.sha256(pg_catalog.convert_to(pg_catalog.jsonb_build_object(
   'practice_id',p_practice,'practice_timezone',zone,'practitioner_id',pr.id,'aggregate_version',pr.aggregate_version,
   'practitioner_create_command_id',created.id,'location_id',loc.id,'weekly_rows',0,'override_rows',0)::text,'UTF8')),'hex');
END;
"""

RECEIPT_BODY = """
BEGIN
 IF c.state<>'committed' THEN RAISE EXCEPTION 'receipt not found' USING ERRCODE='P0002'; END IF;
 RETURN pg_catalog.jsonb_build_object('schema_version','practitioner.first_weekly_window.receipt.v1',
   'command_id',c.id,'command_key',c.command_key,'practice_id',c.practice_id,'practitioner_id',c.practitioner_id,
   'location_id',c.location_id,'schedule_id',c.schedule_id,'body',c.canonical_body,'body_digest',c.body_digest,
   'context_digest',c.context_digest,'actor_account_id',c.actor_account_id,'actor_membership_id',c.actor_membership_id,
   'actor_user_id',c.actor_user_id,'role',c.role,'authority_generation',c.authority_generation,
   'audit_event_id',c.audit_event_id,'outbox_event_id',c.outbox_event_id,
   'committed_at',pg_catalog.to_char(c.committed_at AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"'));
END;
"""

DRAFT_BODY = """
BEGIN
 RETURN pg_catalog.jsonb_build_object('state','prepared','receipt',NULL,'confirmation_evidence',NULL,
   'draft',pg_catalog.jsonb_build_object('command_id',c.id,'command_key',c.command_key,
     'canonicalization_version',c.canonicalization_version,'body',c.canonical_body,'body_digest',c.body_digest,
     'context_digest',c.context_digest,'role',c.role,'authority_generation',c.authority_generation,
     'expires_at',pg_catalog.to_char(c.expires_at AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"')));
END;
"""

PREPARE_BODY = """
DECLARE b jsonb; c public.practitioner_first_weekly_window_commands%ROWTYPE; ctx text; now_at timestamptz;
BEGIN
 PERFORM weekly_window_api._authorize(p_account,p_membership,p_user,p_practice,p_role,p_generation,p_expiry);
 IF p_key IS NULL THEN RAISE EXCEPTION 'command key required' USING ERRCODE='22023'; END IF;
 b:=weekly_window_api._body(p_canonical,p_digest);
 SELECT x.* INTO c FROM public.practitioner_first_weekly_window_commands x
   WHERE x.practice_id=p_practice AND x.actor_membership_id=p_membership AND x.command_key=p_key FOR UPDATE;
 IF FOUND THEN
   IF c.actor_account_id IS DISTINCT FROM p_account OR c.actor_user_id IS DISTINCT FROM p_user
     OR c.canonical_text IS DISTINCT FROM p_canonical OR c.body_digest IS DISTINCT FROM p_digest
   THEN RAISE EXCEPTION 'command key body mismatch' USING ERRCODE='P0001'; END IF;
   IF c.state='committed' THEN RETURN pg_catalog.jsonb_build_object('state','committed','draft',NULL,
     'receipt',weekly_window_api._receipt(c),'confirmation_evidence',NULL); END IF;
   IF c.authority_generation IS DISTINCT FROM p_generation OR pg_catalog.clock_timestamp()>=c.expires_at
   THEN RAISE EXCEPTION 'prepared window expired or authority changed' USING ERRCODE='P0001'; END IF;
   ctx:=weekly_window_api._context(p_account,p_membership,p_user,p_practice,b);
   IF ctx IS DISTINCT FROM c.context_digest THEN RAISE EXCEPTION 'prepared window context stale' USING ERRCODE='P0001'; END IF;
   RETURN weekly_window_api._draft(c);
 END IF;
 ctx:=weekly_window_api._context(p_account,p_membership,p_user,p_practice,b);
 now_at:=pg_catalog.clock_timestamp();
 IF now_at>=p_expiry THEN RAISE EXCEPTION 'authority expired' USING ERRCODE='42501'; END IF;
 INSERT INTO public.practitioner_first_weekly_window_commands
   (id,practice_id,actor_account_id,actor_membership_id,actor_user_id,role,authority_generation,
    command_key,practitioner_id,location_id,canonicalization_version,canonical_text,canonical_body,
    body_digest,context_digest,prepared_at,expires_at,state)
 VALUES(pg_catalog.gen_random_uuid(),p_practice,p_account,p_membership,p_user,p_role,p_generation,
   p_key,(b->>'practitioner_id')::uuid,(b->>'location_id')::uuid,'practitioner.first_weekly_window.body.v1',
   p_canonical,b,p_digest,ctx,now_at,LEAST(p_expiry,now_at+interval '5 minutes'),'prepared') RETURNING * INTO c;
 RETURN weekly_window_api._draft(c);
END;
"""

CONFIRM_BODY = """
DECLARE c public.practitioner_first_weekly_window_commands%ROWTYPE; ctx text;
 sid uuid; aid uuid; oid uuid; now_at timestamptz;
BEGIN
 PERFORM weekly_window_api._authorize(p_account,p_membership,p_user,p_practice,p_role,p_generation,p_expiry);
 SELECT x.* INTO c FROM public.practitioner_first_weekly_window_commands x
   WHERE x.practice_id=p_practice AND x.actor_membership_id=p_membership AND x.command_key=p_key FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION 'window command not found' USING ERRCODE='P0002'; END IF;
 IF p_confirmed IS DISTINCT FROM true OR c.id IS DISTINCT FROM p_command
   OR c.actor_account_id IS DISTINCT FROM p_account OR c.actor_user_id IS DISTINCT FROM p_user
   OR c.body_digest IS DISTINCT FROM p_digest OR c.context_digest IS DISTINCT FROM p_context
   OR c.role IS DISTINCT FROM p_original_role OR c.authority_generation IS DISTINCT FROM p_original_generation
   OR c.expires_at IS DISTINCT FROM p_draft_expiry
 THEN RAISE EXCEPTION 'window confirmation mismatch' USING ERRCODE='P0001'; END IF;
 -- Fresh owner authentication is required even for historical exact replay.
 -- Original proposal expiry/generation are not renewed or silently overwritten.
 IF c.state='committed' THEN RETURN weekly_window_api._receipt(c); END IF;
 IF c.state<>'prepared' OR c.authority_generation IS DISTINCT FROM p_generation
   OR pg_catalog.clock_timestamp()>=c.expires_at
 THEN RAISE EXCEPTION 'window confirmation stale' USING ERRCODE='P0001'; END IF;
 ctx:=weekly_window_api._context(p_account,p_membership,p_user,p_practice,c.canonical_body);
 IF ctx IS DISTINCT FROM c.context_digest THEN RAISE EXCEPTION 'window context changed' USING ERRCODE='P0001'; END IF;
 now_at:=pg_catalog.clock_timestamp();
 IF now_at>=LEAST(c.expires_at,p_expiry) THEN RAISE EXCEPTION 'window confirmation expired' USING ERRCODE='P0001'; END IF;
 sid:=pg_catalog.gen_random_uuid(); aid:=pg_catalog.gen_random_uuid(); oid:=pg_catalog.gen_random_uuid();
 INSERT INTO public.practitioner_schedules(id,practitioner_id,location_id,day_of_week,start_time,end_time,slot_duration_minutes)
 VALUES(sid,c.practitioner_id,c.location_id,(c.canonical_body->>'weekday')::integer,
   (c.canonical_body->>'start_time')::time,(c.canonical_body->>'end_time')::time,
   (c.canonical_body->>'slot_duration_minutes')::integer);
 INSERT INTO public.practitioner_first_weekly_window_audit
   (id,practice_id,command_id,schedule_id,practitioner_id,location_id,actor_account_id,actor_membership_id,
    actor_user_id,event_code,body_digest,context_digest,created_at)
 VALUES(aid,p_practice,c.id,sid,c.practitioner_id,c.location_id,p_account,p_membership,p_user,
   'first_weekly_window_created',c.body_digest,c.context_digest,now_at);
 INSERT INTO public.practitioner_first_weekly_window_outbox
   (id,practice_id,command_id,audit_event_id,schedule_id,practitioner_id,location_id,actor_account_id,actor_membership_id,
    actor_user_id,correlation_id,event_type,schema_version,source_system,payload,published,created_at)
 VALUES(oid,p_practice,c.id,aid,sid,c.practitioner_id,c.location_id,p_account,p_membership,p_user,c.id,
   'practitioner.first_weekly_window_created','practitioner.first_weekly_window_created.v1','emr4-practice-administration',
   pg_catalog.jsonb_build_object('command_id',c.id,'practice_id',p_practice,'practitioner_id',c.practitioner_id,
     'schedule_id',sid,'location_id',c.location_id,'body',c.canonical_body,'body_digest',c.body_digest,'context_digest',c.context_digest),false,now_at);
 UPDATE public.practitioner_first_weekly_window_commands SET state='committed',schedule_id=sid,
   audit_event_id=aid,outbox_event_id=oid,committed_at=now_at WHERE id=c.id RETURNING * INTO c;
 RETURN weekly_window_api._receipt(c);
END;
"""

READBACK_BODY = """
DECLARE c public.practitioner_first_weekly_window_commands%ROWTYPE; s record; facts jsonb; label text;
BEGIN
 PERFORM weekly_window_api._authorize(p_account,p_membership,p_user,p_practice,p_role,p_generation,p_expiry);
 SELECT x.* INTO c FROM public.practitioner_first_weekly_window_commands x
   WHERE x.practice_id=p_practice AND x.actor_membership_id=p_membership AND x.command_key=p_key;
 IF NOT FOUND OR c.state<>'committed' OR c.actor_account_id IS DISTINCT FROM p_account OR c.actor_user_id IS DISTINCT FROM p_user
 THEN RAISE EXCEPTION 'window receipt not found' USING ERRCODE='P0002'; END IF;
 SELECT w.id,w.practitioner_id,w.location_id,w.day_of_week,w.start_time,w.end_time,w.slot_duration_minutes,
   p.timezone,r.is_active AS practitioner_active,l.is_active AS location_active INTO s
 FROM public.practitioner_schedules w JOIN public.practitioners r ON r.id=w.practitioner_id AND r.practice_id=p_practice
 JOIN public.practices p ON p.id=p_practice LEFT JOIN public.practice_locations l ON l.id=w.location_id AND l.practice_id=p_practice
 WHERE w.id=c.schedule_id;
 IF NOT FOUND THEN facts:=NULL; label:='missing';
 ELSE
   facts:=pg_catalog.jsonb_build_object('schedule_id',s.id,'practitioner_id',s.practitioner_id,'location_id',s.location_id,
     'weekday',s.day_of_week,'start_time',s.start_time::text,
     'end_time',s.end_time::text,'slot_duration_minutes',s.slot_duration_minutes,
     'practice_timezone',s.timezone,'practitioner_active',s.practitioner_active,'location_active',s.location_active);
   IF s.practitioner_id=c.practitioner_id AND s.location_id=c.location_id
     AND s.day_of_week=(c.canonical_body->>'weekday')::integer
     AND s.start_time=(c.canonical_body->>'start_time')::time AND s.end_time=(c.canonical_body->>'end_time')::time
     AND s.slot_duration_minutes=(c.canonical_body->>'slot_duration_minutes')::integer
     AND s.timezone=c.canonical_body->>'practice_timezone'
     AND s.practitioner_active IS true AND s.location_active IS true
   THEN label:='matches_created'; ELSE label:='diverged'; END IF;
 END IF;
 RETURN pg_catalog.jsonb_build_object('receipt',weekly_window_api._receipt(c),
   'readback',pg_catalog.jsonb_build_object('status',label,'expected',c.canonical_body,'current',facts));
END;
"""

TRANSITION_BODY = """
BEGIN
 IF OLD.state<>'prepared' OR NEW.state<>'committed'
   OR (pg_catalog.to_jsonb(NEW)-ARRAY['state','schedule_id','audit_event_id','outbox_event_id','committed_at']::text[])
     IS DISTINCT FROM (pg_catalog.to_jsonb(OLD)-ARRAY['state','schedule_id','audit_event_id','outbox_event_id','committed_at']::text[])
 THEN RAISE EXCEPTION 'immutable first window command' USING ERRCODE='P0001'; END IF;
 RETURN NEW;
END;
"""

CONTEXT_READ_BODY = """
DECLARE resolved record;
BEGIN
 PERFORM weekly_window_api._authorize(p_account,p_membership,p_user,p_practice,p_role,p_generation,p_expiry);
 IF p_practitioner_key IS NULL OR p_location_key IS NULL
 THEN RAISE EXCEPTION 'exact create command keys required' USING ERRCODE='22023'; END IF;
 -- One current snapshot; no caller actor, practice or resource ID is accepted.
 -- These are committed command records, not fixture/directories/defaults.
 SELECT pc.id AS practitioner_command_id,pc.command_key AS practitioner_command_key,
   r.id AS practitioner_id,lc.id AS location_command_id,lc.command_key AS location_command_key,
   l.id AS location_id,p.timezone,r.is_active AS practitioner_active,l.is_active AS location_active
 INTO resolved
 FROM public.practitioner_create_commands pc
 JOIN public.practitioners r ON r.id=pc.practitioner_id AND r.practice_id=p_practice
 JOIN public.practice_location_create_commands lc ON lc.practice_id=p_practice
   AND lc.actor_account_id=p_account AND lc.actor_membership_id=p_membership
   AND lc.actor_user_id=p_user AND lc.command_key=p_location_key AND lc.state='committed'
 JOIN public.practice_locations l ON l.id=lc.location_id AND l.practice_id=p_practice
 JOIN public.practices p ON p.id=p_practice
 WHERE pc.practice_id=p_practice AND pc.actor_account_id=p_account
   AND pc.actor_membership_id=p_membership AND pc.actor_user_id=p_user
   AND pc.command_key=p_practitioner_key AND pc.state='committed'
 FOR SHARE OF r,l;
 IF NOT FOUND THEN RAISE EXCEPTION 'owned create context not found' USING ERRCODE='P0002'; END IF;
 IF resolved.practitioner_active IS DISTINCT FROM true OR resolved.location_active IS DISTINCT FROM true
   OR resolved.timezone IS NULL
   OR NOT EXISTS(SELECT 1 FROM pg_catalog.pg_timezone_names z WHERE z.name=resolved.timezone)
 THEN RAISE EXCEPTION 'create context no longer active' USING ERRCODE='P0001'; END IF;
 IF pg_catalog.clock_timestamp()>=p_expiry
 THEN RAISE EXCEPTION 'owner context expired' USING ERRCODE='42501'; END IF;
 -- No draft, calendar, audit or outbox DML. The caller must still prepare and
 -- separately confirm; both paths retain all original full revalidation.
 RETURN pg_catalog.jsonb_build_object('schema_version','practitioner.first_weekly_window.context.v1',
   'practice_id',p_practice,'practitioner_id',resolved.practitioner_id,
   'practitioner_create_command_id',resolved.practitioner_command_id,
   'practitioner_create_command_key',resolved.practitioner_command_key,
   'location_id',resolved.location_id,'location_create_command_id',resolved.location_command_id,
   'location_create_command_key',resolved.location_command_key,'practice_timezone',resolved.timezone,
   'practitioner_active',resolved.practitioner_active,'location_active',resolved.location_active,
   'role',p_role,'authority_generation',p_generation);
END;
"""

FUNCTIONS = (
    ("_authorize", AUTH_ARGS, AUTH_TYPES, "void", AUTHORITY_BODY, False),
    ("_body", "p_canonical text,p_digest text", "text,text", "jsonb", BODY_BODY, False),
    ("_context", "p_account uuid,p_membership uuid,p_user uuid,p_practice uuid,p_body jsonb", "uuid,uuid,uuid,uuid,jsonb", "text", CONTEXT_BODY, False),
    ("_receipt", "c public.practitioner_first_weekly_window_commands", "public.practitioner_first_weekly_window_commands", "jsonb", RECEIPT_BODY, False),
    ("_draft", "c public.practitioner_first_weekly_window_commands", "public.practitioner_first_weekly_window_commands", "jsonb", DRAFT_BODY, False),
    ("_command_transition", "", "", "trigger", TRANSITION_BODY, False),
    ("read_context", AUTH_ARGS+",p_practitioner_key uuid,p_location_key uuid", AUTH_TYPES+",uuid,uuid", "jsonb", CONTEXT_READ_BODY, True),
    ("prepare_first", AUTH_ARGS+",p_key uuid,p_canonical text,p_digest text", AUTH_TYPES+",uuid,text,text", "jsonb", PREPARE_BODY, True),
    ("confirm_first", AUTH_ARGS+",p_key uuid,p_command uuid,p_digest text,p_context text,p_original_role text,p_original_generation bigint,p_draft_expiry timestamptz,p_confirmed boolean",
     AUTH_TYPES+",uuid,uuid,text,text,text,bigint,timestamptz,boolean", "jsonb", CONFIRM_BODY, True),
    ("read_first_receipt", AUTH_ARGS+",p_key uuid", AUTH_TYPES+",uuid", "jsonb", READBACK_BODY, True),
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
      FROM pg_catalog.pg_roles WHERE rolname IN ('raisa_local_weekly_window_functions','raisa_local_tenant')
      ORDER BY rolname
    """)).all()
    if [tuple(r) for r in rows] != [
        (TENANT, True, False, False, False, False, False, False),
        (OWNER, False, False, False, False, False, False, False)]:
        raise RuntimeError("weekly window restricted roles unavailable")
    if connection.execute(sa.text("""
      SELECT EXISTS (SELECT 1 FROM pg_catalog.pg_auth_members e JOIN pg_catalog.pg_roles r
        ON r.oid=e.member OR r.oid=e.roleid WHERE r.rolname IN
        ('raisa_local_weekly_window_functions','raisa_local_tenant'))
      OR pg_catalog.has_schema_privilege('raisa_local_weekly_window_functions','public','CREATE')
      OR pg_catalog.has_schema_privilege('raisa_local_tenant','public','CREATE')
    """)).scalar_one():
        raise RuntimeError("weekly window role membership/schema boundary unavailable")
    for table, sets in COLUMNS.items():
        if not final and table in NEW_TABLES:
            continue
        columns = _columns(connection, table)
        if not columns:
            raise RuntimeError("weekly window relation missing")
        if connection.execute(sa.text("""
          SELECT c.relowner=r.oid FROM pg_catalog.pg_class c
          JOIN pg_catalog.pg_roles r ON r.rolname=:role
          WHERE c.oid=pg_catalog.to_regclass(:table)
        """), {"role": OWNER, "table": "public."+table}).scalar_one():
            raise RuntimeError("weekly window function owner must not own public tables")
        for privilege, names in zip(("SELECT", "INSERT", "UPDATE"), sets):
            requested = set(names.split(",")) if names else set()
            if final and not requested.issubset(columns):
                raise RuntimeError("weekly window exact column matrix unavailable")
            for column in columns:
                actual = connection.execute(sa.text("""
                  SELECT pg_catalog.has_column_privilege(:role,:table,:column,:privilege)
                """), {"role": OWNER, "table": "public."+table,
                         "column": column, "privilege": privilege}).scalar_one()
                if actual != (final and column in requested):
                    raise RuntimeError("weekly window owner exact column ACL mismatch")
        for privilege in ("DELETE", "TRUNCATE", "REFERENCES", "TRIGGER"):
            if connection.execute(sa.text("SELECT pg_catalog.has_table_privilege(:role,:table,:privilege)"),
                {"role": OWNER, "table": "public."+table, "privilege": privilege}).scalar_one():
                raise RuntimeError("weekly window owner excess table ACL")
        # Column REFERENCES is independent of table REFERENCES.
        for column in columns:
            if connection.execute(sa.text("SELECT pg_catalog.has_column_privilege(:role,:table,:column,'REFERENCES')"),
                {"role": OWNER, "table": "public."+table, "column": column}).scalar_one():
                raise RuntimeError("weekly window owner excess column REFERENCES")


def _assert_storage_contract(connection):
    # Source-grounded baseline fields: no existing grid default, calendar
    # uniqueness or practitioner/location composite FK is invented or added.
    if connection.execute(sa.text("SHOW server_encoding")).scalar_one() != "UTF8":
        raise RuntimeError("weekly window canonical bytes require UTF8")
    expected = {
        "practitioner_schedules": [
            ("day_of_week", "integer", True), ("end_time", "time without time zone", True),
            ("id", "uuid", True), ("location_id", "uuid", False),
            ("practitioner_id", "uuid", True), ("slot_duration_minutes", "integer", False),
            ("start_time", "time without time zone", True)],
        "schedule_overrides": [
            ("date", "date", True), ("id", "uuid", True), ("is_unavailable", "boolean", False),
            ("override_end", "time without time zone", False), ("override_start", "time without time zone", False),
            ("practitioner_id", "uuid", True), ("reason", "character varying(255)", False)],
    }
    for table, fields in expected.items():
        rows = connection.execute(sa.text("""
          SELECT a.attname,pg_catalog.format_type(a.atttypid,a.atttypmod),a.attnotnull,
            a.attgenerated,a.attidentity,d.adbin IS NULL
          FROM pg_catalog.pg_attribute a LEFT JOIN pg_catalog.pg_attrdef d
            ON d.adrelid=a.attrelid AND d.adnum=a.attnum
          WHERE a.attrelid=pg_catalog.to_regclass(:table) AND a.attnum>0 AND NOT a.attisdropped
          ORDER BY a.attname
        """), {"table": "public."+table}).all()
        if [tuple(r) for r in rows] != [(*f, "", "", True) for f in fields]:
            raise RuntimeError("existing calendar physical fields/defaults changed")
        # This supported profile never changes existing calendar RLS bits.
        # False/False is a prerequisite, not a claim of tenant row isolation.
        bits = connection.execute(sa.text("""
          SELECT relrowsecurity,relforcerowsecurity FROM pg_catalog.pg_class
          WHERE oid=pg_catalog.to_regclass(:table)
        """), {"table": "public."+table}).one()
        if tuple(bits) != (False, False):
            raise RuntimeError("unmapped calendar RLS requires separate source reconciliation")
        if connection.execute(sa.text("""
          SELECT EXISTS(SELECT 1 FROM pg_catalog.pg_trigger
            WHERE tgrelid=pg_catalog.to_regclass(:table) AND NOT tgisinternal AND tgenabled<>'D')
        """), {"table": "public."+table}).scalar_one():
            raise RuntimeError("unmapped existing calendar trigger")
    for table in ("users", "practitioners", "practice_locations", "practitioner_create_commands", "practice_location_create_commands"):
        if not connection.execute(sa.text("""
          SELECT EXISTS(SELECT 1 FROM pg_catalog.pg_constraint c
            WHERE c.conrelid=pg_catalog.to_regclass(:table) AND c.contype IN ('p','u')
              AND c.convalidated AND NOT c.condeferrable
              AND (SELECT pg_catalog.array_agg(a.attname::text ORDER BY k.ord)
                FROM pg_catalog.unnest(c.conkey) WITH ORDINALITY k(num,ord)
                JOIN pg_catalog.pg_attribute a ON a.attrelid=c.conrelid AND a.attnum=k.num)
                  =ARRAY['practice_id','id']::text[])
        """), {"table": "public."+table}).scalar_one():
            raise RuntimeError("existing same-practice composite key unavailable")


def _assert_tenant_and_surface(connection):
    for table in ("practitioner_schedules", "schedule_overrides", *NEW_TABLES):
        for column in _columns(connection, table):
            privileges = ("INSERT", "UPDATE", "REFERENCES")
            if table in NEW_TABLES:
                privileges = ("SELECT", *privileges)
            for privilege in privileges:
                actual = connection.execute(sa.text(
                    "SELECT pg_catalog.has_column_privilege(:role,:table,:column,:privilege)"
                ), {"role": TENANT, "table": "public."+table,
                    "column": column, "privilege": privilege}).scalar_one()
                # Existing calendar SELECT is preserved; no direct calendar write
                # or new command-table access is admitted by this migration.
                if actual:
                    raise RuntimeError("weekly window tenant direct-write/table ACL mismatch")
        for privilege in ("DELETE", "TRUNCATE", "TRIGGER", "REFERENCES"):
            if connection.execute(sa.text("SELECT pg_catalog.has_table_privilege(:role,:table,:privilege)"),
                {"role": TENANT, "table": "public."+table, "privilege": privilege}).scalar_one():
                raise RuntimeError("weekly window tenant excess direct-table ACL")
    for table in NEW_TABLES:
        if tuple(connection.execute(sa.text("""
          SELECT relrowsecurity,relforcerowsecurity FROM pg_catalog.pg_class
          WHERE oid=pg_catalog.to_regclass(:table)
        """), {"table": "public."+table}).one()) != (True, True):
            raise RuntimeError("weekly window command RLS unavailable")
    for name, args, types, returns, body, public in FUNCTIONS:
        signature = "weekly_window_api."+name+"("+types+")"
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
            raise RuntimeError("weekly window function owner/search-path/ACL mismatch")
    row = connection.execute(sa.text("""
      SELECT r.rolname,pg_catalog.has_schema_privilege(:tenant,n.oid,'USAGE'),
        pg_catalog.has_schema_privilege(:tenant,n.oid,'CREATE'),
        EXISTS (SELECT 1 FROM pg_catalog.aclexplode(COALESCE(n.nspacl,
          pg_catalog.acldefault('n',n.nspowner))) a WHERE a.grantee=0)
      FROM pg_catalog.pg_namespace n JOIN pg_catalog.pg_roles r ON r.oid=n.nspowner
      WHERE n.nspname='weekly_window_api'
    """), {"tenant": TENANT}).one()
    if tuple(row) != (OWNER, True, False, False):
        raise RuntimeError("weekly window schema ACL mismatch")


def upgrade():
    if context.is_offline_mode() or not op.get_bind().in_transaction():
        raise RuntimeError("first weekly window migration requires an owned online transaction")
    connection = op.get_bind()
    if connection.execute(sa.text("SHOW transaction_isolation")).scalar_one() != "read committed":
        raise RuntimeError("first weekly window migration requires read committed")
    _assert_roles(connection)
    # Existing table shape and RLS bits are inspected, never silently changed.
    for table in ("practitioner_schedules", "schedule_overrides"):
        op.execute(f"LOCK TABLE public.{table} IN SHARE ROW EXCLUSIVE MODE")
    _assert_storage_contract(connection)
    op.execute("CREATE SCHEMA weekly_window_api AUTHORIZATION raisa_local_weekly_window_functions")
    op.execute("REVOKE ALL ON SCHEMA weekly_window_api FROM PUBLIC")
    op.execute("GRANT USAGE ON SCHEMA weekly_window_api TO raisa_local_tenant")
    op.execute("GRANT USAGE ON SCHEMA public TO raisa_local_weekly_window_functions")
    op.execute(SCHEMA_SQL)
    for table in NEW_TABLES:
        op.execute(f"REVOKE ALL ON public.{table} FROM PUBLIC,raisa_local_tenant")
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE public.{table} FORCE ROW LEVEL SECURITY")
    for table, sets in COLUMNS.items():
        for privilege, columns in zip(("SELECT", "INSERT", "UPDATE"), sets):
            if columns:
                op.execute(f"GRANT {privilege}({columns}) ON public.{table} TO {OWNER}")
    practice = "NULLIF(pg_catalog.current_setting('app.current_practice_id',true),'')::uuid"
    account = "NULLIF(pg_catalog.current_setting('first_weekly_window.account_id',true),'')::uuid"
    member = "NULLIF(pg_catalog.current_setting('first_weekly_window.membership_id',true),'')::uuid"
    user = "NULLIF(pg_catalog.current_setting('first_weekly_window.user_id',true),'')::uuid"
    actor = "practice_id="+practice+" AND actor_account_id="+account+" AND actor_membership_id="+member+" AND actor_user_id="+user
    predicates = {
        "accounts": "id="+account,
        "practice_memberships": "id="+member+" AND practice_id="+practice+" AND account_id="+account+" AND legacy_user_id="+user,
        "users": "id="+user+" AND practice_id="+practice,
        "practice_membership_roles": "membership_id="+member+" AND EXISTS(SELECT 1 FROM public.practice_memberships m WHERE m.id=membership_id AND m.practice_id="+practice+")",
        "practices": "id="+practice,
        "practitioners": "practice_id="+practice,
        "practice_locations": "practice_id="+practice,
        "practitioner_create_commands": actor,
        "practice_location_create_commands": actor,
        "practitioner_first_weekly_window_commands": actor,
        "practitioner_first_weekly_window_audit": actor,
        "practitioner_first_weekly_window_outbox": actor,
    }
    # Policies apply to this new role only. Existing policies/bits are preserved.
    # Calendar tables have no added policy: supported-profile RLS is off, queries
    # join/lock the exact scoped practitioner and direct tenant writes stay closed.
    for table, predicate in predicates.items():
        for privilege, columns in zip(("SELECT", "INSERT", "UPDATE"), COLUMNS[table]):
            if columns:
                if privilege == "SELECT":
                    op.execute(f"CREATE POLICY first_weekly_window_read ON public.{table} FOR SELECT TO {OWNER} USING ({predicate})")
                elif privilege == "INSERT":
                    op.execute(f"CREATE POLICY first_weekly_window_insert ON public.{table} FOR INSERT TO {OWNER} WITH CHECK ({predicate})")
                else:
                    op.execute(f"CREATE POLICY first_weekly_window_lock_or_finish ON public.{table} FOR UPDATE TO {OWNER} USING ({predicate}) WITH CHECK ({predicate})")
    for name, args, types, returns, body, public in FUNCTIONS:
        op.execute(f"CREATE FUNCTION weekly_window_api.{name}({args}) RETURNS {returns} LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $weekly$\n{body}\n$weekly$")
        signature = f"weekly_window_api.{name}({types})"
        op.execute(f"ALTER FUNCTION {signature} OWNER TO {OWNER}")
        op.execute(f"REVOKE ALL ON FUNCTION {signature} FROM PUBLIC,raisa_local_tenant")
        if public:
            op.execute(f"GRANT EXECUTE ON FUNCTION {signature} TO {TENANT}")
    op.execute("CREATE TRIGGER first_weekly_window_terminal BEFORE UPDATE ON public.practitioner_first_weekly_window_commands "
               "FOR EACH ROW EXECUTE FUNCTION weekly_window_api._command_transition()")
    _assert_roles(connection, final=True)
    _assert_tenant_and_surface(connection)
    _assert_storage_contract(connection)


def downgrade():
    raise RuntimeError("first weekly window source has no admitted destructive downgrade")
