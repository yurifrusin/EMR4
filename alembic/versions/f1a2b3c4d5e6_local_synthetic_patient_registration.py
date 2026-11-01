"""INERT local synthetic patient registration, selected36 migration closure.

One command row is both durable draft and immutable committed receipt. Patient
truth stays in public.patients. No roles, engine, application or database is
provisioned here. Activation requires a separately admitted exact successor.
"""
from alembic import context, op
import sqlalchemy as sa

revision = "f1a2b3c4d5e6"
down_revision = "e0f1a2b3c4d5"
branch_labels = None
depends_on = None
OWNER = "raisa_local_patient_functions"
TENANT = "raisa_local_tenant"
AUTH_ARGS = "p_account uuid,p_membership uuid,p_user uuid,p_practice uuid,p_role text,p_generation bigint,p_expiry timestamptz"
AUTH_TYPES = "uuid,uuid,uuid,uuid,text,bigint,timestamptz"
AUTH_CALL = "p_account,p_membership,p_user,p_practice,p_role,p_generation,p_expiry"

# Read, insert and update column sets: UPDATE(key) is only for row locking.
# No passwords, credentials, user/member insertion or general identity mutation.
COLUMNS = {
    "accounts": ("id,is_active", "", "id"),
    "practice_memberships": ("id,account_id,practice_id,legacy_user_id,is_active,authority_generation", "", "id"),
    "users": ("id,practice_id,role,is_active,authority_generation", "", "id"),
    "practice_membership_roles": ("membership_id,role", "", "membership_id"),
    "patients": ("id,practice_id,first_name,last_name,date_of_birth",
        "id,practice_id,first_name,last_name,date_of_birth,consent_facial_recognition,sms_consent,created_at,updated_at", ""),
    "patient_registration_commands": ("*", "*", "state,patient_id,audit_event_id,committed_at"),
    "patient_registration_audit": ("", "*", ""),
}

GUARD = """
  IF session_user <> 'raisa_local_tenant' OR current_user <> 'raisa_local_patient_functions'
     OR (SELECT count(*) FROM pg_catalog.pg_roles r WHERE r.rolname IN
          ('raisa_local_tenant','raisa_local_patient_functions')) <> 2
     OR EXISTS (SELECT 1 FROM pg_catalog.pg_roles r WHERE r.rolname IN
          ('raisa_local_tenant','raisa_local_patient_functions') AND
          (r.rolsuper OR r.rolbypassrls OR r.rolinherit OR r.rolcreaterole OR r.rolcreatedb
           OR r.rolreplication OR r.rolcanlogin <> (r.rolname='raisa_local_tenant')))
     OR EXISTS (SELECT 1 FROM pg_catalog.pg_auth_members e JOIN pg_catalog.pg_roles r
          ON r.oid=e.member OR r.oid=e.roleid WHERE r.rolname IN
          ('raisa_local_tenant','raisa_local_patient_functions'))
     OR pg_catalog.has_schema_privilege('raisa_local_patient_functions','public','CREATE')
     OR pg_catalog.has_schema_privilege('raisa_local_tenant','public','CREATE')
     OR pg_catalog.has_column_privilege('raisa_local_patient_functions','public.accounts','password_hash','SELECT')
     OR pg_catalog.has_column_privilege('raisa_local_patient_functions','public.users','password_hash','SELECT')
  THEN RAISE EXCEPTION 'patient authority denied' USING ERRCODE='42501'; END IF;
"""

