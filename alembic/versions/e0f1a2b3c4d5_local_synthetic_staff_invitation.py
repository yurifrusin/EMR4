"""Inert local-synthetic invitation successor; no roles provisioned here.

Requires independently provisioned NOLOGIN owner in a fresh disposable cluster.
Four public API functions only; no HTTP, email ownership or production claim.
"""
from alembic import op
import sqlalchemy as sa

revision = "e0f1a2b3c4d5"
down_revision = "d9e0f1a2b3c4"
branch_labels = None
depends_on = None
OWNER = "raisa_local_invitation_functions"
AUTH = "raisa_local_account_auth"

# Role privileges are the union needed by these four static bodies. UPDATE(id)
# is required for row locks; it is never exposed as a general mutation API.
COLUMNS = {
    "accounts": ("id,is_active", "", "id"),
    "practice_memberships": ("id,account_id,practice_id,legacy_user_id,is_active,authority_generation",
        "id,account_id,practice_id,legacy_user_id,is_active,authority_generation", "id"),
    "users": ("id,practice_id,role,is_active,authority_generation",
        "id,practice_id,email,password_hash,role,practitioner_id,is_active,authority_generation", "id"),
    "practice_membership_roles": ("membership_id,role", "membership_id,role", "membership_id"),
    "local_invitation_fixture_binding": ("id,normalized_handle,account_id,practice_id,active", "", "id"),
    "local_invitation": ("id,practice_id,issuer_membership_id,fixture_binding_id,intended_account_id,role,state,requested_ttl_seconds,expires_at,issue_key,verifier_digest,accepted_membership_id,created_at",
        "id,practice_id,issuer_membership_id,fixture_binding_id,intended_account_id,role,state,requested_ttl_seconds,expires_at,issue_key,verifier_digest,accepted_membership_id,created_at", "id,state,accepted_membership_id"),
    "local_invitation_audit": ("", "id,invitation_id,practice_id,actor_account_id,event_code,created_at", ""),
}

GUARD = """
  IF session_user <> 'raisa_local_account_auth'
     OR current_user <> 'raisa_local_invitation_functions'
     OR EXISTS (SELECT 1 FROM pg_catalog.pg_roles r
         WHERE r.rolname IN ('raisa_local_account_auth','raisa_local_invitation_functions')
         AND (r.rolsuper OR r.rolbypassrls OR r.rolinherit OR r.rolcreaterole
           OR r.rolcreatedb OR r.rolreplication
           OR r.rolcanlogin <> (r.rolname='raisa_local_account_auth')))
     OR (SELECT count(*) FROM pg_catalog.pg_roles r WHERE r.rolname IN
         ('raisa_local_account_auth','raisa_local_invitation_functions')) <> 2
     OR EXISTS (SELECT 1 FROM pg_catalog.pg_auth_members e
         JOIN pg_catalog.pg_roles r ON r.oid=e.member OR r.oid=e.roleid
         WHERE r.rolname IN ('raisa_local_account_auth','raisa_local_invitation_functions'))
     OR pg_catalog.has_schema_privilege('raisa_local_invitation_functions','public','CREATE')
     OR pg_catalog.has_schema_privilege('raisa_local_account_auth','public','CREATE')
  THEN RAISE EXCEPTION 'invitation denied' USING ERRCODE='42501'; END IF;
"""

OWNER_LOCKS = """
  SELECT m.id,m.account_id,m.practice_id,m.legacy_user_id,m.is_active,m.authority_generation
    INTO member_row FROM public.practice_memberships m WHERE m.id=p_membership FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'invitation denied' USING ERRCODE='42501'; END IF;
  SELECT u.id,u.practice_id,u.role,u.is_active,u.authority_generation
    INTO user_row FROM public.users u WHERE u.id=p_user FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'invitation denied' USING ERRCODE='42501'; END IF;
  SELECT r.role INTO owner_role FROM public.practice_membership_roles r
    WHERE r.membership_id=p_membership FOR UPDATE;
  IF NOT FOUND OR p_role IS DISTINCT FROM 'PracticeOwner' OR p_generation IS NULL OR p_generation<1
     OR member_row.account_id IS DISTINCT FROM p_account OR member_row.practice_id IS DISTINCT FROM p_practice
     OR member_row.legacy_user_id IS DISTINCT FROM p_user OR member_row.is_active IS DISTINCT FROM true
     OR user_row.practice_id IS DISTINCT FROM p_practice OR user_row.is_active IS DISTINCT FROM true
     OR user_row.role::text IS DISTINCT FROM p_role OR owner_role IS DISTINCT FROM p_role
     OR member_row.authority_generation IS DISTINCT FROM p_generation
     OR user_row.authority_generation IS DISTINCT FROM p_generation
  THEN RAISE EXCEPTION 'invitation denied' USING ERRCODE='42501'; END IF;
"""

