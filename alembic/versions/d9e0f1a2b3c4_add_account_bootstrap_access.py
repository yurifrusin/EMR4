"""Restricted local-synthetic Account/bootstrap functions, never role provisioning.

Revision ID: d9e0f1a2b3c4
Revises: c8d9e0f1a2b3

Requires exact independently provisioned isolated roles and PostgreSQL >= 13.
No production role topology is inferred. All DDL/ACL changes require the same
reviewed transaction. Retained data makes downgrade intentionally fail closed.
"""
from alembic import context, op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "d9e0f1a2b3c4"
down_revision = "c8d9e0f1a2b3"
branch_labels = None
depends_on = None

AUTH = "raisa_local_account_auth"
TENANT = "raisa_local_tenant"
DEFINER = "raisa_local_account_functions"
MIGRATOR = "raisa_local_account_migrator"
TABLES = ("accounts", "practice_memberships", "practice_membership_roles", "practices", "users")
DEFINER_COLUMNS = (
    ("accounts", "id,normalized_email,password_hash,is_active", "id,normalized_email,password_hash,is_active"),
    ("practices", "id,name", "id,name,timezone"),
    ("users", "id,practice_id,is_active,authority_generation,role", "id,practice_id,email,password_hash,role,is_active,authority_generation"),
    ("practice_memberships", "id,account_id,practice_id,legacy_user_id,is_active,authority_generation", "id,account_id,practice_id,legacy_user_id,is_active,authority_generation"),
    ("practice_membership_roles", "membership_id,role", "membership_id,role"),
    ("account_bootstrap_audit", "", "id,account_id,membership_id,practice_id,event_code"),
)