SCHEMA_SQL = """
CREATE TABLE public.patient_registration_commands (
 id uuid PRIMARY KEY,
 practice_id uuid NOT NULL REFERENCES public.practices(id),
 actor_account_id uuid NOT NULL REFERENCES public.accounts(id),
 actor_membership_id uuid NOT NULL REFERENCES public.practice_memberships(id),
 actor_user_id uuid NOT NULL,
 role text NOT NULL CHECK (role IN ('Receptionist','PracticeOwner')),
 authority_generation bigint NOT NULL CHECK (authority_generation>=1),
 command_key uuid NOT NULL,
 registration_intent_id uuid NOT NULL,
 draft_revision bigint NOT NULL CHECK (draft_revision>=1),
 request_intent_id uuid,
 supersedes_command_id uuid,
 predecessor_revision bigint,
 started_new_intent boolean NOT NULL,
 canonicalization_version text NOT NULL CHECK (canonicalization_version='patient.registration.body.v1'),
 canonical_text text NOT NULL,
 canonical_body jsonb NOT NULL,
 body_digest text NOT NULL CHECK (body_digest ~ '^[0-9a-f]{64}$'),
 prepared_at timestamptz NOT NULL,
 expires_at timestamptz NOT NULL CHECK (expires_at>prepared_at),
 state text NOT NULL CHECK (state IN ('prepared','superseded','committed')),
 patient_id uuid,
 audit_event_id uuid,
 committed_at timestamptz,
 CONSTRAINT uq_patient_command_key UNIQUE(practice_id,actor_membership_id,command_key),
 CONSTRAINT uq_patient_intent_revision UNIQUE(practice_id,actor_membership_id,registration_intent_id,draft_revision),
 CONSTRAINT uq_patient_command_practice UNIQUE(practice_id,id),
 CONSTRAINT fk_patient_command_user FOREIGN KEY(practice_id,actor_user_id) REFERENCES public.users(practice_id,id),
 CONSTRAINT fk_patient_command_patient FOREIGN KEY(practice_id,patient_id) REFERENCES public.patients(practice_id,id),
 CONSTRAINT fk_patient_command_predecessor FOREIGN KEY(practice_id,supersedes_command_id)
   REFERENCES public.patient_registration_commands(practice_id,id),
 CONSTRAINT ck_patient_command_context CHECK (
   (started_new_intent AND draft_revision=1 AND request_intent_id IS NULL
      AND supersedes_command_id IS NULL AND predecessor_revision IS NULL)
   OR (NOT started_new_intent AND request_intent_id IS NOT NULL AND request_intent_id=registration_intent_id
      AND supersedes_command_id IS NOT NULL AND predecessor_revision IS NOT NULL AND predecessor_revision>=1
      AND draft_revision=predecessor_revision+1)),
 CONSTRAINT ck_patient_command_terminal CHECK (
   (state='committed' AND patient_id IS NOT NULL AND audit_event_id IS NOT NULL AND committed_at IS NOT NULL)
   OR (state IN ('prepared','superseded') AND patient_id IS NULL AND audit_event_id IS NULL AND committed_at IS NULL))
);
CREATE UNIQUE INDEX uq_patient_prepared_intent ON public.patient_registration_commands
 (practice_id,actor_membership_id,registration_intent_id) WHERE state='prepared';
CREATE UNIQUE INDEX uq_patient_committed_intent ON public.patient_registration_commands
 (practice_id,actor_membership_id,registration_intent_id) WHERE state='committed';
CREATE UNIQUE INDEX uq_patient_one_successor ON public.patient_registration_commands(supersedes_command_id)
 WHERE supersedes_command_id IS NOT NULL;
CREATE INDEX ix_patient_command_patient ON public.patient_registration_commands(practice_id,patient_id);
CREATE INDEX ix_patient_command_account ON public.patient_registration_commands(actor_account_id);
CREATE INDEX ix_patient_command_user ON public.patient_registration_commands(practice_id,actor_user_id);
CREATE TABLE public.patient_registration_audit (
 id uuid PRIMARY KEY,
 practice_id uuid NOT NULL REFERENCES public.practices(id),
 command_id uuid NOT NULL,
 patient_id uuid NOT NULL,
 actor_account_id uuid NOT NULL REFERENCES public.accounts(id),
 actor_membership_id uuid NOT NULL REFERENCES public.practice_memberships(id),
 actor_user_id uuid NOT NULL,
 event_code text NOT NULL CHECK (event_code='patient.registration.created'),
 body_digest text NOT NULL CHECK (body_digest ~ '^[0-9a-f]{64}$'),
 created_at timestamptz NOT NULL,
 CONSTRAINT uq_patient_creation_audit_command UNIQUE(practice_id,command_id),
 CONSTRAINT uq_patient_creation_audit_practice UNIQUE(practice_id,id),
 CONSTRAINT fk_patient_audit_command FOREIGN KEY(practice_id,command_id)
    REFERENCES public.patient_registration_commands(practice_id,id),
 CONSTRAINT fk_patient_audit_patient FOREIGN KEY(practice_id,patient_id) REFERENCES public.patients(practice_id,id),
 CONSTRAINT fk_patient_audit_user FOREIGN KEY(practice_id,actor_user_id) REFERENCES public.users(practice_id,id)
);
ALTER TABLE public.patient_registration_commands ADD CONSTRAINT fk_patient_command_audit
 FOREIGN KEY(practice_id,audit_event_id) REFERENCES public.patient_registration_audit(practice_id,id);
CREATE INDEX ix_patient_audit_patient ON public.patient_registration_audit(practice_id,patient_id);
CREATE INDEX ix_patient_audit_account ON public.patient_registration_audit(actor_account_id);
CREATE INDEX ix_patient_audit_membership ON public.patient_registration_audit(actor_membership_id);
CREATE INDEX ix_patient_audit_user ON public.patient_registration_audit(practice_id,actor_user_id);
"""

