"""Independent B32 SQL acceptance; source-only until separately admitted.

One pytest node owns the ordered migration lifecycle in one disposable database.
The caller supplies the existing tenant_runtime fixture and the real migration
callback bound by RelationshipMigrationPlugin in the companion adapter.
"""
from __future__ import annotations

from contextlib import contextmanager
import json

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DBAPIError

from tenant_relationship_helpers import (
    DATA_TABLES, EDGES, UPDATE_EDGES, World, insert, update_reference,
    snapshot, seed_dedicated_parent, move_parent,
)

BASELINE = "z5a6b7c8d9e0"
CANDIDATE = "a6b7c8d9e0f1"
UNIQUE_KEYS = {
    "appointment_types": "uq_appointment_types_practice_id_id",
    "encounters": "uq_encounters_practice_id_id",
    "patients": "uq_patients_practice_id_id",
    "practice_locations": "uq_practice_locations_practice_id_id",
    "practitioners": "uq_practitioners_practice_id_id",
    "waiting_areas": "uq_waiting_areas_practice_id_id",
}
CHILDREN = tuple(sorted({e.child for e in EDGES}))
META_TABLES = tuple(sorted(set(DATA_TABLES) | {"users", "access_ai_audit_log"}))
UPDATE_COLUMNS = {e.column for e in UPDATE_EDGES}


def require(condition, label):
    if not condition:
        pytest.fail(label, pytrace=False)


def _rows(conn, sql, params=None):
    return [dict(row) for row in conn.execute(text(sql), params or {}).mappings()]


def _revision(conn):
    return conn.execute(text("SELECT version_num FROM public.alembic_version")).scalars().all()


def _catalogue(conn):
    """Semantic metadata for an exact ordinary table set; no object OIDs."""
    params = {"tables": list(META_TABLES)}
    return {
        "tables": _rows(conn, """
            SELECT c.relname AS table_name, c.relkind, pg_get_userbyid(c.relowner) AS owner,
                   c.relrowsecurity, c.relforcerowsecurity, c.relacl::text AS grants
            FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
            WHERE n.nspname='public' AND c.relname=ANY(:tables)
            ORDER BY c.relname
        """, params),
        "columns": _rows(conn, """
            SELECT c.relname AS table_name,a.attname AS column_name,a.attnum,
                   format_type(a.atttypid,a.atttypmod) AS type,a.attnotnull,
                   a.attidentity,a.attgenerated,pg_get_expr(d.adbin,d.adrelid) AS default_expr,
                   co.collname AS collation,a.attacl::text AS grants
            FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
            JOIN pg_attribute a ON a.attrelid=c.oid AND a.attnum>0 AND NOT a.attisdropped
            LEFT JOIN pg_attrdef d ON d.adrelid=c.oid AND d.adnum=a.attnum
            LEFT JOIN pg_collation co ON co.oid=a.attcollation
            WHERE n.nspname='public' AND c.relname=ANY(:tables)
            ORDER BY c.relname,a.attnum
        """, params),
        "constraints": _rows(conn, """
            SELECT c.relname AS table_name,k.conname,k.contype,k.convalidated,
                   k.condeferrable,k.condeferred,k.confupdtype,k.confdeltype,k.confmatchtype,
                   pn.nspname AS parent_schema,p.relname AS parent_table,
                   ARRAY(SELECT a.attname FROM unnest(k.conkey) WITH ORDINALITY x(num,ord)
                         JOIN pg_attribute a ON a.attrelid=c.oid AND a.attnum=x.num
                         ORDER BY x.ord) AS columns,
                   ARRAY(SELECT a.attname FROM unnest(k.confkey) WITH ORDINALITY x(num,ord)
                         JOIN pg_attribute a ON a.attrelid=p.oid AND a.attnum=x.num
                         ORDER BY x.ord) AS parent_columns,
                   pg_get_constraintdef(k.oid,true) AS definition
            FROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid
            JOIN pg_namespace n ON n.oid=c.relnamespace
            LEFT JOIN pg_class p ON p.oid=k.confrelid
            LEFT JOIN pg_namespace pn ON pn.oid=p.relnamespace
            WHERE n.nspname='public' AND c.relname=ANY(:tables)
            ORDER BY c.relname,k.conname
        """, params),
        "indexes": _rows(conn, """
            SELECT c.relname AS table_name,ic.relname AS index_name,
                   pg_get_indexdef(i.indexrelid) AS definition,i.indisunique,
                   i.indisprimary,i.indisvalid,i.indisready,k.conname AS constraint_name
            FROM pg_index i JOIN pg_class c ON c.oid=i.indrelid
            JOIN pg_namespace n ON n.oid=c.relnamespace
            JOIN pg_class ic ON ic.oid=i.indexrelid
            LEFT JOIN pg_constraint k ON k.conindid=i.indexrelid AND k.contype IN ('p','u','x')
            WHERE n.nspname='public' AND c.relname=ANY(:tables)
            ORDER BY c.relname,ic.relname
        """, params),
        "policies": _rows(conn, """
            SELECT tablename AS table_name,policyname,permissive,roles,cmd,qual,with_check
            FROM pg_policies WHERE schemaname='public' AND tablename=ANY(:tables)
            ORDER BY tablename,policyname
        """, params),
        "triggers": _rows(conn, """
            SELECT c.relname AS table_name,t.tgisinternal,t.tgenabled,t.tgtype,
                   k.conname AS constraint_name,p.proname AS function_name,
                   pn.nspname AS function_schema,
                   CASE WHEN t.tgisinternal THEN NULL ELSE t.tgname END AS trigger_name,
                   CASE WHEN t.tgisinternal THEN NULL ELSE pg_get_triggerdef(t.oid,true) END AS definition
            FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid
            JOIN pg_namespace n ON n.oid=c.relnamespace
            JOIN pg_proc p ON p.oid=t.tgfoid JOIN pg_namespace pn ON pn.oid=p.pronamespace
            LEFT JOIN pg_constraint k ON k.oid=t.tgconstraint
            WHERE n.nspname='public' AND c.relname=ANY(:tables)
            ORDER BY c.relname,k.conname NULLS FIRST,p.proname,t.tgtype,t.tgname
        """, params),
    }