def _assert_roles(connection, initial=False):
    # Fail rather than creating/changing a role or accepting a privileged pool
    # connection which merely SET ROLEs to the desired application identity.
    identity = connection.execute(sa.text("SELECT session_user, current_user")).one()
    if tuple(identity) != (MIGRATOR, MIGRATOR):
        raise RuntimeError("account access requires the exact isolated migration identity")
    rows = connection.execute(sa.text("""
        SELECT rolname, rolcanlogin, rolsuper, rolbypassrls, rolcreaterole,
               rolcreatedb, rolreplication, rolinherit
        FROM pg_catalog.pg_roles WHERE rolname IN
        ('raisa_local_account_auth', 'raisa_local_tenant', 'raisa_local_account_functions')
    """)).mappings().all()
    if len(rows) != 3:
        raise RuntimeError("account access roles must be independently provisioned")
    for row in rows:
        if (row["rolcanlogin"] != (row["rolname"] != DEFINER) or any(row[key] for key in (
            "rolsuper", "rolbypassrls", "rolcreaterole", "rolcreatedb", "rolreplication", "rolinherit",
        ))):
            raise RuntimeError("account access role flags are not isolated")
    edges = connection.execute(sa.text("""
        SELECT EXISTS (
            SELECT 1 FROM pg_catalog.pg_auth_members m
            JOIN pg_catalog.pg_roles r ON r.oid = m.roleid OR r.oid = m.member
            WHERE r.rolname IN
            ('raisa_local_account_auth', 'raisa_local_tenant', 'raisa_local_account_functions')
        )
    """)).scalar_one()
    if edges:
        raise RuntimeError("account access roles must have no membership or SET ROLE chains")
    for role in (AUTH, TENANT, DEFINER):
        if connection.execute(sa.text("SELECT pg_catalog.has_schema_privilege(:role, 'public', 'CREATE')"), {"role": role}).scalar_one():
            raise RuntimeError("account access roles cannot create public objects")
    for table in TABLES:
        owner = connection.execute(sa.text("""
            SELECT pg_catalog.pg_get_userbyid(relowner) FROM pg_catalog.pg_class
            WHERE oid = pg_catalog.to_regclass(:table)
        """), {"table": "public." + table}).scalar_one()
        if owner in (AUTH, TENANT, DEFINER):
            raise RuntimeError("runtime/definer roles cannot own protected tables")
    for table in TABLES:
        if connection.execute(sa.text("""
            SELECT pg_catalog.has_table_privilege(:role, :table,
                'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')
              OR pg_catalog.has_any_column_privilege(:role, :table, 'SELECT,INSERT,UPDATE,REFERENCES')
        """), {"role": AUTH, "table": "public." + table}).scalar_one():
            raise RuntimeError("auth caller has direct protected-table privileges")
    if connection.execute(sa.text("""
        SELECT pg_catalog.has_table_privilege(:role, 'public.accounts',
            'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')
          OR pg_catalog.has_any_column_privilege(:role, 'public.accounts', 'SELECT,INSERT,UPDATE,REFERENCES')
    """), {"role": TENANT}).scalar_one():
        raise RuntimeError("tenant caller has global account privileges")
    if initial:
        for table in TABLES:
            if connection.execute(sa.text("""
                SELECT pg_catalog.has_table_privilege(:role, :table,
                    'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')
                  OR pg_catalog.has_any_column_privilege(:role, :table, 'SELECT,INSERT,UPDATE,REFERENCES')
            """), {"role": DEFINER, "table": "public." + table}).scalar_one():
                raise RuntimeError("definer must start without protected-table grants")
    else:
        for role in (AUTH, TENANT, DEFINER):
            if connection.execute(sa.text("SELECT pg_catalog.has_schema_privilege(:role, 'account_api', 'CREATE')"), {"role": role}).scalar_one():
                raise RuntimeError("runtime/definer roles cannot create Account API objects")
        for role in (AUTH, TENANT):
            if connection.execute(sa.text("""
                SELECT pg_catalog.has_table_privilege(:role, 'public.account_bootstrap_audit',
                    'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')
                  OR pg_catalog.has_any_column_privilege(:role, 'public.account_bootstrap_audit', 'SELECT,INSERT,UPDATE,REFERENCES')
            """), {"role": role}).scalar_one():
                raise RuntimeError("runtime caller has direct global audit privileges")
        unexpected_schema_acl = connection.execute(sa.text("""
            SELECT EXISTS (
                SELECT 1 FROM pg_catalog.pg_namespace n
                CROSS JOIN LATERAL pg_catalog.aclexplode(COALESCE(n.nspacl, pg_catalog.acldefault('n', n.nspowner))) a
                WHERE n.nspname = 'account_api' AND (
                    pg_catalog.pg_get_userbyid(n.nspowner) <> 'raisa_local_account_migrator'
                    OR a.grantee = 0
                    OR pg_catalog.pg_get_userbyid(a.grantee) NOT IN
                       ('raisa_local_account_migrator','raisa_local_account_auth','raisa_local_tenant','raisa_local_account_functions')
                    OR (pg_catalog.pg_get_userbyid(a.grantee) <> 'raisa_local_account_migrator'
                        AND (a.privilege_type <> 'USAGE' OR a.is_grantable))
                )
            )
        """)).scalar_one()
        if unexpected_schema_acl:
            raise RuntimeError("private Account API schema ACL closure mismatch")


def _assert_definer_columns(connection):
    for table, read_columns, write_columns in DEFINER_COLUMNS:
        if connection.execute(sa.text("""
            SELECT pg_catalog.has_table_privilege(:role, :table,
                'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')
        """), {"role": DEFINER, "table": "public." + table}).scalar_one():
            raise RuntimeError("definer cannot have table-wide grants")
        attributes = connection.execute(sa.text("""
            SELECT attname FROM pg_catalog.pg_attribute
            WHERE attrelid = pg_catalog.to_regclass(:table) AND attnum > 0 AND NOT attisdropped
        """), {"table": "public." + table}).scalars().all()
        for column in attributes:
            for privilege, allowed in (
                ("SELECT", column in read_columns.split(",")),
                ("INSERT", column in write_columns.split(",")),
                ("UPDATE", table == "accounts" and column == "id"),
                ("REFERENCES", False),
            ):
                actual = connection.execute(sa.text("""
                    SELECT pg_catalog.has_column_privilege(:role, :table, :column, :privilege)
                """), {"role": DEFINER, "table": "public." + table, "column": column, "privilege": privilege}).scalar_one()
                if actual != allowed:
                    raise RuntimeError("definer exact column-privilege closure mismatch")