# All five public operations acquire this same authority prefix before commands.
# Claims come only from the existing verified server adapter. Compromise of that
# trusted server/DB credential remains outside this boundary, as with Account.
AUTHORITY_BODY = """
DECLARE account_row record; member_row record; user_row record; actual_role text;
BEGIN
""" + GUARD + """
  IF p_account IS NULL OR p_membership IS NULL OR p_user IS NULL OR p_practice IS NULL
     OR p_role IS NULL OR p_role NOT IN ('Receptionist','PracticeOwner')
     OR p_generation IS NULL OR p_generation<1 OR p_expiry IS NULL
     OR p_action IS NULL OR p_action NOT IN ('patient.read','patient.create')
  THEN RAISE EXCEPTION 'patient authority denied' USING ERRCODE='42501'; END IF;
  PERFORM pg_catalog.set_config('app.current_practice_id',p_practice::text,true);
  PERFORM pg_catalog.set_config('patient.account_id',p_account::text,true);
  PERFORM pg_catalog.set_config('patient.membership_id',p_membership::text,true);
  PERFORM pg_catalog.set_config('patient.user_id',p_user::text,true);
  SELECT a.id,a.is_active INTO account_row FROM public.accounts a WHERE a.id=p_account FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'patient authority denied' USING ERRCODE='42501'; END IF;
  SELECT m.id,m.account_id,m.practice_id,m.legacy_user_id,m.is_active,m.authority_generation
    INTO member_row FROM public.practice_memberships m
    WHERE m.id=p_membership AND m.practice_id=p_practice FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'patient authority denied' USING ERRCODE='42501'; END IF;
  SELECT u.id,u.practice_id,u.role,u.is_active,u.authority_generation INTO user_row
    FROM public.users u WHERE u.id=p_user AND u.practice_id=p_practice FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'patient authority denied' USING ERRCODE='42501'; END IF;
  SELECT r.role INTO actual_role FROM public.practice_membership_roles r
    WHERE r.membership_id=p_membership FOR UPDATE;
  IF NOT FOUND OR account_row.is_active IS DISTINCT FROM true
     OR member_row.account_id IS DISTINCT FROM p_account OR member_row.legacy_user_id IS DISTINCT FROM p_user
     OR member_row.practice_id IS DISTINCT FROM p_practice OR member_row.is_active IS DISTINCT FROM true
     OR user_row.practice_id IS DISTINCT FROM p_practice OR user_row.is_active IS DISTINCT FROM true
     OR user_row.role::text IS DISTINCT FROM p_role OR actual_role IS DISTINCT FROM p_role
     OR member_row.authority_generation IS DISTINCT FROM p_generation
     OR user_row.authority_generation IS DISTINCT FROM p_generation
     OR pg_catalog.clock_timestamp()>=p_expiry
  THEN RAISE EXCEPTION 'patient authority denied' USING ERRCODE='42501'; END IF;
END;
"""

RECEIPT_BODY = """
BEGIN
  IF c.state<>'committed' THEN RAISE EXCEPTION 'patient command conflict' USING ERRCODE='P0001'; END IF;
  RETURN pg_catalog.jsonb_build_object('schema_version','patient.registration.receipt.v1',
    'command_id',c.id,'command_key',c.command_key,'registration_intent_id',c.registration_intent_id,
    'draft_revision',c.draft_revision,'practice_id',c.practice_id,'patient_id',c.patient_id,
    'actor_account_id',c.actor_account_id,'actor_membership_id',c.actor_membership_id,
    'actor_user_id',c.actor_user_id,'role',c.role,'authority_generation',c.authority_generation,
    'body_digest',c.body_digest,'audit_event_id',c.audit_event_id,
    'created_at',pg_catalog.to_char(c.committed_at AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"'));
END;
"""

DRAFT_BODY = """
DECLARE matches jsonb;
BEGIN
  SELECT COALESCE(pg_catalog.jsonb_agg(x.j ORDER BY x.id),'[]'::jsonb) INTO matches FROM (
    SELECT p.id,pg_catalog.jsonb_build_object('id',p.id,'practice_id',p.practice_id,
      'first_name',p.first_name,'last_name',p.last_name,'date_of_birth',p.date_of_birth) AS j
    FROM public.patients p WHERE p.practice_id=c.practice_id
      AND pg_catalog.lower(p.first_name)=pg_catalog.lower(c.canonical_body->>'first_name')
      AND pg_catalog.lower(p.last_name)=pg_catalog.lower(c.canonical_body->>'last_name')
      AND p.date_of_birth=(c.canonical_body->>'date_of_birth')::date ORDER BY p.id LIMIT 10
  ) x;
  RETURN pg_catalog.jsonb_build_object('state','prepared','draft',pg_catalog.jsonb_build_object(
    'command_id',c.id,'command_key',c.command_key,'registration_intent_id',c.registration_intent_id,
    'draft_revision',c.draft_revision,'body',c.canonical_body,'body_digest',c.body_digest,
    'role',c.role,'authority_generation',c.authority_generation,
    'expires_at',pg_catalog.to_char(c.expires_at AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"'),
    'advisory_matches',matches,'requires_distinct_person_decision',
       pg_catalog.jsonb_array_length(matches)>0 AND NOT (c.canonical_body->>'distinct_person')::boolean));
END;
"""