def _observe(runtime):
    with runtime["observer_engine"].connect() as conn:
        return snapshot(conn), _catalogue(conn), _revision(conn)


def _context(conn, runtime, role, practice=None):
    row = conn.execute(text("""
        SELECT current_database(),session_user,current_user,current_setting('row_security'),
               current_setting('app.current_practice_id',true),
               (SELECT setting::integer FROM pg_settings WHERE name='statement_timeout'),
               (SELECT setting::integer FROM pg_settings WHERE name='lock_timeout')
    """)).one()
    require(tuple(row[:4]) == (runtime["database_name"],role,role,"on"), "actual database/login/RLS context")
    require(row[4] == str(practice) if practice is not None else row[4] in (None,""), "transaction tenant context")
    require(tuple(row[5:]) == (runtime["statement_timeout_ms"],runtime["lock_timeout_ms"]), "actual SQL budgets")


def _runtime_contract(runtime, migration):
    keys = ("engine", "command_engine", "observer_engine", "admin_engine")
    require(all(isinstance(runtime[k], Engine) for k in keys), "four real engines")
    require(len({id(runtime[k]) for k in keys}) == 4, "distinct engine objects")
    endpoints = {(runtime[k].url.host,runtime[k].url.port,runtime[k].url.database) for k in keys}
    require(len(endpoints)==1 and next(iter(endpoints))[0] in {"127.0.0.1","::1"}, "one loopback database")
    require(runtime["expected_revision"] == BASELINE, "adapter baseline revision")
    roles = {k:runtime[k].url.username for k in ("engine","observer_engine","admin_engine")}
    require(len(set(roles.values()))==3 and roles["engine"]==runtime["application_role"], "separate actual logins")
    require(set(migration)=={"baseline_revision","successor_revision","migrate"} and migration["baseline_revision"]==BASELINE and migration["successor_revision"]==CANDIDATE and callable(migration["migrate"]), "pinned real migration callback")
    with runtime["observer_engine"].connect() as conn:
        require(_revision(conn)==[BASELINE], "31-migration baseline required")
        _context(conn,runtime,roles["observer_engine"])
        observed = _rows(conn,"""
            SELECT rolname,rolsuper,rolbypassrls,rolcreaterole,rolcreatedb,rolreplication,rolcanlogin
            FROM pg_roles WHERE rolname=ANY(:roles) ORDER BY rolname
        """, {"roles": list(roles.values())})
        require(len(observed)==3, "three role records")
        app = next(r for r in observed if r["rolname"]==roles["engine"])
        require(app["rolcanlogin"] and not any(app[k] for k in ("rolsuper","rolbypassrls","rolcreaterole","rolcreatedb","rolreplication")), "restricted application role")
        observer = next(r for r in observed if r["rolname"]==roles["observer_engine"])
        require(observer["rolcanlogin"] and observer["rolbypassrls"] and not any(observer[k] for k in ("rolsuper","rolcreaterole","rolcreatedb","rolreplication")), "read-only observer role")
        for role in (roles["engine"],roles["observer_engine"]):
            require(conn.execute(text("SELECT NOT EXISTS(SELECT 1 FROM pg_auth_members WHERE member=(SELECT oid FROM pg_roles WHERE rolname=:role))"),{"role":role}).scalar_one(), "no role memberships")
            require(not conn.execute(text("SELECT has_schema_privilege(:role,'public','CREATE')"),{"role":role}).scalar_one(), "no schema creation privilege")
        cat = _catalogue(conn)
        require({r["table_name"] for r in cat["tables"]}==set(META_TABLES), "complete named catalogue")
        for row in cat["tables"]:
            require(row["owner"] not in (roles["engine"],roles["observer_engine"]), "roles are not table owners")
            table = row["table_name"]
            if table in CHILDREN or table == "patients":
                require(row["relrowsecurity"] and row["relforcerowsecurity"], "baseline forced RLS: "+table)
            for role in (roles["engine"],roles["observer_engine"]):
                for privilege in ("DELETE","TRUNCATE","REFERENCES","TRIGGER"):
                    require(not conn.execute(text("SELECT has_table_privilege(:role,:table,:privilege)"),{"role":role,"table":"public."+table,"privilege":privilege}).scalar_one(), "no unneeded table privilege")
            require(conn.execute(text("SELECT has_table_privilege(:role,:table,'SELECT')"),{"role":roles["observer_engine"],"table":"public."+table}).scalar_one(), "observer SELECT: "+table)
            require(not conn.execute(text("SELECT has_any_column_privilege(:role,:table,'INSERT')"),{"role":roles["observer_engine"],"table":"public."+table}).scalar_one(), "observer cannot INSERT")
            if table not in CHILDREN:
                require(not conn.execute(text("SELECT has_any_column_privilege(:role,:table,'INSERT')"),{"role":roles["engine"],"table":"public."+table}).scalar_one(), "application INSERT limited to six child tables")
            for column in (c["column_name"] for c in cat["columns"] if c["table_name"]==table):
                for role in (roles["engine"],roles["observer_engine"]):
                    actual = conn.execute(text("SELECT has_column_privilege(:role,:table,:column,'UPDATE')"),{"role":role,"table":"public."+table,"column":column}).scalar_one()
                    allowed = role==roles["engine"] and table=="appointments" and column in UPDATE_COLUMNS
                    require(actual == allowed, "column-limited UPDATE authority")
        for table in CHILDREN:
            require(conn.execute(text("SELECT has_table_privilege(:role,:table,'SELECT') AND has_table_privilege(:role,:table,'INSERT')"),{"role":roles["engine"],"table":"public."+table}).scalar_one(), "application insert/read surface")
        for edge in EDGES:
            columns = [r for r in cat["columns"] if r["table_name"]==edge.child and r["column_name"]==edge.column]
            require(len(columns)==1 and columns[0]["attnotnull"] == (not edge.nullable), "baseline edge nullability: "+edge.id)
            old = [r for r in cat["constraints"] if r["table_name"]==edge.child and r["contype"]=="f" and r["columns"]==[edge.column] and r["parent_table"]==edge.parent and r["parent_columns"]==["id"]]
            require(len(old)==1 and old[0]["convalidated"], "existing single-ID FK: "+edge.id)
            require(not any(r["conname"]==edge.constraint for r in cat["constraints"]), "new FK absent at baseline")
    with runtime["admin_engine"].connect() as conn:
        _context(conn,runtime,roles["admin_engine"])
        require(conn.execute(text("SELECT rolsuper AND rolcanlogin FROM pg_roles WHERE rolname=current_user")).scalar_one(),"isolated owner/setup login")
    return roles