OWNER_ARGS = "p_account uuid,p_membership uuid,p_user uuid,p_practice uuid,p_role text,p_generation bigint,p_expiry timestamptz"
FUNCTIONS = (
    ("local_invitation_issue", OWNER_ARGS + ",p_fixture uuid,p_requested_role text,p_ttl integer,p_key uuid,p_digest bytea",
     "TABLE(invitation_id uuid,state text,expires_at timestamptz,created boolean)", """
DECLARE recipient uuid; hint_practice uuid; f record; member_row record; user_row record; owner_role text;
        prior public.local_invitation%ROWTYPE; instant timestamptz; fresh uuid;
BEGIN
""" + GUARD + """
  IF p_account IS NULL OR p_membership IS NULL OR p_user IS NULL OR p_practice IS NULL
     OR p_fixture IS NULL OR p_key IS NULL OR p_requested_role IS NULL
     OR p_requested_role NOT IN ('GP','Receptionist') OR p_ttl IS NULL OR p_ttl NOT BETWEEN 60 AND 3600
     OR p_digest IS NULL OR pg_catalog.octet_length(p_digest)<>32 OR p_expiry IS NULL
  THEN RAISE EXCEPTION 'invitation denied' USING ERRCODE='42501'; END IF;
  -- Untrusted hint only. Its identity is rechecked after the ordered locks.
  SELECT b.account_id,b.practice_id INTO recipient,hint_practice
    FROM public.local_invitation_fixture_binding b WHERE b.id=p_fixture;
  IF NOT FOUND THEN RAISE EXCEPTION 'invitation denied' USING ERRCODE='42501'; END IF;
  PERFORM a.id FROM public.accounts a WHERE a.id IN (p_account,recipient) ORDER BY a.id FOR UPDATE;
  IF NOT EXISTS (SELECT 1 FROM public.accounts a WHERE a.id=p_account AND a.is_active)
     OR NOT EXISTS (SELECT 1 FROM public.accounts a WHERE a.id=recipient AND a.is_active)
  THEN RAISE EXCEPTION 'invitation denied' USING ERRCODE='42501'; END IF;
""" + OWNER_LOCKS + """
  SELECT b.id,b.account_id,b.practice_id,b.active INTO f
    FROM public.local_invitation_fixture_binding b WHERE b.id=p_fixture FOR UPDATE;
  IF NOT FOUND OR f.account_id IS DISTINCT FROM recipient OR f.practice_id IS DISTINCT FROM hint_practice
     OR f.practice_id IS DISTINCT FROM p_practice OR f.active IS DISTINCT FROM true
  THEN RAISE EXCEPTION 'invitation denied' USING ERRCODE='42501'; END IF;
  SELECT i.* INTO prior FROM public.local_invitation i
    WHERE i.practice_id=p_practice AND i.issuer_membership_id=p_membership AND i.issue_key=p_key
    ORDER BY i.id FOR UPDATE;
  instant:=pg_catalog.clock_timestamp();
  IF instant>=p_expiry THEN RAISE EXCEPTION 'invitation denied' USING ERRCODE='42501'; END IF;
  IF FOUND THEN
    IF prior.fixture_binding_id IS DISTINCT FROM p_fixture OR prior.role IS DISTINCT FROM p_requested_role
       OR prior.requested_ttl_seconds IS DISTINCT FROM p_ttl OR prior.intended_account_id IS DISTINCT FROM recipient
    THEN RAISE EXCEPTION 'invitation denied' USING ERRCODE='42501'; END IF;
    RETURN QUERY SELECT prior.id,prior.state,prior.expires_at,false; RETURN;
  END IF;
  fresh:=pg_catalog.gen_random_uuid();
  INSERT INTO public.local_invitation(id,practice_id,issuer_membership_id,fixture_binding_id,
      intended_account_id,role,state,requested_ttl_seconds,expires_at,issue_key,verifier_digest,created_at)
    VALUES(fresh,p_practice,p_membership,p_fixture,recipient,p_requested_role,'pending',p_ttl,
      instant+pg_catalog.make_interval(secs=>p_ttl),p_key,p_digest,instant);
  INSERT INTO public.local_invitation_audit(id,invitation_id,practice_id,actor_account_id,event_code,created_at)
    VALUES(pg_catalog.gen_random_uuid(),fresh,p_practice,p_account,'issue',instant);
  RETURN QUERY SELECT fresh,'pending'::text,instant+pg_catalog.make_interval(secs=>p_ttl),true;
END
"""),
    ("local_invitation_accept_lock", "p_account uuid,p_expiry timestamptz,p_invitation uuid",
     "TABLE(verifier_digest bytea,expires_at timestamptz)", """
DECLARE hint public.local_invitation%ROWTYPE; i public.local_invitation%ROWTYPE; f record;
BEGIN
""" + GUARD + """
  IF p_account IS NULL OR p_invitation IS NULL OR p_expiry IS NULL
  THEN RAISE EXCEPTION 'invitation denied' USING ERRCODE='42501'; END IF;
  SELECT x.* INTO hint FROM public.local_invitation x WHERE x.id=p_invitation;
  IF NOT FOUND THEN RAISE EXCEPTION 'invitation denied' USING ERRCODE='42501'; END IF;
  PERFORM a.id FROM public.accounts a WHERE a.id=p_account AND a.is_active FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'invitation denied' USING ERRCODE='42501'; END IF;
  SELECT b.id,b.account_id,b.practice_id,b.active INTO f
    FROM public.local_invitation_fixture_binding b WHERE b.id=hint.fixture_binding_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'invitation denied' USING ERRCODE='42501'; END IF;
  SELECT x.* INTO i FROM public.local_invitation x WHERE x.id=p_invitation FOR UPDATE;
  IF NOT FOUND OR i.fixture_binding_id IS DISTINCT FROM hint.fixture_binding_id
     OR i.intended_account_id IS DISTINCT FROM hint.intended_account_id
     OR i.practice_id IS DISTINCT FROM hint.practice_id OR i.intended_account_id IS DISTINCT FROM p_account
     OR f.account_id IS DISTINCT FROM p_account OR f.practice_id IS DISTINCT FROM i.practice_id
     OR f.active IS DISTINCT FROM true OR i.state<>'pending'
     OR pg_catalog.clock_timestamp()>=p_expiry OR pg_catalog.clock_timestamp()>=i.expires_at
  THEN RAISE EXCEPTION 'invitation denied' USING ERRCODE='42501'; END IF;
  RETURN QUERY SELECT i.verifier_digest,i.expires_at;
END
"""),
    ("local_invitation_accept_finish", "p_account uuid,p_expiry timestamptz,p_invitation uuid",
     "TABLE(membership_id uuid,practice_id uuid,role text)", """
DECLARE hint public.local_invitation%ROWTYPE; i public.local_invitation%ROWTYPE; f record;
        fresh_user uuid; fresh_membership uuid; instant timestamptz;
BEGIN
""" + GUARD + """
  -- Trusted server only: the database cannot prove compare_digest occurred.
  IF p_account IS NULL OR p_invitation IS NULL OR p_expiry IS NULL
  THEN RAISE EXCEPTION 'invitation denied' USING ERRCODE='42501'; END IF;
  SELECT x.* INTO hint FROM public.local_invitation x WHERE x.id=p_invitation;
  IF NOT FOUND THEN RAISE EXCEPTION 'invitation denied' USING ERRCODE='42501'; END IF;
  PERFORM a.id FROM public.accounts a WHERE a.id=p_account AND a.is_active FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'invitation denied' USING ERRCODE='42501'; END IF;
  SELECT b.id,b.account_id,b.practice_id,b.active INTO f
    FROM public.local_invitation_fixture_binding b WHERE b.id=hint.fixture_binding_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'invitation denied' USING ERRCODE='42501'; END IF;
  SELECT x.* INTO i FROM public.local_invitation x WHERE x.id=p_invitation FOR UPDATE;
  instant:=pg_catalog.clock_timestamp();
  IF NOT FOUND OR i.fixture_binding_id IS DISTINCT FROM hint.fixture_binding_id
     OR i.intended_account_id IS DISTINCT FROM hint.intended_account_id OR i.practice_id IS DISTINCT FROM hint.practice_id
     OR i.intended_account_id IS DISTINCT FROM p_account OR f.account_id IS DISTINCT FROM p_account
     OR f.practice_id IS DISTINCT FROM i.practice_id OR f.active IS DISTINCT FROM true
     OR i.state<>'pending' OR instant>=p_expiry OR instant>=i.expires_at
  THEN RAISE EXCEPTION 'invitation denied' USING ERRCODE='42501'; END IF;
  fresh_user:=pg_catalog.gen_random_uuid(); fresh_membership:=pg_catalog.gen_random_uuid();
  INSERT INTO public.users(id,practice_id,email,password_hash,role,practitioner_id,is_active,authority_generation)
    VALUES(fresh_user,i.practice_id,'invitation-'||fresh_user::text||'@synthetic.invalid',
       '!account-only:'||fresh_user::text,i.role::public.userrole,NULL,true,1);
  INSERT INTO public.practice_memberships(id,account_id,practice_id,legacy_user_id,is_active,authority_generation)
    VALUES(fresh_membership,p_account,i.practice_id,fresh_user,true,1);
  INSERT INTO public.practice_membership_roles(membership_id,role) VALUES(fresh_membership,i.role);
  UPDATE public.local_invitation SET state='accepted',accepted_membership_id=fresh_membership WHERE id=i.id;
  INSERT INTO public.local_invitation_audit(id,invitation_id,practice_id,actor_account_id,event_code,created_at)
    VALUES(pg_catalog.gen_random_uuid(),i.id,i.practice_id,p_account,'accept',instant);
  RETURN QUERY SELECT fresh_membership,i.practice_id,i.role;
END
"""),
    ("local_invitation_revoke", OWNER_ARGS+",p_invitation uuid", "TABLE(invitation_id uuid,state text)", """
DECLARE member_row record; user_row record; owner_role text; i public.local_invitation%ROWTYPE; instant timestamptz;
BEGIN
""" + GUARD + """
  IF p_account IS NULL OR p_membership IS NULL OR p_user IS NULL OR p_practice IS NULL
     OR p_invitation IS NULL OR p_expiry IS NULL
  THEN RAISE EXCEPTION 'invitation denied' USING ERRCODE='42501'; END IF;
  PERFORM a.id FROM public.accounts a WHERE a.id=p_account AND a.is_active FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'invitation denied' USING ERRCODE='42501'; END IF;
""" + OWNER_LOCKS + """
  SELECT x.* INTO i FROM public.local_invitation x WHERE x.id=p_invitation FOR UPDATE;
  instant:=pg_catalog.clock_timestamp();
  IF NOT FOUND OR i.practice_id IS DISTINCT FROM p_practice
     OR i.issuer_membership_id IS DISTINCT FROM p_membership OR instant>=p_expiry OR i.state='accepted'
  THEN RAISE EXCEPTION 'invitation denied' USING ERRCODE='42501'; END IF;
  IF i.state='revoked' THEN RETURN QUERY SELECT i.id,i.state; RETURN; END IF;
  UPDATE public.local_invitation SET state='revoked' WHERE id=i.id;
  INSERT INTO public.local_invitation_audit(id,invitation_id,practice_id,actor_account_id,event_code,created_at)
    VALUES(pg_catalog.gen_random_uuid(),i.id,p_practice,p_account,'revoke',instant);
  RETURN QUERY SELECT i.id,'revoked'::text;
END
"""),
)