SEARCH_BODY = """
DECLARE answer jsonb;
BEGIN
  PERFORM patient_api._authority(""" + AUTH_CALL + """,'patient.read');
  IF p_limit IS NULL OR p_limit NOT BETWEEN 1 AND 20 OR (p_query IS NULL AND p_dob IS NULL)
     OR (p_query IS NOT NULL AND (pg_catalog.char_length(p_query) NOT BETWEEN 2 AND 100
        OR pg_catalog.btrim(p_query)<>p_query))
     OR (p_dob IS NOT NULL AND (p_dob<date '0001-01-01' OR p_dob>(pg_catalog.clock_timestamp() AT TIME ZONE 'UTC')::date))
  THEN RAISE EXCEPTION 'patient search invalid' USING ERRCODE='22023'; END IF;
  SELECT COALESCE(pg_catalog.jsonb_agg(x.j ORDER BY x.last_name,x.first_name,x.date_of_birth,x.id),'[]'::jsonb)
    INTO answer FROM (
      SELECT p.id,p.last_name,p.first_name,p.date_of_birth,
        pg_catalog.jsonb_build_object('id',p.id,'practice_id',p.practice_id,
          'first_name',p.first_name,'last_name',p.last_name,'date_of_birth',p.date_of_birth) AS j
      FROM public.patients p WHERE p.practice_id=p_practice
        AND (p_dob IS NULL OR p.date_of_birth=p_dob)
        AND (p_query IS NULL OR pg_catalog.strpos(pg_catalog.lower(p.first_name||' '||p.last_name),pg_catalog.lower(p_query))>0)
      ORDER BY p.last_name,p.first_name,p.date_of_birth,p.id LIMIT p_limit
    ) x;
  IF pg_catalog.clock_timestamp()>=p_expiry THEN RAISE EXCEPTION 'patient authority denied' USING ERRCODE='42501'; END IF;
  RETURN answer;
END;
"""

READ_BODY = """
DECLARE answer jsonb;
BEGIN
  PERFORM patient_api._authority(""" + AUTH_CALL + """,'patient.read');
  SELECT pg_catalog.jsonb_build_object('id',p.id,'practice_id',p.practice_id,
    'first_name',p.first_name,'last_name',p.last_name,'date_of_birth',p.date_of_birth)
    INTO answer FROM public.patients p WHERE p.id=p_patient AND p.practice_id=p_practice;
  IF NOT FOUND THEN RAISE EXCEPTION 'patient not found' USING ERRCODE='P0002'; END IF;
  IF pg_catalog.clock_timestamp()>=p_expiry THEN RAISE EXCEPTION 'patient authority denied' USING ERRCODE='42501'; END IF;
  RETURN answer;
END;
"""