@contextmanager
def _app_transaction(runtime, world):
    with runtime["engine"].connect() as conn:
        tx = conn.begin()
        try:
            _context(conn,runtime,runtime["application_role"])
            conn.execute(text("SELECT set_config('app.current_practice_id',:practice,true)"),{"practice":str(world.practices["P"])})
            _context(conn,runtime,runtime["application_role"],world.practices["P"])
            yield conn
        finally:
            tx.rollback()
        # A failed SQL statement must not leave P on this pooled physical connection.
        _context(conn,runtime,runtime["application_role"])
        conn.rollback()


def _expect_error(operation, edge, *, null=False):
    try:
        operation()
    except DBAPIError as error:
        diag = getattr(error.orig,"diag",None)
        require(getattr(error.orig,"pgcode",None)==("23502" if null else "23503"), "exact SQLSTATE: "+edge.id)
        require(getattr(diag,"table_name",None)==edge.child, "exact rejected child table: "+edge.id)
        if null:
            require(getattr(diag,"column_name",None)==edge.column, "exact NOT NULL column: "+edge.id)
        else:
            require(getattr(diag,"constraint_name",None)==edge.constraint, "exact new FK rejection: "+edge.id)
    else:
        pytest.fail("required database rejection missing: "+edge.id,pytrace=False)