def upgrade():
    c = op.get_bind()
    if tuple(c.execute(sa.text("SELECT session_user,current_user")).one()) != (
            "raisa_local_account_migrator", "raisa_local_account_migrator"):
        raise RuntimeError("invitation migration identity denied")
    owner = c.execute(sa.text("SELECT rolcanlogin,rolsuper,rolbypassrls,rolinherit,rolcreaterole,rolcreatedb,rolreplication FROM pg_catalog.pg_roles WHERE rolname=:r"), {"r": OWNER}).one_or_none()
    if owner is None or any(owner) or c.execute(sa.text("SELECT EXISTS(SELECT 1 FROM pg_catalog.pg_auth_members m JOIN pg_catalog.pg_roles r ON r.oid=m.roleid OR r.oid=m.member WHERE r.rolname=:r)"), {"r": OWNER}).scalar_one():
        raise RuntimeError("invitation owner must be independently isolated")
    if c.execute(sa.text("SELECT pg_catalog.has_schema_privilege(:r,'public','CREATE')"), {"r": OWNER}).scalar_one():
        raise RuntimeError("invitation owner cannot create objects")
    for table in ("accounts", "practice_memberships", "users", "practice_membership_roles"):
        if c.execute(sa.text("SELECT pg_catalog.has_table_privilege(:r,:t,'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER') OR pg_catalog.has_any_column_privilege(:r,:t,'SELECT,INSERT,UPDATE,REFERENCES')"), {"r": OWNER, "t": "public."+table}).scalar_one():
            raise RuntimeError("invitation owner must start without protected grants")
        if c.execute(sa.text("SELECT pg_catalog.pg_get_userbyid(relowner)=:r FROM pg_catalog.pg_class WHERE oid=pg_catalog.to_regclass(:t)"), {"r": OWNER, "t": "public."+table}).scalar_one():
            raise RuntimeError("invitation owner cannot own protected tables")
    op.execute("""
CREATE TABLE public.local_invitation_fixture_binding (
 id uuid PRIMARY KEY, normalized_handle text NOT NULL UNIQUE,
 account_id uuid NOT NULL REFERENCES public.accounts(id),
 practice_id uuid NOT NULL REFERENCES public.practices(id), active boolean NOT NULL,
 CHECK(normalized_handle ~ '^synthetic:[a-z0-9-]{1,64}$'),
 UNIQUE(id,account_id,practice_id));
CREATE TABLE public.local_invitation (
 id uuid PRIMARY KEY, practice_id uuid NOT NULL REFERENCES public.practices(id),
 issuer_membership_id uuid NOT NULL REFERENCES public.practice_memberships(id),
 fixture_binding_id uuid NOT NULL, intended_account_id uuid NOT NULL,
 role text NOT NULL CHECK(role IN ('GP','Receptionist')),
 state text NOT NULL CHECK(state IN ('pending','accepted','revoked')),
 requested_ttl_seconds integer NOT NULL CHECK(requested_ttl_seconds BETWEEN 60 AND 3600),
 expires_at timestamptz NOT NULL, issue_key uuid NOT NULL,
 verifier_digest bytea NOT NULL CHECK(pg_catalog.octet_length(verifier_digest)=32),
 accepted_membership_id uuid REFERENCES public.practice_memberships(id), created_at timestamptz NOT NULL,
 CHECK(expires_at>created_at), CHECK((state='accepted')=(accepted_membership_id IS NOT NULL)),
 FOREIGN KEY(fixture_binding_id,intended_account_id,practice_id)
   REFERENCES public.local_invitation_fixture_binding(id,account_id,practice_id),
 UNIQUE(practice_id,issuer_membership_id,issue_key));
CREATE UNIQUE INDEX uq_local_invitation_pending_fixture ON public.local_invitation(practice_id,fixture_binding_id) WHERE state='pending';
CREATE TABLE public.local_invitation_audit (
 id uuid PRIMARY KEY, invitation_id uuid NOT NULL REFERENCES public.local_invitation(id),
 practice_id uuid NOT NULL REFERENCES public.practices(id), actor_account_id uuid NOT NULL REFERENCES public.accounts(id),
 event_code text NOT NULL CHECK(event_code IN ('issue','accept','revoke')), created_at timestamptz NOT NULL,
 UNIQUE(invitation_id,event_code));
""")
    op.execute(f"GRANT USAGE ON SCHEMA account_api,public TO {OWNER}")
    for table, (read, insert, update) in COLUMNS.items():
        op.execute(f"REVOKE ALL ON TABLE public.{table} FROM {OWNER}")
        for privilege, columns in (("SELECT", read), ("INSERT", insert), ("UPDATE", update)):
            if columns:
                op.execute(f"GRANT {privilege} ({columns}) ON public.{table} TO {OWNER}")
        if table.startswith("local_invitation"):
            op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY")
            op.execute(f"ALTER TABLE public.{table} FORCE ROW LEVEL SECURITY")
            op.execute(f"REVOKE ALL ON TABLE public.{table} FROM PUBLIC,{AUTH},raisa_local_tenant,raisa_local_account_functions")
        if table != "accounts":
            for command, columns in (("SELECT", read), ("INSERT", insert), ("UPDATE", update)):
                if columns:
                    tail = "WITH CHECK (true)" if command == "INSERT" else "USING (true)" + (" WITH CHECK (true)" if command == "UPDATE" else "")
                    op.execute(f"CREATE POLICY invitation_owner_{command.lower()} ON public.{table} FOR {command} TO {OWNER} {tail}")
    for name, args, returns, body in FUNCTIONS:
        op.execute(f"CREATE FUNCTION account_api.{name}({args}) RETURNS {returns} LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $invitation$\n{body}\n$invitation$")
        types = ",".join(arg.strip().split()[1] for arg in args.split(","))
        signature = f"account_api.{name}({types})"
        op.execute(f"REVOKE ALL ON FUNCTION {signature} FROM PUBLIC,raisa_local_tenant,raisa_local_account_functions")
        op.execute(f"ALTER FUNCTION {signature} OWNER TO {OWNER}")
        op.execute(f"GRANT EXECUTE ON FUNCTION {signature} TO {AUTH}")


def downgrade():
    raise RuntimeError("invitation records retained; separately reviewed non-destructive recovery required")