PREPARE_BODY = """
DECLARE prior public.patient_registration_commands%ROWTYPE; head public.patient_registration_commands%ROWTYPE;
        fresh public.patient_registration_commands%ROWTYPE; instant timestamptz; canonical text;
        fresh_intent uuid; next_revision bigint; answer jsonb; trim_chars text;
BEGIN
  PERFORM patient_api._authority(""" + AUTH_CALL + """,'patient.create');
  -- Python str.strip Unicode whitespace; ASCII controls are rejected below.
  SELECT pg_catalog.string_agg(pg_catalog.chr(n),'') INTO trim_chars FROM
    (VALUES (32),(133),(160),(5760),(8192),(8193),(8194),(8195),(8196),(8197),
      (8198),(8199),(8200),(8201),(8202),(8232),(8233),(8239),(8287),(12288)) AS ws(n);
  IF p_key IS NULL OR p_first IS NULL OR p_last IS NULL OR p_dob IS NULL OR p_distinct IS NULL
     OR p_new IS NULL OR p_canonical IS NULL OR p_digest IS NULL
     OR pg_catalog.char_length(p_first) NOT BETWEEN 1 AND 100 OR pg_catalog.char_length(p_last) NOT BETWEEN 1 AND 100
     OR pg_catalog.btrim(p_first,trim_chars)<>p_first OR pg_catalog.btrim(p_last,trim_chars)<>p_last
     OR EXISTS (SELECT 1 FROM pg_catalog.generate_series(1,pg_catalog.char_length(p_first||p_last)) n
        WHERE pg_catalog.ascii(pg_catalog.substr(p_first||p_last,n,1))<32
           OR pg_catalog.ascii(pg_catalog.substr(p_first||p_last,n,1))=127)
     OR p_dob<date '0001-01-01' OR p_dob>(pg_catalog.clock_timestamp() AT TIME ZONE 'UTC')::date
     OR (p_new AND (p_intent IS NOT NULL OR p_predecessor IS NOT NULL OR p_revision IS NOT NULL))
     OR (NOT p_new AND (p_intent IS NULL OR p_predecessor IS NULL OR p_revision IS NULL OR p_revision<1))
  THEN RAISE EXCEPTION 'patient registration invalid' USING ERRCODE='22023'; END IF;
  -- Same flat primitive/canonical JSON bytes as the pure Python contract.
  canonical:='{"canonicalization_version":"patient.registration.body.v1","date_of_birth":'
    ||pg_catalog.to_json(pg_catalog.to_char(p_dob,'YYYY-MM-DD'))::text
    ||',"distinct_person":'||CASE WHEN p_distinct THEN 'true' ELSE 'false' END
    ||',"first_name":'||pg_catalog.to_json(p_first)::text||',"last_name":'||pg_catalog.to_json(p_last)::text||'}';
  IF p_canonical IS DISTINCT FROM canonical
     OR p_digest IS DISTINCT FROM pg_catalog.encode(pg_catalog.sha256(pg_catalog.convert_to(canonical,'UTF8')),'hex')
  THEN RAISE EXCEPTION 'patient registration invalid' USING ERRCODE='22023'; END IF;
  SELECT c.* INTO prior FROM public.patient_registration_commands c
    WHERE c.practice_id=p_practice AND c.actor_membership_id=p_membership AND c.command_key=p_key FOR UPDATE;
  instant:=pg_catalog.clock_timestamp();
  IF instant>=p_expiry THEN RAISE EXCEPTION 'patient authority denied' USING ERRCODE='42501'; END IF;
  IF FOUND THEN
    IF prior.actor_account_id IS DISTINCT FROM p_account OR prior.actor_user_id IS DISTINCT FROM p_user
       OR prior.canonical_text IS DISTINCT FROM canonical OR prior.canonical_body IS DISTINCT FROM canonical::jsonb
       OR prior.body_digest IS DISTINCT FROM p_digest OR prior.started_new_intent IS DISTINCT FROM p_new
       OR prior.request_intent_id IS DISTINCT FROM p_intent OR prior.supersedes_command_id IS DISTINCT FROM p_predecessor
       OR prior.predecessor_revision IS DISTINCT FROM p_revision
    THEN RAISE EXCEPTION 'patient command conflict' USING ERRCODE='P0001'; END IF;
    IF prior.state='committed' THEN
      RETURN pg_catalog.jsonb_build_object('state','committed','receipt',patient_api._receipt(prior));
    END IF;
    IF prior.state<>'prepared' OR prior.role IS DISTINCT FROM p_role
       OR prior.authority_generation IS DISTINCT FROM p_generation OR instant>=prior.expires_at
    THEN RAISE EXCEPTION 'patient command conflict' USING ERRCODE='P0001'; END IF;
    answer:=patient_api._draft(prior);
    IF pg_catalog.clock_timestamp()>=p_expiry THEN RAISE EXCEPTION 'patient authority denied' USING ERRCODE='42501'; END IF;
    RETURN answer;
  END IF;
  IF p_new THEN
    fresh_intent:=pg_catalog.gen_random_uuid(); next_revision:=1;
  ELSE
    SELECT c.* INTO head FROM public.patient_registration_commands c
      WHERE c.practice_id=p_practice AND c.actor_membership_id=p_membership AND c.registration_intent_id=p_intent
      ORDER BY c.draft_revision DESC LIMIT 1 FOR UPDATE;
    instant:=pg_catalog.clock_timestamp();
    IF instant>=p_expiry THEN RAISE EXCEPTION 'patient authority denied' USING ERRCODE='42501'; END IF;
    IF NOT FOUND OR head.actor_account_id IS DISTINCT FROM p_account OR head.actor_user_id IS DISTINCT FROM p_user
       OR head.state<>'prepared' OR head.id IS DISTINCT FROM p_predecessor OR head.draft_revision IS DISTINCT FROM p_revision
       OR EXISTS (SELECT 1 FROM public.patient_registration_commands c WHERE c.practice_id=p_practice
          AND c.actor_membership_id=p_membership AND c.registration_intent_id=p_intent AND c.state='committed')
    THEN RAISE EXCEPTION 'patient command conflict' USING ERRCODE='P0001'; END IF;
    -- A correction may replace an expired draft; the old capability never revives.
    UPDATE public.patient_registration_commands SET state='superseded' WHERE id=head.id AND practice_id=p_practice;
    fresh_intent:=p_intent; next_revision:=head.draft_revision+1;
  END IF;
  instant:=pg_catalog.clock_timestamp();
  IF instant>=p_expiry THEN RAISE EXCEPTION 'patient authority denied' USING ERRCODE='42501'; END IF;
  INSERT INTO public.patient_registration_commands(id,practice_id,actor_account_id,actor_membership_id,actor_user_id,
    role,authority_generation,command_key,registration_intent_id,draft_revision,request_intent_id,
    supersedes_command_id,predecessor_revision,started_new_intent,canonicalization_version,canonical_text,canonical_body,
    body_digest,prepared_at,expires_at,state,patient_id,audit_event_id,committed_at)
    VALUES(pg_catalog.gen_random_uuid(),p_practice,p_account,p_membership,p_user,p_role,p_generation,p_key,
      fresh_intent,next_revision,p_intent,p_predecessor,p_revision,p_new,'patient.registration.body.v1',canonical,canonical::jsonb,
      p_digest,instant,instant+interval '300 seconds','prepared',NULL,NULL,NULL)
    ON CONFLICT (practice_id,actor_membership_id,command_key) DO NOTHING RETURNING * INTO fresh;
  IF NOT FOUND THEN RAISE EXCEPTION 'patient command conflict' USING ERRCODE='P0001'; END IF;
  answer:=patient_api._draft(fresh);
  IF pg_catalog.clock_timestamp()>=p_expiry THEN RAISE EXCEPTION 'patient authority denied' USING ERRCODE='42501'; END IF;
  RETURN answer;
END;
"""