def _data(runtime):
    with runtime["observer_engine"].connect() as conn:
        return snapshot(conn)


def _unchanged(runtime, before, label):
    after = _data(runtime)
    require(after==before, "full P/Q snapshots changed: "+label)


def _reference_exists(runtime, edge, world):
    with runtime["observer_engine"].connect() as conn:
        for tenant in ("P","Q"):
            rows = conn.execute(text('SELECT practice_id FROM public."'+edge.parent+'" WHERE id=:id'),{"id":world.targets[edge.parent][tenant]}).scalars().all()
            require(rows==[world.practices[tenant]], "real parent ownership: "+edge.id+tenant)


def _insert_probes(runtime, world, edge, *, enforced, null_control):
    before = _data(runtime)
    _reference_exists(runtime,edge,world)
    original = world.payload(edge,world.targets[edge.parent]["P"])
    for tenant in ("P","Q"):
        payload = dict(original, **{edge.column:world.targets[edge.parent][tenant]})
        with _app_transaction(runtime,world) as conn:
            operation = lambda: insert(conn,edge.child,payload)
            if tenant=="Q" and enforced:
                _expect_error(operation,edge)
            else:
                row=operation()
                require(row[edge.column]==payload[edge.column] and row["practice_id"]==world.practices["P"], "actual returned INSERT: "+edge.id+tenant)
        _unchanged(runtime,before,edge.id+tenant)
    if null_control:
        payload=dict(original,**{edge.column:None})
        with _app_transaction(runtime,world) as conn:
            operation=lambda: insert(conn,edge.child,payload)
            if edge.nullable:
                require(operation()[edge.column] is None,"optional NULL remains valid: "+edge.id)
            else:
                _expect_error(operation,edge,null=True)
        _unchanged(runtime,before,edge.id+"NULL")


def _update_probes(runtime,world,edge,*,enforced,null_control):
    before=_data(runtime)
    _reference_exists(runtime,edge,world)
    # Row is inserted and updated in the same real restricted P transaction,
    # then rolled back. The success target is a second, distinct P parent.
    payload=world.payload(edge)
    with runtime["observer_engine"].connect() as conn:
        owner=conn.execute(text('SELECT practice_id FROM public."'+edge.parent+'" WHERE id=:id'),{"id":world.alternates[edge.parent]["P"]}).scalar_one()
        require(owner==world.practices["P"] and world.alternates[edge.parent]["P"]!=payload[edge.column],"distinct valid P UPDATE target")
    for tenant in (("P","Q",None) if null_control else ("P","Q")):
        with _app_transaction(runtime,world) as conn:
            seed=dict(payload)
            if tenant is None:
                seed[edge.column]=world.targets[edge.parent]["P"]
            row=insert(conn,"appointments",seed)
            target=None if tenant is None else (world.alternates[edge.parent]["P"] if tenant=="P" else world.targets[edge.parent]["Q"])
            operation=lambda: update_reference(conn,row["id"],edge.column,target)
            if tenant=="Q" and enforced:
                _expect_error(operation,edge)
            else:
                changed=operation()
                expected=dict(row,**{edge.column:target,"appointment_state_version":row["appointment_state_version"]+1})
                require(changed==expected,"exact UPDATE and version effect: "+edge.id)
        _unchanged(runtime,before,"UPDATE "+edge.id)