def _function(signature, returns, body):
    # All arguments below are literal migration-owned source, no user-derived
    # identifiers. Explicit pg_catalog search path, qualified relations, no SQL
    # assembled from application input, and PUBLIC receives no EXECUTE window
    # outside this transaction.
    op.execute(
        f"CREATE FUNCTION account_api.{signature} RETURNS {returns} "
        "LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $account$\n"
        + body + "\n$account$"
    )


SIGNATURES = (
    ("_assert_caller(boolean)", False, False),
    ("account_is_active(uuid)", True, True),
    ("credential_lookup(text)", True, False),
    ("eligible_memberships(uuid,uuid)", True, False),
    ("register_account(text,text)", True, False),
    ("create_first_practice(uuid,text)", True, False),
    ("record_login(uuid,boolean)", True, False),
    ("record_selection(uuid,uuid)", True, False),
    ("_reject_audit_mutation()", False, False),
)


def upgrade():
    if context.is_offline_mode():
        raise RuntimeError("account access requires an online transaction")
    connection = op.get_bind()
    if not connection.in_transaction():
        raise RuntimeError("account access requires one transaction")
    _assert_roles(connection, initial=True)
    # CREATE without IF NOT EXISTS refuses an unknown prior schema/overload.
    op.execute("CREATE SCHEMA account_api AUTHORIZATION raisa_local_account_migrator")
    op.execute("REVOKE ALL ON SCHEMA account_api FROM PUBLIC")
    op.execute("GRANT USAGE ON SCHEMA account_api TO raisa_local_account_auth, raisa_local_tenant, raisa_local_account_functions")

    op.create_table(
        "account_bootstrap_audit",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("public.accounts.id")),
        sa.Column("membership_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("public.practice_memberships.id")),
        sa.Column("practice_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("public.practices.id")),
        sa.Column("event_code", sa.String(32), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "event_code IN ('registered', 'login_allowed', 'login_denied', 'practice_created', 'membership_selected')",
            name="ck_account_bootstrap_audit_code",
        ),
        sa.CheckConstraint(
            "(event_code = 'login_denied' OR account_id IS NOT NULL) AND "
            "((event_code IN ('practice_created', 'membership_selected') AND membership_id IS NOT NULL AND practice_id IS NOT NULL) "
            "OR (event_code NOT IN ('practice_created', 'membership_selected') AND membership_id IS NULL AND practice_id IS NULL))",
            name="ck_account_bootstrap_audit_attribution",
        ), schema="public",
    )
    op.execute("REVOKE ALL ON TABLE public.account_bootstrap_audit FROM PUBLIC")
    for table, read_columns, write_columns in DEFINER_COLUMNS:
        if read_columns:
            op.execute(f"GRANT SELECT({read_columns}) ON TABLE public.{table} TO raisa_local_account_functions")
        op.execute(f"GRANT INSERT({write_columns}) ON TABLE public.{table} TO raisa_local_account_functions")
    # PostgreSQL row locks need an UPDATE privilege on at least one column;
    # no exposed API updates account identity or password state.
    op.execute("GRANT UPDATE(id) ON public.accounts TO raisa_local_account_functions")
    op.execute("GRANT SELECT ON public.practice_memberships, public.practice_membership_roles TO raisa_local_tenant")
    for table in ("practice_memberships", "practice_membership_roles"):
        op.execute(f"CREATE POLICY account_function_read ON public.{table} FOR SELECT TO raisa_local_account_functions USING (true)")
        op.execute(f"CREATE POLICY account_function_insert ON public.{table} FOR INSERT TO raisa_local_account_functions WITH CHECK (true)")
    # These policies matter if an existing/future bound source enables RLS on
    # the two legacy tables. They do not disable or relax ordinary policies.
    for table in ("users", "practices"):
        op.execute(f"CREATE POLICY account_function_read ON public.{table} FOR SELECT TO raisa_local_account_functions USING (true)")
        op.execute(f"CREATE POLICY account_function_insert ON public.{table} FOR INSERT TO raisa_local_account_functions WITH CHECK (true)")

    _function("_assert_caller(allow_tenant boolean)", "void", """
    DECLARE caller_oid oid; definer_oid oid;
    BEGIN
      IF current_user <> 'raisa_local_account_functions' OR
         NOT (session_user = 'raisa_local_account_auth' OR
              (allow_tenant AND session_user = 'raisa_local_tenant')) THEN
        RAISE EXCEPTION 'account API caller rejected' USING ERRCODE = '42501';
      END IF;
      SELECT oid INTO STRICT caller_oid FROM pg_catalog.pg_roles WHERE rolname = session_user;
      SELECT oid INTO STRICT definer_oid FROM pg_catalog.pg_roles WHERE rolname = current_user;
      IF EXISTS (SELECT 1 FROM pg_catalog.pg_roles WHERE oid IN (caller_oid, definer_oid)
         AND (rolsuper OR rolbypassrls OR rolcreaterole OR rolcreatedb OR rolreplication OR rolinherit))
         OR EXISTS (SELECT 1 FROM pg_catalog.pg_auth_members
             WHERE member IN (caller_oid, definer_oid) OR roleid IN (caller_oid, definer_oid))
         OR EXISTS (SELECT 1 FROM pg_catalog.pg_roles WHERE oid = definer_oid AND rolcanlogin)
         OR pg_catalog.has_schema_privilege(session_user, 'public', 'CREATE')
         OR pg_catalog.has_schema_privilege(session_user, 'account_api', 'CREATE')
         OR pg_catalog.has_schema_privilege(current_user, 'public', 'CREATE')
         OR pg_catalog.has_schema_privilege(current_user, 'account_api', 'CREATE')
         OR pg_catalog.has_table_privilege(session_user, 'public.accounts',
             'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')
         OR pg_catalog.has_any_column_privilege(session_user, 'public.accounts', 'SELECT,INSERT,UPDATE,REFERENCES') THEN
        RAISE EXCEPTION 'account API privilege closure rejected' USING ERRCODE = '42501';
      END IF;
    END
    """)
    _function("account_is_active(account uuid)", "boolean", """
    BEGIN
      PERFORM account_api._assert_caller(true);
      RETURN EXISTS (SELECT 1 FROM public.accounts a WHERE a.id = account AND a.is_active);
    END
    """)
    _function("credential_lookup(email_input text)", "TABLE(account_id uuid, password_hash text)", """
    BEGIN
      PERFORM account_api._assert_caller(false);
      IF pg_catalog.length(email_input) NOT BETWEEN 1 AND 255 THEN RETURN; END IF;
      RETURN QUERY SELECT a.id, a.password_hash::text FROM public.accounts a
        WHERE a.normalized_email = pg_catalog.lower(pg_catalog.btrim(email_input)) AND a.is_active;
    END
    """)
    _function("eligible_memberships(account uuid, selected uuid)", "TABLE(membership_id uuid, account_id uuid, practice_id uuid, practice_name text, legacy_user_id uuid, authority_generation bigint, role text)", """
    BEGIN
      PERFORM account_api._assert_caller(false);
      RETURN QUERY SELECT m.id, m.account_id, m.practice_id, p.name::text,
          u.id, m.authority_generation, r.role::text
        FROM public.accounts a JOIN public.practice_memberships m ON m.account_id = a.id
        JOIN public.users u ON u.id = m.legacy_user_id AND u.practice_id = m.practice_id
        JOIN public.practices p ON p.id = m.practice_id
        JOIN public.practice_membership_roles r ON r.membership_id = m.id
        WHERE a.id = account AND a.is_active AND m.is_active AND u.is_active
          AND (selected IS NULL OR m.id = selected)
          AND m.authority_generation = u.authority_generation
          AND r.role = u.role::text
          AND r.role IN ('GP', 'Receptionist', 'Nurse', 'Admin', 'PracticeOwner')
        ORDER BY m.id;
    END
    """)
    _function("register_account(email_input text, verifier text)", "uuid", """
    DECLARE new_account uuid := pg_catalog.gen_random_uuid();
    BEGIN
      PERFORM account_api._assert_caller(false);
      IF pg_catalog.length(email_input) NOT BETWEEN 1 AND 255 OR
         pg_catalog.btrim(email_input) = '' OR pg_catalog.length(verifier) NOT BETWEEN 1 AND 255 THEN
        RAISE EXCEPTION 'invalid account registration' USING ERRCODE = '23514';
      END IF;
      INSERT INTO public.accounts(id, normalized_email, password_hash, is_active)
        VALUES(new_account, pg_catalog.lower(pg_catalog.btrim(email_input)), verifier, true);
      INSERT INTO public.account_bootstrap_audit(id, account_id, event_code)
        VALUES(pg_catalog.gen_random_uuid(), new_account, 'registered');
      RETURN new_account;
    END
    """)
    _function("create_first_practice(account uuid, practice_name_input text)", "TABLE(membership_id uuid, account_id uuid, practice_id uuid, practice_name text, legacy_user_id uuid, authority_generation bigint, role text)", """
    DECLARE account_email text; account_active boolean;
      new_practice uuid := pg_catalog.gen_random_uuid();
      new_membership uuid := pg_catalog.gen_random_uuid();
      new_user uuid := pg_catalog.gen_random_uuid();
    BEGIN
      PERFORM account_api._assert_caller(false);
      SELECT a.normalized_email, a.is_active INTO account_email, account_active
        FROM public.accounts a WHERE a.id = account FOR UPDATE;
      IF NOT FOUND OR NOT account_active OR
          pg_catalog.length(pg_catalog.btrim(practice_name_input)) NOT BETWEEN 1 AND 255 OR
          EXISTS (SELECT 1 FROM public.practice_memberships m WHERE m.account_id = account) THEN
        RETURN;
      END IF;
      INSERT INTO public.practices(id, name, timezone)
        VALUES(new_practice, pg_catalog.btrim(practice_name_input), 'Australia/Sydney');
      INSERT INTO public.users(id, practice_id, email, password_hash, role, is_active, authority_generation)
        VALUES(new_user, new_practice, account_email,
          '!account-only:' || new_user::text, 'PracticeOwner', true, 1);
      INSERT INTO public.practice_memberships(id, account_id, practice_id, legacy_user_id, is_active, authority_generation)
        VALUES(new_membership, account, new_practice, new_user, true, 1);
      INSERT INTO public.practice_membership_roles(membership_id, role) VALUES(new_membership, 'PracticeOwner');
      INSERT INTO public.account_bootstrap_audit(id, account_id, membership_id, practice_id, event_code)
        VALUES(pg_catalog.gen_random_uuid(), account, new_membership, new_practice, 'practice_created');
      RETURN QUERY SELECT new_membership, account, new_practice,
        pg_catalog.btrim(practice_name_input), new_user, 1::bigint, 'PracticeOwner'::text;
    END
    """)
    _function("record_login(account uuid, allowed boolean)", "void", """
    BEGIN
      PERFORM account_api._assert_caller(false);
      IF allowed AND NOT EXISTS (SELECT 1 FROM public.accounts a WHERE a.id = account AND a.is_active) THEN
        RAISE EXCEPTION 'account is not active' USING ERRCODE = '23514';
      END IF;
      INSERT INTO public.account_bootstrap_audit(id, account_id, event_code)
        VALUES(pg_catalog.gen_random_uuid(), account, CASE WHEN allowed THEN 'login_allowed' ELSE 'login_denied' END);
    END
    """)
    _function("record_selection(account uuid, selected uuid)", "boolean", """
    BEGIN
      PERFORM account_api._assert_caller(false);
      IF NOT EXISTS (SELECT 1 FROM account_api.eligible_memberships(account, selected)) THEN RETURN false; END IF;
      INSERT INTO public.account_bootstrap_audit(id, account_id, membership_id, practice_id, event_code)
        SELECT pg_catalog.gen_random_uuid(), account, m.membership_id, m.practice_id, 'membership_selected'
        FROM account_api.eligible_memberships(account, selected) m;
      RETURN FOUND;
    END
    """)
    _function("_reject_audit_mutation()", "trigger", """
    BEGIN
      RAISE EXCEPTION 'account bootstrap audit is append-only' USING ERRCODE = '55000';
    END
    """)
    op.execute("CREATE TRIGGER account_bootstrap_audit_append_only BEFORE UPDATE OR DELETE ON public.account_bootstrap_audit FOR EACH ROW EXECUTE FUNCTION account_api._reject_audit_mutation()")
    op.execute("CREATE TRIGGER account_bootstrap_audit_no_truncate BEFORE TRUNCATE ON public.account_bootstrap_audit FOR EACH STATEMENT EXECUTE FUNCTION account_api._reject_audit_mutation()")
    for signature, auth, tenant in SIGNATURES:
        op.execute(f"REVOKE ALL ON FUNCTION account_api.{signature} FROM PUBLIC")
        op.execute(f"ALTER FUNCTION account_api.{signature} OWNER TO raisa_local_account_functions")
        if auth:
            op.execute(f"GRANT EXECUTE ON FUNCTION account_api.{signature} TO raisa_local_account_auth")
        if tenant:
            op.execute(f"GRANT EXECUTE ON FUNCTION account_api.{signature} TO raisa_local_tenant")
    _assert_roles(connection)
    _assert_definer_columns(connection)
    # Exact ACL readback includes PUBLIC and any unexpected role. No overloads
    # can preexist because this transaction created the private schema anew.
    for signature, auth, tenant in SIGNATURES:
        acl = connection.execute(sa.text("""
            SELECT pg_catalog.pg_get_userbyid(p.proowner) AS owner, a.grantee,
                   a.privilege_type, a.is_grantable
            FROM pg_catalog.pg_proc p
            CROSS JOIN LATERAL pg_catalog.aclexplode(COALESCE(p.proacl, pg_catalog.acldefault('f', p.proowner))) a
            WHERE p.oid = pg_catalog.to_regprocedure(:signature)
        """), {"signature": "account_api." + signature}).mappings().all()
        expected = {DEFINER}
        if auth:
            expected.add(AUTH)
        if tenant:
            expected.add(TENANT)
        role_names = {}
        for item in acl:
            if item["owner"] != DEFINER or item["privilege_type"] != "EXECUTE" or item["is_grantable"]:
                raise RuntimeError("account API function ownership/ACL mismatch")
            if item["grantee"] == 0:
                raise RuntimeError("account API PUBLIC execute forbidden")
            role_names[item["grantee"]] = connection.execute(sa.text("SELECT pg_catalog.pg_get_userbyid(:oid)"), {"oid": item["grantee"]}).scalar_one()
        if set(role_names.values()) != expected:
            raise RuntimeError("account API function execute closure mismatch")


def downgrade():
    raise RuntimeError("account/bootstrap evidence retained; reviewed non-destructive recovery required")