CONFIRM_BODY = """
DECLARE c public.patient_registration_commands%ROWTYPE; instant timestamptz; fresh_patient uuid; fresh_audit uuid;
BEGIN
  PERFORM patient_api._authority(""" + AUTH_CALL + """,'patient.create');
  SELECT x.* INTO c FROM public.patient_registration_commands x
    WHERE x.practice_id=p_practice AND x.actor_membership_id=p_membership AND x.command_key=p_key FOR UPDATE;
  instant:=pg_catalog.clock_timestamp();
  IF instant>=p_expiry THEN RAISE EXCEPTION 'patient authority denied' USING ERRCODE='42501'; END IF;
  IF NOT FOUND OR c.actor_account_id IS DISTINCT FROM p_account OR c.actor_user_id IS DISTINCT FROM p_user
     OR c.id IS DISTINCT FROM p_command OR c.registration_intent_id IS DISTINCT FROM p_intent
     OR c.draft_revision IS DISTINCT FROM p_revision OR c.body_digest IS DISTINCT FROM p_digest
     OR c.role IS DISTINCT FROM p_original_role OR c.authority_generation IS DISTINCT FROM p_original_generation
     OR c.expires_at IS DISTINCT FROM p_draft_expiry OR p_confirmed IS DISTINCT FROM true
  THEN RAISE EXCEPTION 'patient command conflict' USING ERRCODE='P0001'; END IF;
  -- A committed replay is immutable and needs fresh authority, not a live draft.
  IF c.state='committed' THEN RETURN patient_api._receipt(c); END IF;
  IF c.state<>'prepared' OR c.role IS DISTINCT FROM p_role OR c.authority_generation IS DISTINCT FROM p_generation
     OR instant>=c.expires_at
     OR EXISTS (SELECT 1 FROM public.patient_registration_commands x WHERE x.practice_id=p_practice
        AND x.actor_membership_id=p_membership AND x.registration_intent_id=c.registration_intent_id
        AND (x.draft_revision>c.draft_revision OR x.state='committed'))
  THEN RAISE EXCEPTION 'patient command conflict' USING ERRCODE='P0001'; END IF;
  IF NOT (c.canonical_body->>'distinct_person')::boolean AND EXISTS (
      SELECT 1 FROM public.patients p WHERE p.practice_id=p_practice
        AND pg_catalog.lower(p.first_name)=pg_catalog.lower(c.canonical_body->>'first_name')
        AND pg_catalog.lower(p.last_name)=pg_catalog.lower(c.canonical_body->>'last_name')
        AND p.date_of_birth=(c.canonical_body->>'date_of_birth')::date)
  THEN RAISE EXCEPTION 'patient command conflict' USING ERRCODE='P0001'; END IF;
  fresh_patient:=pg_catalog.gen_random_uuid(); fresh_audit:=pg_catalog.gen_random_uuid();
  INSERT INTO public.patients(id,practice_id,first_name,last_name,date_of_birth,
      consent_facial_recognition,sms_consent,created_at,updated_at)
    VALUES(fresh_patient,p_practice,c.canonical_body->>'first_name',c.canonical_body->>'last_name',
      (c.canonical_body->>'date_of_birth')::date,false,false,instant,instant);
  INSERT INTO public.patient_registration_audit(id,practice_id,command_id,patient_id,
      actor_account_id,actor_membership_id,actor_user_id,event_code,body_digest,created_at)
    VALUES(fresh_audit,p_practice,c.id,fresh_patient,p_account,p_membership,p_user,
      'patient.registration.created',c.body_digest,instant);
  UPDATE public.patient_registration_commands SET state='committed',patient_id=fresh_patient,
    audit_event_id=fresh_audit,committed_at=instant WHERE id=c.id AND practice_id=p_practice RETURNING * INTO c;
  -- Includes waits on writes/FKs/triggers; an expired token/draft rolls back all.
  instant:=pg_catalog.clock_timestamp();
  IF instant>=p_expiry THEN RAISE EXCEPTION 'patient authority denied' USING ERRCODE='42501'; END IF;
  IF instant>=c.expires_at THEN RAISE EXCEPTION 'patient command conflict' USING ERRCODE='P0001'; END IF;
  RETURN patient_api._receipt(c);
END;
"""