def _catalogue_upgrade(before,after):
    new_fks={e.constraint:e for e in EDGES}
    new_names=set(new_fks)|set(UNIQUE_KEYS.values())
    require(not (new_names & {r["conname"] for r in before["constraints"]}), "new constraint collision")
    for key in ("tables","columns","policies"):
        require(after[key]==before[key],"unchanged metadata: "+key)
    require([r for r in after["constraints"] if r["conname"] not in new_names]==before["constraints"],"every old constraint retained")
    additions=[r for r in after["constraints"] if r["conname"] in new_names]
    require(len(additions)==24,"exact 18 FK plus six unique constraints")
    for row in additions:
        require(row["convalidated"] and not row["condeferrable"] and not row["condeferred"],"validated nondeferrable new constraint")
        if row["conname"] in new_fks:
            edge=new_fks[row["conname"]]
            require(row["table_name"]==edge.child and row["contype"]=="f" and row["columns"]==["practice_id",edge.column] and row["parent_schema"]=="public" and row["parent_table"]==edge.parent and row["parent_columns"]==["practice_id","id"],"exact new FK shape: "+edge.id)
            require((row["confmatchtype"],row["confupdtype"],row["confdeltype"])==("s","a","a"),"MATCH SIMPLE and NO ACTION: "+edge.id)
        else:
            require(UNIQUE_KEYS.get(row["table_name"])==row["conname"] and row["contype"]=="u" and row["columns"]==["practice_id","id"],"exact new parent unique key")
    require([r for r in after["indexes"] if r["constraint_name"] not in UNIQUE_KEYS.values()]==before["indexes"],"old indexes retained")
    added_indexes=[r for r in after["indexes"] if r["constraint_name"] in UNIQUE_KEYS.values()]
    require(len(added_indexes)==6 and all(r["indisunique"] and r["indisvalid"] and r["indisready"] and not r["indisprimary"] for r in added_indexes),"six valid supporting unique indexes")
    require([r for r in after["triggers"] if r["constraint_name"] not in new_fks]==before["triggers"],"old triggers retained")
    added_triggers=[r for r in after["triggers"] if r["constraint_name"] in new_fks]
    require(len(added_triggers)==72 and all(r["tgisinternal"] and r["tgenabled"]=="O" for r in added_triggers),"four enabled PostgreSQL RI triggers per new FK")


def _dirty_preflight(runtime,migration,world,edges,baseline_data,baseline_cat):
    dirty=[]
    with runtime["admin_engine"].begin() as conn:
        for edge in edges:
            payload=world.payload(edge,world.targets[edge.parent]["Q"])
            inserted=insert(conn,edge.child,payload)
            dirty.append((edge,inserted["id"]))
    before,cat,revision=_observe(runtime)
    require(revision==[BASELINE] and cat==baseline_cat,"dirty fixture is schema-neutral")
    require(before!=baseline_data,"dirty fixture actually committed")
    try:
        migration["migrate"]("upgrade",CANDIDATE)
    except Exception as error:
        # Real migration fail-fast order is its literal declared edge order;
        # individual scenarios prove every edge, combined scenario proves no DDL
        # happens before a dirty-reference rejection. Never accept generic 23503.
        message=str(error)
        expected="existing related-practice mismatch: "+edges[0].constraint
        require(expected in message,"specific actual dirty-preflight diagnostic")
    else:
        pytest.fail("dirty-reference migration unexpectedly succeeded",pytrace=False)
    after,after_cat,revision=_observe(runtime)
    require(after==before and after_cat==cat and revision==[BASELINE],"failed migration preserves dirty data/schema/revision")
    # Delete only this explicitly committed synthetic setup after preservation
    # is proved; a failed assertion leaves cleanup to the owned outer database.
    with runtime["admin_engine"].begin() as conn:
        for edge,row_id in reversed(dirty):
            result=conn.execute(text('DELETE FROM public."'+edge.child+'" WHERE id=:id AND practice_id=:practice'),{"id":row_id,"practice":world.practices["P"]})
            require(result.rowcount==1,"exact owned dirty-fixture cleanup")
    after,cat,revision=_observe(runtime)
    require(after==baseline_data and cat==baseline_cat and revision==[BASELINE],"coherent baseline restored exactly")