RECEIPT_READ_BODY = """
DECLARE c public.patient_registration_commands%ROWTYPE;
BEGIN
  PERFORM patient_api._authority(""" + AUTH_CALL + """,'patient.read');
  SELECT x.* INTO c FROM public.patient_registration_commands x WHERE x.practice_id=p_practice
    AND x.actor_membership_id=p_membership AND x.command_key=p_key AND x.state='committed';
  IF NOT FOUND OR c.actor_account_id IS DISTINCT FROM p_account OR c.actor_user_id IS DISTINCT FROM p_user
  THEN RAISE EXCEPTION 'patient not found' USING ERRCODE='P0002'; END IF;
  IF pg_catalog.clock_timestamp()>=p_expiry THEN RAISE EXCEPTION 'patient authority denied' USING ERRCODE='42501'; END IF;
  RETURN patient_api._receipt(c);
END;
"""

FUNCTIONS = (
    ("_authority", AUTH_ARGS+",p_action text", AUTH_TYPES+",text", "void", AUTHORITY_BODY, False),
    ("_receipt", "c public.patient_registration_commands", "public.patient_registration_commands", "jsonb", RECEIPT_BODY, False),
    ("_draft", "c public.patient_registration_commands", "public.patient_registration_commands", "jsonb", DRAFT_BODY, False),
    ("patient_search", AUTH_ARGS+",p_query text,p_dob date,p_limit integer", AUTH_TYPES+",text,date,integer", "jsonb", SEARCH_BODY, True),
    ("patient_read", AUTH_ARGS+",p_patient uuid", AUTH_TYPES+",uuid", "jsonb", READ_BODY, True),
    ("registration_prepare", AUTH_ARGS+",p_key uuid,p_first text,p_last text,p_dob date,p_distinct boolean,p_canonical text,p_digest text,p_new boolean,p_intent uuid,p_predecessor uuid,p_revision bigint",
        AUTH_TYPES+",uuid,text,text,date,boolean,text,text,boolean,uuid,uuid,bigint", "jsonb", PREPARE_BODY, True),
    ("registration_confirm", AUTH_ARGS+",p_key uuid,p_command uuid,p_intent uuid,p_revision bigint,p_digest text,p_original_role text,p_original_generation bigint,p_draft_expiry timestamptz,p_confirmed boolean",
        AUTH_TYPES+",uuid,uuid,uuid,bigint,text,text,bigint,timestamptz,boolean", "jsonb", CONFIRM_BODY, True),
    ("registration_receipt", AUTH_ARGS+",p_key uuid", AUTH_TYPES+",uuid", "jsonb", RECEIPT_READ_BODY, True),
)


def _assert_roles(connection, *, final=False):
    rows = connection.execute(sa.text("""
      SELECT rolname,rolcanlogin,rolsuper,rolbypassrls,rolinherit,rolcreaterole,rolcreatedb,rolreplication
      FROM pg_catalog.pg_roles WHERE rolname IN ('raisa_local_patient_functions','raisa_local_tenant')
      ORDER BY rolname
    """)).all()
    if [tuple(r) for r in rows] != [
        (OWNER, False, False, False, False, False, False, False),
        (TENANT, True, False, False, False, False, False, False)]:
        raise RuntimeError("patient restricted roles unavailable")
    if connection.execute(sa.text("""
      SELECT EXISTS (SELECT 1 FROM pg_catalog.pg_auth_members e JOIN pg_catalog.pg_roles r
        ON r.oid=e.member OR r.oid=e.roleid WHERE r.rolname IN
        ('raisa_local_patient_functions','raisa_local_tenant'))
      OR pg_catalog.has_schema_privilege('raisa_local_patient_functions','public','CREATE')
      OR pg_catalog.has_schema_privilege('raisa_local_tenant','public','CREATE')
    """)).scalar_one():
        raise RuntimeError("patient role ownership boundary unavailable")
    # Fail on inherited/PUBLIC/column grants outside the exact owner matrix.
    for table, sets in COLUMNS.items():
        if not final and table.startswith("patient_registration_"):
            continue
        columns = connection.execute(sa.text("""
          SELECT a.attname FROM pg_catalog.pg_attribute a
          WHERE a.attrelid=pg_catalog.to_regclass(:table) AND a.attnum>0 AND NOT a.attisdropped
        """), {"table": "public."+table}).scalars().all()
        if not columns:
            raise RuntimeError("patient relation missing")
        for column in columns:
            for privilege, names in zip(("SELECT", "INSERT", "UPDATE"), sets):
                allowed = final and (names == "*" or column in names.split(","))
                actual = connection.execute(sa.text("""
                  SELECT pg_catalog.has_column_privilege(:role,:table,:column,:privilege)
                """), {"role":OWNER,"table":"public."+table,"column":column,"privilege":privilege}).scalar_one()
                if actual != allowed:
                    raise RuntimeError("patient owner exact column ACL mismatch")
        for privilege in ("DELETE", "TRUNCATE", "REFERENCES", "TRIGGER"):
            if connection.execute(sa.text("SELECT pg_catalog.has_table_privilege(:role,:table,:privilege)"),
                {"role":OWNER,"table":"public."+table,"privilege":privilege}).scalar_one():
                raise RuntimeError("patient owner excess table ACL")


def upgrade():
    if context.is_offline_mode() or not op.get_bind().in_transaction():
        raise RuntimeError("patient migration requires an owned online transaction")
    connection = op.get_bind()
    _assert_roles(connection)
    op.execute("CREATE SCHEMA patient_api AUTHORIZATION raisa_local_patient_functions")
    op.execute("REVOKE ALL ON SCHEMA patient_api FROM PUBLIC")
    op.execute("GRANT USAGE ON SCHEMA patient_api TO raisa_local_tenant")
    op.execute(SCHEMA_SQL)
    # Existing Patient identity/FKs/default contract remains the single store.
    op.execute("ALTER TABLE public.patients ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE public.patients FORCE ROW LEVEL SECURITY")
    op.execute("REVOKE INSERT,UPDATE,DELETE ON public.patients FROM raisa_local_tenant,PUBLIC")
    for table in ("patient_registration_commands", "patient_registration_audit"):
        op.execute(f"REVOKE ALL ON public.{table} FROM PUBLIC,raisa_local_tenant")
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE public.{table} FORCE ROW LEVEL SECURITY")
    for table, sets in COLUMNS.items():
        for privilege, columns in zip(("SELECT", "INSERT", "UPDATE"), sets):
            if columns:
                target = privilege if columns == "*" else privilege+"("+columns+")"
                op.execute(f"GRANT {target} ON public.{table} TO {OWNER}")
    practice = "practice_id=NULLIF(pg_catalog.current_setting('app.current_practice_id',true),'')::uuid"
    selected_member = "NULLIF(pg_catalog.current_setting('patient.membership_id',true),'')::uuid"
    selected_user = "NULLIF(pg_catalog.current_setting('patient.user_id',true),'')::uuid"
    selected_account = "NULLIF(pg_catalog.current_setting('patient.account_id',true),'')::uuid"
    predicates = {
        "practice_memberships": practice+" AND id="+selected_member+" AND account_id="+selected_account+" AND legacy_user_id="+selected_user,
        "users": practice+" AND id="+selected_user,
        "practice_membership_roles": "membership_id="+selected_member+" AND EXISTS (SELECT 1 FROM public.practice_memberships m WHERE m.id=membership_id AND m.practice_id=NULLIF(pg_catalog.current_setting('app.current_practice_id',true),'')::uuid)",
        "patients": practice,
        "patient_registration_commands": practice+" AND actor_membership_id="+selected_member+" AND actor_account_id="+selected_account+" AND actor_user_id="+selected_user,
        "patient_registration_audit": practice+" AND actor_membership_id="+selected_member+" AND actor_account_id="+selected_account+" AND actor_user_id="+selected_user,
    }
    for table, predicate in predicates.items():
        read, insert, update = COLUMNS[table]
        if read:
            op.execute(f"CREATE POLICY patient_function_read ON public.{table} FOR SELECT TO {OWNER} USING ({predicate})")
        if insert:
            op.execute(f"CREATE POLICY patient_function_insert ON public.{table} FOR INSERT TO {OWNER} WITH CHECK ({predicate})")
        if update:
            op.execute(f"CREATE POLICY patient_function_lock_or_finish ON public.{table} FOR UPDATE TO {OWNER} USING ({predicate}) WITH CHECK ({predicate})")
    for name, args, types, returns, body, public in FUNCTIONS:
        op.execute(f"CREATE FUNCTION patient_api.{name}({args}) RETURNS {returns} LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $patient$\n{body}\n$patient$")
        signature = f"patient_api.{name}({types})"
        op.execute(f"ALTER FUNCTION {signature} OWNER TO {OWNER}")
        op.execute(f"REVOKE ALL ON FUNCTION {signature} FROM PUBLIC,raisa_local_tenant")
        if public:
            op.execute(f"GRANT EXECUTE ON FUNCTION {signature} TO {TENANT}")
    _assert_roles(connection, final=True)
    for table in ("patients", "patient_registration_commands", "patient_registration_audit"):
        for column in connection.execute(sa.text("SELECT attname FROM pg_catalog.pg_attribute WHERE attrelid=pg_catalog.to_regclass(:table) AND attnum>0 AND NOT attisdropped"), {"table":"public."+table}).scalars():
            for privilege in ("INSERT", "UPDATE", "DELETE"):
                if privilege == "DELETE":
                    allowed = connection.execute(sa.text("SELECT pg_catalog.has_table_privilege(:role,:table,'DELETE')"), {"role":TENANT,"table":"public."+table}).scalar_one()
                else:
                    allowed = connection.execute(sa.text("SELECT pg_catalog.has_column_privilege(:role,:table,:column,:privilege)"), {"role":TENANT,"table":"public."+table,"column":column,"privilege":privilege}).scalar_one()
                if allowed:
                    raise RuntimeError("patient application role must use functions only")


def downgrade():
    # No implicit destructive reverse migration for patient/audit truth.
    raise RuntimeError("patient source has no admitted destructive downgrade")