def _parent_move_probes(runtime,world,edge):
    before=_data(runtime)
    for referenced in (False,True):
        with runtime["admin_engine"].connect() as conn:
            tx=conn.begin()
            try:
                dedicated=seed_dedicated_parent(conn,edge,world)
                parent_id=dedicated.id
                if referenced:
                    insert(conn,edge.child,world.payload(edge,parent_id))
                operation=lambda: move_parent(conn,dedicated,world)
                if referenced:
                    _expect_error(operation,edge)
                else:
                    moved=operation()
                    require(moved["id"]==parent_id and moved["practice_id"]==world.practices["Q"],"coherent unreferenced parent move control: "+edge.id)
            finally:
                tx.rollback()
        _unchanged(runtime,before,"owner parent move "+edge.id)


def test_tenant_relationship_migration_lifecycle(tenant_runtime,relationship_migration,record_property):
    """One ordered node; fail closed at the first unexpected phase outcome."""
    runtime=tenant_runtime
    migration=relationship_migration
    roles=_runtime_contract(runtime,migration)
    require(len(EDGES)==18 and len(UPDATE_EDGES)==3,"fixed relationship population")
    world=World.seed(runtime["admin_engine"])
    baseline_data,baseline_cat,revision=_observe(runtime)
    require(revision==[BASELINE],"populated baseline revision")
    for table in set(CHILDREN)|{e.parent for e in EDGES}:
        rows=baseline_data[table]
        require(rows and all(any(str(r["practice_id"])==str(world.practices[p]) for r in rows) for p in ("P","Q")),"nonempty P/Q anchors: "+table)
    for edge in EDGES:
        if edge.nullable:
            for tenant in ("P","Q"):
                require(any(str(row["practice_id"])==str(world.practices[tenant]) and row[edge.column] is None for row in baseline_data[edge.child]),"populated optional NULL baseline: "+edge.id)
    progress=[]
    def phase(name,count):
        progress.append({"phase":name,"scenarios":count})
        record_property("relationship_phase_"+name,json.dumps(progress[-1],sort_keys=True))
    for edge in EDGES:
        _insert_probes(runtime,world,edge,enforced=False,null_control=False)
    for edge in UPDATE_EDGES:
        _update_probes(runtime,world,edge,enforced=False,null_control=False)
    phase("rollback_precursor",21)
    for edge in EDGES:
        _dirty_preflight(runtime,migration,world,(edge,),baseline_data,baseline_cat)
    # Keep combined ordering aligned with migration's first selected edge only;
    # the independent cases above cover all edges irrespective of declaration order.
    _dirty_preflight(runtime,migration,world,EDGES,baseline_data,baseline_cat)
    phase("dirty_preflight",19)
    migration["migrate"]("upgrade",CANDIDATE)
    data,candidate_cat,revision=_observe(runtime)
    require(revision==[CANDIDATE] and data==baseline_data,"populated upgrade preserves all rows")
    _catalogue_upgrade(baseline_cat,candidate_cat)
    phase("populated_upgrade",1)
    for edge in EDGES:
        _insert_probes(runtime,world,edge,enforced=True,null_control=True)
    for edge in UPDATE_EDGES:
        _update_probes(runtime,world,edge,enforced=True,null_control=True)
    phase("enforced_references",21)
    for edge in EDGES:
        _parent_move_probes(runtime,world,edge)
    phase("parent_practice_changes",18)
    data,cat,revision=_observe(runtime)
    require(data==baseline_data and cat==candidate_cat and revision==[CANDIDATE],"all rollback probes preserve upgraded world")
    migration["migrate"]("downgrade",BASELINE)
    data,cat,revision=_observe(runtime)
    require(data==baseline_data and cat==baseline_cat and revision==[BASELINE],"successor-only downgrade preserves exact data and baseline schema")
    for edge in EDGES:
        _insert_probes(runtime,world,edge,enforced=False,null_control=False)
    for edge in UPDATE_EDGES:
        _update_probes(runtime,world,edge,enforced=False,null_control=False)
    phase("populated_downgrade",22)
    data,cat,revision=_observe(runtime)
    require(data==baseline_data and cat==baseline_cat and revision==[BASELINE],"final preserved baseline")
    record_property("relationship_case_count",1)
    record_property("relationship_migration_calls",21)
    record_property("relationship_edge_count",18)
    record_property("relationship_update_edges",3)
