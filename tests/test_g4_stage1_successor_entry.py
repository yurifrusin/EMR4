"""Focused successor policy checks using the exact permitted UI12 prestate."""
import copy
import base64
import hashlib
import json
from pathlib import Path
import pytest
from orchestration_harness import bounded_g1b, raisa_policy

# Schema20 additions are source-only test preparation. These exercise the exact
# selected controller predicates; synthetic Git observations below do not prove
# native admission, application behaviour or an execution authorization.
_PREDECESSOR_CONTROL_ROOT = Path("C:/Users/there/EMR4-tools/owner-bootstrap-admission-successor-preparation-v1/before")
_PREDECESSOR_CONTROL_SHA256 = {
    "orchestration_harness/bounded_g1b.py": "03a7d4097b842ab0f6cb647432b32877b4a17d6b844b45a744420550ba851fae",
    "orchestration/programme/g4-stage1-successor-entry-scope.json": "53c1824377865422fa7340fd1ab2fddc65d9ac47ab5c0e5889e4d213a2d48df9",
    "tests/test_g4_stage1_successor_entry.py": "5f76d887541964c019be2bd574c4b4fea01d950109866504bcf6924d7b15effc",
}


def _pinned_predecessor_control(path):
    raw = (_PREDECESSOR_CONTROL_ROOT / path).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == _PREDECESSOR_CONTROL_SHA256[path]
    return raw


_HISTORICAL_V19_CONTROL_ROOT = Path("C:/Users/there/EMR4-tools/g4-account-http-acl-enable01")
_HISTORICAL_V19_CONTROL_SHA256 = {
    "orchestration_harness/bounded_g1b.py": "087858d9826b1a1c1e30438193109c8044691d9cb3fff80c96e7658ebac9f0b7",
    "orchestration/programme/g4-stage1-successor-entry-scope.json": "5b6c9b7570cc3e28a7d66b54aebf3215e9e734128c598cc5f9ce8c68acdb632d",
    "tests/test_g4_stage1_successor_entry.py": "de187a685382c25a7781b716a07059133f7b78c999133873b336944095b26528",
}


def _pinned_historical_v19_control(path):
    raw = (_HISTORICAL_V19_CONTROL_ROOT / path).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == _HISTORICAL_V19_CONTROL_SHA256[path]
    return raw

def _seeded_scope():
    return json.loads(_pinned_predecessor_control(bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE))


def _seeded_q(stage="enable", phase="development"):
    b=bounded_g1b;scope=_seeded_scope()
    base=b.G4_SEEDED_LOGIN_BASE if stage=="enable" else {"commit":"b"*40,"tree":"c"*40}
    candidate=base["tree"] if stage=="admit" else "a"*40
    owned=b.G4_SEEDED_LOGIN_CONTROL if stage=="enable" else b.G4_SEEDED_LOGIN_PRODUCT if stage=="apply" else ()
    return {"schema_version":b.G4_SEEDED_LOGIN_SCHEMA,"operation_id":"seeded-source-test",
        "operation_kind":b.G4_SEEDED_LOGIN_ADMIT_KIND if stage=="admit" else
            "enable_g4_stage1_successor" if stage=="enable" else "implement_g4_stage1_successor",
        "stage":stage,"phase":phase,"base_commit":base["commit"],"base_tree":base["tree"],
        "expected_head":base["commit"] if phase=="development" else "e"*40,
        "expected_index_tree":base["tree"] if phase=="development" else candidate,
        "candidate_tree":candidate,"source_sha256":scope["source_sha256"],"payload_sha256":{},
        "repair_sha256":{p:{} for p in owned},"source_review":{},
        "activation_acceptance":None if stage=="enable" else {"path":(
            b.G4_SEEDED_LOGIN_ROOT/"entry-admission-v1/independent-enable-push-effect-review-v1.json").as_posix(),"sha256":"f"*64},
        "product_vector":scope["product_vector"],"mapping_review":scope["mapping_review"]}


def _seeded_read(path,digest):
    raw=path.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==digest
    return raw


def test_seeded_scope_exact_six_and_prior_schema19_dispatch():
    b=bounded_g1b;scope=_seeded_scope()
    b.validate_g4_seeded_login_scope(scope)
    for stage in ("enable","admit","apply"):
        q=_seeded_q(stage)
        expected=b.G4_SEEDED_LOGIN_CONTROL if stage=="enable" else b.G4_SEEDED_LOGIN_PRODUCT if stage=="apply" else frozenset()
        assert b.operation_paths(q["operation_kind"],q)==expected
    old={"schema_version":b.G4_ACCOUNT_HTTP_SCHEMA,"stage":"admit",
        "operation_kind":b.G4_ACCOUNT_HTTP_ADMIT_KIND,"repair_sha256":{}}
    assert b.operation_paths(old["operation_kind"],old)==frozenset()
    assert b._operation(old["operation_kind"],old)["g4_account_http_external_source"] is True
    assert b.G4_ACCOUNT_HTTP_SCOPE_SCHEMA=="ariadne.g4_stage1_successor_entry_scope.v19"
    assert not b._is_g4_seeded_login_binding(old)
    for schema,expected in ((b.G4_BUREAU_V9_SCHEMA,b.G4_BUREAU_V9_PRODUCT),
                            (b.G4_ACCOUNT_BOOTSTRAP_SCHEMA,b.G4_ACCOUNT_BOOTSTRAP_PRODUCT)):
        prior={"schema_version":schema,"stage":"apply","operation_kind":"implement_g4_stage1_successor",
               "repair_sha256":{p:{} for p in expected}}
        assert b.operation_paths(prior["operation_kind"],prior)==expected


@pytest.mark.parametrize("mutation",["extra","base","predecessor","review","runtime","product"])
def test_seeded_scope_rejects_widening_or_wrong_baseline(mutation):
    b=bounded_g1b;scope=_seeded_scope()
    if mutation=="extra":scope["allowed_paths"].append("app/unowned.py")
    if mutation=="base":scope["selected_base"]["commit"]="0"*40
    if mutation=="predecessor":scope["predecessor_scope"]["sha256"]="0"*64
    if mutation=="review":scope["mapping_review"]["sha256"]="0"*64
    if mutation=="runtime":scope["admission_grants_runtime_authority"]=True
    if mutation=="product":scope["product_sha256"]["app/dependencies.py"]="0"*64
    with pytest.raises(b.BoundedG1BError) as err:b.validate_g4_seeded_login_scope(scope)
    assert err.value.reason_code=="bounded_g4_seeded_login_scope_boundary"


@pytest.mark.parametrize("mutation,reason",[(None,None),("extra","bounded_g4_seeded_login_external_vector"),
    ("duplicate","bounded_g4_seeded_login_external_vector"),("namespace","bounded_g4_seeded_login_external_vector"),
    ("file","bounded_g4_seeded_login_external_vector"),("maps","bounded_g4_seeded_login_source_maps"),
    ("map_duplicate","bounded_g4_seeded_login_source_maps"),("review_pin","bounded_g4_seeded_login_external_pins"),
    ("review_authorship","bounded_g4_seeded_login_independent_source")])
def test_seeded_external_exact_subject_and_separate_maps(mutation,reason):
    b=bounded_g1b;q=_seeded_q("admit")
    if mutation=="review_pin":q["mapping_review"]["sha256"]="0"*64
    def read(path,digest):
        raw=_seeded_read(path,digest)
        # Substitute one JSON field AFTER independently checking its pinned
        # ordinary baseline, to isolate the named controller predicate.
        if path==b.G4_SEEDED_LOGIN_VECTOR and mutation in {"extra","duplicate","namespace","file"}:
            value=json.loads(raw)
            if mutation=="extra":value["files"].append(copy.deepcopy(value["files"][0]))
            if mutation=="duplicate":value["files"][1]=copy.deepcopy(value["files"][0])
            if mutation=="namespace":value["files"][0]["namespace"]="SITE"
            if mutation=="file":value["files"][0]["after"]["path"]="C:/unowned.py"
            return json.dumps(value).encode()
        if path==b.G4_SEEDED_LOGIN_MAPS and mutation in {"maps","map_duplicate"}:
            value=json.loads(raw)
            if mutation=="maps":value["backend_count"]=156
            else:value["site_rows"][1]=copy.deepcopy(value["site_rows"][0])
            return json.dumps(value).encode()
        if path==b.G4_SEEDED_LOGIN_PREPARATION_REVIEW and mutation=="review_authorship":
            value=json.loads(raw);value["reviewer"]["implementation_authored"]=True
            return json.dumps(value).encode()
        return raw
    if reason:
        with pytest.raises(b.BoundedG1BError) as err:b._g4_seeded_login_external_inputs(read,q)
        assert err.value.reason_code==reason
    else:
        vector,review=b._g4_seeded_login_external_inputs(read,q)
        assert len(vector["files"])==15 and review["execution_authorized"] is False


@pytest.mark.parametrize("entrypoint,phase",[("recovery_preflight","development"),
    ("task_branch_commit","development"),("task_branch_push","pre-push"),("recovery_preflight","post-push")])
def test_seeded_admit_entrypoint_cannot_publish_or_execute(entrypoint,phase):
    b=bounded_g1b;q=_seeded_q("admit")
    if (entrypoint,phase)==("recovery_preflight","development"):
        b._g4_seeded_login_require_entrypoint(q,entrypoint,phase)
        assert b.operation_effects(q["operation_kind"])==frozenset({"repository_read"})
        assert "admission grants no runtime" in " ".join(b.G4_SEEDED_LOGIN_LIMITS)
    else:
        with pytest.raises(b.BoundedG1BError) as err:b._g4_seeded_login_require_entrypoint(q,entrypoint,phase)
        assert err.value.reason_code=="bounded_g4_seeded_login_admit_entrypoint"


def _seeded_loader_fixture(monkeypatch,stage,phase):
    b=bounded_g1b;root=Path(__file__).resolve().parents[1]
    target=Path("C:/synthetic-seeded-target");source=Path("C:/synthetic-seeded-source")
    paths=(b.CONFIGURATION_PATHS|{b.STATE,b.GATES,b.OVERLAY,b.AGENTS,b.G4_STAGE1_INTERACTIVE_SCOPE,
        b.G4_STAGE1_SUCCESSOR_SCOPE,b.G4_STAGE1_SUCCESSOR_TEST,b.G4_CI_WORKFLOW}|b.SOURCE_PATHS|b.CONTROLLER_PATHS)
    original={p:("accepted:"+p).encode() for p in paths}
    for p in b.G4_SEEDED_LOGIN_CONTROL:original[p]=_pinned_historical_v19_control(p)
    installed=dict(original)
    for p in b.G4_SEEDED_LOGIN_CONTROL:installed[p]=(root/p).read_bytes()
    after=dict(installed)
    if stage=="apply":
        paths|=b.G4_SEEDED_LOGIN_PRODUCT
        for p,logical in b.G4_SEEDED_LOGIN_PRODUCT_LOGICAL.items():
            row=b.G4_SEEDED_LOGIN_EXTERNAL_ROWS[logical][1]
            after[p]=_seeded_read(Path(row["path"]),row["sha256"])
        vector=json.loads(_seeded_read(b.G4_SEEDED_LOGIN_VECTOR,b.G4_SEEDED_LOGIN_VECTOR_SHA))
        for p,logical in b.G4_SEEDED_LOGIN_PRODUCT_LOGICAL.items():
            if b.G4_SEEDED_LOGIN_BEFORE_SHA[p] is None:continue
            entry=next(r for r in vector["files"] if r["logical_path"]==logical)
            row=entry["before"] if entry["namespace"]=="BACKEND" else entry["original_baseline"]
            old_path=Path(row.get("source_path",row.get("path")))
            installed[p]=_seeded_read(old_path,b.G4_SEEDED_LOGIN_BEFORE_SHA[p])
    # Bind the deliberately synthetic ordinary controls to the actual candidate
    # controller/test bytes, without invoking the whole-policy/config loader.
    scope=_seeded_scope()
    scope["source_sha256"]={p:hashlib.sha256(after[p]).hexdigest() for p in b.SOURCE_PATHS|b.CONTROLLER_PATHS}
    scope["control_sha256"]={p:hashlib.sha256(after[p]).hexdigest()
        for p in b.G4_SEEDED_LOGIN_CONTROL-{b.G4_STAGE1_SUCCESSOR_SCOPE}}
    after[b.G4_STAGE1_SUCCESSOR_SCOPE]=b._canonical(scope)+b"\n"
    if stage!="enable":installed[b.G4_STAGE1_SUCCESSOR_SCOPE]=after[b.G4_STAGE1_SUCCESSOR_SCOPE]
    q=_seeded_q(stage,phase)
    q["source_sha256"]={p:hashlib.sha256(after[p]).hexdigest() for p in b.SOURCE_PATHS|b.CONTROLLER_PATHS}
    q["payload_sha256"]={p:hashlib.sha256(after[p]).hexdigest() for p in paths}
    owned=b._g4_seeded_login_paths(q["operation_kind"],q)
    for p in owned:
        before=b.G4_SEEDED_LOGIN_PREIMAGES[p] if stage=="enable" else b.G4_SEEDED_LOGIN_BEFORE_SHA[p]
        q["repair_sha256"][p]={"before_sha256":before,"after_sha256":q["payload_sha256"][p]}
    subject=b.G4_SEEDED_LOGIN_ROOT/"entry-admission-v1"/("independent-"+stage+"-"+phase+"-subject-review-v1.json")
    q["source_review"]={"path":subject.as_posix(),"sha256":"d"*64}
    external={Path(b.G4_SEEDED_LOGIN_EXTERNAL_ROWS[logical][1]["path"]):
        (p,b.G4_SEEDED_LOGIN_PRODUCT_SHA[p],b.G4_SEEDED_LOGIN_PRODUCT_BYTES[p])
        for p,logical in b.G4_SEEDED_LOGIN_PRODUCT_LOGICAL.items()}
    assert len(external)==6 and {row[0] for row in external.values()}==b.G4_SEEDED_LOGIN_PRODUCT
    external_seen=set()
    def read(path,digest):
        if path==subject:
            return json.dumps({"schema":"emr4.g4_operation_review.v1","status":"PASS",
                "verdict":"PASS_G4_STAGE1_SEEDED_LOGIN_EXACT_ADMISSION_SUBJECT","subject_sha256":b.g4_seeded_login_review_subject(q),
                "independent":True,"implementation_authorship":False,"blocking_findings":[],
                "reviewer_agent":"/root/synthetic-independent-reviewer","stage":stage,"phase":phase}).encode()
        if stage!="enable" and path==Path(q["activation_acceptance"]["path"]):
            return json.dumps({"schema":"emr4.g4_operation_review.v1","status":"PASS",
                "verdict":"PASS_G4_STAGE1_SEEDED_LOGIN_CONTROL_PUBLICATION_EFFECT","independent":True,
                "implementation_authorship":False,"blocking_findings":[],"reviewer_agent":"/root/synthetic-independent-reviewer",
                "stage":"enable","phase":"push","base":b.G4_SEEDED_LOGIN_BASE["commit"],"commit":q["base_commit"],
                "candidate_tree":q["base_tree"],"control_activation_accepted":True,"same_attempt_remote_readback_verified":True,
                "protected_refs_unchanged":True,"whole_inverse_verified_same_attempt":True,"published_ref":b.G4_STAGE1_INTERACTIVE_BACKEND_REF}).encode()
        if path in external:
            relative,expected,size=external[path]
            assert stage=="apply" and digest==expected
            raw=after[relative]
            assert len(raw)==size and hashlib.sha256(raw).hexdigest()==expected
            external_seen.add(relative)
            return raw
        assert path.is_relative_to(target) or path.is_relative_to(source), "unbound synthetic read"
        relative=path.relative_to(target if path.is_relative_to(target) else source).as_posix()
        raw=after[relative]
        assert hashlib.sha256(raw).hexdigest()==digest
        return raw
    read.external_seen=external_seen
    def git_bytes(_target,*args):
        if args[0]=="ls-tree":return b"tracked" if args[-1] in (original if stage=="enable" else installed) else b""
        assert args[:2]==("cat-file","blob")
        commit,p=args[2].split(":",1)
        return (original if commit==b.G4_SEEDED_LOGIN_BASE["commit"] else installed)[p]
    def git(_target,*args):
        if args[0]=="rev-parse":return b.G4_SEEDED_LOGIN_BASE["tree"]
        parent=b.G4_SEEDED_LOGIN_BASE["commit"] if args[2]==q["base_commit"] and stage!="enable" else q["base_commit"]
        tree=q["base_tree"] if args[2]==q["base_commit"] and stage!="enable" else q["candidate_tree"]
        return "tree "+tree+"\nparent "+parent+"\n\nsynthetic\n"
    observations=[]
    monkeypatch.setattr(b.trusted_git,"run_git_bytes",git_bytes)
    monkeypatch.setattr(b.trusted_git,"run_git",git)
    monkeypatch.setattr(b.trusted_git,"attest_target_index",lambda *a,**k:observations.append(k) or {"observation_sha256":"sha256:"+"0"*64})
    monkeypatch.setattr(b,"_g4_seeded_login_external_inputs",lambda *a:({"synthetic_source_join":True},{}))
    def run(reader=read):return b._load_g4_seeded_login_inputs(None,target,source,b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT,
        Path("C:/synthetic-seeded-scratch"),q,reader,{})
    return run,q,read,observations


@pytest.mark.parametrize("stage,phase",[("enable","development"),("enable","pre-push"),
    ("admit","development"),("apply","development"),("apply","pre-push"),("apply","post-push")])
def test_seeded_loader_exact_stages_reach_selected_index_predicate(monkeypatch,stage,phase):
    run,q,read,observations=_seeded_loader_fixture(monkeypatch,stage,phase)
    result=run()
    assert result.binding is q and len(observations)==1
    assert read.external_seen==(bounded_g1b.G4_SEEDED_LOGIN_PRODUCT if stage=="apply" else set())
    assert set(q["repair_sha256"])==(bounded_g1b.G4_SEEDED_LOGIN_CONTROL if stage=="enable" else
        bounded_g1b.G4_SEEDED_LOGIN_PRODUCT if stage=="apply" else set())
    assert bounded_g1b._operation(q["operation_kind"],q)["g4_seeded_login_source"] is True


@pytest.mark.parametrize("phase,delta",[("development",True),("pre-push",False)])
def test_seeded_admit_loader_rejects_delta_and_publication_phase(monkeypatch,phase,delta):
    b=bounded_g1b;run,q,read,observations=_seeded_loader_fixture(monkeypatch,"admit",phase)
    if delta:q["candidate_tree"]="a"*40
    with pytest.raises(b.BoundedG1BError) as err:run()
    assert err.value.reason_code=="bounded_g4_seeded_login_admit_no_delta" and observations==[]


def test_seeded_admit_report_has_no_runtime_authority(monkeypatch):
    b=bounded_g1b;q=_seeded_q("admit")
    inputs=b.BoundedG1BInputs(q,{},{},{},{"observation_sha256":"sha256:"+"0"*64})
    context=b.BoundedG1BContext(target_root=Path("C:/synthetic-seeded-target"),
        source_root=Path("C:/synthetic-seeded-source"),evidence_root=b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT,
        binding_path=Path("C:/synthetic-seeded-binding.json"),expected_binding_sha256="0"*64,
        scratch_root=Path("C:/synthetic-seeded-scratch"))
    monkeypatch.setattr(b,"load_bounded_g1b_inputs",lambda context:inputs)
    monkeypatch.setattr(b,"_validate_g4_seeded_login_loaded_policy",lambda inputs:({},None))
    manifest=b.build_bounded_g1b_manifest(context)
    report=b.bounded_g1b_report(context=context,manifest=manifest,entrypoint="recovery_preflight",phase="development")
    assert manifest["allowed_paths"]==[] and manifest["intended_side_effect_classes"]==["repository_read"]
    assert report["policy_eligible"] is True and report["execution_authorized"] is False
    assert report["feature_work_eligible"] is False


@pytest.mark.parametrize("mode,reason",[("extra","bounded_g4_seeded_login_changed_paths"),
    ("preimage","bounded_g4_seeded_login_change_preimage"),("activation","bounded_g4_seeded_login_activation_acceptance"),
    ("subject","bounded_g4_seeded_login_independent_subject"),("stage_review","bounded_g4_seeded_login_independent_subject")])
def test_seeded_apply_cannot_reuse_admit_or_wrong_product_acceptance(monkeypatch,mode,reason):
    b=bounded_g1b;run,q,read,observations=_seeded_loader_fixture(monkeypatch,"apply","development")
    if mode=="extra":q["repair_sha256"]["backend_child_text_v1.py"]={}
    if mode=="preimage":q["repair_sha256"]["static/demo/stage1-interactive.html"]["before_sha256"]=None
    def changed(path,digest):
        raw=read(path,digest)
        if path.name=="independent-enable-push-effect-review-v1.json" and mode=="activation":
            value=json.loads(raw);value["control_activation_accepted"]=False;return json.dumps(value).encode()
        if path.name=="independent-apply-development-subject-review-v1.json" and mode in {"subject","stage_review"}:
            value=json.loads(raw)
            if mode=="subject":value["subject_sha256"]="0"*64
            else:value["stage"]="admit"
            return json.dumps(value).encode()
        return raw
    with pytest.raises(b.BoundedG1BError) as err:run(changed)
    assert err.value.reason_code==reason and observations==[]

BASE = Path("C:/Users/there/EMR4-tools/g4-stage1-interactive-product-actual-v1")
PUBLICATION = Path("C:/Users/there/EMR4-migration/20260911-v1/current-control-repair-20260912-v1/demo-led-stage1-20261012-v2/stage1-interactive-product-publication-source-v2/independent-stage1-interactive-product-push-effect-review-v2.json")
HISTORICAL_AFTERIMAGES = Path("C:/Users/there/EMR4-tools/g4-stage1-successor-control-actual-v2")
# Historical v1 tests retain their own accepted phase and exact Scope6e9/afterimages.
PUBLICATION_SHA = "7453f0a1819cf350464687599be78477d8d0cccde072b322cf6539bfdad476df"

def _scope():
    raw = (HISTORICAL_AFTERIMAGES / bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == "6e9ece8b95fe3b47b5969d44b0f1b644cef92e751ec62ab03bd2b6be25bcacd8"
    return json.loads(raw)

def _before():
    expected = {path: bounded_g1b.G4_STAGE1_SUCCESSOR_BASE_CONTROL[path]
                for path in (bounded_g1b.STATE, bounded_g1b.GATES, bounded_g1b.OVERLAY, bounded_g1b.AGENTS)}
    result = {}
    for path, digest in expected.items():
        raw = (BASE / path).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == digest
        result[path] = raw
    return result

def _publication():
    raw = PUBLICATION.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PUBLICATION_SHA
    return json.loads(raw)

def _build(scope):
    return bounded_g1b.build_g4_stage1_successor_transition(_before(), scope, _publication())

def test_valid_pinned_transition_matches_authored_afterimages():
    before = _before()
    result = _build(_scope())
    assert set(result) == {bounded_g1b.STATE, bounded_g1b.OVERLAY, bounded_g1b.AGENTS,
                           bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE}
    for path, raw in result.items():
        assert raw == (HISTORICAL_AFTERIMAGES / path).read_bytes()
    original = json.loads(before[bounded_g1b.STATE])
    proposed = json.loads(result[bounded_g1b.STATE])
    assert proposed["g2"] == original["g2"] and proposed["g3"] == original["g3"]

def test_missing_timestamp_is_rejected_with_valid_pinned_prestate():
    scope = _scope()
    assert scope["recorded_at"] is not None and len(scope["source_sha256"]) == 8
    scope["recorded_at"] = None
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        _build(scope)
    assert caught.value.reason_code == "bounded_g4_stage1_successor_scope_boundary"

def test_missing_source_map_is_rejected_by_required_digest_validator():
    # Exercise the mandatory source-map primitive; this is not whole-loader proof.
    scope = _scope()
    scope["source_sha256"] = None
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b._digest_map(scope["source_sha256"],
            bounded_g1b.SOURCE_PATHS | bounded_g1b.CONTROLLER_PATHS,
            "bounded_g4_stage1_successor_sources")
    assert caught.value.reason_code == "bounded_g4_stage1_successor_sources"

@pytest.mark.parametrize("change", [
    {"selected_base": {"commit": "0" * 40, "tree": "0" * 40}},
    {"voice_activation": True},
    {"admission_grants_runtime_authority": True},
    {"allowed_paths": ["app/main.py"]},
    {"allowed_effects": ["provider_invocation"]},
])
def test_wrong_base_or_wider_scope_is_rejected(change):
    scope = _scope()
    scope.update(change)
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        _build(scope)
    assert caught.value.reason_code == "bounded_g4_stage1_successor_scope_boundary"

def test_reviewed_eight_file_map_cannot_be_replaced():
    scope = _scope()
    scope["product_sha256"]["stage1_demo_http.py"] = "0" * 64
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        _build(scope)
    assert caught.value.reason_code == "bounded_g4_stage1_successor_required_product"

def test_path_selection_is_exact_and_old_profile_is_preserved():
    required = frozenset(bounded_g1b.G4_STAGE1_SUCCESSOR_PRODUCT_AFTERIMAGES)
    binding = {"operation_kind": "implement_g4_stage1_successor",
               "repair_sha256": {path: {} for path in required}}
    assert bounded_g1b.operation_paths("implement_g4_stage1_successor", binding) == required
    for path, add in (("app/main.py", True), ("stage1_demo_http.py", False)):
        invalid = copy.deepcopy(binding)
        if add:
            invalid["repair_sha256"][path] = {}
        else:
            del invalid["repair_sha256"][path]
        with pytest.raises(bounded_g1b.BoundedG1BError):
            bounded_g1b.operation_paths("implement_g4_stage1_successor", invalid)
    assert len(raisa_policy.g4_stage1_interactive_profile()["allowed_paths"]) == 12
    assert set(bounded_g1b.G4_STAGE1_SUCCESSOR_PRODUCT_AFTERIMAGES) <= set(
        raisa_policy.g4_stage1_successor_profile()["allowed_paths"])
    assert len(raisa_policy.g4_stage1_successor_profile()["allowed_paths"]) == 28


def _intention_scope():
    raw = base64.b64decode(
        "eyJhY3RpdmVfcHJvZmlsZSI6Ikc0X1NUQUdFMV9MT0NBTF9TVUNDRVNTT1IiLCJhZG1pc3Npb25fZ3JhbnRzX3J1bnRpbWVfYXV0"
        "aG9yaXR5IjpmYWxzZSwiYWxsb3dlZF9lZmZlY3RzIjpbImNvbnRyb2xfcGxhbmVfZWRpdCIsInByb2R1Y3RfYmVoYXZpb3JfY2hh"
        "bmdlIiwicmVwb3NpdG9yeV9yZWFkIiwidGFza19icmFuY2hfY29tbWl0IiwidGFza19icmFuY2hfcHVzaCJdLCJhbGxvd2VkX3Bh"
        "dGhzIjpbInN0YWdlMV9kZW1vX2FkYXB0ZXJfY29yZS5weSIsInN0YWdlMV9kZW1vX2h0dHAucHkiLCJzdGFnZTFfZGlhcnlfcm91"
        "dGVfZ3VhcmQucHkiLCJzdGFnZTFfc3RhZmZfZGlhcnlfcmVhZC5weSIsInN0YXRpYy9kZW1vL3N0YWdlMS1kaWFyeS12aWV3Lmpz"
        "Iiwic3RhdGljL2RlbW8vc3RhZ2UxLWludGVyYWN0aXZlLmNzcyIsInN0YXRpYy9kZW1vL3N0YWdlMS1pbnRlcmFjdGl2ZS5odG1s"
        "Iiwic3RhdGljL2RlbW8vc3RhZ2UxLWludGVyYWN0aXZlLmpzIiwidGVzdHMvdGVzdF9zdGFnZTFfZGlhcnlfdmlldy5janMiLCJ0"
        "ZXN0cy90ZXN0X3N0YWdlMV9pbnRlbnRfY29uZmlybWF0aW9uLmNqcyIsInRlc3RzL3Rlc3Rfc3RhZ2UxX3N0YWZmX2RpYXJ5X3Jl"
        "YWQucHkiXSwiYWxsb3dlZF90YXNrX2tpbmQiOiJnNF9zdGFnZTFfbG9jYWxfc3VjY2Vzc29yIiwiY29udHJvbF9zaGEyNTYiOnsi"
        "b3JjaGVzdHJhdGlvbi9oYXJuZXNzX3NldHRpbmdzL3Byb2dyYW1tZV9yZWNvdmVyeS55YW1sIjoiNTNhOGM1NzI1MWY4ZmY3M2Nm"
        "ZjI1OGY5NWFiYTJlY2ZmNDFlYTgwNTIzNWIwODM4YmU0YzBiY2ZlODQ3MWE4NiIsIm9yY2hlc3RyYXRpb25faGFybmVzcy9ib3Vu"
        "ZGVkX2cxYi5weSI6IjY0NGVhNWVkMWI0NDg3Y2Y2YmNlMDkwZjVjMDk3ODZlODljNzQyYTdmZTY0Nzg3OTMyOGRjMTljY2MyYTBi"
        "MmMiLCJvcmNoZXN0cmF0aW9uX2hhcm5lc3MvcmFpc2FfcG9saWN5LnB5IjoiMTBlZTg4NGEwNGYwMzM5MzI3ZDM2NTNmYjMyMzFi"
        "MDNlMDhiMDY0MTYxYjIyM2JlZTE1NWE3NDM4YTRjZWY0MSIsInRlc3RzL3Rlc3RfZzRfc3RhZ2UxX3N1Y2Nlc3Nvcl9lbnRyeS5w"
        "eSI6IjA1MTg0YzA2NWUyNmFkYmM2YzA1OTYwMGU1OWJhZTAxNjBmMjQ4OTM2NTY0MjljODk4MjJkYTRhYzVlMWI1MGEifSwiZXhj"
        "bHVkZWRfZWZmZWN0cyI6WyJ1bnJldmlld2VkX2FwcGxpY2F0aW9uX29yX2RhdGFiYXNlX3J1bnRpbWUiLCJ1bnJldmlld2VkX2Jy"
        "b3dzZXJfb3JfbWljcm9waG9uZV9ydW50aW1lIiwidW5yZXZpZXdlZF92b2ljZV9jaGlsZF9vcl9uZXR3b3JrX2VncmVzcyIsInBy"
        "b3ZpZGVyX2ludm9jYXRpb24iLCJyZWFsX2RhdGFfYWNjZXNzIiwicHJvdGVjdGVkX3JlZl9tb3ZlbWVudCIsImRlcGxveW1lbnQi"
        "LCJwdWJsaWNfbGlzdGVuZXIiXSwibWFwcGluZ19yZXZpZXciOnsicGF0aCI6IkM6L1VzZXJzL3RoZXJlL0VNUjQtbWlncmF0aW9u"
        "LzIwMjYwOTExLXYxL2N1cnJlbnQtY29udHJvbC1yZXBhaXItMjAyNjA5MTItdjEvZGVtby1sZWQtc3RhZ2UxLTIwMjYxMDEyLXYy"
        "L3N0YWdlMS1tb2NrLXZvaWNlLWRhdGFiYXNlLWludGVncmF0aW9uLXYxL2ludGVyYWN0aXZlLXJ1bnRpbWUtdjEvcmVjZXB0aW9u"
        "LWludGVudC11aS12MS9kaWFyeS1yZWFkLXJlY29ubmVjdGlvbi12MS9pbmRlcGVuZGVudC1wcm9kdWN0LW1hcHBpbmctcmV2aWV3"
        "LXYyLmpzb24iLCJzaGEyNTYiOiI1OGFiNDRmYzAwNzRiNDUzMWI1ODQxOGY2YmM2MDNlOTA4NGQ2YTNmMzIwNjU3ZDI5MTc3YTBh"
        "NDkzNTZkZGU0In0sInByZWRlY2Vzc29yX3Njb3BlIjp7InNoYTI1NiI6ImZjOTM3YzJlMWYzMDllZjBiMGEyMzM1YWYwNzY4ZDg4"
        "YTAwZTFhZTMzN2FjZjZlODZjZDljMjIxOGQ3MGI5YzYifSwicHJvZHVjdF9zaGEyNTYiOnsic3RhZ2UxX2RlbW9fYWRhcHRlcl9j"
        "b3JlLnB5IjoiNmIzZGNkZjVlNGVlYmQzZmUwMjI1ZDdkYzcxYjRjYTU2OTk3M2I2NWU4ZmUwNTQwZmZjNGUxZjk3YjA2ODcxNiIs"
        "InN0YWdlMV9kZW1vX2h0dHAucHkiOiIzYWM4MTE5ZmNiY2VhNzY0NjUyNjEwODllNWU5MjVkOGQ0MGQ1M2VhNjcyNzc4Yjg2MGI4"
        "OGM4YmQxN2M1OGY5Iiwic3RhZ2UxX2RpYXJ5X3JvdXRlX2d1YXJkLnB5IjoiOTNmOGQ0NGVlYmM5ZDdhODUyMTczNjdjYTdmZGE1"
        "MmIyY2RhNDgzYWE3MjdjZDE1MDY2NzY0OTI3YzhiYzljMiIsInN0YWdlMV9zdGFmZl9kaWFyeV9yZWFkLnB5IjoiOTAzNzhmYWJk"
        "MDAyNjA5YmE4NWJjMTk2MTZkZjFlMmQ4MjI1ZTZhYmM3NmQ3ZDViYzM5M2VmMDFmMWYyOWRmYiIsInN0YXRpYy9kZW1vL3N0YWdl"
        "MS1kaWFyeS12aWV3LmpzIjoiYzdjODkwYjBlZDBmZWQyZjJkM2NlMDkyZWY5NGE5MzE0MzUzNTZkZTQ4NTNjOTQzOTBjZjM5ZDg5"
        "YTA0ZTg2MiIsInN0YXRpYy9kZW1vL3N0YWdlMS1pbnRlcmFjdGl2ZS5jc3MiOiIwYjRmYTk1NjcwNjYwMzhiYWY2ZGE1MTEyZmU1"
        "NTJjNjgzN2U5NzMxNjg3MzllZTI3YTg5YTBjMjRjOWE5NGY3Iiwic3RhdGljL2RlbW8vc3RhZ2UxLWludGVyYWN0aXZlLmh0bWwi"
        "OiI3NDI1NTI5MDNmYzRmNTQxMjlmNzdkMDI1MjUzMWY2MjVlN2M3M2EzMDg2N2E1OTAzMzE5NGUzZjkzOTcwY2YyIiwic3RhdGlj"
        "L2RlbW8vc3RhZ2UxLWludGVyYWN0aXZlLmpzIjoiMjg2YzcwOGQ1Yzc5YjQ3MjMyYzUyZTg5OGM5YTRmOWE3NTQ3YmE5MTA5NTk5"
        "ZTZkYWI4NTdiN2Q1OWRhN2NkMCIsInRlc3RzL3Rlc3Rfc3RhZ2UxX2RpYXJ5X3ZpZXcuY2pzIjoiMTdiYzdkODYyOWJmYWQ4OTgx"
        "N2U4NzljMWE1ZmJlYWVhOTk0M2MxNDU1ZTRjMDg3NzQ3M2U2MzQzZDFlZjJkYSIsInRlc3RzL3Rlc3Rfc3RhZ2UxX2ludGVudF9j"
        "b25maXJtYXRpb24uY2pzIjoiZDEyMmI3YWZjNTZiYmQwOTRjNTQ2M2I4NWRjNGU5NDM1MGZkZjYyYTBjODhhMDM2YmJhMGU1Njdl"
        "ZmM3ZDFiMCIsInRlc3RzL3Rlc3Rfc3RhZ2UxX3N0YWZmX2RpYXJ5X3JlYWQucHkiOiI2MjU3NTYwZmQ4MTM3MTFiNmQ3MzRhN2Q4"
        "OTNmNTQ4YjRmNGIwZTZlYzA3Mzc5Y2Y5ODVmZWIwZGMwNWI5YTc4In0sInByb2R1Y3RfdmVjdG9yIjp7InBhdGgiOiJDOi9Vc2Vy"
        "cy90aGVyZS9FTVI0LW1pZ3JhdGlvbi8yMDI2MDkxMS12MS9jdXJyZW50LWNvbnRyb2wtcmVwYWlyLTIwMjYwOTEyLXYxL2RlbW8t"
        "bGVkLXN0YWdlMS0yMDI2MTAxMi12Mi9zdGFnZTEtbW9jay12b2ljZS1kYXRhYmFzZS1pbnRlZ3JhdGlvbi12MS9pbnRlcmFjdGl2"
        "ZS1ydW50aW1lLXYxL3JlY2VwdGlvbi1pbnRlbnQtdWktdjEvZGlhcnktcmVhZC1yZWNvbm5lY3Rpb24tdjEvcHJvZHVjdC12ZWN0"
        "b3ItdjIuanNvbiIsInNoYTI1NiI6IjFjMGY3YjUxNDNiZDE1MzdiYTlkMmQ3NWQyNzA1YjEwYjVlNDQ3OGFhNWU1YjBkY2YzYzBk"
        "NDVlNWVmYTQyNGQifSwicmVjb3JkZWRfYXQiOiIyMDI2LTEwLTI0VDEyOjQ4OjE1Ljc1Nzg2MyswMDowMCIsInJ1bnRpbWVfYmlu"
        "ZGluZ19yZXF1aXJlZCI6dHJ1ZSwic2NoZW1hX3ZlcnNpb24iOiJhcmlhZG5lLmc0X3N0YWdlMV9zdWNjZXNzb3JfZW50cnlfc2Nv"
        "cGUudjciLCJzZWxlY3RlZF9iYXNlIjp7ImNvbW1pdCI6IjFhMGEwZTJjNWY1OGMzNDJmOTAxMjU4NDU1YjZiZjRmNGQ3NjIxMWUi"
        "LCJ0cmVlIjoiNzYyMzU4Y2UzY2U1M2M0ODhlNjZkMGZiYjFjN2E2ZDIyNDEzYTg5MyJ9LCJzb3VyY2Vfc2hhMjU2Ijp7Im9yY2hl"
        "c3RyYXRpb25faGFybmVzcy9ib3VuZGVkX2cxYi5weSI6IjY0NGVhNWVkMWI0NDg3Y2Y2YmNlMDkwZjVjMDk3ODZlODljNzQyYTdm"
        "ZTY0Nzg3OTMyOGRjMTljY2MyYTBiMmMiLCJvcmNoZXN0cmF0aW9uX2hhcm5lc3MvY29uZmlndXJhdGlvbl9jb3JlLnB5IjoiZjdi"
        "YTdhODBlYjBhNTkwZjlmYjcxYjg2NGU2YzFmOWY0MzI0MWQ5ZjdkNzBhMzhkYTY3YTkyNDNmZWEyMDhlNSIsIm9yY2hlc3RyYXRp"
        "b25faGFybmVzcy9waW5uZWRfcHJvZ3JhbW1lX2dhdGVrZWVwZXIucHkiOiJjMWZlYTlhMjg0OTA2OGVkOGU4N2RiZTFlN2NlYzFj"
        "YzdlNzYyZmEyYmM4ODc2ZmMzMmJiZGE4MGQyMjZjZjM5Iiwib3JjaGVzdHJhdGlvbl9oYXJuZXNzL3Byb2dyYW1tZV9hZG1pc3Np"
        "b24ucHkiOiJhYzgxNmE4YTc5YjJkODIyMmZhMzU3Nzc3YzA3NTk1MDkyN2U4NmNmMzBjOGE1YjI1ZmZkMDhhNDc0MDUyMTgxIiwi"
        "b3JjaGVzdHJhdGlvbl9oYXJuZXNzL3JhaXNhX3BvbGljeS5weSI6IjEwZWU4ODRhMDRmMDMzOTMyN2QzNjUzZmIzMjMxYjAzZTA4"
        "YjA2NDE2MWIyMjNiZWUxNTVhNzQzOGE0Y2VmNDEiLCJvcmNoZXN0cmF0aW9uX2hhcm5lc3MvdHJ1c3RlZF9naXQucHkiOiI0YTg1"
        "NmJmZmUyYjY4ZDdjN2UxODc1MTUyNjI5YzkwMjRhMzI2NzliNTlkOWIxZWQ4MzAxYzM2OGQ0MWZmNTI3Iiwic2NyaXB0cy9yYWlz"
        "YV9hcmlhZG5lX3JlY292ZXJ5X3ByZWZsaWdodC5weSI6ImVkZmQzN2IzMDY3M2I4NTQ0ZDMwOWI1MzJjOTViM2ZkN2MyMGZmNTky"
        "ODgwYThhMDIzNWRmZGU2Y2ZjOGU3ZTQiLCJ0ZXN0cy90ZXN0X2JvdW5kZWRfZzFiLnB5IjoiYmIxYmU4NmNhMzkyMzJmZWEzMGMx"
        "ZWE4NGNkZmIxMTQ0MjhkNTdiZTBmOGY2N2JmN2U4NmRhYWIwYmE3M2JjNSJ9LCJ2b2ljZV9hY3RpdmF0aW9uIjpmYWxzZX0K"
    )
    assert hashlib.sha256(raw).hexdigest() == "f2c85be2e803cf1d051de692d09de4eb98789aa1ce47964c8990146f0f29a607"
    return json.loads(raw)


def _bureau_scope():
    # Accepted V8 fixture stays immutable when this checkout installs V9 scope.
    raw = base64.b64decode(
        "eyJhY3RpdmVfcHJvZmlsZSI6Ikc0X1NUQUdFMV9MT0NBTF9TVUNDRVNTT1IiLCJhZG1pc3Npb25fZ3JhbnRzX3J1bnRpbWVfYXV0"
        "aG9yaXR5IjpmYWxzZSwiYWxsb3dlZF9lZmZlY3RzIjpbImNvbnRyb2xfcGxhbmVfZWRpdCIsInByb2R1Y3RfYmVoYXZpb3JfY2hh"
        "bmdlIiwicmVwb3NpdG9yeV9yZWFkIiwidGFza19icmFuY2hfY29tbWl0IiwidGFza19icmFuY2hfcHVzaCJdLCJhbGxvd2VkX3Bh"
        "dGhzIjpbImFwcC9zZXJ2aWNlcy9yZWNlcHRpb25fb25lX3Byb3Bvc2FsX3J1bnRpbWUucHkiLCJvcmNoZXN0cmF0aW9uL2NvbnRp"
        "bnVpdHkvcmVjZXB0aW9uLW9uZS1idXJlYXUtdHlwZWQtcGxhbi1wcm90b2NvbC9vcGVyYXRvci1jYXRhbG9nLmpzb24iLCJzY3Jp"
        "cHRzL3JlY2VwdGlvbl9vbmVfYnVyZWF1X3R5cGVkX3BsYW5fcHJvdG9jb2wucHkiLCJzdGFnZTFfZGVtb19odHRwLnB5Iiwic3Rh"
        "dGljL2RlbW8vc3RhZ2UxLWludGVyYWN0aXZlLmpzIiwidGVzdHMvdGVzdF9yZWNlcHRpb25fb25lX3NlbGVjdGVkX2NvbnRleHQu"
        "cHkiLCJ0ZXN0cy90ZXN0X3N0YWdlMV9idXJlYXVfcHJvamVjdGlvbi5weSIsInRlc3RzL3Rlc3Rfc3RhZ2UxX2J1cmVhdV9zdWdn"
        "ZXN0aW9uLmNqcyJdLCJhbGxvd2VkX3Rhc2tfa2luZCI6Imc0X3N0YWdlMV9sb2NhbF9zdWNjZXNzb3IiLCJjb250cm9sX3NoYTI1"
        "NiI6eyJvcmNoZXN0cmF0aW9uL2hhcm5lc3Nfc2V0dGluZ3MvcHJvZ3JhbW1lX3JlY292ZXJ5LnlhbWwiOiJhMjU3ODk0YTY2Njdj"
        "NGNkZGUyODBlZjVlYzE3Y2RjYzA1NTlkZDc3MDA5MmIyZGVjZDI3NmFiNDJkYzNiZDMyIiwib3JjaGVzdHJhdGlvbl9oYXJuZXNz"
        "L2JvdW5kZWRfZzFiLnB5IjoiYWE3NDk3OWVmNzM2OWU2OGNiNmUzM2NhZGYyOWU3YmU0NTEzNzBiZTRlYTZhZjZjOTZkZDBlMjlk"
        "N2ViMGY5MyIsIm9yY2hlc3RyYXRpb25faGFybmVzcy9yYWlzYV9wb2xpY3kucHkiOiIwZjkxM2EzNTFlNDA3N2ZhMmU4NjM2YmNj"
        "OTE2OWY0MmYwZDQ1YjlhNmNlMjU0NjlhNzM5NjNmY2ViYmIxY2FjIiwidGVzdHMvdGVzdF9nNF9zdGFnZTFfc3VjY2Vzc29yX2Vu"
        "dHJ5LnB5IjoiMGZjNmM3ODBlYmRjY2RkOTQ2ZGJhNWI2YjFmYmRiOTdkMWMzM2MzMzRmMTg3MTJkODBiNGQzMTEyODMyZTY5YiJ9"
        "LCJleGNsdWRlZF9lZmZlY3RzIjpbInVucmV2aWV3ZWRfYXBwbGljYXRpb25fb3JfZGF0YWJhc2VfcnVudGltZSIsInVucmV2aWV3"
        "ZWRfYnJvd3Nlcl9vcl9taWNyb3Bob25lX3J1bnRpbWUiLCJ1bnJldmlld2VkX3ZvaWNlX2NoaWxkX29yX25ldHdvcmtfZWdyZXNz"
        "IiwicHJvdmlkZXJfaW52b2NhdGlvbiIsInJlYWxfZGF0YV9hY2Nlc3MiLCJwcm90ZWN0ZWRfcmVmX21vdmVtZW50IiwiZGVwbG95"
        "bWVudCIsInB1YmxpY19saXN0ZW5lciJdLCJtYXBwaW5nX3JldmlldyI6eyJwYXRoIjoiQzovVXNlcnMvdGhlcmUvRU1SNC10b29s"
        "cy9zZWxlY3RlZC1jb250ZXh0LWJ1cmVhdS1jYW5kaWRhdGUtdjIvaW5kZXBlbmRlbnQtY29tYmluZWQtc291cmNlLW1hcHBpbmct"
        "YmluZGluZy12Mi5qc29uIiwic2hhMjU2IjoiOTVkMjc0ZGRjYzU3NGJiNGFmNjdlMTE0NTQ5ZmUzZDVjYWVkODQ0NDcyNzk0NWZk"
        "NmZmOWFlNjE1YWNkZjVlMSJ9LCJwcmVkZWNlc3Nvcl9zY29wZSI6eyJzaGEyNTYiOiJmMmM4NWJlMmU4MDNjZjFkMDUxZGU2OTJk"
        "MDlkZTRlYjk4Nzg5YWExY2U0Nzk2NGM4OTkwMTQ2ZjBmMjlhNjA3In0sInByb2R1Y3Rfc2hhMjU2Ijp7ImFwcC9zZXJ2aWNlcy9y"
        "ZWNlcHRpb25fb25lX3Byb3Bvc2FsX3J1bnRpbWUucHkiOiIyZTM2ODdkZTVjY2UzODMzNTFlNmJiNTllYTM3YmQxMzY1M2MyYTEz"
        "NDlmYWUxYjZiYmNjMGRkY2U2ZmIxZmNiIiwib3JjaGVzdHJhdGlvbi9jb250aW51aXR5L3JlY2VwdGlvbi1vbmUtYnVyZWF1LXR5"
        "cGVkLXBsYW4tcHJvdG9jb2wvb3BlcmF0b3ItY2F0YWxvZy5qc29uIjoiZmI5NjQyMDg0NzdmMTJmMDg0YWFjODc1MGZlMjVlN2Yy"
        "YzVhNWQ2NDhhYjYyZDI5ZjUyMWVlNWQ4MDE5ZjU3OSIsInNjcmlwdHMvcmVjZXB0aW9uX29uZV9idXJlYXVfdHlwZWRfcGxhbl9w"
        "cm90b2NvbC5weSI6IjQwNmE1YjhiY2FhMjgyYjY4Njk5NzA5MjAzMzQyZDhlMTA4OTM2YjgzNjQ0YzllN2I3ZTAzNTlhMzhiYWUx"
        "OWQiLCJzdGFnZTFfZGVtb19odHRwLnB5IjoiYzU5NGMxYzBiZmFjNzJjNjM5MzRiNjRjNzZkM2Y3NjdhZDlmNWUxZjFjMzUwOGVi"
        "NWFkMmQyMzZkZTliMDUyOCIsInN0YXRpYy9kZW1vL3N0YWdlMS1pbnRlcmFjdGl2ZS5qcyI6ImNjZmNiMzI3YjgyNjQyMDE3NzYw"
        "YmU2NmUzZmNhYTI0MTZmNDI1ODExM2Q5MjRkNzEzZmIzZWIzMjUyZDJlY2EiLCJ0ZXN0cy90ZXN0X3JlY2VwdGlvbl9vbmVfc2Vs"
        "ZWN0ZWRfY29udGV4dC5weSI6IjFlYTE1Yjk0NGRhNTJjN2IwN2E3MDQwYzAwZDNiMDljYWU1YTFjZWM3MjdhYmM2NDU5MjBmODAy"
        "OTY5MDJhNTUiLCJ0ZXN0cy90ZXN0X3N0YWdlMV9idXJlYXVfcHJvamVjdGlvbi5weSI6ImRkOWU0NGVjZjAyYjNjMjc2YTMzYzMy"
        "NWRkNGQ5OTYzOWVmYjQ3ZmNhMDhmNTM4OGFmY2ZlMzg4MzVlMDE0OTMiLCJ0ZXN0cy90ZXN0X3N0YWdlMV9idXJlYXVfc3VnZ2Vz"
        "dGlvbi5janMiOiIzZTVlNTgwMjQwYTk4NDI1NDI5ZGIzNzcyMTE2NTE1NjA3YjZiZmI4N2FmNWY0YTUyZGZkNDZlZjM4ZmZlZjdj"
        "In0sInByb2R1Y3RfdmVjdG9yIjp7InBhdGgiOiJDOi9Vc2Vycy90aGVyZS9FTVI0LXRvb2xzL3NlbGVjdGVkLWNvbnRleHQtYnVy"
        "ZWF1LWNhbmRpZGF0ZS12Mi9wcm9kdWN0LXZlY3Rvci12Mi5qc29uIiwic2hhMjU2IjoiODk3M2JiOWJkOWQyNDMxZDNiY2RhM2Mx"
        "ZmYwNjk4ZGY1NzAzZGMxZGU3MDliZjYzOTkxNjkwMDUwZmE2MDk2YyJ9LCJyZWNvcmRlZF9hdCI6IjIwMjYtMTAtMjVUMTQ6NTk6"
        "MTQrMDA6MDAiLCJydW50aW1lX2JpbmRpbmdfcmVxdWlyZWQiOnRydWUsInNjaGVtYV92ZXJzaW9uIjoiYXJpYWRuZS5nNF9zdGFn"
        "ZTFfc3VjY2Vzc29yX2VudHJ5X3Njb3BlLnY4Iiwic2VsZWN0ZWRfYmFzZSI6eyJjb21taXQiOiJmNTkyZTRkOTljMzQyNDM5OTZm"
        "NmJmNTY3NDQzMmIyZWI2Zjg1N2YwIiwidHJlZSI6IjhlMjc2NzJhZWE0ZWMzNDBiMmM1OGYxN2NhZTg3YjBjMzlhNGMzOGYifSwi"
        "c291cmNlX3NoYTI1NiI6eyJvcmNoZXN0cmF0aW9uX2hhcm5lc3MvYm91bmRlZF9nMWIucHkiOiJhYTc0OTc5ZWY3MzY5ZTY4Y2I2"
        "ZTMzY2FkZjI5ZTdiZTQ1MTM3MGJlNGVhNmFmNmM5NmRkMGUyOWQ3ZWIwZjkzIiwib3JjaGVzdHJhdGlvbl9oYXJuZXNzL2NvbmZp"
        "Z3VyYXRpb25fY29yZS5weSI6ImY3YmE3YTgwZWIwYTU5MGY5ZmI3MWI4NjRlNmMxZjlmNDMyNDFkOWY3ZDcwYTM4ZGE2N2E5MjQz"
        "ZmVhMjA4ZTUiLCJvcmNoZXN0cmF0aW9uX2hhcm5lc3MvcGlubmVkX3Byb2dyYW1tZV9nYXRla2VlcGVyLnB5IjoiYzFmZWE5YTI4"
        "NDkwNjhlZDhlODdkYmUxZTdjZWMxY2M3ZTc2MmZhMmJjODg3NmZjMzJiYmRhODBkMjI2Y2YzOSIsIm9yY2hlc3RyYXRpb25faGFy"
        "bmVzcy9wcm9ncmFtbWVfYWRtaXNzaW9uLnB5IjoiYWM4MTZhOGE3OWIyZDgyMjJmYTM1Nzc3N2MwNzU5NTA5MjdlODZjZjMwYzhh"
        "NWIyNWZmZDA4YTQ3NDA1MjE4MSIsIm9yY2hlc3RyYXRpb25faGFybmVzcy9yYWlzYV9wb2xpY3kucHkiOiIwZjkxM2EzNTFlNDA3"
        "N2ZhMmU4NjM2YmNjOTE2OWY0MmYwZDQ1YjlhNmNlMjU0NjlhNzM5NjNmY2ViYmIxY2FjIiwib3JjaGVzdHJhdGlvbl9oYXJuZXNz"
        "L3RydXN0ZWRfZ2l0LnB5IjoiNGE4NTZiZmZlMmI2OGQ3YzdlMTg3NTE1MjYyOWM5MDI0YTMyNjc5YjU5ZDliMWVkODMwMWMzNjhk"
        "NDFmZjUyNyIsInNjcmlwdHMvcmFpc2FfYXJpYWRuZV9yZWNvdmVyeV9wcmVmbGlnaHQucHkiOiJlZGZkMzdiMzA2NzNiODU0NGQz"
        "MDliNTMyYzk1YjNmZDdjMjBmZjU5Mjg4MGE4YTAyMzVkZmRlNmNmYzhlN2U0IiwidGVzdHMvdGVzdF9ib3VuZGVkX2cxYi5weSI6"
        "ImJiMWJlODZjYTM5MjMyZmVhMzBjMWVhODRjZGZiMTE0NDI4ZDU3YmUwZjhmNjdiZjdlODZkYWFiMGJhNzNiYzUifSwidm9pY2Vf"
        "YWN0aXZhdGlvbiI6ZmFsc2V9Cg=="
    )
    assert hashlib.sha256(raw).hexdigest() == "25878fe3ae6e0b159edd73a5a789ba3b8f24074d5f70c49577342c0cea919666"
    return json.loads(raw)

def test_selected_bureau_successor_exact_paths_and_unfrozen_inputs():
    scope = _bureau_scope()
    assert bounded_g1b.G4_INTENT_SCOPE_SCHEMA == "ariadne.g4_stage1_successor_entry_scope.v7"
    assert bounded_g1b.G4_BUREAU_SCOPE_SCHEMA == "ariadne.g4_stage1_successor_entry_scope.v8"
    assert bounded_g1b.G4_BUREAU_BASE == {
        "commit": "f592e4d99c34243996f6bf5674432b2eb6f857f0",
        "tree": "8e27672aea4ec340b2c58f17cae87b0c39a4c38f",
    }
    expected = set(bounded_g1b.G4_BUREAU_PRODUCT_SHA)
    assert len(expected) == 8
    assert scope["allowed_paths"] == sorted(expected)
    assert set(raisa_policy.g4_stage1_successor_profile()["allowed_paths"]) >= expected
    assert scope["runtime_binding_required"] is True
    assert scope["admission_grants_runtime_authority"] is False
    assert scope["voice_activation"] is False
    for kind, stage, paths in (
        ("enable_g4_stage1_successor", "enable", bounded_g1b.G4_BUREAU_CONTROL),
        ("implement_g4_stage1_successor", "apply", bounded_g1b.G4_BUREAU_PRODUCT),
    ):
        binding = {"schema_version": bounded_g1b.G4_BUREAU_SCHEMA,
                   "operation_kind": kind, "stage": stage,
                   "repair_sha256": {path: {} for path in paths}}
        assert bounded_g1b.operation_paths(kind, binding) == paths
        assert bounded_g1b._operation(kind, binding)["g4_selected_bureau_source"] is True
        changed = copy.deepcopy(binding)
        changed["repair_sha256"]["app/main.py"] = {}
        with pytest.raises(bounded_g1b.BoundedG1BError):
            bounded_g1b.operation_paths(kind, changed)
    if (bounded_g1b.G4_BUREAU_VECTOR_SHA == "0" * 64
            or bounded_g1b.G4_BUREAU_MAPPING_SHA == "0" * 64):
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b.validate_g4_bureau_scope(scope)
        assert caught.value.reason_code == "bounded_g4_bureau_inputs_unfrozen"
    else:
        bounded_g1b.validate_g4_bureau_scope(scope)


def test_intention_diary_scope_exact_and_ci_scope_separate():
    scope = _intention_scope()
    bounded_g1b.validate_g4_intent_scope(scope)
    assert scope["allowed_paths"] == sorted(bounded_g1b.G4_INTENT_PRODUCT)
    assert scope["product_sha256"] == bounded_g1b.G4_INTENT_PRODUCT_SHA
    assert scope["admission_grants_runtime_authority"] is False
    assert bounded_g1b.G4_CI_WORKFLOW not in scope["allowed_paths"]
    for field, bad in (("allowed_paths", ["app/main.py"]),
                       ("allowed_effects", ["provider_invocation"]),
                       ("admission_grants_runtime_authority", True),
                       ("runtime_binding_required", False),
                       ("voice_activation", True),
                       ("selected_base", {"commit": "0" * 40, "tree": "0" * 40})):
        changed = copy.deepcopy(scope)
        changed[field] = bad
        with pytest.raises(bounded_g1b.BoundedG1BError):
            bounded_g1b.validate_g4_intent_scope(changed)


def test_intention_diary_enable_apply_paths_are_exact():
    for kind, stage, expected in (
        ("enable_g4_stage1_successor", "enable", bounded_g1b.G4_INTENT_CONTROL),
        ("implement_g4_stage1_successor", "apply", bounded_g1b.G4_INTENT_PRODUCT),
    ):
        binding = {"schema_version": bounded_g1b.G4_INTENT_SCHEMA,
                   "operation_kind": kind, "stage": stage,
                   "repair_sha256": {p: {} for p in expected}}
        assert bounded_g1b.operation_paths(kind, binding) == expected
        for paths in (set(expected) - {next(iter(expected))},
                      set(expected) | {"app/main.py"}):
            changed = copy.deepcopy(binding)
            changed["repair_sha256"] = {p: {} for p in paths}
            with pytest.raises(bounded_g1b.BoundedG1BError):
                bounded_g1b.operation_paths(kind, changed)
        changed = copy.deepcopy(binding)
        changed["stage"] = "apply" if stage == "enable" else "enable"
        with pytest.raises(bounded_g1b.BoundedG1BError):
            bounded_g1b.operation_paths(kind, changed)


def test_ci_and_intention_review_verdicts_remain_separate():
    subject = "b" * 64
    ci_path = (bounded_g1b.G4_CI_EVIDENCE /
               "ci-maintenance-control-source-v1/"
               "independent-enable-exact-subject-review-v1.json")
    intent_path = (bounded_g1b.G4_INTENT_ROOT / "admission-source-v4/"
                   "independent-enable-development-subject-review-v2.json")
    cases = (
        (bounded_g1b._g4_ci_review, ci_path, "enable", "development",
         "PASS_G4_STAGE1_CI_MAINTENANCE_EXACT_ADMISSION_SUBJECT",
         "/root/audit_admission_route_review"),
        (bounded_g1b._g4_intent_review, intent_path, "enable", "development",
         "PASS_G4_STAGE1_INTENTION_DIARY_EXACT_ADMISSION_SUBJECT",
         "/root/frontier18_exact_metadata_review"),
    )
    for validator, path, stage, phase, verdict, actor in cases:
        row = {"path": path.as_posix(), "sha256": "a" * 64}
        review = {"schema": "emr4.g4_operation_review.v1", "status": "PASS",
                  "verdict": verdict, "subject_sha256": subject,
                  "independent": True, "implementation_authorship": False,
                  "blocking_findings": [], "reviewer_agent": actor,
                  "stage": stage, "phase": phase}
        def read(_path, _digest):
            return json.dumps(review).encode()
        assert validator(read, row, bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT,
                         subject, stage, phase) == review
        for field, bad in (("verdict", "PASS_OTHER_ROUTE"),
                           ("independent", False),
                           ("implementation_authorship", True),
                           ("subject_sha256", "0" * 64)):
            changed = copy.deepcopy(review)
            changed[field] = bad
            def rejected_read(_path, _digest):
                return json.dumps(changed).encode()
            with pytest.raises(bounded_g1b.BoundedG1BError):
                validator(rejected_read, row,
                          bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT,
                          subject, stage, phase)


# Current v2 correction tests. The v1 tests above retain the frozen prestate and
# frozen afterimages of their own accepted transition.
def _correction_scope():
    raw = (Path("C:/Users/there/EMR4-tools/g4-stage1-header-control-actual-v1") / bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == "21a77991d10acf9cb62bea845bfeeb51b23cc4b5804edde578528f883203b1e5"
    return json.loads(raw)

def test_header_correction_scope_and_literal_operations():
    scope = _correction_scope()
    assert bounded_g1b.validate_g4_header_correction_scope(scope) == scope["source_sha256"]
    assert scope["product_sha256"] == {"stage1_demo_http.py":
        "49c9424dc8a6f92f9c312c0d198691901869752889481a1d5f8b41168cce63dc"}
    for kind, paths in (
        ("enable_g4_stage1_successor", bounded_g1b.G4_HEADER_CONTROL),
        ("implement_g4_stage1_successor", bounded_g1b.G4_HEADER_PRODUCT)):
        q = {"schema_version": bounded_g1b.G4_HEADER_BINDING_SCHEMA,
             "operation_kind": kind, "repair_sha256": {p: {} for p in paths}}
        assert bounded_g1b.operation_paths(kind, q) == paths
        assert bounded_g1b._operation(kind, q)["g4_header_correction"] is True
        assert bounded_g1b._operation(kind, q)["profile"] == raisa_policy.G4_STAGE1_SUCCESSOR_PROFILE
    assert len(bounded_g1b.G4_HEADER_CONTROL) == 3
    assert len(bounded_g1b.G4_HEADER_PRODUCT) == 1

@pytest.mark.parametrize("change", [
    {"selected_base": {"commit": "0" * 40, "tree": "0" * 40}},
    {"selected_base": bounded_g1b.G4_STAGE1_SUCCESSOR_BASE},
    {"voice_activation": True},
    {"admission_grants_runtime_authority": True},
    {"runtime_binding_required": False},
    {"allowed_paths": ["static/demo/stage1-interactive.js"]},
    {"allowed_effects": ["provider_invocation"]},
    {"recorded_at": None},
])
def test_header_correction_scope_rejects_stale_or_wider_contract(change):
    scope = _correction_scope()
    scope.update(change)
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b.validate_g4_header_correction_scope(scope)
    assert caught.value.reason_code == "bounded_g4_header_scope_boundary"

def test_header_correction_rejects_any_other_product_hash():
    scope = _correction_scope()
    scope["product_sha256"]["stage1_demo_http.py"] = "0" * 64
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b.validate_g4_header_correction_scope(scope)
    assert caught.value.reason_code == "bounded_g4_header_product_map"

@pytest.mark.parametrize("field", ["predecessor_scope", "predecessor_publication", "correction_source_review"])
def test_header_correction_literal_evidence_cannot_be_substituted(field):
    scope = _correction_scope()
    scope[field]["path"] = "C:/unpermitted-authored-placeholder.json"
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b.validate_g4_header_correction_scope(scope)
    assert caught.value.reason_code == "bounded_g4_header_literal_evidence"

def test_header_correction_keeps_eight_closed_source_rows():
    scope = _correction_scope()
    assert len(scope["source_sha256"]) == 8
    for path in scope["source_sha256"]:
        changed = copy.deepcopy(scope)
        if path == bounded_g1b.G4_HEADER_CODE:
            changed["control_sha256"][path] = "0" * 64
        else:
            changed["source_sha256"][path] = "0" * 64
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b.validate_g4_header_correction_scope(changed)
        assert caught.value.reason_code == "bounded_g4_header_source_vector"

@pytest.mark.parametrize("paths", [
    frozenset(bounded_g1b.G4_STAGE1_SUCCESSOR_PRODUCT_AFTERIMAGES),
    frozenset({"stage1_demo_http.py", "static/demo/stage1-interactive.js"}),
    frozenset({"app/main.py"}),
    frozenset(),
])
def test_header_correction_exact_one_delta_is_not_profile_ceiling(paths):
    q = {"schema_version": bounded_g1b.G4_HEADER_BINDING_SCHEMA,
         "operation_kind": "implement_g4_stage1_successor",
         "repair_sha256": {path: {} for path in paths}}
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b.operation_paths(q["operation_kind"], q)
    assert caught.value.reason_code == "bounded_g4_header_changed_paths"

def test_header_correction_does_not_relax_v1_exact_eight():
    q = {"schema_version": "ariadne.g4_stage1_successor_operation_binding.v1",
         "operation_kind": "implement_g4_stage1_successor",
         "repair_sha256": {"stage1_demo_http.py": {}}}
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b.operation_paths(q["operation_kind"], q)
    assert caught.value.reason_code == "bounded_g4_stage1_successor_changed_paths"
    q["repair_sha256"] = {p: {} for p in bounded_g1b.G4_STAGE1_SUCCESSOR_PRODUCT_AFTERIMAGES}
    assert bounded_g1b.operation_paths(q["operation_kind"], q) == frozenset(q["repair_sha256"])

def test_header_source_review_uses_actual_split_blocker_schema():
    row = bounded_g1b.G4_HEADER_SOURCE_REVIEW
    raw = Path(row["path"]).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == row["sha256"]
    review = json.loads(raw)
    assert "reviewer_agent" not in review
    bounded_g1b._g4_header_product_source_acceptance(review)
    for field, value in (("independent", False), ("implementation_authorship", True),
                         ("blocking_findings_for_patch", ["authored"]), ("blocking_findings_for_current_fixture", ["authored"])):
        changed = copy.deepcopy(review)
        changed[field] = value
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b._g4_header_product_source_acceptance(changed)
        assert caught.value.reason_code == "bounded_g4_header_product_source_acceptance"


# Dormant v3 voice source: exercise the narrow validators, not runtime authority.
def _voice_scope():
    path = Path("C:/Users/there/EMR4-migration/20260911-v1/current-control-repair-20260912-v1/demo-led-stage1-20261012-v2/stage1-voice-current-entry-source-v1/candidate-source-v2/orchestration/programme/g4-stage1-successor-entry-scope.json")
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == "516c286e63e94c5968eb6187783f62eb4d65b3a9eb6bfbe48a7a719ba03d037b"
    return json.loads(raw)


def _voice_binding(kind="enable_g4_stage1_successor"):
    scope = _voice_scope()
    paths = (bounded_g1b.G4_VOICE_CONTROL if kind.startswith("enable_")
             else bounded_g1b.G4_VOICE_PRODUCT)
    return {"schema_version": bounded_g1b.G4_VOICE_BINDING_SCHEMA,
            "operation_id": "voice-source-enable-development",
            "operation_kind": kind, "phase": "development",
            "base_commit": bounded_g1b.G4_VOICE_BASE["commit"],
            "base_tree": bounded_g1b.G4_VOICE_BASE["tree"],
            "expected_head": bounded_g1b.G4_VOICE_BASE["commit"],
            "expected_index_tree": bounded_g1b.G4_VOICE_BASE["tree"],
            "candidate_tree": "a" * 40, "source_sha256": scope["source_sha256"],
            "payload_sha256": {bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE: "b" * 64},
            "repair_sha256": {p: {"before_sha256": bounded_g1b.G4_VOICE_PREIMAGES[p],
                                  "after_sha256": "c" * 64} for p in paths},
            "source_review": None,
            "predecessor_publication": scope["predecessor_publication"],
            "correction_source_review": scope["correction_source_review"],
            "activation_acceptance": None}


def test_voice_v3_exact_three_path_dispatch_preserves_legacy_schemas():
    scope = _voice_scope()
    assert bounded_g1b.validate_g4_voice_source_scope(scope) == scope["source_sha256"]
    for kind, paths in (("enable_g4_stage1_successor", bounded_g1b.G4_VOICE_CONTROL),
                        ("implement_g4_stage1_successor", bounded_g1b.G4_VOICE_PRODUCT)):
        q = _voice_binding(kind)
        assert bounded_g1b.operation_paths(kind, q) == paths
        assert len(paths) == 3
        operation = bounded_g1b._operation(kind, q)
        assert operation["g4_voice_source"] is True
        assert operation["gate"] == "G4"
        assert operation["profile"] == raisa_policy.G4_STAGE1_SUCCESSOR_PROFILE
        assert "g4_header_correction" not in operation
    assert bounded_g1b.G4_HEADER_BINDING_SCHEMA.endswith(".v2")
    assert bounded_g1b.G4_HEADER_PRODUCT == {"stage1_demo_http.py"}


@pytest.mark.parametrize("change", [
    {"schema_version": bounded_g1b.G4_HEADER_SCOPE_SCHEMA},
    {"selected_base": bounded_g1b.G4_HEADER_BASE},
    {"selected_base": {"commit": bounded_g1b.G4_VOICE_BASE["commit"], "tree": "0" * 40}},
    {"voice_activation": True}, {"runtime_binding_required": False},
    {"admission_grants_runtime_authority": True}, {"native08_dependency_only": False},
    {"allowed_paths": ["stage1_demo_http.py"]},
    {"allowed_effects": ["provider_invocation"]}, {"recorded_at": None},
    {"recorded_at": "malformed"}, {"recorded_at": "2026-10-17T00:00:00"},
])
def test_voice_scope_rejects_stale_or_wider_contract(change):
    scope = _voice_scope()
    scope.update(change)
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b.validate_g4_voice_source_scope(scope)
    assert caught.value.reason_code == "bounded_g4_voice_scope_boundary"


def test_voice_scope_rejects_extra_keys_product_replacement_and_source_drift():
    scope = _voice_scope()
    for mutate, reason in (
        (lambda s: s.update(extra=True), "bounded_g4_voice_scope_schema"),
        (lambda s: s["product_sha256"].update({"stage1_demo_voice.py": "0" * 64}),
         "bounded_g4_voice_product_map"),
        (lambda s: s["source_sha256"].update({"orchestration_harness/trusted_git.py": "0" * 64}),
         "bounded_g4_voice_source_vector"),
        (lambda s: s["control_sha256"].update({bounded_g1b.G4_VOICE_CODE: "0" * 64}),
         "bounded_g4_voice_source_vector"),
        (lambda s: s["predecessor_publication"].update(sha256="0" * 64),
         "bounded_g4_voice_literal_evidence"),
        (lambda s: s["correction_source_review"].update(path="C:/substitute.json"),
         "bounded_g4_voice_source_review_pin"),
    ):
        changed = copy.deepcopy(scope)
        mutate(changed)
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b.validate_g4_voice_source_scope(changed)
        assert caught.value.reason_code == reason


@pytest.mark.parametrize("kind", ["enable_g4_stage1_successor", "implement_g4_stage1_successor"])
def test_voice_dispatch_rejects_any_extra_or_missing_path(kind):
    for extra in (True, False):
        q = _voice_binding(kind)
        if extra:
            q["repair_sha256"]["app/main.py"] = {}
        else:
            q["repair_sha256"].pop(next(iter(q["repair_sha256"])))
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b.operation_paths(kind, q)
        assert caught.value.reason_code == "bounded_g4_voice_changed_paths"


@pytest.mark.parametrize("field", [
    "schema_version", "operation_id", "operation_kind", "phase", "base_commit",
    "base_tree", "expected_head", "expected_index_tree", "candidate_tree",
    "source_sha256", "payload_sha256", "repair_sha256", "predecessor_publication",
    "correction_source_review", "activation_acceptance",
])
def test_voice_exact_subject_changes_for_every_authority_bearing_field(field):
    q = _voice_binding()
    before = bounded_g1b.g4_voice_source_review_subject(q)
    changed = copy.deepcopy(q)
    changed[field] = {"substituted": True} if isinstance(q[field], dict) else "substituted"
    assert bounded_g1b.g4_voice_source_review_subject(changed) != before
    q["source_review"] = {"path": "not-in-self-referential-subject", "sha256": "d" * 64}
    assert bounded_g1b.g4_voice_source_review_subject(q) == before


def test_voice_product_review_requires_exact_map_and_independent_named_reviewer():
    review = {"schema": "emr4.stage1_voice_current_product_source_review.v1",
              "verdict": "PASS_SOURCE_ONLY", "reviewer_agent": "/root/voice_entry_scope_review",
              "independent": True, "implementation_authorship": False,
              "blocking_findings": [], "product_sha256": dict(bounded_g1b.G4_VOICE_AFTER)}
    bounded_g1b._g4_voice_product_source_acceptance(review)
    for field, value in (("reviewer_agent", "/root/author"), ("independent", False),
                         ("implementation_authorship", True), ("blocking_findings", ["blocker"]),
                         ("product_sha256", {}), ("verdict", "PENDING")):
        changed = copy.deepcopy(review)
        changed[field] = value
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b._g4_voice_product_source_acceptance(changed)
        assert caught.value.reason_code == "bounded_g4_voice_product_source_acceptance"


@pytest.mark.parametrize("kind", ["enable_g4_stage1_successor", "implement_g4_stage1_successor"])
@pytest.mark.parametrize("phase", ["development", "pre-push", "post-push"])
def test_voice_subject_review_rejects_swapped_subject_reviewer_and_operation_path(kind, phase):
    q = _voice_binding(kind)
    q["phase"] = phase
    subject = bounded_g1b.g4_voice_source_review_subject(q)
    root = bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT
    operation = "enable" if kind.startswith("enable_") else "implement"
    suffix = "" if phase == "development" else "-" + phase
    path = root / ("stage1-voice-current-entry-source-v1/independent-" + operation
                   + suffix + "-exact-subject-review-v1.json")
    row = {"path": str(path), "sha256": "a" * 64}
    verdict = "PASS_G4_STAGE1_VOICE_SOURCE_EXACT_ADMISSION_SUBJECT"
    review = {"schema": "emr4.g4_operation_review.v1", "status": "PASS", "verdict": verdict,
              "independent": True, "implementation_authorship": False, "blocking_findings": [],
              "reviewer_agent": "/root/voice_entry_scope_review", "subject_sha256": subject}
    reads = []
    def read(path, digest):
        reads.append((path, digest))
        return json.dumps(review_body).encode()
    def check(value, selected_kind=kind, selected_phase=phase):
        nonlocal review_body
        review_body = value
        return bounded_g1b._g4_voice_subject_review(
            read, row, root, subject, verdict, selected_kind, selected_phase)
    review_body = review
    assert check(review) == review
    assert reads == [(path, row["sha256"])]
    for field, value in (("subject_sha256", "0" * 64), ("reviewer_agent", "/root/author"),
                         ("independent", False), ("implementation_authorship", True),
                         ("blocking_findings", ["blocker"]), ("status", "PENDING")):
        changed = copy.deepcopy(review)
        changed[field] = value
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            check(changed)
        assert caught.value.reason_code == "bounded_g4_voice_independent_subject"
    other_kind = ("implement_g4_stage1_successor" if kind.startswith("enable_")
                  else "enable_g4_stage1_successor")
    for selected_kind, selected_phase, reason in (
        (other_kind, phase, "bounded_g4_voice_review_path"),
        ("unknown", phase, "bounded_g4_voice_review_kind"),
        (kind, "unknown", "bounded_g4_voice_review_phase"),
        (kind, None, "bounded_g4_voice_review_phase"),
        *((kind, other_phase, "bounded_g4_voice_review_path")
          for other_phase in ("development", "pre-push", "post-push") if other_phase != phase),
    ):
        reads.clear()
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            check(review, selected_kind, selected_phase)
        assert caught.value.reason_code == reason
        assert reads == []


def test_voice_six_phase_kind_subjects_remain_distinct_and_bind_head_and_index():
    subjects = set()
    for kind in ("enable_g4_stage1_successor", "implement_g4_stage1_successor"):
        for phase in ("development", "pre-push", "post-push"):
            q = _voice_binding(kind)
            q["phase"] = phase
            subject = bounded_g1b.g4_voice_source_review_subject(q)
            subjects.add(subject)
            for field in ("expected_head", "expected_index_tree"):
                changed = copy.deepcopy(q)
                changed[field] = "0" * 40
                assert bounded_g1b.g4_voice_source_review_subject(changed) != subject
    assert len(subjects) == 6


def test_voice_control_publication_effect_review_keeps_its_fixed_path():
    root = bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT
    path = root / "stage1-voice-current-entry-source-v1/independent-voice-control-push-effect-review-v1.json"
    row = {"path": str(path), "sha256": "a" * 64}
    verdict = "PASS_G4_STAGE1_VOICE_SOURCE_CONTROL_PUBLICATION_EFFECT"
    subject = "c" * 40
    review = {"schema": "emr4.g4_operation_review.v1", "status": "PASS", "verdict": verdict,
              "independent": True, "implementation_authorship": False, "blocking_findings": [],
              "reviewer_agent": "/root/voice_entry_scope_review", "subject_sha256": subject}
    reads = []
    def read(selected_path, digest):
        reads.append((selected_path, digest))
        return json.dumps(review).encode()
    assert bounded_g1b._g4_voice_subject_review(read, row, root, subject, verdict) == review
    assert reads == [(path, row["sha256"])]


def test_voice_change_pair_rejects_wrong_preimage_afterimage_and_pair_shape():
    for path, after in bounded_g1b.G4_VOICE_AFTER.items():
        before = bounded_g1b.G4_VOICE_PREIMAGES[path]
        pair = {"before_sha256": before, "after_sha256": after}
        assert bounded_g1b._g4_voice_change_pair(path, pair, after) == before
        for field in ("before_sha256", "after_sha256"):
            changed = dict(pair)
            changed[field] = "0" * 64
            with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
                bounded_g1b._g4_voice_change_pair(path, changed, after)
            assert caught.value.reason_code == "bounded_g4_voice_change_preimage"
        pair["extra"] = True
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b._g4_voice_change_pair(path, pair, after)
        assert caught.value.reason_code == "bounded_g4_voice_change_pair"


def test_voice_activation_requires_exact_control_publication_effect():
    q = {"base_commit": "c" * 40, "base_tree": "d" * 40}
    receipt = {"tree": q["base_tree"], "base": bounded_g1b.G4_VOICE_BASE["commit"],
               "commit": q["base_commit"], "candidate": "control", "phase": "push",
               "published_ref": bounded_g1b.G4_STAGE1_INTERACTIVE_BACKEND_REF,
               "whole_inverse_verified_same_attempt": True,
               "protected_refs_unchanged": True, "same_attempt_remote_readback_verified": True}
    bounded_g1b._g4_voice_activation_acceptance(receipt, q)
    for key in receipt:
        changed = copy.deepcopy(receipt)
        changed[key] = False if receipt[key] is True else "substituted"
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b._g4_voice_activation_acceptance(changed, q)
        assert caught.value.reason_code == "bounded_g4_voice_activation_acceptance"


def test_voice_loaded_policy_rejects_configuration_drift_before_configuration_loading():
    scope = _voice_scope()
    payloads = {bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE: bounded_g1b._canonical(scope) + b"\n"}
    payloads.update({path: b"changed" for path in bounded_g1b.G4_VOICE_BASE_CONFIG})
    inputs = bounded_g1b.BoundedG1BInputs({}, {}, payloads, {"scope": scope}, None)
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b._validate_g4_voice_source_loaded_policy(inputs)
    assert caught.value.reason_code == "bounded_g4_voice_configuration_unchanged"


# Additive v4 manual handoff source: narrow current validators, no runtime authority.
def _handoff_scope():
    path = Path("C:/Users/there/EMR4-migration/20260911-v1/current-control-repair-20260912-v1/demo-led-stage1-20261012-v2/stage1-voice-current-entry-source-v1/native-voice-intent-handoff-source-v1/control-admission-source-v1/candidate-source/orchestration/programme/g4-stage1-successor-entry-scope.json")
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == "d2fcc9c4284478a89ea28b44f8ed80731523b67790d03ec2a54fc39966b277df"
    return json.loads(raw)


def _handoff_binding(kind="enable_g4_stage1_successor"):
    scope = _handoff_scope()
    paths = (bounded_g1b.G4_HANDOFF_CONTROL if kind.startswith("enable_")
             else bounded_g1b.G4_HANDOFF_PRODUCT)
    return {"schema_version": bounded_g1b.G4_HANDOFF_BINDING_SCHEMA,
            "operation_id": "voice-source-enable-development",
            "operation_kind": kind, "phase": "development",
            "base_commit": bounded_g1b.G4_HANDOFF_BASE["commit"],
            "base_tree": bounded_g1b.G4_HANDOFF_BASE["tree"],
            "expected_head": bounded_g1b.G4_HANDOFF_BASE["commit"],
            "expected_index_tree": bounded_g1b.G4_HANDOFF_BASE["tree"],
            "candidate_tree": "a" * 40, "source_sha256": scope["source_sha256"],
            "payload_sha256": {bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE: "b" * 64},
            "repair_sha256": {p: {"before_sha256": bounded_g1b.G4_HANDOFF_PREIMAGES[p],
                                  "after_sha256": "c" * 64} for p in paths},
            "source_review": None,
            "predecessor_publication": scope["predecessor_publication"],
            "correction_source_review": scope["correction_source_review"],
            "activation_acceptance": None}


def test_handoff_v4_exact_four_path_dispatch_preserves_legacy_schemas():
    scope = _handoff_scope()
    assert bounded_g1b.validate_g4_handoff_source_scope(scope) == scope["source_sha256"]
    for kind, paths in (("enable_g4_stage1_successor", bounded_g1b.G4_HANDOFF_CONTROL),
                        ("implement_g4_stage1_successor", bounded_g1b.G4_HANDOFF_PRODUCT)):
        q = _handoff_binding(kind)
        assert bounded_g1b.operation_paths(kind, q) == paths
        assert len(paths) == (3 if kind.startswith("enable_") else 4)
        operation = bounded_g1b._operation(kind, q)
        assert operation["g4_handoff_source"] is True
        assert operation["gate"] == "G4"
        assert operation["profile"] == raisa_policy.G4_STAGE1_SUCCESSOR_PROFILE
        assert "g4_header_correction" not in operation
    assert bounded_g1b.G4_HEADER_BINDING_SCHEMA.endswith(".v2")
    assert bounded_g1b.G4_HEADER_PRODUCT == {"stage1_demo_http.py"}
    assert bounded_g1b.G4_VOICE_BINDING_SCHEMA.endswith(".v3")
    for kind, paths in (("enable_g4_stage1_successor", bounded_g1b.G4_VOICE_CONTROL),
                        ("implement_g4_stage1_successor", bounded_g1b.G4_VOICE_PRODUCT)):
        legacy = {"schema_version": bounded_g1b.G4_VOICE_BINDING_SCHEMA,
                  "operation_kind": kind, "repair_sha256": {p: {} for p in paths}}
        assert bounded_g1b.operation_paths(kind, legacy) == paths
        assert bounded_g1b._operation(kind, legacy)["g4_voice_source"] is True


@pytest.mark.parametrize("change", [
    {"schema_version": bounded_g1b.G4_HEADER_SCOPE_SCHEMA},
    {"selected_base": bounded_g1b.G4_HEADER_BASE},
    {"selected_base": {"commit": bounded_g1b.G4_HANDOFF_BASE["commit"], "tree": "0" * 40}},
    {"voice_activation": True}, {"runtime_binding_required": False},
    {"admission_grants_runtime_authority": True}, {"native08_dependency_only": False},
    {"allowed_paths": ["stage1_demo_http.py"]},
    {"allowed_effects": ["provider_invocation"]}, {"recorded_at": None},
    {"recorded_at": "malformed"}, {"recorded_at": "2026-10-17T00:00:00"},
])
def test_handoff_scope_rejects_stale_or_wider_contract(change):
    scope = _handoff_scope()
    scope.update(change)
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b.validate_g4_handoff_source_scope(scope)
    assert caught.value.reason_code == "bounded_g4_handoff_scope_boundary"


def test_handoff_scope_rejects_extra_keys_product_replacement_and_source_drift():
    scope = _handoff_scope()
    for mutate, reason in (
        (lambda s: s.update(extra=True), "bounded_g4_handoff_scope_schema"),
        (lambda s: s["product_sha256"].update({"stage1_demo_voice.py": "0" * 64}),
         "bounded_g4_handoff_product_map"),
        (lambda s: s["source_sha256"].update({"orchestration_harness/trusted_git.py": "0" * 64}),
         "bounded_g4_handoff_source_vector"),
        (lambda s: s["control_sha256"].update({bounded_g1b.G4_HANDOFF_CODE: "0" * 64}),
         "bounded_g4_handoff_source_vector"),
        (lambda s: s["predecessor_publication"].update(sha256="0" * 64),
         "bounded_g4_handoff_literal_evidence"),
        (lambda s: s["correction_source_review"].update(path="C:/substitute.json"),
         "bounded_g4_handoff_source_review_pin"),
    ):
        changed = copy.deepcopy(scope)
        mutate(changed)
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b.validate_g4_handoff_source_scope(changed)
        assert caught.value.reason_code == reason


@pytest.mark.parametrize("kind", ["enable_g4_stage1_successor", "implement_g4_stage1_successor"])
def test_handoff_dispatch_rejects_any_extra_or_missing_path(kind):
    for extra in (True, False):
        q = _handoff_binding(kind)
        if extra:
            q["repair_sha256"]["app/main.py"] = {}
        else:
            q["repair_sha256"].pop(next(iter(q["repair_sha256"])))
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b.operation_paths(kind, q)
        assert caught.value.reason_code == "bounded_g4_handoff_changed_paths"


@pytest.mark.parametrize("field", [
    "schema_version", "operation_id", "operation_kind", "phase", "base_commit",
    "base_tree", "expected_head", "expected_index_tree", "candidate_tree",
    "source_sha256", "payload_sha256", "repair_sha256", "predecessor_publication",
    "correction_source_review", "activation_acceptance",
])
def test_handoff_exact_subject_changes_for_every_authority_bearing_field(field):
    q = _handoff_binding()
    before = bounded_g1b.g4_handoff_source_review_subject(q)
    changed = copy.deepcopy(q)
    changed[field] = {"substituted": True} if isinstance(q[field], dict) else "substituted"
    assert bounded_g1b.g4_handoff_source_review_subject(changed) != before
    q["source_review"] = {"path": "not-in-self-referential-subject", "sha256": "d" * 64}
    assert bounded_g1b.g4_handoff_source_review_subject(q) == before


def test_handoff_product_review_requires_exact_map_and_independent_named_reviewer():
    review = {"schema": "emr4.stage1_voice_current_product_source_review.v1",
              "verdict": "PASS_SOURCE_ONLY", "reviewer_agent": "/root/voice_entry_scope_review",
              "independent": True, "implementation_authorship": False,
              "blocking_findings": [], "product_sha256": dict(bounded_g1b.G4_HANDOFF_AFTER)}
    bounded_g1b._g4_handoff_product_source_acceptance(review)
    for field, value in (("reviewer_agent", "/root/author"), ("independent", False),
                         ("implementation_authorship", True), ("blocking_findings", ["blocker"]),
                         ("product_sha256", {}), ("verdict", "PENDING")):
        changed = copy.deepcopy(review)
        changed[field] = value
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b._g4_handoff_product_source_acceptance(changed)
        assert caught.value.reason_code == "bounded_g4_handoff_product_source_acceptance"


@pytest.mark.parametrize("kind", ["enable_g4_stage1_successor", "implement_g4_stage1_successor"])
@pytest.mark.parametrize("phase", ["development", "pre-push", "post-push"])
def test_handoff_subject_review_rejects_swapped_subject_reviewer_and_operation_path(kind, phase):
    q = _handoff_binding(kind)
    q["phase"] = phase
    subject = bounded_g1b.g4_handoff_source_review_subject(q)
    root = bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT
    operation = "enable" if kind.startswith("enable_") else "implement"
    suffix = "" if phase == "development" else "-" + phase
    path = root / ("stage1-voice-current-entry-source-v1/native-voice-intent-handoff-source-v1/control-admission-source-v1/independent-" + operation
                   + suffix + "-exact-subject-review-v1.json")
    row = {"path": str(path), "sha256": "a" * 64}
    verdict = "PASS_G4_STAGE1_VOICE_SOURCE_EXACT_ADMISSION_SUBJECT"
    review = {"schema": "emr4.g4_operation_review.v1", "status": "PASS", "verdict": verdict,
              "independent": True, "implementation_authorship": False, "blocking_findings": [],
              "reviewer_agent": "/root/voice_entry_scope_review", "subject_sha256": subject}
    reads = []
    def read(path, digest):
        reads.append((path, digest))
        return json.dumps(review_body).encode()
    def check(value, selected_kind=kind, selected_phase=phase):
        nonlocal review_body
        review_body = value
        return bounded_g1b._g4_handoff_subject_review(
            read, row, root, subject, verdict, selected_kind, selected_phase)
    review_body = review
    assert check(review) == review
    assert reads == [(path, row["sha256"])]
    for field, value in (("subject_sha256", "0" * 64), ("reviewer_agent", "/root/author"),
                         ("independent", False), ("implementation_authorship", True),
                         ("blocking_findings", ["blocker"]), ("status", "PENDING")):
        changed = copy.deepcopy(review)
        changed[field] = value
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            check(changed)
        assert caught.value.reason_code == "bounded_g4_handoff_independent_subject"
    other_kind = ("implement_g4_stage1_successor" if kind.startswith("enable_")
                  else "enable_g4_stage1_successor")
    for selected_kind, selected_phase, reason in (
        (other_kind, phase, "bounded_g4_handoff_review_path"),
        ("unknown", phase, "bounded_g4_handoff_review_kind"),
        (kind, "unknown", "bounded_g4_handoff_review_phase"),
        (kind, None, "bounded_g4_handoff_review_phase"),
        *((kind, other_phase, "bounded_g4_handoff_review_path")
          for other_phase in ("development", "pre-push", "post-push") if other_phase != phase),
    ):
        reads.clear()
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            check(review, selected_kind, selected_phase)
        assert caught.value.reason_code == reason
        assert reads == []


def test_handoff_six_phase_kind_subjects_remain_distinct_and_bind_head_and_index():
    subjects = set()
    for kind in ("enable_g4_stage1_successor", "implement_g4_stage1_successor"):
        for phase in ("development", "pre-push", "post-push"):
            q = _handoff_binding(kind)
            q["phase"] = phase
            subject = bounded_g1b.g4_handoff_source_review_subject(q)
            subjects.add(subject)
            for field in ("expected_head", "expected_index_tree"):
                changed = copy.deepcopy(q)
                changed[field] = "0" * 40
                assert bounded_g1b.g4_handoff_source_review_subject(changed) != subject
    assert len(subjects) == 6


def test_handoff_control_publication_effect_review_keeps_its_fixed_path():
    root = bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT
    path = root / "stage1-voice-current-entry-source-v1/native-voice-intent-handoff-source-v1/control-admission-source-v1/independent-voice-control-push-effect-review-v1.json"
    row = {"path": str(path), "sha256": "a" * 64}
    verdict = "PASS_G4_STAGE1_VOICE_SOURCE_CONTROL_PUBLICATION_EFFECT"
    subject = "c" * 40
    review = {"schema": "emr4.g4_operation_review.v1", "status": "PASS", "verdict": verdict,
              "independent": True, "implementation_authorship": False, "blocking_findings": [],
              "reviewer_agent": "/root/voice_entry_scope_review", "subject_sha256": subject}
    reads = []
    def read(selected_path, digest):
        reads.append((selected_path, digest))
        return json.dumps(review).encode()
    assert bounded_g1b._g4_handoff_subject_review(read, row, root, subject, verdict) == review
    assert reads == [(path, row["sha256"])]


def test_handoff_change_pair_rejects_wrong_preimage_afterimage_and_pair_shape():
    for path, after in bounded_g1b.G4_HANDOFF_AFTER.items():
        before = bounded_g1b.G4_HANDOFF_PREIMAGES[path]
        pair = {"before_sha256": before, "after_sha256": after}
        assert bounded_g1b._g4_handoff_change_pair(path, pair, after) == before
        for field in ("before_sha256", "after_sha256"):
            changed = dict(pair)
            changed[field] = "0" * 64
            with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
                bounded_g1b._g4_handoff_change_pair(path, changed, after)
            assert caught.value.reason_code == "bounded_g4_handoff_change_preimage"
        pair["extra"] = True
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b._g4_handoff_change_pair(path, pair, after)
        assert caught.value.reason_code == "bounded_g4_handoff_change_pair"


def test_handoff_activation_requires_exact_control_publication_effect():
    q = {"base_commit": "c" * 40, "base_tree": "d" * 40}
    receipt = {"tree": q["base_tree"], "base": bounded_g1b.G4_HANDOFF_BASE["commit"],
               "commit": q["base_commit"], "candidate": "control", "phase": "push",
               "published_ref": bounded_g1b.G4_STAGE1_INTERACTIVE_BACKEND_REF,
               "whole_inverse_verified_same_attempt": True,
               "protected_refs_unchanged": True, "same_attempt_remote_readback_verified": True}
    bounded_g1b._g4_handoff_activation_acceptance(receipt, q)
    for key in receipt:
        changed = copy.deepcopy(receipt)
        changed[key] = False if receipt[key] is True else "substituted"
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b._g4_handoff_activation_acceptance(changed, q)
        assert caught.value.reason_code == "bounded_g4_handoff_activation_acceptance"


def test_handoff_loaded_policy_rejects_configuration_drift_before_configuration_loading():
    scope = _handoff_scope()
    payloads = {bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE: bounded_g1b._canonical(scope) + b"\n"}
    payloads.update({path: b"changed" for path in bounded_g1b.G4_HANDOFF_BASE_CONFIG})
    inputs = bounded_g1b.BoundedG1BInputs({}, {}, payloads, {"scope": scope}, None)
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b._validate_g4_handoff_source_loaded_policy(inputs)
    assert caught.value.reason_code == "bounded_g4_handoff_configuration_unchanged"


def test_handoff_only_new_test_accepts_absent_preimage():
    absent = "tests/test_stage1_voice_intent_handoff.cjs"
    assert bounded_g1b.G4_HANDOFF_PREIMAGES[absent] is None
    assert [p for p, value in bounded_g1b.G4_HANDOFF_PREIMAGES.items() if value is None] == [absent]
    after = bounded_g1b.G4_HANDOFF_AFTER[absent]
    assert bounded_g1b._g4_handoff_change_pair(absent, {"before_sha256": None, "after_sha256": after}, after) is None
    for path, before in bounded_g1b.G4_HANDOFF_PREIMAGES.items():
        if path == absent:
            continue
        with pytest.raises(bounded_g1b.BoundedG1BError):
            bounded_g1b._g4_handoff_change_pair(path, {"before_sha256": None, "after_sha256": "a" * 64}, "a" * 64)


# Prospective v5 audit correction. These checks do not execute an operation.
def _audit_scope():
    path = Path("C:/Users/there/EMR4-migration/20260911-v1/"
                "current-control-repair-20260912-v1/demo-led-stage1-20261012-v2/"
                "midstream-audit-correction-source-v1/control-admission-source-v1/"
                "correction-v6/candidate-source/orchestration/programme/"
                "g4-stage1-successor-entry-scope.json")
    raw = path.read_bytes()
    assert len(raw) == 5871
    assert bounded_g1b._sha(raw) == (
        "464f388a07fcc6eaa20090a9dc844a8709500cb5ad7c9ae305ed0ce92af1924d")
    return json.loads(raw)


def _audit_binding(kind):
    return {
        "schema_version": bounded_g1b.G4_AUDIT_BINDING_SCHEMA,
        "operation_id": "stage1-audit-example",
        "operation_kind": kind,
        "phase": "development",
        "base_commit": bounded_g1b.G4_AUDIT_BASE["commit"],
        "base_tree": bounded_g1b.G4_AUDIT_BASE["tree"],
        "expected_head": bounded_g1b.G4_AUDIT_BASE["commit"],
        "expected_index_tree": bounded_g1b.G4_AUDIT_BASE["tree"],
        "candidate_tree": "c" * 40,
        "source_sha256": _audit_scope()["source_sha256"],
        "payload_sha256": {},
        "repair_sha256": {path: {"before_sha256": bounded_g1b.G4_AUDIT_PREIMAGES[path],
                                 "after_sha256": "a" * 64}
                          for path in (bounded_g1b.G4_AUDIT_CONTROL if kind.startswith("enable_")
                                       else bounded_g1b.G4_AUDIT_PRODUCT)},
        "predecessor_publication": bounded_g1b.G4_AUDIT_BASE_EFFECT,
        "correction_source_review": {"path": str(bounded_g1b.G4_AUDIT_SOURCE_REVIEW_PATH),
                                     "sha256": bounded_g1b.G4_AUDIT_SOURCE_REVIEW_SHA},
        "entry_route_opinion": bounded_g1b.G4_AUDIT_ROUTE_REVIEW,
        "activation_acceptance": None,
        "source_review": {"path": "not-part-of-subject", "sha256": "a" * 64},
    }


def test_audit_scope_exact_nine_and_frozen_control_profile():
    scope = _audit_scope()
    bounded_g1b.validate_g4_audit_source_scope(scope)
    assert set(scope["product_sha256"]) == bounded_g1b.G4_AUDIT_PRODUCT
    assert scope["product_sha256"]["stage1_demo_http.py"] == "81628d878d86465734a955f945e05ac31797338b6697889670e50c91ff74268c"
    assert scope["product_sha256"]["tests/test_stage1_voice_intent_handoff.cjs"] == "e0e54bafd8a94bd10bbdc382f255c482554279349f06e6a33a5a77d25de34667"
    assert scope["correction_source_review"] == {
        "path": (bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT /
                    "midstream-audit-correction-source-v1/independent-product-source-review-v4.json").as_posix(),
        "sha256": "d17b9a91e918033ad85610ae8ac122e311bd01fa2bb952663792f7887e51dfde"}
    assert set(scope["control_sha256"]) == {bounded_g1b.G4_AUDIT_CODE,
                                            bounded_g1b.G4_STAGE1_SUCCESSOR_TEST}
    assert scope["active_profile"] == raisa_policy.G4_STAGE1_SUCCESSOR_PROFILE
    for key, value, reason in (
        ("allowed_paths", ["stage1_demo_http.py"], "bounded_g4_audit_scope_boundary"),
        ("voice_activation", True, "bounded_g4_audit_scope_boundary"),
        ("selected_base", {"commit": "0" * 40, "tree": "0" * 40}, "bounded_g4_audit_scope_boundary"),
        ("product_sha256", {}, "bounded_g4_audit_product_map"),
        ("entry_route_opinion", {"path": "wrong", "sha256": "0" * 64},
         "bounded_g4_audit_route_opinion_pin"),
    ):
        changed = copy.deepcopy(scope)
        changed[key] = value
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b.validate_g4_audit_source_scope(changed)
        assert caught.value.reason_code == reason


def test_audit_frozen_literal_rows_keep_forward_slashes_and_reject_aliases():
    scope = _audit_scope()
    for key, expected, reason in (
        ("entry_route_opinion", bounded_g1b.G4_AUDIT_ROUTE_REVIEW,
         "bounded_g4_audit_route_opinion_pin"),
        ("predecessor_scope", bounded_g1b.G4_AUDIT_PREDECESSOR_SCOPE,
         "bounded_g4_audit_literal_evidence"),
    ):
        assert scope[key] == expected
        assert expected["path"].startswith("C:/")
        assert "\\" not in expected["path"]
        for changed in (
            {**expected, "path": expected["path"].replace("/", "\\")},
            {**expected, "sha256": "0" * 64},
        ):
            with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
                bounded_g1b._g4_audit_row(changed, expected, reason)
            assert caught.value.reason_code == reason


@pytest.mark.parametrize("kind", ["enable_g4_stage1_successor", "implement_g4_stage1_successor"])
def test_audit_dispatch_uses_only_exact_kind_paths(kind):
    q = _audit_binding(kind)
    expected = (bounded_g1b.G4_AUDIT_CONTROL if kind.startswith("enable_")
                else bounded_g1b.G4_AUDIT_PRODUCT)
    assert bounded_g1b._g4_audit_paths(kind, q) == expected
    changed = copy.deepcopy(q)
    changed["repair_sha256"]["unowned.py"] = {"before_sha256": "a" * 64,
                                               "after_sha256": "b" * 64}
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b._g4_audit_paths(kind, changed)
    assert caught.value.reason_code == "bounded_g4_audit_changed_paths"
    with pytest.raises(bounded_g1b.BoundedG1BError):
        bounded_g1b._g4_audit_paths("not-a-kind", q)


@pytest.mark.parametrize("kind", ["enable_g4_stage1_successor", "implement_g4_stage1_successor"])
def test_audit_public_operation_dispatch_keeps_exact_owned_paths(kind):
    q = _audit_binding(kind)
    expected = (bounded_g1b.G4_AUDIT_CONTROL if kind.startswith("enable_")
                else bounded_g1b.G4_AUDIT_PRODUCT)
    assert bounded_g1b.operation_paths(kind, q) == expected
    operation = bounded_g1b._operation(kind, q)
    assert operation["paths"] == expected
    assert operation["g4_audit_source"] is True
    assert operation["profile"] == raisa_policy.G4_STAGE1_SUCCESSOR_PROFILE
    assert operation["gate"] == "G4"
    assert not any(operation.get(flag) for flag in (
        "g4_handoff_source", "g4_voice_source", "g4_header_correction"))
    changed = copy.deepcopy(q)
    changed["repair_sha256"].pop(next(iter(expected)))
    for entry in (bounded_g1b.operation_paths, bounded_g1b._operation):
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            entry(kind, changed)
        assert caught.value.reason_code == "bounded_g4_audit_changed_paths"


def test_audit_review_requires_exact_independent_product_map():
    review = {"schema": "emr4.stage1_midstream_audit_product_source_review.v2",
              "status": "PASS_SOURCE_ONLY_EXACT_FINAL_CORRECTION", "independent": True,
              "implementation_authorship": False, "source_only": True,
              "runtime_accepted": False, "blocking_findings": [],
              "reviewer_agent": "/root/audit_product_source_review",
              "base": bounded_g1b.G4_AUDIT_BASE,
              "candidate": {"source_sha256": dict(bounded_g1b.G4_AUDIT_AFTER)}}
    bounded_g1b._g4_audit_product_source_acceptance(review)
    for field, value in (("status", "PASS_SOURCE_ONLY"), ("independent", False),
                         ("runtime_accepted", True), ("reviewer_agent", "/root/author"),
                         ("blocking_findings", ["unresolved"])):
        changed = copy.deepcopy(review)
        changed[field] = value
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b._g4_audit_product_source_acceptance(changed)
        assert caught.value.reason_code == "bounded_g4_audit_product_source_acceptance"
    review["candidate"]["source_sha256"]["stage1_demo_http.py"] = "0" * 64
    with pytest.raises(bounded_g1b.BoundedG1BError):
        bounded_g1b._g4_audit_product_source_acceptance(review)


@pytest.mark.parametrize("kind", ["enable_g4_stage1_successor", "implement_g4_stage1_successor"])
@pytest.mark.parametrize("phase", ["development", "pre-push", "post-push"])
def test_audit_subject_is_phase_specific_and_review_path_is_exact(kind, phase):
    q = _audit_binding(kind)
    q["phase"] = phase
    subject = bounded_g1b.g4_audit_source_review_subject(q)
    for field in ("schema_version", "operation_id", "operation_kind", "phase",
                  "base_commit", "base_tree", "expected_head", "expected_index_tree",
                  "candidate_tree", "source_sha256", "payload_sha256", "repair_sha256",
                  "predecessor_publication", "correction_source_review",
                  "entry_route_opinion", "activation_acceptance"):
        changed = copy.deepcopy(q)
        changed[field] = "changed"
        assert bounded_g1b.g4_audit_source_review_subject(changed) != subject
    changed = copy.deepcopy(q)
    changed["source_review"] = {"path": "other", "sha256": "b" * 64}
    assert bounded_g1b.g4_audit_source_review_subject(changed) == subject
    operation = "enable" if kind.startswith("enable_") else "implement"
    suffix = "" if phase == "development" else "-" + phase
    root = bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT
    path = root / "midstream-audit-correction-source-v1/control-admission-source-v1" / (
        "independent-" + operation + suffix + "-exact-subject-review-v2.json")
    row = {"path": str(path), "sha256": "a" * 64}
    verdict = "PASS_G4_STAGE1_AUDIT_SOURCE_EXACT_ADMISSION_SUBJECT"
    review = {"schema": "emr4.g4_operation_review.v1", "status": "PASS", "verdict": verdict,
              "independent": True, "implementation_authorship": False,
              "blocking_findings": [], "reviewer_agent": "/root/audit_admission_route_review",
              "subject_sha256": subject}
    def read(selected_path, digest):
        assert (selected_path, digest) == (path, row["sha256"])
        return json.dumps(review).encode()
    assert bounded_g1b._g4_audit_subject_review(read, row, root, subject, verdict,
                                                  kind, phase) == review
    for field, value in (("reviewer_agent", "/root/author"), ("independent", False),
                         ("subject_sha256", "0" * 64), ("status", "PENDING")):
        changed_review = dict(review)
        changed_review[field] = value
        with pytest.raises(bounded_g1b.BoundedG1BError):
            bounded_g1b._g4_audit_subject_review(
                lambda _p, _d: json.dumps(changed_review).encode(), row, root,
                subject, verdict, kind, phase)
    wrong_row = {"path": str(path.with_name("unexpected.json")), "sha256": "a" * 64}
    with pytest.raises(bounded_g1b.BoundedG1BError):
        bounded_g1b._g4_audit_subject_review(read, wrong_row, root, subject, verdict, kind, phase)
    old_row = {"path": str(path.with_name(path.name.replace("-v2.json", "-v1.json"))),
               "sha256": "a" * 64}
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b._g4_audit_subject_review(read, old_row, root, subject, verdict, kind, phase)
    assert caught.value.reason_code == "bounded_g4_audit_review_path"


def test_audit_only_parser_and_parser_test_have_absent_preimages():
    absent = {"stage1_demo_intent.py", "tests/test_stage1_demo_intent.py"}
    assert {path for path, before in bounded_g1b.G4_AUDIT_PREIMAGES.items()
            if before is None} == absent
    for path, after in bounded_g1b.G4_AUDIT_AFTER.items():
        before = bounded_g1b.G4_AUDIT_PREIMAGES[path]
        assert bounded_g1b._g4_audit_change_pair(
            path, {"before_sha256": before, "after_sha256": after}, after) == before
        wrong_before = "0" * 64 if before is None else None
        with pytest.raises(bounded_g1b.BoundedG1BError):
            bounded_g1b._g4_audit_change_pair(
                path, {"before_sha256": wrong_before, "after_sha256": after}, after)


def test_audit_loaded_policy_rejects_configuration_drift_before_loading():
    scope = _audit_scope()
    payloads = {bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE: bounded_g1b._canonical(scope) + b"\n"}
    payloads.update({path: b"changed" for path in bounded_g1b.G4_AUDIT_BASE_CONFIG})
    inputs = bounded_g1b.BoundedG1BInputs({}, {}, payloads, {"scope": scope}, None)
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b._validate_g4_audit_source_loaded_policy(inputs)
    assert caught.value.reason_code == "bounded_g4_audit_configuration_unchanged"


def test_audit_activation_requires_exact_independent_control_publication_effect():
    q = {"base_commit": "c" * 40, "base_tree": "d" * 40}
    receipt = {"tree": q["base_tree"], "base": bounded_g1b.G4_AUDIT_BASE["commit"],
               "commit": q["base_commit"], "candidate": "control", "phase": "push",
               "published_ref": bounded_g1b.G4_STAGE1_INTERACTIVE_BACKEND_REF,
               "whole_inverse_verified_same_attempt": True,
               "protected_refs_unchanged": True,
               "same_attempt_remote_readback_verified": True}
    bounded_g1b._g4_audit_activation_acceptance(receipt, q)
    for field in receipt:
        changed = copy.deepcopy(receipt)
        changed[field] = False if receipt[field] is True else "substituted"
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b._g4_audit_activation_acceptance(changed, q)
        assert caught.value.reason_code == "bounded_g4_audit_activation_acceptance"


# Current G4 CI maintenance checks are source only; no operation runs here.
def _ci_scope():
    raw = base64.b64decode(
        "eyJhY3RpdmVfcHJvZmlsZSI6Ikc0X1NUQUdFMV9MT0NBTF9TVUNDRVNTT1IiLCJhZG1pc3Npb25fZ3JhbnRzX3J1bnRpbWVfYXV0"
        "aG9yaXR5IjpmYWxzZSwiYWxsb3dlZF9lZmZlY3RzIjpbImNvbnRyb2xfcGxhbmVfZWRpdCIsInJlcG9zaXRvcnlfcmVhZCIsInRh"
        "c2tfYnJhbmNoX2NvbW1pdCIsInRhc2tfYnJhbmNoX3B1c2giXSwiYWxsb3dlZF9wYXRocyI6WyIuZ2l0aHViL3dvcmtmbG93cy9n"
        "Mi1ib3VuZGVkLXB5dGhvbi55bWwiXSwiYWxsb3dlZF90YXNrX2tpbmQiOiJnNF9zdGFnZTFfbG9jYWxfc3VjY2Vzc29yIiwiY2lf"
        "bWFpbnRlbmFuY2UiOnsicm91dGVfb3BpbmlvbiI6eyJwYXRoIjoiQzovVXNlcnMvdGhlcmUvRU1SNC1taWdyYXRpb24vMjAyNjA5"
        "MTEtdjEvY3VycmVudC1jb250cm9sLXJlcGFpci0yMDI2MDkxMi12MS9kZW1vLWxlZC1zdGFnZTEtMjAyNjEwMTItdjIvbWlkc3Ry"
        "ZWFtLWF1ZGl0LWNvcnJlY3Rpb24tc291cmNlLXYxL2luZGVwZW5kZW50LWNpLW1haW50ZW5hbmNlLXJvdXRlLXJldmlldy12MS5q"
        "c29uIiwic2hhMjU2IjoiY2JjNWUyMzI2MTcxMGRmYjM3MjExMjkyMzgyNmMxYWRjMjcwYzUxYTRkZmMwMjZiZWFlNTUzOWFjYzBj"
        "MDJmNiJ9LCJzZWxlY3Rpb25fc2hhMjU2IjoiNGU3ZmI0YjM5NGE3ZmM1YTA0NTlmMmIxNjJjYzAwMDUxOTVjZTQxMzFlMjI1Mjlh"
        "YjdjYjM2ODUwNGRhNGEyYyIsInNvdXJjZV9zdWJqZWN0X2NvbW1pdCI6Ijc0ZGQ1MjQyYTdmMmE5NTNmNjk0MmQ5YTA0M2Q0Njlj"
        "OTVmNzRhOWMiLCJ3b3JrZmxvd19hZnRlcl9zaGEyNTYiOiIwNjUwMmQ2OGIwMTZmYmE3NWZiMGFhYjk4ZTg5MDNkNTJjMTI0YjRj"
        "ZjVkNDBiYzUyNDVlMzUyODQzN2RkZmY5Iiwid29ya2Zsb3dfYmVmb3JlX3NoYTI1NiI6IjUwNjA2NWM1ZTMxZjFkNTRhOWY0MTQ5"
        "YTliYmIyNzdhN2MxNTEzZDA5YWU2NmU0M2U0ZmI0NWQzZjhkMWRjYjYiLCJ3b3JrZmxvd19jYW5kaWRhdGUiOnsicGF0aCI6IkM6"
        "L1VzZXJzL3RoZXJlL0VNUjQtbWlncmF0aW9uLzIwMjYwOTExLXYxL2N1cnJlbnQtY29udHJvbC1yZXBhaXItMjAyNjA5MTItdjEv"
        "ZGVtby1sZWQtc3RhZ2UxLTIwMjYxMDEyLXYyL21pZHN0cmVhbS1hdWRpdC1jb3JyZWN0aW9uLXNvdXJjZS12MS9jb3JyZWN0aW9u"
        "LXYyL2NhbmRpZGF0ZS1zb3VyY2UvLmdpdGh1Yi93b3JrZmxvd3MvZzItYm91bmRlZC1weXRob24ueW1sIiwic2hhMjU2IjoiMDY1"
        "MDJkNjhiMDE2ZmJhNzVmYjBhYWI5OGU4OTAzZDUyYzEyNGI0Y2Y1ZDQwYmM1MjQ1ZTM1Mjg0MzdkZGZmOSJ9LCJ3b3JrZmxvd19w"
        "YXRoIjoiLmdpdGh1Yi93b3JrZmxvd3MvZzItYm91bmRlZC1weXRob24ueW1sIn0sImNvbWJpbmVkX3Byb2R1Y3Rfc291cmNlX2Jp"
        "bmRpbmciOnsicGF0aCI6IkM6XFxVc2Vyc1xcdGhlcmVcXEVNUjQtbWlncmF0aW9uXFwyMDI2MDkxMS12MVxcY3VycmVudC1jb250"
        "cm9sLXJlcGFpci0yMDI2MDkxMi12MVxcZGVtby1sZWQtc3RhZ2UxLTIwMjYxMDEyLXYyXFxzdGFnZTEtaW50ZXJhY3RpdmUtc3Vj"
        "Y2Vzc29yLWVudHJ5LXNvdXJjZS12NVxcY29tYmluZWQtcHJvZHVjdC1zb3VyY2UtYmluZGluZy1JTkVSVC12NS5qc29uIiwic2hh"
        "MjU2IjoiYTViN2YxNGMxYmUzMmQwODc3YzQ1ZGQxNWNiYmZmZThjZTkwNDliMGYzODY2OWFkNmZmNjQyM2Y3N2Y5N2QxMiJ9LCJj"
        "b250cm9sX3NoYTI1NiI6eyJvcmNoZXN0cmF0aW9uX2hhcm5lc3MvYm91bmRlZF9nMWIucHkiOiI4NjVjNWQ0YWI1OTg0NjY0Y2M1"
        "OGM4ZDNiNTU4MjhkMDQ2NDBjNGRlZjgwZjhlMmRmNDVkNDEzNzUzODIzYTBjIiwidGVzdHMvdGVzdF9nNF9zdGFnZTFfc3VjY2Vz"
        "c29yX2VudHJ5LnB5IjoiNTY2ZjUzMWE0YTI0ODU5NWM0OGYxOTJmYjA5ZjRjMGU0M2VmYTdlOGYwODVlYzhkZjk2NjEyMTAzNjM0"
        "ZjM4MyJ9LCJjb3JyZWN0aW9uX3NvdXJjZV9yZXZpZXciOnsicGF0aCI6IkM6L1VzZXJzL3RoZXJlL0VNUjQtbWlncmF0aW9uLzIw"
        "MjYwOTExLXYxL2N1cnJlbnQtY29udHJvbC1yZXBhaXItMjAyNjA5MTItdjEvZGVtby1sZWQtc3RhZ2UxLTIwMjYxMDEyLXYyL21p"
        "ZHN0cmVhbS1hdWRpdC1jb3JyZWN0aW9uLXNvdXJjZS12MS9pbmRlcGVuZGVudC1wcm9kdWN0LXNvdXJjZS1yZXZpZXctdjQuanNv"
        "biIsInNoYTI1NiI6ImQxN2I5YTkxZTkxODAzM2FkODU2MTBhZThhYzEyMmUzMTFiZDAxZmEyYmI5NTI2NjM3OTJmNzg4N2U1MWRm"
        "ZGUifSwiZW50cnlfcm91dGVfb3BpbmlvbiI6eyJwYXRoIjoiQzovVXNlcnMvdGhlcmUvRU1SNC1taWdyYXRpb24vMjAyNjA5MTEt"
        "djEvY3VycmVudC1jb250cm9sLXJlcGFpci0yMDI2MDkxMi12MS9kZW1vLWxlZC1zdGFnZTEtMjAyNjEwMTItdjIvbWlkc3RyZWFt"
        "LWF1ZGl0LWNvcnJlY3Rpb24tc291cmNlLXYxL2luZGVwZW5kZW50LWVudHJ5LXJvdXRlLXJldmlldy12MS5qc29uIiwic2hhMjU2"
        "IjoiODE2OGMyM2YwNmI0NjZlNDI0Mjc3YjFiMWRmYTI3NGM1NjEwN2YzZGNkOTY1MmE4NDJjMzllMTZmZTEyYTY3YyJ9LCJleGNs"
        "dWRlZF9lZmZlY3RzIjpbInVucmV2aWV3ZWRfYXBwbGljYXRpb25fb3JfZGF0YWJhc2VfcnVudGltZSIsInVucmV2aWV3ZWRfYnJv"
        "d3Nlcl9vcl9taWNyb3Bob25lX3J1bnRpbWUiLCJ1bnJldmlld2VkX3ZvaWNlX2NoaWxkX29yX25ldHdvcmtfZWdyZXNzIiwicHJv"
        "dmlkZXJfaW52b2NhdGlvbiIsInJlYWxfZGF0YV9hY2Nlc3MiLCJwcm90ZWN0ZWRfcmVmX21vdmVtZW50IiwiZGVwbG95bWVudCIs"
        "InB1YmxpY19saXN0ZW5lciJdLCJsYWJfc291cmNlX3JldmlldyI6eyJwYXRoIjoiQzpcXFVzZXJzXFx0aGVyZVxcRU1SNC1taWdy"
        "YXRpb25cXDIwMjYwOTExLXYxXFxjdXJyZW50LWNvbnRyb2wtcmVwYWlyLTIwMjYwOTEyLXYxXFxkZW1vLWxlZC1zdGFnZTEtMjAy"
        "NjEwMTItdjJcXHN0YWdlMS1yZWxpYWJpbGl0eS1sYWItc291cmNlLXY3XFxpbmRlcGVuZGVudC1zb3VyY2UtcmV2aWV3LXY3Lmpz"
        "b24iLCJzaGEyNTYiOiJiMDAzMGMxMTk2ODE3ZmZhNjNmOGYyNDc4ZDI1YzU1YTZkZWZlZmM2YWNlYTA2ZDFlYjkwMmMzOTlhNGU5"
        "MGE3In0sIm5hdGl2ZTA4X2RlcGVuZGVuY3lfb25seSI6dHJ1ZSwicHJlZGVjZXNzb3JfcHVibGljYXRpb24iOnsicGF0aCI6IkM6"
        "L1VzZXJzL3RoZXJlL0VNUjQtbWlncmF0aW9uLzIwMjYwOTExLXYxL2N1cnJlbnQtY29udHJvbC1yZXBhaXItMjAyNjA5MTItdjEv"
        "ZGVtby1sZWQtc3RhZ2UxLTIwMjYxMDEyLXYyL21pZHN0cmVhbS1hdWRpdC1jb3JyZWN0aW9uLXNvdXJjZS12MS9wcm9kdWN0LXB1"
        "YmxpY2F0aW9uLXNvdXJjZS12My9pbmRlcGVuZGVudC1zdGFnZTEtbWlkc3RyZWFtLWF1ZGl0LXByb2R1Y3QtcHVzaC1lZmZlY3Qt"
        "cmV2aWV3LXYxLmpzb24iLCJzaGEyNTYiOiI3YzlmMGM5ODhkMWE4NzBkZmNmMjQxMTE2NDFmY2IzODBiYjY4OGI5OWNkMjljNGYz"
        "OGU1NGVhOWYyODc2YmEyIn0sInByZWRlY2Vzc29yX3Njb3BlIjp7InBhdGgiOiJDOi9Vc2Vycy90aGVyZS9FTVI0LW1pZ3JhdGlv"
        "bi8yMDI2MDkxMS12MS9jdXJyZW50LWNvbnRyb2wtcmVwYWlyLTIwMjYwOTEyLXYxL2RlbW8tbGVkLXN0YWdlMS0yMDI2MTAxMi12"
        "Mi9taWRzdHJlYW0tYXVkaXQtY29ycmVjdGlvbi1zb3VyY2UtdjEvY29udHJvbC1hZG1pc3Npb24tc291cmNlLXYxL2NvcnJlY3Rp"
        "b24tdjYvY2FuZGlkYXRlLXNvdXJjZS9vcmNoZXN0cmF0aW9uL3Byb2dyYW1tZS9nNC1zdGFnZTEtc3VjY2Vzc29yLWVudHJ5LXNj"
        "b3BlLmpzb24iLCJzaGEyNTYiOiI0NjRmMzg4YTA3ZmNjNmVhYTIwMDkwYTlkYzg0NGE4NzA5NTAwY2I1YWQ3YzlhZTMwNWVkMGNl"
        "OTJhZjE5MjRkIn0sInByb2R1Y3Rfc2hhMjU2Ijp7InN0YWdlMV9kZW1vX2h0dHAucHkiOiI4MTYyOGQ4NzhkODY0NjU3MzRhOTU1"
        "Zjk0NWUwNWFjMzE3OTczMzhiNjY5Nzg4OTY3MGU1MGM5MWZmNzQyNjhjIiwic3RhZ2UxX2RlbW9faW50ZW50LnB5IjoiOGQxZWUw"
        "ZDEzN2E0MGNiYWRjZGM4OTdkYjZmZWRlNDAzZGIyNGUzOTU0YmY5MGFmNDM3ZGU0NDVjOWRhMWRhZiIsInN0YXRpYy9kZW1vL3N0"
        "YWdlMS1pbnRlcmFjdGl2ZS5odG1sIjoiZTE0YzcyNTcwOWFkOWIwNmI5OWU2OWYzMzY3MTllZTA5NWJhN2FhMWYzMjEzY2ZjNWYy"
        "NmQ4Mjk1Y2NjNGM4MCIsInN0YXRpYy9kZW1vL3N0YWdlMS1pbnRlcmFjdGl2ZS5qcyI6Ijk4OTMwZmM2YmZkMWJjY2VjODIzYmZk"
        "MzQzZWUyOTEzMDg1Y2MyMjAzNjk1MmNiM2FlYTlmNmM1NDAxYzMxZTgiLCJ0ZXN0cy90ZXN0X3N0YWdlMV9kZW1vX2h0dHAucHki"
        "OiJmNWYxNzMxZTc3MzM1NTZmMGU0YmFiNDM4Nzk1YWMzMDZjOGZlZjRlNTQyNjRjZWFmNWUzYzUyZGMyYjhlODVhIiwidGVzdHMv"
        "dGVzdF9zdGFnZTFfZGVtb19pbnRlbnQucHkiOiIwNzIyMGEyOGQwYzMzNmRhZTdlMzI3Mzg4NjIyMWVlNjZhZWNjMjVkNzM3MzY0"
        "MTA0Mjk3OWQ3MjQ2M2IwNzIwIiwidGVzdHMvdGVzdF9zdGFnZTFfcmVsaWFiaWxpdHlfbGFiLnB5IjoiOGJlOTI2NjgxYzYwNDdh"
        "ODU3ZGIzMmU1YmQ4ZGFkNmVkOTgyNmFiMWY1M2Y5MGJkYTRhZGFmNTY1NTIxNDk4YyIsInRlc3RzL3Rlc3Rfc3RhZ2UxX3Nwb2tl"
        "bl9yZXBseV9zb3VyY2UucHkiOiI4NTA5Y2ZkZjAyNDY2MDBkMDQ3NTMwY2YwMDY2Yjk0ZGNjZDc1NTQ2MTJhMzQ4ZjhhNDVkMTQ4"
        "MWJlOTFjNmIyIiwidGVzdHMvdGVzdF9zdGFnZTFfdm9pY2VfaW50ZW50X2hhbmRvZmYuY2pzIjoiZTBlNTRiYWZkOGE5NGJkMTBi"
        "YmRjMzgyZjI1NWM0ODI1NTQyNzkzNDlmMDZlNmEzM2E1YTc3ZDI1ZGUzNDY2NyJ9LCJyZWNvcmRlZF9hdCI6IjIwMjYtMTAtMTlU"
        "MDc6MTA6NTMuMzY5NDAyKzAwOjAwIiwicnVudGltZV9iaW5kaW5nX3JlcXVpcmVkIjp0cnVlLCJzY2hlbWFfdmVyc2lvbiI6ImFy"
        "aWFkbmUuZzRfc3RhZ2UxX3N1Y2Nlc3Nvcl9lbnRyeV9zY29wZS52NiIsInNlbGVjdGVkX2Jhc2UiOnsiY29tbWl0IjoiOTljNmU0"
        "ZjljMmVmNzgxN2QwMjc3NTk3ZjAzY2QwNWNiYjIwOWMwMCIsInRyZWUiOiJmYmJjNWE2Njg0NTk5OGQ0ODA5MTBmY2IyNTU4MGZl"
        "OGQxYzQ0ZWI5In0sInNvdXJjZV9zaGEyNTYiOnsib3JjaGVzdHJhdGlvbl9oYXJuZXNzL2JvdW5kZWRfZzFiLnB5IjoiODY1YzVk"
        "NGFiNTk4NDY2NGNjNThjOGQzYjU1ODI4ZDA0NjQwYzRkZWY4MGY4ZTJkZjQ1ZDQxMzc1MzgyM2EwYyIsIm9yY2hlc3RyYXRpb25f"
        "aGFybmVzcy9jb25maWd1cmF0aW9uX2NvcmUucHkiOiJmN2JhN2E4MGViMGE1OTBmOWZiNzFiODY0ZTZjMWY5ZjQzMjQxZDlmN2Q3"
        "MGEzOGRhNjdhOTI0M2ZlYTIwOGU1Iiwib3JjaGVzdHJhdGlvbl9oYXJuZXNzL3Bpbm5lZF9wcm9ncmFtbWVfZ2F0ZWtlZXBlci5w"
        "eSI6ImMxZmVhOWEyODQ5MDY4ZWQ4ZTg3ZGJlMWU3Y2VjMWNjN2U3NjJmYTJiYzg4NzZmYzMyYmJkYTgwZDIyNmNmMzkiLCJvcmNo"
        "ZXN0cmF0aW9uX2hhcm5lc3MvcHJvZ3JhbW1lX2FkbWlzc2lvbi5weSI6ImFjODE2YThhNzliMmQ4MjIyZmEzNTc3NzdjMDc1OTUw"
        "OTI3ZTg2Y2YzMGM4YTViMjVmZmQwOGE0NzQwNTIxODEiLCJvcmNoZXN0cmF0aW9uX2hhcm5lc3MvcmFpc2FfcG9saWN5LnB5Ijoi"
        "ZGIxOTcxNDczM2U3MGU2ZDU1YjIyMTQ0OGNjMmZlMGU4ZDYwNjVjM2ZlNDBhMzU5MDhmZWJiMGUxYjc0YmI4MyIsIm9yY2hlc3Ry"
        "YXRpb25faGFybmVzcy90cnVzdGVkX2dpdC5weSI6IjRhODU2YmZmZTJiNjhkN2M3ZTE4NzUxNTI2MjljOTAyNGEzMjY3OWI1OWQ5"
        "YjFlZDgzMDFjMzY4ZDQxZmY1MjciLCJzY3JpcHRzL3JhaXNhX2FyaWFkbmVfcmVjb3ZlcnlfcHJlZmxpZ2h0LnB5IjoiZWRmZDM3"
        "YjMwNjczYjg1NDRkMzA5YjUzMmM5NWIzZmQ3YzIwZmY1OTI4ODBhOGEwMjM1ZGZkZTZjZmM4ZTdlNCIsInRlc3RzL3Rlc3RfYm91"
        "bmRlZF9nMWIucHkiOiJiYjFiZTg2Y2EzOTIzMmZlYTMwYzFlYTg0Y2RmYjExNDQyOGQ1N2JlMGY4ZjY3YmY3ZTg2ZGFhYjBiYTcz"
        "YmM1In0sInVpMTJfcHVibGljYXRpb25fcmV2aWV3Ijp7InBhdGgiOiJDOi9Vc2Vycy90aGVyZS9FTVI0LW1pZ3JhdGlvbi8yMDI2"
        "MDkxMS12MS9jdXJyZW50LWNvbnRyb2wtcmVwYWlyLTIwMjYwOTEyLXYxL2RlbW8tbGVkLXN0YWdlMS0yMDI2MTAxMi12Mi9zdGFn"
        "ZTEtaW50ZXJhY3RpdmUtcHJvZHVjdC1wdWJsaWNhdGlvbi1zb3VyY2UtdjIvaW5kZXBlbmRlbnQtc3RhZ2UxLWludGVyYWN0aXZl"
        "LXByb2R1Y3QtcHVzaC1lZmZlY3QtcmV2aWV3LXYyLmpzb24iLCJzaGEyNTYiOiI3NDUzZjBhMTgxOWNmMzUwNDY0Njg3NTk5YmU3"
        "ODQ3N2Q4ZDBjY2NkZTA3MmIzMjJjZjY1MzliZmRhZDQ3NmRmIn0sInZvaWNlX2FjdGl2YXRpb24iOmZhbHNlLCJ2b2ljZV9zb3Vy"
        "Y2VfcmV2aWV3Ijp7InBhdGgiOiJDOi9Vc2Vycy90aGVyZS9FTVI0LW1pZ3JhdGlvbi8yMDI2MDkxMS12MS9jdXJyZW50LWNvbnRy"
        "b2wtcmVwYWlyLTIwMjYwOTEyLXYxL2RlbW8tbGVkLXN0YWdlMS0yMDI2MTAxMi12Mi9zdGFnZTEtdm9pY2UtaW50ZXJhY3RpdmUt"
        "c2VhbS1zb3VyY2UtdjQvaW5kZXBlbmRlbnQtc291cmNlLXJldmlldy12NC5qc29uIiwic2hhMjU2IjoiY2Q1YzlmYTRkNzY4YmQx"
        "YWRmNzRjOWFjNTg2ZmMzZGUwOTE2Y2NmNjQxOGE4MjY2NmZiZDhjOTNjNzNhNjBmMyJ9fQo="
    )
    assert hashlib.sha256(raw).hexdigest() == "fc937c2e1f309ef0b0a2335af0768d88a00e1ae337acf6e86cd9c2218d70b9c6"
    return json.loads(raw)


def _ci_binding(stage):
    paths = (bounded_g1b.G4_CI_CONTROL if stage == "enable"
             else {bounded_g1b.G4_CI_WORKFLOW})
    return {"schema_version": bounded_g1b.G4_CI_BINDING_SCHEMA,
            "operation_kind": bounded_g1b.G4_CI_KIND, "stage": stage,
            "repair_sha256": {p: {"before_sha256": bounded_g1b.G4_CI_PREIMAGES[p],
                                  "after_sha256": "a" * 64} for p in paths}}


def test_ci_maintenance_exact_paths_and_effects():
    for stage, paths in (("enable", bounded_g1b.G4_CI_CONTROL),
                         ("apply", frozenset({bounded_g1b.G4_CI_WORKFLOW}))):
        q = _ci_binding(stage)
        assert bounded_g1b.operation_paths(bounded_g1b.G4_CI_KIND, q) == paths
        assert bounded_g1b._operation(bounded_g1b.G4_CI_KIND, q)["g4_ci_maintenance"] is True
        assert bounded_g1b.operation_effects(bounded_g1b.G4_CI_KIND) == bounded_g1b.EFFECTS
        for mutation in (lambda row: row["repair_sha256"].pop(next(iter(row["repair_sha256"]))),
                         lambda row: row["repair_sha256"].update({"AGENTS.md": {}})):
            changed = copy.deepcopy(q)
            mutation(changed)
            with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
                bounded_g1b.operation_paths(bounded_g1b.G4_CI_KIND, changed)
            assert caught.value.reason_code == "bounded_g4_ci_changed_paths"
    assert "product_behavior_change" in bounded_g1b.operation_effects(
        "implement_g4_stage1_successor")


def test_ci_maintenance_scope_exact_product_and_workflow():
    scope = _ci_scope()
    bounded_g1b.validate_g4_ci_maintenance_scope(scope)
    assert scope["selected_base"] == bounded_g1b.G4_CI_BASE
    assert scope["predecessor_publication"] == bounded_g1b.G4_CI_PRODUCT_PUBLICATION
    assert scope["ci_maintenance"]["workflow_after_sha256"] == bounded_g1b.G4_CI_WORKFLOW_AFTER
    for field, value in (
        ("selected_base", {"commit": "0" * 40, "tree": "0" * 40}),
        ("allowed_paths", ["AGENTS.md"]), ("allowed_effects", ["repository_read"]),
        ("predecessor_publication", {"path": "other", "sha256": "0" * 64})):
        changed = copy.deepcopy(scope)
        changed[field] = value
        with pytest.raises(bounded_g1b.BoundedG1BError):
            bounded_g1b.validate_g4_ci_maintenance_scope(changed)
    for field in ("workflow_before_sha256", "workflow_after_sha256",
                  "source_subject_commit", "selection_sha256"):
        changed = copy.deepcopy(scope)
        changed["ci_maintenance"][field] = "0" * (40 if field.endswith("commit") else 64)
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b.validate_g4_ci_maintenance_scope(changed)
        assert caught.value.reason_code == "bounded_g4_ci_workflow_identity"


def test_ci_maintenance_preimages_and_review_subject_are_exact():
    for path in (*sorted(bounded_g1b.G4_CI_CONTROL), bounded_g1b.G4_CI_WORKFLOW):
        pair = {"before_sha256": bounded_g1b.G4_CI_PREIMAGES[path],
                "after_sha256": "a" * 64}
        bounded_g1b._g4_ci_pair(path, pair, "a" * 64)
        changed = dict(pair, before_sha256="0" * 64)
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b._g4_ci_pair(path, changed, "a" * 64)
        assert caught.value.reason_code == "bounded_g4_ci_change_preimage"
    q = {k: "a" for k in ("schema_version", "operation_id", "operation_kind",
                         "stage", "phase", "base_commit", "base_tree", "expected_head",
                         "expected_index_tree", "candidate_tree", "source_sha256",
                         "payload_sha256", "repair_sha256", "predecessor_scope",
                         "predecessor_publication", "route_opinion", "activation_acceptance")}
    subject = bounded_g1b.g4_ci_review_subject(q)
    for key in q:
        changed = dict(q, **{key: "changed"})
        assert bounded_g1b.g4_ci_review_subject(changed) != subject
    q["source_review"] = {"path": "excluded", "sha256": "b" * 64}
    assert bounded_g1b.g4_ci_review_subject(q) == subject


def test_ci_maintenance_product_receipt_checks_actual_abi():
    row = bounded_g1b.G4_CI_PRODUCT_PUBLICATION
    raw = Path(row["path"]).read_bytes()
    assert len(raw) == 30664 and bounded_g1b._sha(raw) == row["sha256"]
    good = json.loads(raw)
    bounded_g1b._g4_ci_product_publication(good)
    for key in ("candidate_tree", "result_sha256",
                "same_attempt_remote_readback_verified",
                "audio_recording_accepted", "rendered_accessibility_accepted",
                "g4_completion_accepted"):
        changed = copy.deepcopy(good)
        changed[key] = (not good[key] if type(good[key]) is bool else "0" * 40)
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b._g4_ci_product_publication(changed)
        assert caught.value.reason_code == "bounded_g4_ci_product_publication"
        absent = copy.deepcopy(good)
        del absent[key]
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b._g4_ci_product_publication(absent)
        assert caught.value.reason_code == "bounded_g4_ci_product_publication"


def test_ci_maintenance_activation_requires_exact_reviewed_enable_effect():
    q = {"base_commit": "c" * 40, "base_tree": "d" * 40,
         "payload_sha256": {p: "a" * 64 for p in bounded_g1b.G4_CI_CONTROL}}
    good = {"schema": "emr4.g4_operation_review.v1", "status": "PASS",
            "verdict": "PASS_G4_STAGE1_CI_MAINTENANCE_CONTROL_PUBLICATION_EFFECT",
            "reviewer_agent": "/root/audit_admission_route_review",
            "independent": True, "implementation_authorship": False,
            "blocking_findings": [], "operation_kind": bounded_g1b.G4_CI_KIND,
            "candidate": "control", "stage": "enable", "phase": "push",
            "base": bounded_g1b.G4_CI_BASE["commit"], "commit": q["base_commit"],
            "candidate_tree": q["base_tree"],
            "published_ref": bounded_g1b.G4_STAGE1_INTERACTIVE_BACKEND_REF,
            "control_sha256": q["payload_sha256"],
            "source_publication_accepted": True, "control_activation_accepted": True,
            "same_attempt_remote_readback_verified": True,
            "protected_refs_unchanged": True,
            "whole_inverse_verified_same_attempt": True}
    bounded_g1b._g4_ci_activation_acceptance(good, q)
    for key in ("verdict", "reviewer_agent", "operation_kind", "candidate",
                "stage", "phase", "published_ref", "control_sha256",
                "source_publication_accepted", "control_activation_accepted"):
        wrong = copy.deepcopy(good)
        wrong[key] = False if type(good[key]) is bool else "substituted"
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b._g4_ci_activation_acceptance(wrong, q)
        assert caught.value.reason_code == "bounded_g4_ci_activation_acceptance"
        missing = copy.deepcopy(good)
        del missing[key]
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b._g4_ci_activation_acceptance(missing, q)
        assert caught.value.reason_code == "bounded_g4_ci_activation_acceptance"


@pytest.mark.parametrize("stage", ["enable", "apply"])
@pytest.mark.parametrize("phase", ["development", "pre-push", "post-push"])
def test_ci_maintenance_review_six_exact_slots_and_refusals(stage, phase):
    q = {k: "a" for k in ("schema_version", "operation_id", "operation_kind",
                         "stage", "phase", "base_commit", "base_tree", "expected_head",
                         "expected_index_tree", "candidate_tree", "source_sha256",
                         "payload_sha256", "repair_sha256", "predecessor_scope",
                         "predecessor_publication", "route_opinion", "activation_acceptance")}
    q["stage"], q["phase"] = stage, phase
    subject = bounded_g1b.g4_ci_review_subject(q)
    suffix = "" if phase == "development" else "-" + phase
    path = (bounded_g1b.G4_CI_EVIDENCE / "ci-maintenance-control-source-v1" /
            f"independent-{stage}{suffix}-exact-subject-review-v1.json")
    row = {"path": str(path), "sha256": "a" * 64}
    review = {"schema": "emr4.g4_operation_review.v1", "status": "PASS",
              "verdict": "PASS_G4_STAGE1_CI_MAINTENANCE_EXACT_ADMISSION_SUBJECT",
              "independent": True, "implementation_authorship": False,
              "blocking_findings": [], "reviewer_agent": "/root/audit_admission_route_review",
              "subject_sha256": subject}
    def read(selected, digest):
        assert (selected, digest) == (path, row["sha256"])
        return json.dumps(review).encode()
    assert bounded_g1b._g4_ci_review(
        read, row, bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT,
        subject, stage, phase) == review
    wrong_row = dict(row, path=str(path.with_name("unexpected.json")))
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b._g4_ci_review(read, wrong_row,
            bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT, subject, stage, phase)
    assert caught.value.reason_code == "bounded_g4_ci_review_path"
    for key, value in (("independent", False),
                       ("implementation_authorship", True),
                       ("reviewer_agent", "/root/author"),
                       ("subject_sha256", "0" * 64)):
        changed = dict(review, **{key: value})
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b._g4_ci_review(
                lambda _p, _d: json.dumps(changed).encode(), row,
                bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT, subject, stage, phase)
        assert caught.value.reason_code == "bounded_g4_ci_independent_subject"


def test_selected_bureau_v8_scope_rejects_exact_boundary_changes():
    scope = _bureau_scope()
    bounded_g1b.validate_g4_bureau_scope(scope)
    assert scope["allowed_paths"] == sorted(bounded_g1b.G4_BUREAU_PRODUCT)
    assert scope["product_sha256"] == bounded_g1b.G4_BUREAU_PRODUCT_SHA
    assert scope["product_vector"] == {
        "path": bounded_g1b.G4_BUREAU_VECTOR.as_posix(),
        "sha256": bounded_g1b.G4_BUREAU_VECTOR_SHA}
    assert scope["mapping_review"] == {
        "path": bounded_g1b.G4_BUREAU_MAPPING.as_posix(),
        "sha256": bounded_g1b.G4_BUREAU_MAPPING_SHA}
    assert scope["admission_grants_runtime_authority"] is False
    assert scope["runtime_binding_required"] is True
    assert scope["voice_activation"] is False
    mutations = (
        ("selected_base", {"commit": "0" * 40, "tree": "0" * 40}),
        ("allowed_paths", sorted(set(scope["allowed_paths"]) | {"app/main.py"})),
        ("allowed_paths", scope["allowed_paths"][:-1]),
        ("allowed_effects", sorted(set(scope["allowed_effects"]) | {"provider_invocation"})),
        ("excluded_effects", scope["excluded_effects"][:-1]),
        ("runtime_binding_required", False),
        ("admission_grants_runtime_authority", True),
        ("voice_activation", True),
    )
    for field, value in mutations:
        changed = copy.deepcopy(scope)
        changed[field] = value
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b.validate_g4_bureau_scope(changed)
        assert caught.value.reason_code == "bounded_g4_bureau_scope_boundary"
    for field, item in (
        ("product_sha256", next(iter(scope["product_sha256"]))),
        ("product_vector", "sha256"),
        ("mapping_review", "path"),
    ):
        changed = copy.deepcopy(scope)
        changed[field][item] = "0" * 64 if item != "path" else "other.json"
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b.validate_g4_bureau_scope(changed)
        assert caught.value.reason_code == "bounded_g4_bureau_scope_boundary"


def test_selected_bureau_v8_all_six_phase_subjects_and_independence():
    scope = _bureau_scope()
    subjects = {}
    for stage, kind in (("enable", "enable_g4_stage1_successor"),
                        ("apply", "implement_g4_stage1_successor")):
        for phase in ("development", "pre-push", "post-push"):
            q = {
                "schema_version": bounded_g1b.G4_BUREAU_SCHEMA,
                "operation_id": "selected-bureau-source",
                "operation_kind": kind, "stage": stage, "phase": phase,
                "base_commit": "a" * 40, "base_tree": "b" * 40,
                "expected_head": "c" * 40, "expected_index_tree": "d" * 40,
                "candidate_tree": "e" * 40,
                "source_sha256": scope["source_sha256"],
                "payload_sha256": {},
                "repair_sha256": {p: {} for p in (
                    bounded_g1b.G4_BUREAU_CONTROL if stage == "enable"
                    else bounded_g1b.G4_BUREAU_PRODUCT)},
                "activation_acceptance": None if stage == "enable" else {
                    "path": "review.json", "sha256": "f" * 64},
                "product_vector": scope["product_vector"],
                "mapping_review": scope["mapping_review"],
            }
            subject = bounded_g1b.g4_bureau_review_subject(q)
            subjects[stage, phase] = subject
            for field, replacement in (
                ("stage", "apply" if stage == "enable" else "enable"),
                ("phase", "post-push" if phase != "post-push" else "development"),
                ("expected_head", "1" * 40),
                ("expected_index_tree", "2" * 40),
                ("candidate_tree", "3" * 40),
                ("operation_id", "other-operation"),
            ):
                changed = copy.deepcopy(q)
                changed[field] = replacement
                assert bounded_g1b.g4_bureau_review_subject(changed) != subject
            path = (bounded_g1b.G4_BUREAU_ROOT / "entry-admission-v1" /
                    f"independent-{stage}-{phase}-subject-review-v1.json")
            review = {
                "schema": "emr4.g4_operation_review.v1",
                "status": "PASS",
                "verdict": "PASS_G4_STAGE1_SELECTED_BUREAU_EXACT_ADMISSION_SUBJECT",
                "subject_sha256": subject, "independent": True,
                "implementation_authorship": False, "blocking_findings": [],
                "reviewer_agent": "/root/selected_bureau_entry_review",
                "stage": stage, "phase": phase,
            }
            raw = json.dumps(review, sort_keys=True).encode()
            row = {"path": path.as_posix(),
                   "sha256": hashlib.sha256(raw).hexdigest()}
            def read(selected, digest):
                assert (selected, digest) == (path, row["sha256"])
                return raw
            assert bounded_g1b._g4_bureau_review(
                read, row, bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT,
                subject, stage, phase) == review
            wrong_row = dict(row, path=str(path.with_name("swapped.json")))
            with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
                bounded_g1b._g4_bureau_review(
                    read, wrong_row, bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT,
                    subject, stage, phase)
            assert caught.value.reason_code == "bounded_g4_bureau_review_path"
            for field, value in (
                ("subject_sha256", "0" * 64),
                ("stage", "apply" if stage == "enable" else "enable"),
                ("phase", "post-push" if phase != "post-push" else "development"),
                ("independent", False),
                ("implementation_authorship", True),
                ("reviewer_agent", "/root/selected_bureau_entry_author"),
            ):
                changed = dict(review, **{field: value})
                changed_raw = json.dumps(changed, sort_keys=True).encode()
                changed_row = dict(row, sha256=hashlib.sha256(changed_raw).hexdigest())
                with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
                    bounded_g1b._g4_bureau_review(
                        lambda _p, _d: changed_raw, changed_row,
                        bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT,
                        subject, stage, phase)
                assert caught.value.reason_code == "bounded_g4_bureau_independent_subject"
    assert len(set(subjects.values())) == 6


def test_selected_bureau_v8_apply_requires_exact_enable_effect(monkeypatch):
    # The selected ordinary evidence bytes are embedded; no repository loader runs.
    vector_raw = base64.b64decode(
        "ew0KICAic2NoZW1hIjogImVtcjQuc3RhZ2UxX3NlbGVjdGVkX2J1cmVhdV9wcm9kdWN0X3ZlY3Rvci52MSIsDQogICJzdGF0dXMi"
        "OiAiUFJFUEFSRURfTk9UX0FETUlUVEVEX09SX0VYRUNVVEVEIiwNCiAgInNlbGVjdGVkX2Jhc2UiOiB7DQogICAgImNvbW1pdCI6"
        "ICJmNTkyZTRkOTljMzQyNDM5OTZmNmJmNTY3NDQzMmIyZWI2Zjg1N2YwIiwNCiAgICAidHJlZSI6ICI4ZTI3NjcyYWVhNGVjMzQw"
        "YjJjNThmMTdjYWU4N2IwYzM5YTRjMzhmIg0KICB9LA0KICAicHJlZGVjZXNzb3Jfc2NvcGVfc2hhMjU2IjogImYyYzg1YmUyZTgw"
        "M2NmMWQwNTFkZTY5MmQwOWRlNGViOTg3ODlhYTFjZTQ3OTY0Yzg5OTAxNDZmMGYyOWE2MDciLA0KICAiZW50cmllcyI6IFsNCiAg"
        "ICB7DQogICAgICAidGFyZ2V0IjogImFwcC9zZXJ2aWNlcy9yZWNlcHRpb25fb25lX3Byb3Bvc2FsX3J1bnRpbWUucHkiLA0KICAg"
        "ICAgInBhdGgiOiAiQzovVXNlcnMvdGhlcmUvRU1SNC10b29scy9zZWxlY3RlZC1jb250ZXh0LWJ1cmVhdS1jYW5kaWRhdGUtdjIv"
        "YXBwL3NlcnZpY2VzL3JlY2VwdGlvbl9vbmVfcHJvcG9zYWxfcnVudGltZS5weSIsDQogICAgICAiYnl0ZXMiOiAyNzYwMywNCiAg"
        "ICAgICJzaGEyNTYiOiAiMmUzNjg3ZGU1Y2NlMzgzMzUxZTZiYjU5ZWEzN2JkMTM2NTNjMmExMzQ5ZmFlMWI2YmJjYzBkZGNlNmZi"
        "MWZjYiIsDQogICAgICAiYmVmb3JlX3NoYTI1NiI6ICIxM2ExZjAzMDU1ZjRmNGMxYTZhZTg2OTM1M2RhYmZkZjk2OWZhODI2Yzhm"
        "Y2YwNDFmMDU4NmE1MWMwOGYxOWZlIg0KICAgIH0sDQogICAgew0KICAgICAgInRhcmdldCI6ICJzY3JpcHRzL3JlY2VwdGlvbl9v"
        "bmVfYnVyZWF1X3R5cGVkX3BsYW5fcHJvdG9jb2wucHkiLA0KICAgICAgInBhdGgiOiAiQzovVXNlcnMvdGhlcmUvRU1SNC10b29s"
        "cy9zZWxlY3RlZC1jb250ZXh0LWJ1cmVhdS1jYW5kaWRhdGUtdjIvc2NyaXB0cy9yZWNlcHRpb25fb25lX2J1cmVhdV90eXBlZF9w"
        "bGFuX3Byb3RvY29sLnB5IiwNCiAgICAgICJieXRlcyI6IDU5MjcwLA0KICAgICAgInNoYTI1NiI6ICI0MDZhNWI4YmNhYTI4MmI2"
        "ODY5OTcwOTIwMzM0MmQ4ZTEwODkzNmI4MzY0NGM5ZTdiN2UwMzU5YTM4YmFlMTlkIiwNCiAgICAgICJiZWZvcmVfc2hhMjU2Ijog"
        "IjJhYjdlNTMxNTkzYTZlMThhMDg5MWM2ZDVlMDU2MTIzMTdjMTMyMTlkYjU1NWJmY2NiNTVkNDU0MWUwNjU3ZTIiDQogICAgfSwN"
        "CiAgICB7DQogICAgICAidGFyZ2V0IjogIm9yY2hlc3RyYXRpb24vY29udGludWl0eS9yZWNlcHRpb24tb25lLWJ1cmVhdS10eXBl"
        "ZC1wbGFuLXByb3RvY29sL29wZXJhdG9yLWNhdGFsb2cuanNvbiIsDQogICAgICAicGF0aCI6ICJDOi9Vc2Vycy90aGVyZS9FTVI0"
        "LXRvb2xzL3NlbGVjdGVkLWNvbnRleHQtYnVyZWF1LWNhbmRpZGF0ZS12Mi9vcmNoZXN0cmF0aW9uL2NvbnRpbnVpdHkvcmVjZXB0"
        "aW9uLW9uZS1idXJlYXUtdHlwZWQtcGxhbi1wcm90b2NvbC9vcGVyYXRvci1jYXRhbG9nLmpzb24iLA0KICAgICAgImJ5dGVzIjog"
        "ODQzOSwNCiAgICAgICJzaGEyNTYiOiAiZmI5NjQyMDg0NzdmMTJmMDg0YWFjODc1MGZlMjVlN2YyYzVhNWQ2NDhhYjYyZDI5ZjUy"
        "MWVlNWQ4MDE5ZjU3OSIsDQogICAgICAiYmVmb3JlX3NoYTI1NiI6ICJmZTJkNTc1MjQzOGU2OTVmODk2MGUzM2FhYTdmMTVhN2I2"
        "MWYzZDRhMmM1M2ZkNjNiZTM3OTc3MTVlMzUwYmFjIg0KICAgIH0sDQogICAgew0KICAgICAgInRhcmdldCI6ICJ0ZXN0cy90ZXN0"
        "X3JlY2VwdGlvbl9vbmVfc2VsZWN0ZWRfY29udGV4dC5weSIsDQogICAgICAicGF0aCI6ICJDOi9Vc2Vycy90aGVyZS9FTVI0LXRv"
        "b2xzL3NlbGVjdGVkLWNvbnRleHQtYnVyZWF1LWNhbmRpZGF0ZS12Mi90ZXN0cy90ZXN0X3JlY2VwdGlvbl9vbmVfc2VsZWN0ZWRf"
        "Y29udGV4dC5weSIsDQogICAgICAiYnl0ZXMiOiAxMzI3OCwNCiAgICAgICJzaGEyNTYiOiAiMWVhMTViOTQ0ZGE1MmM3YjA3YTcw"
        "NDBjMDBkM2IwOWNhZTVhMWNlYzcyN2FiYzY0NTkyMGY4MDI5NjkwMmE1NSIsDQogICAgICAiYmVmb3JlX3NoYTI1NiI6IG51bGwN"
        "CiAgICB9LA0KICAgIHsNCiAgICAgICJ0YXJnZXQiOiAic3RhZ2UxX2RlbW9faHR0cC5weSIsDQogICAgICAicGF0aCI6ICJDOi9V"
        "c2Vycy90aGVyZS9FTVI0LXRvb2xzL3NlbGVjdGVkLWNvbnRleHQtc3RhZ2UxLWJyaWRnZS1jYW5kaWRhdGUtdjIvc3RhZ2UxX2Rl"
        "bW9faHR0cC5weSIsDQogICAgICAiYnl0ZXMiOiAxMDI2NDksDQogICAgICAic2hhMjU2IjogImM1OTRjMWMwYmZhYzcyYzYzOTM0"
        "YjY0Yzc2ZDNmNzY3YWQ5ZjVlMWYxYzM1MDhlYjVhZDJkMjM2ZGU5YjA1MjgiLA0KICAgICAgImJlZm9yZV9zaGEyNTYiOiAiM2Fj"
        "ODExOWZjYmNlYTc2NDY1MjYxMDg5ZTVlOTI1ZDhkNDBkNTNlYTY3Mjc3OGI4NjBiODhjOGJkMTdjNThmOSINCiAgICB9LA0KICAg"
        "IHsNCiAgICAgICJ0YXJnZXQiOiAic3RhdGljL2RlbW8vc3RhZ2UxLWludGVyYWN0aXZlLmpzIiwNCiAgICAgICJwYXRoIjogIkM6"
        "L1VzZXJzL3RoZXJlL0VNUjQtdG9vbHMvc2VsZWN0ZWQtY29udGV4dC1zdGFnZTEtYnJpZGdlLWNhbmRpZGF0ZS12Mi9zdGF0aWMv"
        "ZGVtby9zdGFnZTEtaW50ZXJhY3RpdmUuanMiLA0KICAgICAgImJ5dGVzIjogNDc5MjcsDQogICAgICAic2hhMjU2IjogImNjZmNi"
        "MzI3YjgyNjQyMDE3NzYwYmU2NmUzZmNhYTI0MTZmNDI1ODExM2Q5MjRkNzEzZmIzZWIzMjUyZDJlY2EiLA0KICAgICAgImJlZm9y"
        "ZV9zaGEyNTYiOiAiMjg2YzcwOGQ1Yzc5YjQ3MjMyYzUyZTg5OGM5YTRmOWE3NTQ3YmE5MTA5NTk5ZTZkYWI4NTdiN2Q1OWRhN2Nk"
        "MCINCiAgICB9LA0KICAgIHsNCiAgICAgICJ0YXJnZXQiOiAidGVzdHMvdGVzdF9zdGFnZTFfYnVyZWF1X3Byb2plY3Rpb24ucHki"
        "LA0KICAgICAgInBhdGgiOiAiQzovVXNlcnMvdGhlcmUvRU1SNC10b29scy9zZWxlY3RlZC1jb250ZXh0LXN0YWdlMS1icmlkZ2Ut"
        "Y2FuZGlkYXRlLXYyL3Rlc3RzL3Rlc3Rfc3RhZ2UxX2J1cmVhdV9wcm9qZWN0aW9uLnB5IiwNCiAgICAgICJieXRlcyI6IDYyNTQs"
        "DQogICAgICAic2hhMjU2IjogImRkOWU0NGVjZjAyYjNjMjc2YTMzYzMyNWRkNGQ5OTYzOWVmYjQ3ZmNhMDhmNTM4OGFmY2ZlMzg4"
        "MzVlMDE0OTMiLA0KICAgICAgImJlZm9yZV9zaGEyNTYiOiBudWxsDQogICAgfSwNCiAgICB7DQogICAgICAidGFyZ2V0IjogInRl"
        "c3RzL3Rlc3Rfc3RhZ2UxX2J1cmVhdV9zdWdnZXN0aW9uLmNqcyIsDQogICAgICAicGF0aCI6ICJDOi9Vc2Vycy90aGVyZS9FTVI0"
        "LXRvb2xzL3NlbGVjdGVkLWNvbnRleHQtc3RhZ2UxLWJyaWRnZS1jYW5kaWRhdGUtdjIvdGVzdHMvdGVzdF9zdGFnZTFfYnVyZWF1"
        "X3N1Z2dlc3Rpb24uY2pzIiwNCiAgICAgICJieXRlcyI6IDM5MzcsDQogICAgICAic2hhMjU2IjogIjNlNWU1ODAyNDBhOTg0MjU0"
        "MjlkYjM3NzIxMTY1MTU2MDdiNmJmYjg3YWY1ZjRhNTJkZmQ0NmVmMzhmZmVmN2MiLA0KICAgICAgImJlZm9yZV9zaGEyNTYiOiBu"
        "dWxsDQogICAgfQ0KICBdLA0KICAic291cmNlX3Jldmlld19xdWFsaWZpY2F0aW9uIjogIkNvcnJlY3RlZCBwcm9zcGVjdGl2ZSBl"
        "aWdodC1maWxlIFYyIHNvdXJjZSBzdWJqZWN0LiBSZXNvbHZlcyBuYW1lZCBWMSByZXZpZXcgZmluZGluZ3M7IGluZGVwZW5kZW50"
        "IHRhcmdldGVkIHJldmlldyBwZW5kaW5nLiBObyBwcm9kdWN0IGFwcGxpY2F0aW9uLCBhZG1pc3Npb24sIHJ1bnRpbWUgb3IgdGVz"
        "dCBleGVjdXRpb24uIiwNCiAgImludGVuZGVkX2ludmFyaWFudCI6ICJFeGlzdGluZyBCdXJlYXUvY29udGV4dC9wcm9vZnJlYWRl"
        "ciBwcmVwYXJlcyBzdGFmZiBzZWxlY3RlZCBtb3ZlOyBvcmlnaW5hbCB3b3JkcyBwcmVzZXJ2ZWQ7IGNvbmZsaWN0cyBjbGFyaWZ5"
        "OyBleGFjdCBjdXJyZW50IElEL3ZlcnNpb24gY2hlY2tlZDsgb25lIGNsZWFuIG9wdGlvbiBlbnRlcnMgZXhpc3Rpbmcgc2lnbmVk"
        "IHByb3Bvc2FsL2h1bWFuIGNvbmZpcm0vaWRlbXBvdGVuY3kvcmVhZGJhY2siLA0KICAiZXhjbHVkZWRfZWZmZWN0cyI6IFsNCiAg"
        "ICAicHJvdmlkZXJzIiwNCiAgICAicmVhbCBkYXRhIiwNCiAgICAicHVibGljIGxpc3RlbmVyIiwNCiAgICAicHJvZHVjdCBydW50"
        "aW1lIiwNCiAgICAicHJvdGVjdGVkIHJlZiBtb3ZlbWVudCIsDQogICAgImRlcGxveW1lbnQiLA0KICAgICJzcGVuZGluZyBleHBh"
        "bnNpb24iDQogIF0sDQogICJsaW1pdGF0aW9ucyI6IFsNCiAgICAiRGV0ZXJtaW5pc3RpYyBwYXRoLCBub3QgY29udGV4dHVhbCBM"
        "TE0gYWNjZXB0YW5jZSIsDQogICAgIk9ubHkgb25lIHVuYW1iaWd1b3VzIGNsZWFuIGNhbmRpZGF0ZTsgbXVsdGlwbGUgb3B0aW9u"
        "cyBvciB1bmtub3duIHdhcm5pbmdzIGNsYXJpZnkiLA0KICAgICJCYWNrZW5kIHVuaXQgc291cmNlIGluY2x1ZGVzIGZha2Ugc2Nv"
        "cGVkIE9STSBxdWVyeSBvYnNlcnZhdGlvbnMsIG5vdCBkYXRhYmFzZSBpc29sYXRpb24gcHJvb2YiLA0KICAgICJFbnRyeS1lbmFi"
        "bGVtZW50LCB0ZXN0IGJpbmRpbmcsIGFwcGxpY2F0aW9uIGFuZCBydW50aW1lIGFjY2VwdGFuY2UgcmVtYWluIHNlcGFyYXRlIg0K"
        "ICBdLA0KICAiY29ycmVjdGlvbl9vZl9yZXZpZXdfc2hhMjU2IjogImIyYzg2Y2U3YzEzZmZkNzY1MGQ0YjYwOTQyN2FlYWU3OGEz"
        "YmQxNzE0YWZmZmZmYzgyZjA1YjJmMTdiNjEyNjUiDQp9"
    )
    mapping_raw = base64.b64decode(
        "ewogICJzY2hlbWEiOiAiZW1yNC5zdGFnZTFfc2VsZWN0ZWRfYnVyZWF1X2NvbWJpbmVkX3NvdXJjZV9tYXBwaW5nX3Jldmlldy52"
        "MSIsCiAgInN0YXR1cyI6ICJQQVNTIiwKICAidmVyZGljdCI6ICJQQVNTX0c0X1NUQUdFMV9TRUxFQ1RFRF9CVVJFQVVfRVhBQ1Rf"
        "TUFQUElORyIsCiAgInJldmlld2VyX2FnZW50IjogIi9yb290L3NlbGVjdGVkX2NvbnRleHRfZGVzaWduX3JldmlldyIsCiAgImlu"
        "ZGVwZW5kZW50IjogdHJ1ZSwKICAiaW1wbGVtZW50YXRpb25fYXV0aG9yc2hpcCI6IGZhbHNlLAogICJwcm9kdWN0X3ZlY3Rvcl9z"
        "aGEyNTYiOiAiODk3M2JiOWJkOWQyNDMxZDNiY2RhM2MxZmYwNjk4ZGY1NzAzZGMxZGU3MDliZjYzOTkxNjkwMDUwZmE2MDk2YyIs"
        "CiAgInBoeXNpY2FsX3RhcmdldF9yb3dzX2NoZWNrZWQiOiA4LAogICJibG9ja2luZ19maW5kaW5ncyI6IFtdLAogICJuYXJyYXRp"
        "dmVfcmV2aWV3IjogewogICAgInBhdGgiOiAiQzovVXNlcnMvdGhlcmUvRU1SNC10b29scy9zZWxlY3RlZC1jb250ZXh0LWJ1cmVh"
        "dS1jYW5kaWRhdGUtdjIvaW5kZXBlbmRlbnQtY29tYmluZWQtc291cmNlLW1hcHBpbmctcmV2aWV3LXYyLmpzb24iLAogICAgInNo"
        "YTI1NiI6ICIyNjI4MzU5NDlmYzY5ZTJiN2JmZmJiOGRlNjlmMTJhYTdjYWI0NDU4ZjM2ZTdkODM2NjExOGE4MjFhNTFmZTg1Igog"
        "IH0sCiAgInF1YWxpZmljYXRpb24iOiAiSW5kZXBlbmRlbnQgZXhhY3QtZWlnaHQtc291cmNlIG1hcHBpbmcganVkZ21lbnQgb25s"
        "eS4gTm8gcHJvZHVjdCBlbnRyeSBhZG1pc3Npb24sIGV4ZWN1dGFibGUgYWNjZXB0YW5jZSwgdGVzdCByZXN1bHQsIGFwcGxpY2F0"
        "aW9uLCBpbnRlZ3JhdGVkIGpvdXJuZXkgcHJvb2Ygb3IgY29udGV4dHVhbCBMTE0gYWNjZXB0YW5jZSBmb2xsb3dzLiIKfQo="
    )
    assert hashlib.sha256(vector_raw).hexdigest() == bounded_g1b.G4_BUREAU_VECTOR_SHA
    assert hashlib.sha256(mapping_raw).hexdigest() == bounded_g1b.G4_BUREAU_MAPPING_SHA
    predecessor_raw = bounded_g1b._canonical(_intention_scope()) + b"\n"
    assert hashlib.sha256(predecessor_raw).hexdigest() == (
        "f2c85be2e803cf1d051de692d09de4eb98789aa1ce47964c8990146f0f29a607")
    scope = _bureau_scope()
    target = Path("C:/synthetic-bureau-target")
    source = Path("C:/synthetic-bureau-source")
    activation_path = (bounded_g1b.G4_BUREAU_ROOT / "entry-admission-v1" /
                       "independent-enable-push-effect-review-v1.json")
    product_inputs = (
        bounded_g1b.CONFIGURATION_PATHS |
        {bounded_g1b.STATE, bounded_g1b.GATES, bounded_g1b.OVERLAY,
         bounded_g1b.AGENTS, bounded_g1b.G4_STAGE1_INTERACTIVE_SCOPE,
         bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE,
         bounded_g1b.G4_STAGE1_SUCCESSOR_TEST, bounded_g1b.G4_CI_WORKFLOW} |
        bounded_g1b.SOURCE_PATHS | bounded_g1b.CONTROLLER_PATHS |
        bounded_g1b.G4_BUREAU_PRODUCT)
    q = {
        "schema_version": bounded_g1b.G4_BUREAU_SCHEMA,
        "operation_id": "selected-bureau-apply-source",
        "operation_kind": "implement_g4_stage1_successor",
        "stage": "apply", "phase": "development",
        "base_commit": "b" * 40, "base_tree": "c" * 40,
        "expected_head": "d" * 40, "expected_index_tree": "e" * 40,
        "candidate_tree": "f" * 40,
        "source_sha256": scope["source_sha256"],
        "payload_sha256": {path: "a" * 64 for path in product_inputs},
        "repair_sha256": {path: {} for path in bounded_g1b.G4_BUREAU_PRODUCT},
        "source_review": {"path": "unused-before-product-inputs", "sha256": "a" * 64},
        "activation_acceptance": {},
        "product_vector": scope["product_vector"],
        "mapping_review": scope["mapping_review"],
    }
    accepted = {
        "status": "PASS",
        "verdict": "PASS_G4_STAGE1_SELECTED_BUREAU_CONTROL_PUBLICATION_EFFECT",
        "reviewer_agent": "/root/selected_bureau_entry_review",
        "independent": True, "implementation_authorship": False,
        "blocking_findings": [], "stage": "enable", "phase": "push",
        "base": bounded_g1b.G4_BUREAU_BASE["commit"],
        "commit": q["base_commit"], "candidate_tree": q["base_tree"],
        "control_activation_accepted": True,
        "same_attempt_remote_readback_verified": True,
        "protected_refs_unchanged": True,
        "whole_inverse_verified_same_attempt": True,
        "published_ref": bounded_g1b.G4_STAGE1_INTERACTIVE_BACKEND_REF,
    }
    def fake_git_bytes(_target, *args):
        assert args == ("cat-file", "blob",
                        bounded_g1b.G4_BUREAU_BASE["commit"] + ":" +
                        bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE)
        return predecessor_raw
    def fake_git(_target, *args):
        if args == ("rev-parse", bounded_g1b.G4_BUREAU_BASE["commit"] + "^{tree}"):
            return bounded_g1b.G4_BUREAU_BASE["tree"]
        assert args == ("cat-file", "commit", q["base_commit"])
        return ("tree " + q["base_tree"] + "\nparent " +
                bounded_g1b.G4_BUREAU_BASE["commit"] + "\n\nsynthetic")
    monkeypatch.setattr(bounded_g1b.trusted_git, "run_git_bytes", fake_git_bytes)
    monkeypatch.setattr(bounded_g1b.trusted_git, "run_git", fake_git)
    reached_product_inputs = []
    class ProductInputReached(Exception):
        pass
    def attempt(receipt, *, row_path=activation_path, row_sha=None):
        reached_product_inputs.clear()
        raw = json.dumps(receipt, sort_keys=True).encode()
        pin = hashlib.sha256(raw).hexdigest() if row_sha is None else row_sha
        selected_q = copy.deepcopy(q)
        selected_q["activation_acceptance"] = {
            "path": row_path.as_posix(), "sha256": pin}
        def read(path, digest):
            if path == bounded_g1b.G4_BUREAU_VECTOR:
                data = vector_raw
            elif path == bounded_g1b.G4_BUREAU_MAPPING:
                data = mapping_raw
            elif path == activation_path:
                data = raw
            elif path.is_relative_to(target):
                reached_product_inputs.append(path)
                raise ProductInputReached()
            else:
                raise AssertionError(f"unexpected synthetic read: {path}")
            if hashlib.sha256(data).hexdigest() != digest:
                raise bounded_g1b.BoundedG1BError(
                    "bounded_g1b_input_digest_changed")
            return data
        return bounded_g1b._load_g4_bureau_inputs(
            None, target, source,
            bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT,
            Path("C:/synthetic-bureau-scratch"), selected_q, read, {})
    with pytest.raises(ProductInputReached):
        attempt(accepted)
    assert reached_product_inputs
    for receipt, row_path, row_sha, reason in (
        (accepted, activation_path.with_name("swapped.json"), None,
         "bounded_g4_bureau_activation_path"),
        (accepted, activation_path, "0" * 64,
         "bounded_g1b_input_digest_changed"),
        *(
            (dict(accepted, **{field: value}), activation_path, None,
             "bounded_g4_bureau_activation_acceptance")
            for field, value in (
                ("base", "0" * 40),
                ("commit", "0" * 40),
                ("candidate_tree", "0" * 40),
                ("same_attempt_remote_readback_verified", False),
                ("protected_refs_unchanged", False),
                ("whole_inverse_verified_same_attempt", False),
            )
        ),
    ):
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            attempt(receipt, row_path=row_path, row_sha=row_sha)
        assert caught.value.reason_code == reason
        assert reached_product_inputs == []


def _bureau_v9_scope():
    # Frozen accepted V9 scope; the active scope is V10 after enablement.
    raw = base64.b64decode(
        "eyJhY3RpdmVfcHJvZmlsZSI6Ikc0X1NUQUdFMV9MT0NBTF9TVUNDRVNTT1IiLCJhZG1pc3Npb25fZ3JhbnRzX3J1bnRpbWVfYXV0aG9yaXR5IjpmYWxzZSwiYWxsb3dlZF9lZmZlY3RzIjpbImNvbnRyb2xfcGxhbmVfZWRpdCIsInByb2R1Y3RfYmVoYXZpb3JfY2hhbmdlIiwicmVwb3NpdG9yeV9yZWFkIiwidGFza19icmFuY2hfY29tbWl0IiwidGFza19icmFuY2hfcHVzaCJdLCJhbGxvd2VkX3BhdGhzIjpbImFwcC9zZXJ2aWNlcy9yZWNlcHRpb25fb25lX3Byb3Bvc2FsX3J1bnRpbWUucHkiLCJvcmNoZXN0cmF0aW9uL2NvbnRpbnVpdHkvcmVjZXB0aW9uLW9uZS1idXJlYXUtdHlwZWQtcGxhbi1wcm90b2NvbC9vcGVyYXRvci1jYXRhbG9nLmpzb24iLCJvcmNoZXN0cmF0aW9uL2NvbnRpbnVpdHkvcmVjZXB0aW9uLW9uZS1idXJlYXUtdHlwZWQtcGxhbi1wcm90b2NvbC9wbGFuLXJldmlldy5zY2hlbWEuanNvbiIsInNjcmlwdHMvcmVjZXB0aW9uX29uZV9idXJlYXVfdHlwZWRfcGxhbl9wcm90b2NvbC5weSIsInN0YWdlMV9kZW1vX2h0dHAucHkiLCJzdGF0aWMvZGVtby9zdGFnZTEtaW50ZXJhY3RpdmUuanMiLCJ0ZXN0cy90ZXN0X3JlY2VwdGlvbl9vbmVfc2VsZWN0ZWRfY29udGV4dC5weSIsInRlc3RzL3Rlc3Rfc3RhZ2UxX2J1cmVhdV9wcm9qZWN0aW9uLnB5IiwidGVzdHMvdGVzdF9zdGFnZTFfYnVyZWF1X3N1Z2dlc3Rpb24uY2pzIl0sImFsbG93ZWRfdGFza19raW5kIjoiZzRfc3RhZ2UxX2xvY2FsX3N1Y2Nlc3NvciIsImNvbnRyb2xfc2hhMjU2Ijp7Im9yY2hlc3RyYXRpb24vaGFybmVzc19zZXR0aW5ncy9wcm9ncmFtbWVfcmVjb3ZlcnkueWFtbCI6IjU0OTY1YTFmMmViNDc4N2E5N2I5Y2NhZGUwYjVlYmJmY2MwMmIwODljYjVjMTM2YWU1ZmExODY1ZWU2MjYxMTMiLCJvcmNoZXN0cmF0aW9uX2hhcm5lc3MvYm91bmRlZF9nMWIucHkiOiJmNmUxYmFiNDllMGE3MTkxMzlhNWFmNTUyNGZhMDNlMjQ1N2M4YmNmMzhlY2MzZTk4Yzk1YjhiOWFmMmQ5YTdkIiwib3JjaGVzdHJhdGlvbl9oYXJuZXNzL3JhaXNhX3BvbGljeS5weSI6Ijc3ZWU4MzVhY2E0NjYyNTYxNjZhMzk5Njc1ZDI1M2IzZDM2YmFjZjdjN2U4OTZmNTUyZWFjMjhhNmI5NzlhNzYiLCJ0ZXN0cy90ZXN0X2c0X3N0YWdlMV9zdWNjZXNzb3JfZW50cnkucHkiOiJlZmRhNTkzODUyNzdmNDJmZGFlODNmNTM1MWI3ZGJiZWNkOWI2ZWFjMTQ3ZjViY2VhMTk2ZTkwMDk5YzkzNDI2In0sImV4Y2x1ZGVkX2VmZmVjdHMiOlsidW5yZXZpZXdlZF9hcHBsaWNhdGlvbl9vcl9kYXRhYmFzZV9ydW50aW1lIiwidW5yZXZpZXdlZF9icm93c2VyX29yX21pY3JvcGhvbmVfcnVudGltZSIsInVucmV2aWV3ZWRfdm9pY2VfY2hpbGRfb3JfbmV0d29ya19lZ3Jlc3MiLCJwcm92aWRlcl9pbnZvY2F0aW9uIiwicmVhbF9kYXRhX2FjY2VzcyIsInByb3RlY3RlZF9yZWZfbW92ZW1lbnQiLCJkZXBsb3ltZW50IiwicHVibGljX2xpc3RlbmVyIl0sIm1hcHBpbmdfcmV2aWV3Ijp7InBhdGgiOiJDOi9Vc2Vycy90aGVyZS9FTVI0LXRvb2xzL3NlbGVjdGVkLWNvbnRleHQtYnVyZWF1LWNhbmRpZGF0ZS12My9pbmRlcGVuZGVudC1jb21iaW5lZC1zb3VyY2UtbWFwcGluZy1iaW5kaW5nLXYzLmpzb24iLCJzaGEyNTYiOiI3NDRhNGM4NWNmNWJjYTg0NTZkMjgwZWExMjBiOTE3YTlhYzVlZjAxYTlhMTUzNGM5OWU3NmI2NjYzMTkzZjA1In0sInByZWRlY2Vzc29yX3Njb3BlIjp7InNoYTI1NiI6IjI1ODc4ZmUzYWU2ZTBiMTU5ZWRkNzNhNWE3ODliYTNiOGYyNDA3NGQ1ZjcwYzQ5NTc3MzQyYzBjZWE5MTk2NjYifSwicHJvZHVjdF9zaGEyNTYiOnsiYXBwL3NlcnZpY2VzL3JlY2VwdGlvbl9vbmVfcHJvcG9zYWxfcnVudGltZS5weSI6IjJlMzY4N2RlNWNjZTM4MzM1MWU2YmI1OWVhMzdiZDEzNjUzYzJhMTM0OWZhZTFiNmJiY2MwZGRjZTZmYjFmY2IiLCJvcmNoZXN0cmF0aW9uL2NvbnRpbnVpdHkvcmVjZXB0aW9uLW9uZS1idXJlYXUtdHlwZWQtcGxhbi1wcm90b2NvbC9vcGVyYXRvci1jYXRhbG9nLmpzb24iOiJmYjk2NDIwODQ3N2YxMmYwODRhYWM4NzUwZmUyNWU3ZjJjNWE1ZDY0OGFiNjJkMjlmNTIxZWU1ZDgwMTlmNTc5Iiwib3JjaGVzdHJhdGlvbi9jb250aW51aXR5L3JlY2VwdGlvbi1vbmUtYnVyZWF1LXR5cGVkLXBsYW4tcHJvdG9jb2wvcGxhbi1yZXZpZXcuc2NoZW1hLmpzb24iOiI0NmUwMzNmMWEwNGQ1MTAxODRmMmI4ZTQ2MGM2NDEyNzhkYzRmOTM2ZTE2NmNkOTk2MmExZjQ4Y2Y2MmM1ZjE0Iiwic2NyaXB0cy9yZWNlcHRpb25fb25lX2J1cmVhdV90eXBlZF9wbGFuX3Byb3RvY29sLnB5IjoiZGJhM2JkNTdlODg3ZDkyZTlhM2Q3MWI4NjdhN2ZiNzI4YzM2MzY1ZmRkZWUwODJiMTcwZTU1NzFlNmU1YTRkMCIsInN0YWdlMV9kZW1vX2h0dHAucHkiOiJjNTk0YzFjMGJmYWM3MmM2MzkzNGI2NGM3NmQzZjc2N2FkOWY1ZTFmMWMzNTA4ZWI1YWQyZDIzNmRlOWIwNTI4Iiwic3RhdGljL2RlbW8vc3RhZ2UxLWludGVyYWN0aXZlLmpzIjoiY2NmY2IzMjdiODI2NDIwMTc3NjBiZTY2ZTNmY2FhMjQxNmY0MjU4MTEzZDkyNGQ3MTNmYjNlYjMyNTJkMmVjYSIsInRlc3RzL3Rlc3RfcmVjZXB0aW9uX29uZV9zZWxlY3RlZF9jb250ZXh0LnB5IjoiZWM2MmVhOTUyZmU3MWYxOTI4NDZkMDBkMTVlNTNiNWNlYzgwOWQ5M2UzNmY3MTFiYmZkZWNlOWM3YzU4YTkwNSIsInRlc3RzL3Rlc3Rfc3RhZ2UxX2J1cmVhdV9wcm9qZWN0aW9uLnB5IjoiZGQ5ZTQ0ZWNmMDJiM2MyNzZhMzNjMzI1ZGQ0ZDk5NjM5ZWZiNDdmY2EwOGY1Mzg4YWZjZmUzODgzNWUwMTQ5MyIsInRlc3RzL3Rlc3Rfc3RhZ2UxX2J1cmVhdV9zdWdnZXN0aW9uLmNqcyI6IjNlNWU1ODAyNDBhOTg0MjU0MjlkYjM3NzIxMTY1MTU2MDdiNmJmYjg3YWY1ZjRhNTJkZmQ0NmVmMzhmZmVmN2MifSwicHJvZHVjdF92ZWN0b3IiOnsicGF0aCI6IkM6L1VzZXJzL3RoZXJlL0VNUjQtdG9vbHMvc2VsZWN0ZWQtY29udGV4dC1idXJlYXUtY2FuZGlkYXRlLXYzL3Byb2R1Y3QtdmVjdG9yLXYzLmpzb24iLCJzaGEyNTYiOiIyYTk3YTI0NDEzZGI1MTJhZDgzNDU5MTA2NmFkOTZhNjJhNjY0NzVkNzhlOGMyYzAyOTQxMTU1MzdlZTZkOTE3In0sInJlY29yZGVkX2F0IjoiMjAyNi0xMC0yNVQxNDo1OToxNCswMDowMCIsInJ1bnRpbWVfYmluZGluZ19yZXF1aXJlZCI6dHJ1ZSwic2NoZW1hX3ZlcnNpb24iOiJhcmlhZG5lLmc0X3N0YWdlMV9zdWNjZXNzb3JfZW50cnlfc2NvcGUudjkiLCJzZWxlY3RlZF9iYXNlIjp7ImNvbW1pdCI6IjI0MzFkNDFhM2RmMmQ1MGM3N2E1NjEwY2EwYjBlOTI0NDA3NWVlNmYiLCJ0cmVlIjoiYzE0MTZjODViM2JmZGUwMDg0NTZiNmRiNmMwMjk4YmQ5ZTg2Mjg5NiJ9LCJzb3VyY2Vfc2hhMjU2Ijp7Im9yY2hlc3RyYXRpb25faGFybmVzcy9ib3VuZGVkX2cxYi5weSI6ImY2ZTFiYWI0OWUwYTcxOTEzOWE1YWY1NTI0ZmEwM2UyNDU3YzhiY2YzOGVjYzNlOThjOTViOGI5YWYyZDlhN2QiLCJvcmNoZXN0cmF0aW9uX2hhcm5lc3MvY29uZmlndXJhdGlvbl9jb3JlLnB5IjoiZjdiYTdhODBlYjBhNTkwZjlmYjcxYjg2NGU2YzFmOWY0MzI0MWQ5ZjdkNzBhMzhkYTY3YTkyNDNmZWEyMDhlNSIsIm9yY2hlc3RyYXRpb25faGFybmVzcy9waW5uZWRfcHJvZ3JhbW1lX2dhdGVrZWVwZXIucHkiOiJjMWZlYTlhMjg0OTA2OGVkOGU4N2RiZTFlN2NlYzFjYzdlNzYyZmEyYmM4ODc2ZmMzMmJiZGE4MGQyMjZjZjM5Iiwib3JjaGVzdHJhdGlvbl9oYXJuZXNzL3Byb2dyYW1tZV9hZG1pc3Npb24ucHkiOiJhYzgxNmE4YTc5YjJkODIyMmZhMzU3Nzc3YzA3NTk1MDkyN2U4NmNmMzBjOGE1YjI1ZmZkMDhhNDc0MDUyMTgxIiwib3JjaGVzdHJhdGlvbl9oYXJuZXNzL3JhaXNhX3BvbGljeS5weSI6Ijc3ZWU4MzVhY2E0NjYyNTYxNjZhMzk5Njc1ZDI1M2IzZDM2YmFjZjdjN2U4OTZmNTUyZWFjMjhhNmI5NzlhNzYiLCJvcmNoZXN0cmF0aW9uX2hhcm5lc3MvdHJ1c3RlZF9naXQucHkiOiI0YTg1NmJmZmUyYjY4ZDdjN2UxODc1MTUyNjI5YzkwMjRhMzI2NzliNTlkOWIxZWQ4MzAxYzM2OGQ0MWZmNTI3Iiwic2NyaXB0cy9yYWlzYV9hcmlhZG5lX3JlY292ZXJ5X3ByZWZsaWdodC5weSI6ImVkZmQzN2IzMDY3M2I4NTQ0ZDMwOWI1MzJjOTViM2ZkN2MyMGZmNTkyODgwYThhMDIzNWRmZGU2Y2ZjOGU3ZTQiLCJ0ZXN0cy90ZXN0X2JvdW5kZWRfZzFiLnB5IjoiYmIxYmU4NmNhMzkyMzJmZWEzMGMxZWE4NGNkZmIxMTQ0MjhkNTdiZTBmOGY2N2JmN2U4NmRhYWIwYmE3M2JjNSJ9LCJ2b2ljZV9hY3RpdmF0aW9uIjpmYWxzZX0K"
    )
    assert hashlib.sha256(raw).hexdigest() == "0170edc2fcbec1849256c0c8d036aa079c1d5b96dfb05f03349aec5ba2588a7d"
    return json.loads(raw)


def _exact_time_scope():
    """Frozen accepted V10 scope; active V11 does not rewrite its history."""
    raw = base64.b64decode("eyJhY3RpdmVfcHJvZmlsZSI6Ikc0X1NUQUdFMV9MT0NBTF9TVUNDRVNTT1IiLCJhZG1pc3Npb25fZ3JhbnRzX3J1bnRpbWVfYXV0aG9yaXR5IjpmYWxzZSwiYWxsb3dlZF9lZmZlY3RzIjpbImNvbnRyb2xfcGxhbmVfZWRpdCIsInByb2R1Y3RfYmVoYXZpb3JfY2hhbmdlIiwicmVwb3NpdG9yeV9yZWFkIiwidGFza19icmFuY2hfY29tbWl0IiwidGFza19icmFuY2hfcHVzaCJdLCJhbGxvd2VkX3BhdGhzIjpbImFwcC9yb3V0ZXJzL2FwcG9pbnRtZW50cy5weSIsImFwcC9zZXJ2aWNlcy9yZWNlcHRpb25fb25lX3Byb3Bvc2FsX3J1bnRpbWUucHkiXSwiYWxsb3dlZF90YXNrX2tpbmQiOiJnNF9zdGFnZTFfbG9jYWxfc3VjY2Vzc29yIiwiY29udHJvbF9zaGEyNTYiOnsib3JjaGVzdHJhdGlvbi9oYXJuZXNzX3NldHRpbmdzL3Byb2dyYW1tZV9yZWNvdmVyeS55YW1sIjoiNDY0OTFkMGU4N2FkOGM1NTcwYjVmZWZmYWM3NjRjZmI2OGEyZmQyNWIxODgxODkxZDM0NTRmYWQxNzk1OTExMiIsIm9yY2hlc3RyYXRpb25faGFybmVzcy9ib3VuZGVkX2cxYi5weSI6ImRhNjlhNzY2OTBmYmRmZDg4ODQ3MTAwMWQyNGExY2U1NmM1YzY2YWUwNTk4MzZhYzc4NTAyMDg4YWU1NTVkMjYiLCJvcmNoZXN0cmF0aW9uX2hhcm5lc3MvcmFpc2FfcG9saWN5LnB5IjoiMmRhYmVjMTczYmY3ZTM5NjI5ZTcwMzZjYWMyZDEzYzc3N2U1MjY0OWNlYTc0NGExZmVjNzc4YjVlOWI5MzMyZSIsInRlc3RzL3Rlc3RfZzRfc3RhZ2UxX3N1Y2Nlc3Nvcl9lbnRyeS5weSI6ImY1Y2U1MDQ1MmExMjg3YTRjNjQ4MDRkMjM1Njc2MWM3ODZmOTVhMDM4NzIyOTA3OTg0ZDkwYzQ2MWUyZDc1OTAifSwiZXhjbHVkZWRfZWZmZWN0cyI6WyJ1bnJldmlld2VkX2FwcGxpY2F0aW9uX29yX2RhdGFiYXNlX3J1bnRpbWUiLCJ1bnJldmlld2VkX2Jyb3dzZXJfb3JfbWljcm9waG9uZV9ydW50aW1lIiwidW5yZXZpZXdlZF92b2ljZV9jaGlsZF9vcl9uZXR3b3JrX2VncmVzcyIsInByb3ZpZGVyX2ludm9jYXRpb24iLCJyZWFsX2RhdGFfYWNjZXNzIiwicHJvdGVjdGVkX3JlZl9tb3ZlbWVudCIsImRlcGxveW1lbnQiLCJwdWJsaWNfbGlzdGVuZXIiXSwibWFwcGluZ19yZXZpZXciOnsicGF0aCI6IkM6L1VzZXJzL3RoZXJlL0VNUjQtdG9vbHMvc2VsZWN0ZWQtYnVyZWF1LWV4YWN0LXRpbWUtY2FuZGlkYXRlLXYxL2luZGVwZW5kZW50LWV4YWN0LXRpbWUtc291cmNlLXJldmlldy12MS5qc29uIiwic2hhMjU2IjoiNDAwYzU0YzJlMmE1YzliNjI4MzBjMTI2ZWEyOWQ1N2M4MGE4MGFlYWM5ZTgwYWQzMWUzNDA5MjFkM2VhNDkwZiJ9LCJwcmVkZWNlc3Nvcl9zY29wZSI6eyJzaGEyNTYiOiIwMTcwZWRjMmZjYmVjMTg0OTI1NmMwYzhkMDM2YWEwNzljMWQ1Yjk2ZGZiMDVmMDMzNDlhZWM1YmEyNTg4YTdkIn0sInByb2R1Y3Rfc2hhMjU2Ijp7ImFwcC9yb3V0ZXJzL2FwcG9pbnRtZW50cy5weSI6ImMyMzk4ODk3YjUxMmYzZDVhYjA5YWQwMzk3MWIzMzQzMjQ5MWM1MmVjY2M2ZDc1ZTczNTNlY2I3ZDBhNmExN2EiLCJhcHAvc2VydmljZXMvcmVjZXB0aW9uX29uZV9wcm9wb3NhbF9ydW50aW1lLnB5IjoiNGUxZjA2MDdhYmFjZmJlZjFkZDU5OThkMTRkYjI4M2ZhYmRkOGQ0ZWU3MDkwNWYzMDgxOWQxZTVhZGY4Y2E2NyJ9LCJwcm9kdWN0X3ZlY3RvciI6eyJwYXRoIjoiQzovVXNlcnMvdGhlcmUvRU1SNC10b29scy9zZWxlY3RlZC1idXJlYXUtZXhhY3QtdGltZS1jYW5kaWRhdGUtdjEvc291cmNlLXZlY3Rvci12MS5qc29uIiwic2hhMjU2IjoiNzJiNGI2NjIwOWE5YzYyNWU2NWI5Y2YyY2JiOGI4NDdiYjRiMjg0MzRjNzIwYjAwMjI3MDBlNTg0Zjc3Y2ExOSJ9LCJyZWNvcmRlZF9hdCI6IjIwMjYtMTAtMjZUMDA6MDA6MDArMDA6MDAiLCJydW50aW1lX2JpbmRpbmdfcmVxdWlyZWQiOnRydWUsInNjaGVtYV92ZXJzaW9uIjoiYXJpYWRuZS5nNF9zdGFnZTFfc3VjY2Vzc29yX2VudHJ5X3Njb3BlLnYxMCIsInNlbGVjdGVkX2Jhc2UiOnsiY29tbWl0IjoiNzM0NjBkODJmMDE4ZTQ0MWJkYzFmZDZmNTBiMjU5YjNkYzU4ZmNiZiIsInRyZWUiOiI2NmIxZGVmODU0ODkyOWQ4MzFiYmJhMDUxM2MyNzk5NGYyMGQyMTA4In0sInNvdXJjZV9zaGEyNTYiOnsib3JjaGVzdHJhdGlvbl9oYXJuZXNzL2JvdW5kZWRfZzFiLnB5IjoiZGE2OWE3NjY5MGZiZGZkODg4NDcxMDAxZDI0YTFjZTU2YzVjNjZhZTA1OTgzNmFjNzg1MDIwODhhZTU1NWQyNiIsIm9yY2hlc3RyYXRpb25faGFybmVzcy9jb25maWd1cmF0aW9uX2NvcmUucHkiOiJmN2JhN2E4MGViMGE1OTBmOWZiNzFiODY0ZTZjMWY5ZjQzMjQxZDlmN2Q3MGEzOGRhNjdhOTI0M2ZlYTIwOGU1Iiwib3JjaGVzdHJhdGlvbl9oYXJuZXNzL3Bpbm5lZF9wcm9ncmFtbWVfZ2F0ZWtlZXBlci5weSI6ImMxZmVhOWEyODQ5MDY4ZWQ4ZTg3ZGJlMWU3Y2VjMWNjN2U3NjJmYTJiYzg4NzZmYzMyYmJkYTgwZDIyNmNmMzkiLCJvcmNoZXN0cmF0aW9uX2hhcm5lc3MvcHJvZ3JhbW1lX2FkbWlzc2lvbi5weSI6ImFjODE2YThhNzliMmQ4MjIyZmEzNTc3NzdjMDc1OTUwOTI3ZTg2Y2YzMGM4YTViMjVmZmQwOGE0NzQwNTIxODEiLCJvcmNoZXN0cmF0aW9uX2hhcm5lc3MvcmFpc2FfcG9saWN5LnB5IjoiMmRhYmVjMTczYmY3ZTM5NjI5ZTcwMzZjYWMyZDEzYzc3N2U1MjY0OWNlYTc0NGExZmVjNzc4YjVlOWI5MzMyZSIsIm9yY2hlc3RyYXRpb25faGFybmVzcy90cnVzdGVkX2dpdC5weSI6IjRhODU2YmZmZTJiNjhkN2M3ZTE4NzUxNTI2MjljOTAyNGEzMjY3OWI1OWQ5YjFlZDgzMDFjMzY4ZDQxZmY1MjciLCJzY3JpcHRzL3JhaXNhX2FyaWFkbmVfcmVjb3ZlcnlfcHJlZmxpZ2h0LnB5IjoiZWRmZDM3YjMwNjczYjg1NDRkMzA5YjUzMmM5NWIzZmQ3YzIwZmY1OTI4ODBhOGEwMjM1ZGZkZTZjZmM4ZTdlNCIsInRlc3RzL3Rlc3RfYm91bmRlZF9nMWIucHkiOiJiYjFiZTg2Y2EzOTIzMmZlYTMwYzFlYTg0Y2RmYjExNDQyOGQ1N2JlMGY4ZjY3YmY3ZTg2ZGFhYjBiYTczYmM1In0sInZvaWNlX2FjdGl2YXRpb24iOmZhbHNlfQo=")
    assert hashlib.sha256(raw).hexdigest() == "9ccdcf5836ffad8897fca684e3767d082a80eeb88f15b9133364c0e32c0d5a9e"
    return json.loads(raw)


def test_exact_time_successor_is_two_existing_paths_and_requires_acceptance(monkeypatch):
    scope = _exact_time_scope()
    bounded_g1b.validate_g4_exact_time_scope(scope)
    assert scope["allowed_paths"] == sorted(bounded_g1b.G4_EXACT_TIME_PRODUCT)
    assert set(scope["allowed_paths"]) == {
        "app/services/reception_one_proposal_runtime.py",
        "app/routers/appointments.py",
    }
    assert scope["selected_base"] == bounded_g1b.G4_EXACT_TIME_BASE
    assert scope["admission_grants_runtime_authority"] is False
    for changed_field, changed_value in (
        ("selected_base", {"commit": "0" * 40, "tree": "0" * 40}),
        ("allowed_paths", scope["allowed_paths"] + ["app/other.py"]),
        ("product_sha256", {**scope["product_sha256"],
                            "app/routers/appointments.py": "0" * 64}),
        ("mapping_review", None),
    ):
        changed = copy.deepcopy(scope)
        changed[changed_field] = changed_value
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b.validate_g4_exact_time_scope(changed)
        assert caught.value.reason_code == "bounded_g4_exact_time_scope_boundary"

    for stage, kind, paths in (
        ("enable", "enable_g4_stage1_successor", bounded_g1b.G4_EXACT_TIME_CONTROL),
        ("apply", "implement_g4_stage1_successor", bounded_g1b.G4_EXACT_TIME_PRODUCT),
    ):
        q = {"schema_version": bounded_g1b.G4_EXACT_TIME_SCHEMA,
             "operation_kind": kind, "stage": stage,
             "repair_sha256": {p: {} for p in paths}}
        assert bounded_g1b.operation_paths(kind, q) == paths
        for replacement in (set(paths) | {"app/other.py"}, set(paths) - {next(iter(paths))}):
            with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
                bounded_g1b.operation_paths(kind, dict(
                    q, repair_sha256={p: {} for p in replacement}))
            assert caught.value.reason_code == "bounded_g4_exact_time_changed_paths"



def _exact_time_loader_fixture(monkeypatch, stage):
    """Exercise the production loader with pinned ordinary files and literal Git stubs."""
    root = Path("C:/Users/there/EMR4-tools/selected-bureau-exact-time-entry-candidate-v2")
    scope = json.loads((root / bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE).read_bytes())
    bounded_g1b.validate_g4_exact_time_scope(scope)
    target = Path("C:/synthetic-exact-time-target")
    source = Path("C:/synthetic-exact-time-source")
    product_root = Path("C:/Users/there/EMR4-tools/selected-bureau-exact-time-candidate-v1")
    before_files = {
        "app/services/reception_one_proposal_runtime.py": (
            Path("C:/Users/there/EMR4-tools/g4-selected-bureau-apply02/app/services/reception_one_proposal_runtime.py"),
            27603),
        "app/routers/appointments.py": (
            Path("C:/Users/there/EMR4-tools/stage1-mock-voice-database-work-v1/attempt-4/case/app/routers/appointments.py"),
            380498),
    }
    after_lengths = {"app/services/reception_one_proposal_runtime.py": 28549,
                     "app/routers/appointments.py": 381168}
    before_product = {}
    after_product = {}
    for path in sorted(bounded_g1b.G4_EXACT_TIME_PRODUCT):
        before_product[path] = before_files[path][0].read_bytes()
        after_product[path] = (product_root / path).read_bytes()
        assert len(before_product[path]) == before_files[path][1]
        assert len(after_product[path]) == after_lengths[path]
        assert hashlib.sha256(before_product[path]).hexdigest() == bounded_g1b.G4_EXACT_TIME_BEFORE_SHA[path]
        assert hashlib.sha256(after_product[path]).hexdigest() == bounded_g1b.G4_EXACT_TIME_PRODUCT_SHA[path]

    evidence = {}
    for path, digest in (
        (bounded_g1b.G4_EXACT_TIME_VECTOR, bounded_g1b.G4_EXACT_TIME_VECTOR_SHA),
        (bounded_g1b.G4_EXACT_TIME_SOURCE_REVIEW, bounded_g1b.G4_EXACT_TIME_SOURCE_REVIEW_SHA),
    ):
        raw = path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == digest
        evidence[path] = raw
    vector = json.loads(evidence[bounded_g1b.G4_EXACT_TIME_VECTOR])
    selected = (bounded_g1b.G4_EXACT_TIME_CONTROL if stage == "enable"
                else bounded_g1b.G4_EXACT_TIME_PRODUCT)
    inputs = (bounded_g1b.CONFIGURATION_PATHS |
              {bounded_g1b.STATE, bounded_g1b.GATES, bounded_g1b.OVERLAY,
               bounded_g1b.AGENTS, bounded_g1b.G4_STAGE1_INTERACTIVE_SCOPE,
               bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE,
               bounded_g1b.G4_STAGE1_SUCCESSOR_TEST, bounded_g1b.G4_CI_WORKFLOW} |
              bounded_g1b.SOURCE_PATHS | bounded_g1b.CONTROLLER_PATHS |
              (bounded_g1b.G4_EXACT_TIME_PRODUCT if stage == "apply" else set()))
    payload = {path: b"synthetic-v10-payload:" + path.encode("utf-8") for path in inputs}
    for path in ("orchestration_harness/bounded_g1b.py",
                 "orchestration_harness/raisa_policy.py",
                 "orchestration/harness_settings/programme_recovery.yaml",
                 bounded_g1b.G4_STAGE1_SUCCESSOR_TEST):
        payload[path] = (root / path).read_bytes()
        assert hashlib.sha256(payload[path]).hexdigest() == scope["control_sha256"][path]
    payload[bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE] = bounded_g1b._canonical(scope) + b"\n"
    if stage == "apply":
        payload.update(after_product)
    predecessor = bounded_g1b._canonical(_bureau_v9_scope()) + b"\n"
    assert hashlib.sha256(predecessor).hexdigest() == scope["predecessor_scope"]["sha256"]
    base_commit = (bounded_g1b.G4_EXACT_TIME_BASE["commit"] if stage == "enable"
                   else "b" * 40)
    base_tree = (bounded_g1b.G4_EXACT_TIME_BASE["tree"] if stage == "enable"
                 else "c" * 40)
    committed = dict(payload)
    if stage == "enable":
        for path in selected:
            committed[path] = (predecessor if path == bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE
                               else b"synthetic-v10-before:" + path.encode("utf-8"))
    else:
        committed.update(before_product)
    q = {
        "schema_version": bounded_g1b.G4_EXACT_TIME_SCHEMA,
        "operation_id": "exact-time-synthetic-" + stage,
        "operation_kind": ("enable_g4_stage1_successor" if stage == "enable"
                           else "implement_g4_stage1_successor"),
        "stage": stage, "phase": "development",
        "base_commit": base_commit, "base_tree": base_tree,
        "expected_head": base_commit, "expected_index_tree": base_tree,
        "candidate_tree": "d" * 40,
        "source_sha256": copy.deepcopy(scope["source_sha256"]),
        "payload_sha256": {path: hashlib.sha256(raw).hexdigest()
                           for path, raw in payload.items()},
        "repair_sha256": {
            path: {"before_sha256": hashlib.sha256(committed[path]).hexdigest(),
                   "after_sha256": hashlib.sha256(payload[path]).hexdigest()}
            for path in selected},
        "source_review": {}, "activation_acceptance": None,
        "product_vector": scope["product_vector"],
        "mapping_review": scope["mapping_review"],
    }
    activation_path = (bounded_g1b.G4_EXACT_TIME_ROOT / "entry-admission-v1" /
                       "independent-enable-push-effect-review-v1.json")
    activation = None
    if stage == "apply":
        activation = {
            "status": "PASS", "verdict": "PASS_G4_STAGE1_EXACT_TIME_CONTROL_PUBLICATION_EFFECT",
            "reviewer_agent": "/root/independent-enable-reviewer",
            "independent": True, "implementation_authorship": False,
            "blocking_findings": [], "stage": "enable", "phase": "push",
            "base": bounded_g1b.G4_EXACT_TIME_BASE["commit"],
            "commit": base_commit, "candidate_tree": base_tree,
            "control_activation_accepted": True,
            "same_attempt_remote_readback_verified": True,
            "protected_refs_unchanged": True,
            "whole_inverse_verified_same_attempt": True,
            "published_ref": bounded_g1b.G4_STAGE1_INTERACTIVE_BACKEND_REF,
        }
        raw = json.dumps(activation, sort_keys=True).encode("utf-8")
        q["activation_acceptance"] = {
            "path": activation_path.as_posix(),
            "sha256": hashlib.sha256(raw).hexdigest()}
        evidence[activation_path] = raw
    subject_path = (bounded_g1b.G4_EXACT_TIME_ROOT / "entry-admission-v1" /
                    ("independent-" + stage + "-development-subject-review-v1.json"))
    review = {
        "schema": "emr4.g4_operation_review.v1", "status": "PASS",
        "verdict": "PASS_G4_STAGE1_EXACT_TIME_EXACT_ADMISSION_SUBJECT",
        "subject_sha256": bounded_g1b.g4_exact_time_review_subject(q),
        "stage": stage, "phase": "development",
        "independent": True, "implementation_authorship": False,
        "blocking_findings": [], "reviewer_agent": "/root/independent-subject-reviewer",
    }
    raw = json.dumps(review, sort_keys=True).encode("utf-8")
    q["source_review"] = {"path": subject_path.as_posix(),
                          "sha256": hashlib.sha256(raw).hexdigest()}
    evidence[subject_path] = raw

    def read(path, digest):
        if path in evidence:
            raw = evidence[path]
            assert hashlib.sha256(raw).hexdigest() == digest
            return raw
        for root_path in (target, source, Path(vector["owned_candidate_root"])):
            if path.is_relative_to(root_path):
                relative = path.relative_to(root_path).as_posix()
                if root_path == source and relative in bounded_g1b.SOURCE_PATHS | bounded_g1b.CONTROLLER_PATHS:
                    assert digest == q["source_sha256"][relative]
                    return (payload[relative] if stage == "enable" and relative in selected
                            else committed[relative])
                if root_path == target:
                    assert digest == q["payload_sha256"][relative]
                    assert hashlib.sha256(payload[relative]).hexdigest() == digest
                    return payload[relative]
                assert relative in after_product
                assert digest == bounded_g1b.G4_EXACT_TIME_PRODUCT_SHA[relative]
                return after_product[relative]
        raise AssertionError("unexpected synthetic read")

    def fake_git_bytes(_target, *args):
        if args == ("cat-file", "blob", bounded_g1b.G4_EXACT_TIME_BASE["commit"] +
                    ":" + bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE):
            return predecessor
        if args[:3] == ("ls-tree", "-z", base_commit):
            assert args[3] == "--" and args[4] in selected
            return b"100644 blob present\x00"
        assert args[:2] == ("cat-file", "blob")
        commit, relative = args[2].split(":", 1)
        if commit == bounded_g1b.G4_EXACT_TIME_BASE["commit"] and relative in (
                bounded_g1b.STATE, bounded_g1b.GATES, bounded_g1b.OVERLAY,
                bounded_g1b.AGENTS):
            return committed[relative]
        assert commit == base_commit and relative in committed
        return committed[relative]

    def fake_git(_target, *args):
        if args == ("rev-parse", bounded_g1b.G4_EXACT_TIME_BASE["commit"] + "^{tree}"):
            return bounded_g1b.G4_EXACT_TIME_BASE["tree"]
        assert args == ("cat-file", "commit", base_commit)
        return ("tree " + base_tree + "\nparent " +
                bounded_g1b.G4_EXACT_TIME_BASE["commit"] + "\n\nsynthetic")

    monkeypatch.setattr(bounded_g1b.trusted_git, "run_git_bytes", fake_git_bytes)
    monkeypatch.setattr(bounded_g1b.trusted_git, "run_git", fake_git)
    monkeypatch.setattr(bounded_g1b.trusted_git, "attest_target_index",
                        lambda *_args, **_kwargs: {"synthetic": True})

    def load(selected_q):
        return bounded_g1b._load_g4_exact_time_inputs(
            None, target, source, bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT,
            Path("C:/synthetic-exact-time-scratch"), selected_q, read, {})
    return q, load, evidence, subject_path, activation_path


@pytest.mark.parametrize("stage", ["enable", "apply"])
def test_exact_time_loader_valid_baseline_and_targeted_rejections(monkeypatch, stage):
    q, load, evidence, subject_path, activation_path = _exact_time_loader_fixture(
        monkeypatch, stage)
    loaded = load(q)
    assert loaded.binding == q
    assert loaded.evidence["scope"]["schema_version"] == bounded_g1b.G4_EXACT_TIME_SCOPE_SCHEMA
    assert loaded.evidence["review"]["subject_sha256"] == bounded_g1b.g4_exact_time_review_subject(q)

    def rejected(changed, reason):
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            load(changed)
        assert caught.value.reason_code == reason

    changed = copy.deepcopy(q)
    changed["phase"] = "runtime"
    rejected(changed, "bounded_g4_exact_time_binding_version")
    changed = copy.deepcopy(q)
    changed["repair_sha256"]["app/other.py"] = {"before_sha256": "0" * 64,
                                                     "after_sha256": "1" * 64}
    rejected(changed, "bounded_g4_exact_time_changed_paths")
    changed = copy.deepcopy(q)
    changed["source_sha256"]["app/other.py"] = "0" * 64
    rejected(changed, "bounded_g4_exact_time_sources")
    changed = copy.deepcopy(q)
    changed["source_sha256"]["orchestration_harness/bounded_g1b.py"] = "0" * 64
    rejected(changed, "bounded_g4_exact_time_scope_sources")
    changed = copy.deepcopy(q)
    del changed["payload_sha256"][bounded_g1b.STATE]
    rejected(changed, "bounded_g4_exact_time_payload_paths")
    changed = copy.deepcopy(q)
    changed["payload_sha256"]["app/other.py"] = "0" * 64
    rejected(changed, "bounded_g4_exact_time_payload_paths")
    changed = copy.deepcopy(q)
    first_repair = sorted(changed["repair_sha256"])[0]
    changed["repair_sha256"][first_repair] = {}
    rejected(changed, "bounded_g4_exact_time_change_pair")
    changed = copy.deepcopy(q)
    changed["repair_sha256"][first_repair]["after_sha256"] = "0" * 64
    rejected(changed, "bounded_g4_exact_time_change_preimage")
    changed = copy.deepcopy(q)
    changed["candidate_tree"] = "e" * 40
    rejected(changed, "bounded_g4_exact_time_independent_subject")
    review = json.loads(evidence[subject_path])
    review["phase"] = "pre-push"
    evidence[subject_path] = json.dumps(review, sort_keys=True).encode("utf-8")
    changed = copy.deepcopy(q)
    changed["source_review"]["sha256"] = hashlib.sha256(evidence[subject_path]).hexdigest()
    rejected(changed, "bounded_g4_exact_time_independent_subject")
    review["phase"] = "development"
    review["independent"] = False
    evidence[subject_path] = json.dumps(review, sort_keys=True).encode("utf-8")
    changed = copy.deepcopy(q)
    changed["source_review"]["sha256"] = hashlib.sha256(evidence[subject_path]).hexdigest()
    rejected(changed, "bounded_g4_exact_time_independent_subject")
    if stage == "enable":
        changed = copy.deepcopy(q)
        changed["base_commit"] = "0" * 40
        rejected(changed, "bounded_g4_exact_time_enable_base")
    else:
        changed = copy.deepcopy(q)
        changed["activation_acceptance"] = None
        rejected(changed, "bounded_g4_exact_time_activation_row")
        activation = json.loads(evidence[activation_path])
        activation["same_attempt_remote_readback_verified"] = False
        evidence[activation_path] = json.dumps(activation, sort_keys=True).encode("utf-8")
        changed = copy.deepcopy(q)
        changed["activation_acceptance"]["sha256"] = hashlib.sha256(
            evidence[activation_path]).hexdigest()
        rejected(changed, "bounded_g4_exact_time_activation_acceptance")


def test_selected_bureau_v9_scope_exact_nine_and_rejects_widening():
    scope = _bureau_v9_scope()
    bounded_g1b.validate_g4_bureau_v9_scope(scope)
    assert scope["schema_version"] == bounded_g1b.G4_BUREAU_V9_SCOPE_SCHEMA
    assert scope["selected_base"] == bounded_g1b.G4_BUREAU_V9_BASE
    assert scope["allowed_paths"] == sorted(bounded_g1b.G4_BUREAU_V9_PRODUCT)
    assert scope["product_sha256"] == bounded_g1b.G4_BUREAU_V9_PRODUCT_SHA
    assert scope["predecessor_scope"] == {
        "sha256": "25878fe3ae6e0b159edd73a5a789ba3b8f24074d5f70c49577342c0cea919666"}
    assert scope["admission_grants_runtime_authority"] is False
    assert scope["runtime_binding_required"] is True
    for field, value in (
        ("allowed_paths", sorted(set(scope["allowed_paths"]) | {"app/main.py"})),
        ("allowed_paths", scope["allowed_paths"][:-1]),
        ("allowed_effects", sorted(set(scope["allowed_effects"]) | {"provider_invocation"})),
        ("runtime_binding_required", False),
        ("admission_grants_runtime_authority", True),
        ("product_vector", {"path": "other.json", "sha256": "0" * 64}),
        ("mapping_review", {"path": "other.json", "sha256": "0" * 64}),
        ("predecessor_scope", {"sha256": "0" * 64}),
    ):
        changed = copy.deepcopy(scope)
        changed[field] = value
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b.validate_g4_bureau_v9_scope(changed)
        assert caught.value.reason_code == "bounded_g4_bureau_v9_scope_boundary"


def test_selected_bureau_v9_dispatch_exact_nine_and_preserves_v8():
    for stage, kind, expected in (
        ("enable", "enable_g4_stage1_successor", bounded_g1b.G4_BUREAU_V9_CONTROL),
        ("apply", "implement_g4_stage1_successor", bounded_g1b.G4_BUREAU_V9_PRODUCT),
    ):
        q = {"schema_version": bounded_g1b.G4_BUREAU_V9_SCHEMA,
             "operation_kind": kind, "stage": stage,
             "repair_sha256": {p: {} for p in expected}}
        assert bounded_g1b.operation_paths(kind, q) == expected
        for changed_paths in (set(expected) - {next(iter(expected))},
                              set(expected) | {"app/main.py"}):
            changed = dict(q, repair_sha256={p: {} for p in changed_paths})
            with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
                bounded_g1b.operation_paths(kind, changed)
            assert caught.value.reason_code == "bounded_g4_bureau_v9_changed_paths"
    old = {"schema_version": bounded_g1b.G4_BUREAU_SCHEMA,
           "operation_kind": "implement_g4_stage1_successor", "stage": "apply",
           "repair_sha256": {p: {} for p in bounded_g1b.G4_BUREAU_PRODUCT}}
    assert bounded_g1b.operation_paths(old["operation_kind"], old) == bounded_g1b.G4_BUREAU_PRODUCT


def test_selected_bureau_v9_all_six_phase_subjects_and_independence():
    scope = _bureau_v9_scope()
    subjects = {}
    for stage, kind in (("enable", "enable_g4_stage1_successor"),
                        ("apply", "implement_g4_stage1_successor")):
        for phase in ("development", "pre-push", "post-push"):
            q = {
                "schema_version": bounded_g1b.G4_BUREAU_V9_SCHEMA,
                "operation_id": "selected-bureau-source",
                "operation_kind": kind, "stage": stage, "phase": phase,
                "base_commit": "a" * 40, "base_tree": "b" * 40,
                "expected_head": "c" * 40, "expected_index_tree": "d" * 40,
                "candidate_tree": "e" * 40,
                "source_sha256": scope["source_sha256"],
                "payload_sha256": {},
                "repair_sha256": {p: {} for p in (
                    bounded_g1b.G4_BUREAU_V9_CONTROL if stage == "enable"
                    else bounded_g1b.G4_BUREAU_V9_PRODUCT)},
                "activation_acceptance": None if stage == "enable" else {
                    "path": "review.json", "sha256": "f" * 64},
                "product_vector": scope["product_vector"],
                "mapping_review": scope["mapping_review"],
            }
            subject = bounded_g1b.g4_bureau_v9_review_subject(q)
            subjects[stage, phase] = subject
            for field, replacement in (
                ("stage", "apply" if stage == "enable" else "enable"),
                ("phase", "post-push" if phase != "post-push" else "development"),
                ("expected_head", "1" * 40),
                ("expected_index_tree", "2" * 40),
                ("candidate_tree", "3" * 40),
                ("operation_id", "other-operation"),
            ):
                changed = copy.deepcopy(q)
                changed[field] = replacement
                assert bounded_g1b.g4_bureau_v9_review_subject(changed) != subject
            path = (bounded_g1b.G4_BUREAU_V9_ROOT / "entry-admission-v1" /
                    f"independent-{stage}-{phase}-subject-review-v1.json")
            review = {
                "schema": "emr4.g4_operation_review.v1",
                "status": "PASS",
                "verdict": "PASS_G4_STAGE1_SELECTED_BUREAU_V9_EXACT_ADMISSION_SUBJECT",
                "subject_sha256": subject, "independent": True,
                "implementation_authorship": False, "blocking_findings": [],
                "reviewer_agent": "/root/selected_bureau_entry_review",
                "stage": stage, "phase": phase,
            }
            raw = json.dumps(review, sort_keys=True).encode()
            row = {"path": path.as_posix(),
                   "sha256": hashlib.sha256(raw).hexdigest()}
            def read(selected, digest):
                assert (selected, digest) == (path, row["sha256"])
                return raw
            assert bounded_g1b._g4_bureau_v9_review(
                read, row, bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT,
                subject, stage, phase) == review
            wrong_row = dict(row, path=str(path.with_name("swapped.json")))
            with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
                bounded_g1b._g4_bureau_v9_review(
                    read, wrong_row, bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT,
                    subject, stage, phase)
            assert caught.value.reason_code == "bounded_g4_bureau_v9_review_path"
            for field, value in (
                ("subject_sha256", "0" * 64),
                ("stage", "apply" if stage == "enable" else "enable"),
                ("phase", "post-push" if phase != "post-push" else "development"),
                ("independent", False),
                ("implementation_authorship", True),
                ("reviewer_agent", "/root/selected_bureau_entry_author"),
            ):
                changed = dict(review, **{field: value})
                changed_raw = json.dumps(changed, sort_keys=True).encode()
                changed_row = dict(row, sha256=hashlib.sha256(changed_raw).hexdigest())
                with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
                    bounded_g1b._g4_bureau_v9_review(
                        lambda _p, _d: changed_raw, changed_row,
                        bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT,
                        subject, stage, phase)
                assert caught.value.reason_code == "bounded_g4_bureau_v9_independent_subject"
    assert len(set(subjects.values())) == 6




def test_selected_bureau_v9_apply_requires_exact_enable_effect(monkeypatch):
    # The selected ordinary evidence bytes are embedded; no repository loader runs.
    vector_raw = base64.b64decode(
        "ewogICJzY2hlbWEiOiAiZW1yNC5zdGFnZTFfc2VsZWN0ZWRfYnVyZWF1X3Byb2R1Y3RfdmVjdG9yLnYxIiwKICAic3RhdHVzIjog"
        "IkNPUlJFQ1RFRF9TT1VSQ0VfUFJFUEFSQVRJT05fTk9UX0FETUlUVEVEIiwKICAic2VsZWN0ZWRfYmFzZSI6IHsKICAgICJjb21t"
        "aXQiOiAiMjQzMWQ0MWEzZGYyZDUwYzc3YTU2MTBjYTBiMGU5MjQ0MDc1ZWU2ZiIsCiAgICAidHJlZSI6ICJjMTQxNmM4NWIzYmZk"
        "ZTAwODQ1NmI2ZGI2YzAyOThiZDllODYyODk2IgogIH0sCiAgInByZWRlY2Vzc29yX3Njb3BlX3NoYTI1NiI6ICIyNTg3OGZlM2Fl"
        "NmUwYjE1OWVkZDczYTVhNzg5YmEzYjhmMjQwNzRkNWY3MGM0OTU3NzM0MmMwY2VhOTE5NjY2IiwKICAiZW50cmllcyI6IFsKICAg"
        "IHsKICAgICAgInRhcmdldCI6ICJhcHAvc2VydmljZXMvcmVjZXB0aW9uX29uZV9wcm9wb3NhbF9ydW50aW1lLnB5IiwKICAgICAg"
        "InBhdGgiOiAiQzovVXNlcnMvdGhlcmUvRU1SNC10b29scy9zZWxlY3RlZC1jb250ZXh0LWJ1cmVhdS1jYW5kaWRhdGUtdjMvYXBw"
        "L3NlcnZpY2VzL3JlY2VwdGlvbl9vbmVfcHJvcG9zYWxfcnVudGltZS5weSIsCiAgICAgICJieXRlcyI6IDI3NjAzLAogICAgICAi"
        "c2hhMjU2IjogIjJlMzY4N2RlNWNjZTM4MzM1MWU2YmI1OWVhMzdiZDEzNjUzYzJhMTM0OWZhZTFiNmJiY2MwZGRjZTZmYjFmY2Ii"
        "LAogICAgICAiYmVmb3JlX3NoYTI1NiI6ICIxM2ExZjAzMDU1ZjRmNGMxYTZhZTg2OTM1M2RhYmZkZjk2OWZhODI2YzhmY2YwNDFm"
        "MDU4NmE1MWMwOGYxOWZlIgogICAgfSwKICAgIHsKICAgICAgInRhcmdldCI6ICJzY3JpcHRzL3JlY2VwdGlvbl9vbmVfYnVyZWF1"
        "X3R5cGVkX3BsYW5fcHJvdG9jb2wucHkiLAogICAgICAicGF0aCI6ICJDOi9Vc2Vycy90aGVyZS9FTVI0LXRvb2xzL3NlbGVjdGVk"
        "LWNvbnRleHQtYnVyZWF1LWNhbmRpZGF0ZS12My9zY3JpcHRzL3JlY2VwdGlvbl9vbmVfYnVyZWF1X3R5cGVkX3BsYW5fcHJvdG9j"
        "b2wucHkiLAogICAgICAiYnl0ZXMiOiA1OTU2NCwKICAgICAgInNoYTI1NiI6ICJkYmEzYmQ1N2U4ODdkOTJlOWEzZDcxYjg2N2E3"
        "ZmI3MjhjMzYzNjVmZGRlZTA4MmIxNzBlNTU3MWU2ZTVhNGQwIiwKICAgICAgImJlZm9yZV9zaGEyNTYiOiAiMmFiN2U1MzE1OTNh"
        "NmUxOGEwODkxYzZkNWUwNTYxMjMxN2MxMzIxOWRiNTU1YmZjY2I1NWQ0NTQxZTA2NTdlMiIKICAgIH0sCiAgICB7CiAgICAgICJ0"
        "YXJnZXQiOiAib3JjaGVzdHJhdGlvbi9jb250aW51aXR5L3JlY2VwdGlvbi1vbmUtYnVyZWF1LXR5cGVkLXBsYW4tcHJvdG9jb2wv"
        "b3BlcmF0b3ItY2F0YWxvZy5qc29uIiwKICAgICAgInBhdGgiOiAiQzovVXNlcnMvdGhlcmUvRU1SNC10b29scy9zZWxlY3RlZC1j"
        "b250ZXh0LWJ1cmVhdS1jYW5kaWRhdGUtdjMvb3JjaGVzdHJhdGlvbi9jb250aW51aXR5L3JlY2VwdGlvbi1vbmUtYnVyZWF1LXR5"
        "cGVkLXBsYW4tcHJvdG9jb2wvb3BlcmF0b3ItY2F0YWxvZy5qc29uIiwKICAgICAgImJ5dGVzIjogODQzOSwKICAgICAgInNoYTI1"
        "NiI6ICJmYjk2NDIwODQ3N2YxMmYwODRhYWM4NzUwZmUyNWU3ZjJjNWE1ZDY0OGFiNjJkMjlmNTIxZWU1ZDgwMTlmNTc5IiwKICAg"
        "ICAgImJlZm9yZV9zaGEyNTYiOiAiZmUyZDU3NTI0MzhlNjk1Zjg5NjBlMzNhYWE3ZjE1YTdiNjFmM2Q0YTJjNTNmZDYzYmUzNzk3"
        "NzE1ZTM1MGJhYyIKICAgIH0sCiAgICB7CiAgICAgICJ0YXJnZXQiOiAidGVzdHMvdGVzdF9yZWNlcHRpb25fb25lX3NlbGVjdGVk"
        "X2NvbnRleHQucHkiLAogICAgICAicGF0aCI6ICJDOi9Vc2Vycy90aGVyZS9FTVI0LXRvb2xzL3NlbGVjdGVkLWNvbnRleHQtYnVy"
        "ZWF1LWNhbmRpZGF0ZS12My90ZXN0cy90ZXN0X3JlY2VwdGlvbl9vbmVfc2VsZWN0ZWRfY29udGV4dC5weSIsCiAgICAgICJieXRl"
        "cyI6IDEzMjc5LAogICAgICAic2hhMjU2IjogImVjNjJlYTk1MmZlNzFmMTkyODQ2ZDAwZDE1ZTUzYjVjZWM4MDlkOTNlMzZmNzEx"
        "YmJmZGVjZTljN2M1OGE5MDUiLAogICAgICAiYmVmb3JlX3NoYTI1NiI6IG51bGwKICAgIH0sCiAgICB7CiAgICAgICJ0YXJnZXQi"
        "OiAic3RhZ2UxX2RlbW9faHR0cC5weSIsCiAgICAgICJwYXRoIjogIkM6L1VzZXJzL3RoZXJlL0VNUjQtdG9vbHMvc2VsZWN0ZWQt"
        "Y29udGV4dC1idXJlYXUtY2FuZGlkYXRlLXYzL3N0YWdlMV9kZW1vX2h0dHAucHkiLAogICAgICAiYnl0ZXMiOiAxMDI2NDksCiAg"
        "ICAgICJzaGEyNTYiOiAiYzU5NGMxYzBiZmFjNzJjNjM5MzRiNjRjNzZkM2Y3NjdhZDlmNWUxZjFjMzUwOGViNWFkMmQyMzZkZTli"
        "MDUyOCIsCiAgICAgICJiZWZvcmVfc2hhMjU2IjogIjNhYzgxMTlmY2JjZWE3NjQ2NTI2MTA4OWU1ZTkyNWQ4ZDQwZDUzZWE2NzI3"
        "NzhiODYwYjg4YzhiZDE3YzU4ZjkiCiAgICB9LAogICAgewogICAgICAidGFyZ2V0IjogInN0YXRpYy9kZW1vL3N0YWdlMS1pbnRl"
        "cmFjdGl2ZS5qcyIsCiAgICAgICJwYXRoIjogIkM6L1VzZXJzL3RoZXJlL0VNUjQtdG9vbHMvc2VsZWN0ZWQtY29udGV4dC1idXJl"
        "YXUtY2FuZGlkYXRlLXYzL3N0YXRpYy9kZW1vL3N0YWdlMS1pbnRlcmFjdGl2ZS5qcyIsCiAgICAgICJieXRlcyI6IDQ3OTI3LAog"
        "ICAgICAic2hhMjU2IjogImNjZmNiMzI3YjgyNjQyMDE3NzYwYmU2NmUzZmNhYTI0MTZmNDI1ODExM2Q5MjRkNzEzZmIzZWIzMjUy"
        "ZDJlY2EiLAogICAgICAiYmVmb3JlX3NoYTI1NiI6ICIyODZjNzA4ZDVjNzliNDcyMzJjNTJlODk4YzlhNGY5YTc1NDdiYTkxMDk1"
        "OTllNmRhYjg1N2I3ZDU5ZGE3Y2QwIgogICAgfSwKICAgIHsKICAgICAgInRhcmdldCI6ICJ0ZXN0cy90ZXN0X3N0YWdlMV9idXJl"
        "YXVfcHJvamVjdGlvbi5weSIsCiAgICAgICJwYXRoIjogIkM6L1VzZXJzL3RoZXJlL0VNUjQtdG9vbHMvc2VsZWN0ZWQtY29udGV4"
        "dC1idXJlYXUtY2FuZGlkYXRlLXYzL3Rlc3RzL3Rlc3Rfc3RhZ2UxX2J1cmVhdV9wcm9qZWN0aW9uLnB5IiwKICAgICAgImJ5dGVz"
        "IjogNjI1NCwKICAgICAgInNoYTI1NiI6ICJkZDllNDRlY2YwMmIzYzI3NmEzM2MzMjVkZDRkOTk2MzllZmI0N2ZjYTA4ZjUzODhh"
        "ZmNmZTM4ODM1ZTAxNDkzIiwKICAgICAgImJlZm9yZV9zaGEyNTYiOiBudWxsCiAgICB9LAogICAgewogICAgICAidGFyZ2V0Ijog"
        "InRlc3RzL3Rlc3Rfc3RhZ2UxX2J1cmVhdV9zdWdnZXN0aW9uLmNqcyIsCiAgICAgICJwYXRoIjogIkM6L1VzZXJzL3RoZXJlL0VN"
        "UjQtdG9vbHMvc2VsZWN0ZWQtY29udGV4dC1idXJlYXUtY2FuZGlkYXRlLXYzL3Rlc3RzL3Rlc3Rfc3RhZ2UxX2J1cmVhdV9zdWdn"
        "ZXN0aW9uLmNqcyIsCiAgICAgICJieXRlcyI6IDM5MzcsCiAgICAgICJzaGEyNTYiOiAiM2U1ZTU4MDI0MGE5ODQyNTQyOWRiMzc3"
        "MjExNjUxNTYwN2I2YmZiODdhZjVmNGE1MmRmZDQ2ZWYzOGZmZWY3YyIsCiAgICAgICJiZWZvcmVfc2hhMjU2IjogbnVsbAogICAg"
        "fSwKICAgIHsKICAgICAgInRhcmdldCI6ICJvcmNoZXN0cmF0aW9uL2NvbnRpbnVpdHkvcmVjZXB0aW9uLW9uZS1idXJlYXUtdHlw"
        "ZWQtcGxhbi1wcm90b2NvbC9wbGFuLXJldmlldy5zY2hlbWEuanNvbiIsCiAgICAgICJwYXRoIjogIkM6L1VzZXJzL3RoZXJlL0VN"
        "UjQtdG9vbHMvc2VsZWN0ZWQtY29udGV4dC1idXJlYXUtY2FuZGlkYXRlLXYzL29yY2hlc3RyYXRpb24vY29udGludWl0eS9yZWNl"
        "cHRpb24tb25lLWJ1cmVhdS10eXBlZC1wbGFuLXByb3RvY29sL3BsYW4tcmV2aWV3LnNjaGVtYS5qc29uIiwKICAgICAgImJlZm9y"
        "ZV9zaGEyNTYiOiAiMmM2N2NhODFhNzFmZTgzNDQ2YWZkODI0ZjYwOTZhOGIwMGExMDdlMzkyNmE0MzU1OTRhMzdlNTdlMGFmZWZm"
        "NyIsCiAgICAgICJieXRlcyI6IDQ4MzYsCiAgICAgICJzaGEyNTYiOiAiNDZlMDMzZjFhMDRkNTEwMTg0ZjJiOGU0NjBjNjQxMjc4"
        "ZGM0ZjkzNmUxNjZjZDk5NjJhMWY0OGNmNjJjNWYxNCIKICAgIH0KICBdLAogICJzb3VyY2VfcmV2aWV3X3F1YWxpZmljYXRpb24i"
        "OiAiTmluZS1maWxlIGNvcnJlY3RlZCBzb3VyY2UgcHJlcGFyYXRpb24gYWZ0ZXIgc291cmNlMDEgTk9OUEFTUzsgY2Fub25pY2Fs"
        "IHR3by1jb2RlIHNjaGVtYSBjb21wbGV0aW9uLCBwcmVjaXNlIG9wZXJhdGlvbiByZWplY3Rpb24gcmVhc29uLCBwaHlzaWNhbCBC"
        "b29rZWQgZml4dHVyZS4gUHJpb3Igc291cmNlIGFuZCBmYWlsZWQgZXZpZGVuY2UgcHJlc2VydmVkLiBSZXF1aXJlcyByZW5ld2Vk"
        "IGV4YWN0IGVudHJ5IGJpbmRpbmdzIGJlZm9yZSBwcm9kdWN0IGFwcGxpY2F0aW9uOyBpc29sYXRlZCBzb3VyY2Utb25seSB2ZXJp"
        "ZmljYXRpb24gaXMgc2VwYXJhdGVseSBzY29wZWQuIiwKICAiaW50ZW5kZWRfaW52YXJpYW50IjogIkV4aXN0aW5nIEJ1cmVhdS9j"
        "b250ZXh0L3Byb29mcmVhZGVyIHByZXBhcmVzIHN0YWZmIHNlbGVjdGVkIG1vdmU7IG9yaWdpbmFsIHdvcmRzIHByZXNlcnZlZDsg"
        "Y29uZmxpY3RzIGNsYXJpZnk7IGV4YWN0IGN1cnJlbnQgSUQvdmVyc2lvbiBjaGVja2VkOyBvbmUgY2xlYW4gb3B0aW9uIGVudGVy"
        "cyBleGlzdGluZyBzaWduZWQgcHJvcG9zYWwvaHVtYW4gY29uZmlybS9pZGVtcG90ZW5jeS9yZWFkYmFjayIsCiAgImV4Y2x1ZGVk"
        "X2VmZmVjdHMiOiBbCiAgICAicHJvdmlkZXJzIiwKICAgICJyZWFsIGRhdGEiLAogICAgInB1YmxpYyBsaXN0ZW5lciIsCiAgICAi"
        "cHJvZHVjdCBydW50aW1lIiwKICAgICJwcm90ZWN0ZWQgcmVmIG1vdmVtZW50IiwKICAgICJkZXBsb3ltZW50IiwKICAgICJzcGVu"
        "ZGluZyBleHBhbnNpb24iCiAgXSwKICAibGltaXRhdGlvbnMiOiBbCiAgICAiRGV0ZXJtaW5pc3RpYyBwYXRoLCBub3QgY29udGV4"
        "dHVhbCBMTE0gYWNjZXB0YW5jZSIsCiAgICAiT25seSBvbmUgdW5hbWJpZ3VvdXMgY2xlYW4gY2FuZGlkYXRlOyBtdWx0aXBsZSBv"
        "cHRpb25zIG9yIHVua25vd24gd2FybmluZ3MgY2xhcmlmeSIsCiAgICAiQmFja2VuZCB1bml0IHNvdXJjZSBpbmNsdWRlcyBmYWtl"
        "IHNjb3BlZCBPUk0gcXVlcnkgb2JzZXJ2YXRpb25zLCBub3QgZGF0YWJhc2UgaXNvbGF0aW9uIHByb29mIiwKICAgICJFbnRyeS1l"
        "bmFibGVtZW50LCB0ZXN0IGJpbmRpbmcsIGFwcGxpY2F0aW9uIGFuZCBydW50aW1lIGFjY2VwdGFuY2UgcmVtYWluIHNlcGFyYXRl"
        "IgogIF0sCiAgImNvcnJlY3Rpb25fb2ZfcmV2aWV3X3NoYTI1NiI6ICJiMmM4NmNlN2MxM2ZmZDc2NTBkNGI2MDk0MjdhZWFlNzhh"
        "M2JkMTcxNGFmZmZmZmM4MmYwNWIyZjE3YjYxMjY1IiwKICAiY29ycmVjdGlvbl9vZl9zb3VyY2VfcmVzdWx0X3NoYTI1NiI6ICIy"
        "ZmMzYjI0MWExNzAwMjM4ZjNhZmE4ZmVjYmZiYWM2MTA3ZmE3YmVkYTE5OTc5ZGI0Mzc1NTk0MjFlM2Q2MTQ5Igp9Cg=="
    )
    mapping_raw = base64.b64decode(
        "ewogICJzY2hlbWEiOiAiZW1yNC5zdGFnZTFfc2VsZWN0ZWRfYnVyZWF1X2NvbWJpbmVkX3NvdXJjZV9tYXBwaW5nX3Jldmlldy52"
        "MSIsCiAgInN0YXR1cyI6ICJQQVNTIiwKICAidmVyZGljdCI6ICJQQVNTX0c0X1NUQUdFMV9TRUxFQ1RFRF9CVVJFQVVfRVhBQ1Rf"
        "TUFQUElORyIsCiAgInJldmlld2VyX2FnZW50IjogIi9yb290L2J1cmVhdV9jb3JyZWN0aW9uX3JldmlldyIsCiAgImluZGVwZW5k"
        "ZW50IjogdHJ1ZSwKICAiaW1wbGVtZW50YXRpb25fYXV0aG9yc2hpcCI6IGZhbHNlLAogICJwcm9kdWN0X3ZlY3Rvcl9zaGEyNTYi"
        "OiAiMmE5N2EyNDQxM2RiNTEyYWQ4MzQ1OTEwNjZhZDk2YTYyYTY2NDc1ZDc4ZThjMmMwMjk0MTE1NTM3ZWU2ZDkxNyIsCiAgInBo"
        "eXNpY2FsX3RhcmdldF9yb3dzX2NoZWNrZWQiOiA5LAogICJibG9ja2luZ19maW5kaW5ncyI6IFtdLAogICJuYXJyYXRpdmVfcmV2"
        "aWV3IjogewogICAgInBhdGgiOiAiQzovVXNlcnMvdGhlcmUvRU1SNC10b29scy9zZWxlY3RlZC1jb250ZXh0LWJ1cmVhdS1jYW5k"
        "aWRhdGUtdjMvaW5kZXBlbmRlbnQtY29tYmluZWQtc291cmNlLW1hcHBpbmctcmV2aWV3LXYzLmpzb24iLAogICAgInNoYTI1NiI6"
        "ICJmZDVlNTQzY2JhNDJhNjVjYWFiOTY4YjNmNTY1ZTAwZTk0MmJkOWVhMjkyODVmMWIxZDRlZjc3ZWEzMjczZjc3IgogIH0sCiAg"
        "InF1YWxpZmljYXRpb24iOiAiSW5kZXBlbmRlbnQgZXhhY3QtbmluZS1zb3VyY2UgbWFwcGluZyBqdWRnbWVudCBvbmx5LiBUaGUg"
        "VjggcHJvZHVjdCBlbnRyeSBzY29wZSBzdGlsbCBwaW5zIGVpZ2h0IFYyIGZpbGVzIGFuZCBjYW5ub3QgYWRtaXQgVjMgc2NoZW1h"
        "IGFwcGxpY2F0aW9uOyByZW5ldyBleGFjdCBlbnRyeSBzY29wZSBhbmQgYmluZGluZ3MgZmlyc3QuIFRoZSBjb3JyZWN0ZWQgaXNv"
        "bGF0ZWQgc291cmNlLXRlc3QgY2Fwc3VsZSBtYXkgcmVjZWl2ZSBhIHNlcGFyYXRlbHkgcmV2aWV3ZWQgZmluaXRlIHNvdXJjZS1v"
        "bmx5IGJpbmRpbmcsIGJ1dCBpdHMgY3VycmVudCByZWFkeV9mb3JfZXhlY3V0aW9uPWZhbHNlIHRlbXBsYXRlIGlzIG5vdCBhIGdy"
        "YW50IG9yIHRlc3QgcmVzdWx0LiBObyBwcm9kdWN0IGFwcGxpY2F0aW9uLCBleGVjdXRhYmxlIGFjY2VwdGFuY2UsIGludGVncmF0"
        "ZWQgam91cm5leSBwcm9vZiBvciBjb250ZXh0dWFsIExMTSBhY2NlcHRhbmNlIGZvbGxvd3MuIgp9Cg=="
    )
    assert hashlib.sha256(vector_raw).hexdigest() == bounded_g1b.G4_BUREAU_V9_VECTOR_SHA
    assert hashlib.sha256(mapping_raw).hexdigest() == bounded_g1b.G4_BUREAU_V9_MAPPING_SHA
    predecessor_raw = bounded_g1b._canonical(_bureau_scope()) + b"\n"
    assert hashlib.sha256(predecessor_raw).hexdigest() == (
        "25878fe3ae6e0b159edd73a5a789ba3b8f24074d5f70c49577342c0cea919666")
    scope = _bureau_v9_scope()
    target = Path("C:/synthetic-bureau-target")
    source = Path("C:/synthetic-bureau-source")
    activation_path = (bounded_g1b.G4_BUREAU_V9_ROOT / "entry-admission-v1" /
                       "independent-enable-push-effect-review-v1.json")
    product_inputs = (
        bounded_g1b.CONFIGURATION_PATHS |
        {bounded_g1b.STATE, bounded_g1b.GATES, bounded_g1b.OVERLAY,
         bounded_g1b.AGENTS, bounded_g1b.G4_STAGE1_INTERACTIVE_SCOPE,
         bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE,
         bounded_g1b.G4_STAGE1_SUCCESSOR_TEST, bounded_g1b.G4_CI_WORKFLOW} |
        bounded_g1b.SOURCE_PATHS | bounded_g1b.CONTROLLER_PATHS |
        bounded_g1b.G4_BUREAU_V9_PRODUCT)
    q = {
        "schema_version": bounded_g1b.G4_BUREAU_V9_SCHEMA,
        "operation_id": "selected-bureau-apply-source",
        "operation_kind": "implement_g4_stage1_successor",
        "stage": "apply", "phase": "development",
        "base_commit": "b" * 40, "base_tree": "c" * 40,
        "expected_head": "d" * 40, "expected_index_tree": "e" * 40,
        "candidate_tree": "f" * 40,
        "source_sha256": scope["source_sha256"],
        "payload_sha256": {path: "a" * 64 for path in product_inputs},
        "repair_sha256": {path: {} for path in bounded_g1b.G4_BUREAU_V9_PRODUCT},
        "source_review": {"path": "unused-before-product-inputs", "sha256": "a" * 64},
        "activation_acceptance": {},
        "product_vector": scope["product_vector"],
        "mapping_review": scope["mapping_review"],
    }
    accepted = {
        "status": "PASS",
        "verdict": "PASS_G4_STAGE1_SELECTED_BUREAU_V9_CONTROL_PUBLICATION_EFFECT",
        "reviewer_agent": "/root/selected_bureau_entry_review",
        "independent": True, "implementation_authorship": False,
        "blocking_findings": [], "stage": "enable", "phase": "push",
        "base": bounded_g1b.G4_BUREAU_V9_BASE["commit"],
        "commit": q["base_commit"], "candidate_tree": q["base_tree"],
        "control_activation_accepted": True,
        "same_attempt_remote_readback_verified": True,
        "protected_refs_unchanged": True,
        "whole_inverse_verified_same_attempt": True,
        "published_ref": bounded_g1b.G4_STAGE1_INTERACTIVE_BACKEND_REF,
    }
    def fake_git_bytes(_target, *args):
        assert args == ("cat-file", "blob",
                        bounded_g1b.G4_BUREAU_V9_BASE["commit"] + ":" +
                        bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE)
        return predecessor_raw
    def fake_git(_target, *args):
        if args == ("rev-parse", bounded_g1b.G4_BUREAU_V9_BASE["commit"] + "^{tree}"):
            return bounded_g1b.G4_BUREAU_V9_BASE["tree"]
        assert args == ("cat-file", "commit", q["base_commit"])
        return ("tree " + q["base_tree"] + "\nparent " +
                bounded_g1b.G4_BUREAU_V9_BASE["commit"] + "\n\nsynthetic")
    monkeypatch.setattr(bounded_g1b.trusted_git, "run_git_bytes", fake_git_bytes)
    monkeypatch.setattr(bounded_g1b.trusted_git, "run_git", fake_git)
    reached_product_inputs = []
    class ProductInputReached(Exception):
        pass
    def attempt(receipt, *, row_path=activation_path, row_sha=None):
        reached_product_inputs.clear()
        raw = json.dumps(receipt, sort_keys=True).encode()
        pin = hashlib.sha256(raw).hexdigest() if row_sha is None else row_sha
        selected_q = copy.deepcopy(q)
        selected_q["activation_acceptance"] = {
            "path": row_path.as_posix(), "sha256": pin}
        def read(path, digest):
            if path == bounded_g1b.G4_BUREAU_V9_VECTOR:
                data = vector_raw
            elif path == bounded_g1b.G4_BUREAU_V9_MAPPING:
                data = mapping_raw
            elif path == activation_path:
                data = raw
            elif path.is_relative_to(target):
                reached_product_inputs.append(path)
                raise ProductInputReached()
            else:
                raise AssertionError(f"unexpected synthetic read: {path}")
            if hashlib.sha256(data).hexdigest() != digest:
                raise bounded_g1b.BoundedG1BError(
                    "bounded_g1b_input_digest_changed")
            return data
        return bounded_g1b._load_g4_bureau_v9_inputs(
            None, target, source,
            bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT,
            Path("C:/synthetic-bureau-scratch"), selected_q, read, {})
    with pytest.raises(ProductInputReached):
        attempt(accepted)
    assert reached_product_inputs
    for receipt, row_path, row_sha, reason in (
        (accepted, activation_path.with_name("swapped.json"), None,
         "bounded_g4_bureau_v9_activation_path"),
        (accepted, activation_path, "0" * 64,
         "bounded_g1b_input_digest_changed"),
        *(
            (dict(accepted, **{field: value}), activation_path, None,
             "bounded_g4_bureau_v9_activation_acceptance")
            for field, value in (
                ("base", "0" * 40),
                ("commit", "0" * 40),
                ("candidate_tree", "0" * 40),
                ("same_attempt_remote_readback_verified", False),
                ("protected_refs_unchanged", False),
                ("whole_inverse_verified_same_attempt", False),
            )
        ),
    ):
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            attempt(receipt, row_path=row_path, row_sha=row_sha)
        assert caught.value.reason_code == reason
        assert reached_product_inputs == []




def _status_contract_scope():
    """Frozen accepted V11 scope; active V12 does not rewrite its history."""
    raw = Path("C:/Users/there/EMR4-tools/selected-bureau-correlation-binding-entry-candidate-v1/before/orchestration/programme/g4-stage1-successor-entry-scope.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == "302e4a5ae9df0cee9e783fc19793975bf7e362fa5095b23686b19b92b466e1d5"
    return json.loads(raw)


def test_status_contract_successor_is_two_status_paths_and_requires_acceptance(monkeypatch):
    scope = _status_contract_scope()
    bounded_g1b.validate_g4_status_contract_scope(scope)
    assert scope["allowed_paths"] == sorted(bounded_g1b.G4_STATUS_CONTRACT_PRODUCT)
    assert set(scope["allowed_paths"]) == {
        "stage1_demo_http.py",
        "tests/test_stage1_bureau_projection.py",
    }
    assert scope["selected_base"] == bounded_g1b.G4_STATUS_CONTRACT_BASE
    assert scope["admission_grants_runtime_authority"] is False
    for changed_field, changed_value in (
        ("selected_base", {"commit": "0" * 40, "tree": "0" * 40}),
        ("allowed_paths", scope["allowed_paths"] + ["app/other.py"]),
        ("product_sha256", {**scope["product_sha256"],
                            "stage1_demo_http.py": "0" * 64}),
        ("mapping_review", None),
        ("runtime_binding_required", False),
        ("admission_grants_runtime_authority", True),
        ("voice_activation", True),
        ("allowed_effects", scope["allowed_effects"] + ["provider_invocation"]),
        ("predecessor_scope", {"sha256": "0" * 64}),
    ):
        changed = copy.deepcopy(scope)
        changed[changed_field] = changed_value
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b.validate_g4_status_contract_scope(changed)
        assert caught.value.reason_code == "bounded_g4_status_contract_scope_boundary"

    for stage, kind, paths in (
        ("enable", "enable_g4_stage1_successor", bounded_g1b.G4_STATUS_CONTRACT_CONTROL),
        ("apply", "implement_g4_stage1_successor", bounded_g1b.G4_STATUS_CONTRACT_PRODUCT),
    ):
        q = {"schema_version": bounded_g1b.G4_STATUS_CONTRACT_SCHEMA,
             "operation_kind": kind, "stage": stage,
             "repair_sha256": {p: {} for p in paths}}
        assert bounded_g1b.operation_paths(kind, q) == paths
        for replacement in (set(paths) | {"app/other.py"}, set(paths) - {next(iter(paths))}):
            with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
                bounded_g1b.operation_paths(kind, dict(
                    q, repair_sha256={p: {} for p in replacement}))
            assert caught.value.reason_code == "bounded_g4_status_contract_changed_paths"



def _status_contract_loader_fixture(monkeypatch, stage):
    """Exercise the production loader with pinned ordinary files and literal Git stubs."""
    root = Path("C:/Users/there/EMR4-tools/g4-status-contract-apply01-source")
    scope = json.loads((root / bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE).read_bytes())
    bounded_g1b.validate_g4_status_contract_scope(scope)
    target = Path("C:/synthetic-status-contract-target")
    source = Path("C:/synthetic-status-contract-source")
    product_root = Path("C:/Users/there/EMR4-tools/selected-bureau-status-contract-candidate-v1/after")
    before_files = {
        "stage1_demo_http.py": (
            Path("C:/Users/there/EMR4-tools/selected-bureau-status-contract-candidate-v1/before/stage1_demo_http.py"),
            102649),
        "tests/test_stage1_bureau_projection.py": (
            Path("C:/Users/there/EMR4-tools/selected-bureau-status-contract-candidate-v1/committed-before/tests/test_stage1_bureau_projection.py"),
            6254),
    }
    after_lengths = {"stage1_demo_http.py": 102636,
                     "tests/test_stage1_bureau_projection.py": 6950}
    before_product = {}
    after_product = {}
    for path in sorted(bounded_g1b.G4_STATUS_CONTRACT_PRODUCT):
        before_product[path] = before_files[path][0].read_bytes()
        after_product[path] = (product_root / path).read_bytes()
        assert len(before_product[path]) == before_files[path][1]
        assert len(after_product[path]) == after_lengths[path]
        assert hashlib.sha256(before_product[path]).hexdigest() == bounded_g1b.G4_STATUS_CONTRACT_BEFORE_SHA[path]
        assert hashlib.sha256(after_product[path]).hexdigest() == bounded_g1b.G4_STATUS_CONTRACT_PRODUCT_SHA[path]

    evidence = {}
    for path, digest in (
        (bounded_g1b.G4_STATUS_CONTRACT_VECTOR, bounded_g1b.G4_STATUS_CONTRACT_VECTOR_SHA),
        (bounded_g1b.G4_STATUS_CONTRACT_SOURCE_REVIEW, bounded_g1b.G4_STATUS_CONTRACT_SOURCE_REVIEW_SHA),
    ):
        raw = path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == digest
        evidence[path] = raw
    vector = json.loads(evidence[bounded_g1b.G4_STATUS_CONTRACT_VECTOR])
    selected = (bounded_g1b.G4_STATUS_CONTRACT_CONTROL if stage == "enable"
                else bounded_g1b.G4_STATUS_CONTRACT_PRODUCT)
    inputs = (bounded_g1b.CONFIGURATION_PATHS |
              {bounded_g1b.STATE, bounded_g1b.GATES, bounded_g1b.OVERLAY,
               bounded_g1b.AGENTS, bounded_g1b.G4_STAGE1_INTERACTIVE_SCOPE,
               bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE,
               bounded_g1b.G4_STAGE1_SUCCESSOR_TEST, bounded_g1b.G4_CI_WORKFLOW} |
              bounded_g1b.SOURCE_PATHS | bounded_g1b.CONTROLLER_PATHS |
              (bounded_g1b.G4_STATUS_CONTRACT_PRODUCT if stage == "apply" else set()))
    payload = {path: b"synthetic-v11-payload:" + path.encode("utf-8") for path in inputs}
    for path in sorted(bounded_g1b.SOURCE_PATHS | bounded_g1b.CONTROLLER_PATHS):
        payload[path] = (root / path).read_bytes()
        assert hashlib.sha256(payload[path]).hexdigest() == scope["source_sha256"][path]
    payload[bounded_g1b.OVERLAY] = (root / bounded_g1b.OVERLAY).read_bytes()
    payload[bounded_g1b.G4_STAGE1_SUCCESSOR_TEST] = (root / bounded_g1b.G4_STAGE1_SUCCESSOR_TEST).read_bytes()
    assert hashlib.sha256(payload[bounded_g1b.G4_STAGE1_SUCCESSOR_TEST]).hexdigest() == scope["control_sha256"][bounded_g1b.G4_STAGE1_SUCCESSOR_TEST]
    payload[bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE] = bounded_g1b._canonical(scope) + b"\n"
    if stage == "apply":
        payload.update(after_product)
    predecessor = bounded_g1b._canonical(_exact_time_scope()) + b"\n"
    assert hashlib.sha256(predecessor).hexdigest() == scope["predecessor_scope"]["sha256"]
    base_commit = (bounded_g1b.G4_STATUS_CONTRACT_BASE["commit"] if stage == "enable"
                   else "b" * 40)
    base_tree = (bounded_g1b.G4_STATUS_CONTRACT_BASE["tree"] if stage == "enable"
                 else "c" * 40)
    committed = dict(payload)
    if stage == "enable":
        for path in selected:
            committed[path] = (predecessor if path == bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE
                               else b"synthetic-v11-before:" + path.encode("utf-8"))
    else:
        committed.update(before_product)
    q = {
        "schema_version": bounded_g1b.G4_STATUS_CONTRACT_SCHEMA,
        "operation_id": "status-contract-synthetic-" + stage,
        "operation_kind": ("enable_g4_stage1_successor" if stage == "enable"
                           else "implement_g4_stage1_successor"),
        "stage": stage, "phase": "development",
        "base_commit": base_commit, "base_tree": base_tree,
        "expected_head": base_commit, "expected_index_tree": base_tree,
        "candidate_tree": "d" * 40,
        "source_sha256": copy.deepcopy(scope["source_sha256"]),
        "payload_sha256": {path: hashlib.sha256(raw).hexdigest()
                           for path, raw in payload.items()},
        "repair_sha256": {
            path: {"before_sha256": hashlib.sha256(committed[path]).hexdigest(),
                   "after_sha256": hashlib.sha256(payload[path]).hexdigest()}
            for path in selected},
        "source_review": {}, "activation_acceptance": None,
        "product_vector": scope["product_vector"],
        "mapping_review": scope["mapping_review"],
    }
    activation_path = (bounded_g1b.G4_STATUS_CONTRACT_ROOT / "entry-admission-v1" /
                       "independent-enable-push-effect-review-v1.json")
    activation = None
    if stage == "apply":
        activation = {
            "status": "PASS", "verdict": "PASS_G4_STAGE1_STATUS_CONTRACT_CONTROL_PUBLICATION_EFFECT",
            "reviewer_agent": "/root/independent-enable-reviewer",
            "independent": True, "implementation_authorship": False,
            "blocking_findings": [], "stage": "enable", "phase": "push",
            "base": bounded_g1b.G4_STATUS_CONTRACT_BASE["commit"],
            "commit": base_commit, "candidate_tree": base_tree,
            "control_activation_accepted": True,
            "same_attempt_remote_readback_verified": True,
            "protected_refs_unchanged": True,
            "whole_inverse_verified_same_attempt": True,
            "published_ref": bounded_g1b.G4_STAGE1_INTERACTIVE_BACKEND_REF,
        }
        raw = json.dumps(activation, sort_keys=True).encode("utf-8")
        q["activation_acceptance"] = {
            "path": activation_path.as_posix(),
            "sha256": hashlib.sha256(raw).hexdigest()}
        evidence[activation_path] = raw
    subject_path = (bounded_g1b.G4_STATUS_CONTRACT_ROOT / "entry-admission-v1" /
                    ("independent-" + stage + "-development-subject-review-v1.json"))
    review = {
        "schema": "emr4.g4_operation_review.v1", "status": "PASS",
        "verdict": "PASS_G4_STAGE1_STATUS_CONTRACT_EXACT_ADMISSION_SUBJECT",
        "subject_sha256": bounded_g1b.g4_status_contract_review_subject(q),
        "stage": stage, "phase": "development",
        "independent": True, "implementation_authorship": False,
        "blocking_findings": [], "reviewer_agent": "/root/independent-subject-reviewer",
    }
    raw = json.dumps(review, sort_keys=True).encode("utf-8")
    q["source_review"] = {"path": subject_path.as_posix(),
                          "sha256": hashlib.sha256(raw).hexdigest()}
    evidence[subject_path] = raw

    def read(path, digest):
        if path in evidence:
            raw = evidence[path]
            assert hashlib.sha256(raw).hexdigest() == digest
            return raw
        for root_path in (target, source, Path(vector["owned_candidate_root"])):
            if path.is_relative_to(root_path):
                relative = path.relative_to(root_path).as_posix()
                if root_path == source and relative in bounded_g1b.SOURCE_PATHS | bounded_g1b.CONTROLLER_PATHS:
                    assert digest == q["source_sha256"][relative]
                    raw = (payload[relative] if stage == "enable" and relative in selected
                           else committed[relative])
                    assert hashlib.sha256(raw).hexdigest() == digest
                    return raw
                if root_path == target:
                    assert digest == q["payload_sha256"][relative]
                    assert hashlib.sha256(payload[relative]).hexdigest() == digest
                    return payload[relative]
                assert relative in after_product
                assert digest == bounded_g1b.G4_STATUS_CONTRACT_PRODUCT_SHA[relative]
                return after_product[relative]
        raise AssertionError("unexpected synthetic read")

    def fake_git_bytes(_target, *args):
        if args == ("cat-file", "blob", bounded_g1b.G4_STATUS_CONTRACT_BASE["commit"] +
                    ":" + bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE):
            return predecessor
        if args[:3] == ("ls-tree", "-z", base_commit):
            assert args[3] == "--" and args[4] in selected
            return b"100644 blob present\x00"
        assert args[:2] == ("cat-file", "blob")
        commit, relative = args[2].split(":", 1)
        if commit == bounded_g1b.G4_STATUS_CONTRACT_BASE["commit"] and relative in (
                bounded_g1b.STATE, bounded_g1b.GATES, bounded_g1b.OVERLAY,
                bounded_g1b.AGENTS):
            return committed[relative]
        assert commit == base_commit and relative in committed
        return committed[relative]

    def fake_git(_target, *args):
        if args == ("rev-parse", bounded_g1b.G4_STATUS_CONTRACT_BASE["commit"] + "^{tree}"):
            return bounded_g1b.G4_STATUS_CONTRACT_BASE["tree"]
        assert args == ("cat-file", "commit", base_commit)
        return ("tree " + base_tree + "\nparent " +
                bounded_g1b.G4_STATUS_CONTRACT_BASE["commit"] + "\n\nsynthetic")

    monkeypatch.setattr(bounded_g1b.trusted_git, "run_git_bytes", fake_git_bytes)
    monkeypatch.setattr(bounded_g1b.trusted_git, "run_git", fake_git)
    monkeypatch.setattr(bounded_g1b.trusted_git, "attest_target_index",
                        lambda *_args, **_kwargs: {"synthetic": True})

    def load(selected_q):
        return bounded_g1b._load_g4_status_contract_inputs(
            None, target, source, bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT,
            Path("C:/synthetic-status-contract-scratch"), selected_q, read, {})
    return q, load, evidence, subject_path, activation_path


@pytest.mark.parametrize("stage", ["enable", "apply"])
def test_status_contract_loader_valid_baseline_and_targeted_rejections(monkeypatch, stage):
    q, load, evidence, subject_path, activation_path = _status_contract_loader_fixture(
        monkeypatch, stage)
    loaded = load(q)
    assert loaded.binding == q
    assert loaded.evidence["scope"]["schema_version"] == bounded_g1b.G4_STATUS_CONTRACT_SCOPE_SCHEMA
    assert loaded.evidence["review"]["subject_sha256"] == bounded_g1b.g4_status_contract_review_subject(q)

    def rejected(changed, reason):
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            load(changed)
        assert caught.value.reason_code == reason

    changed = copy.deepcopy(q)
    changed["phase"] = "runtime"
    rejected(changed, "bounded_g4_status_contract_binding_version")
    changed = copy.deepcopy(q)
    changed["repair_sha256"]["app/other.py"] = {"before_sha256": "0" * 64,
                                                     "after_sha256": "1" * 64}
    rejected(changed, "bounded_g4_status_contract_changed_paths")
    changed = copy.deepcopy(q)
    changed["source_sha256"]["app/other.py"] = "0" * 64
    rejected(changed, "bounded_g4_status_contract_sources")
    changed = copy.deepcopy(q)
    changed["source_sha256"]["orchestration_harness/bounded_g1b.py"] = "0" * 64
    rejected(changed, "bounded_g4_status_contract_scope_sources")
    changed = copy.deepcopy(q)
    del changed["payload_sha256"][bounded_g1b.STATE]
    rejected(changed, "bounded_g4_status_contract_payload_paths")
    changed = copy.deepcopy(q)
    changed["payload_sha256"]["app/other.py"] = "0" * 64
    rejected(changed, "bounded_g4_status_contract_payload_paths")
    changed = copy.deepcopy(q)
    first_repair = sorted(changed["repair_sha256"])[0]
    changed["repair_sha256"][first_repair] = {}
    rejected(changed, "bounded_g4_status_contract_change_pair")
    changed = copy.deepcopy(q)
    changed["repair_sha256"][first_repair]["after_sha256"] = "0" * 64
    rejected(changed, "bounded_g4_status_contract_change_preimage")
    changed = copy.deepcopy(q)
    changed["candidate_tree"] = "e" * 40
    rejected(changed, "bounded_g4_status_contract_independent_subject")
    review = json.loads(evidence[subject_path])
    review["phase"] = "pre-push"
    evidence[subject_path] = json.dumps(review, sort_keys=True).encode("utf-8")
    changed = copy.deepcopy(q)
    changed["source_review"]["sha256"] = hashlib.sha256(evidence[subject_path]).hexdigest()
    rejected(changed, "bounded_g4_status_contract_independent_subject")
    review["phase"] = "development"
    review["independent"] = False
    evidence[subject_path] = json.dumps(review, sort_keys=True).encode("utf-8")
    changed = copy.deepcopy(q)
    changed["source_review"]["sha256"] = hashlib.sha256(evidence[subject_path]).hexdigest()
    rejected(changed, "bounded_g4_status_contract_independent_subject")
    if stage == "enable":
        changed = copy.deepcopy(q)
        changed["base_commit"] = "0" * 40
        rejected(changed, "bounded_g4_status_contract_enable_base")
    else:
        changed = copy.deepcopy(q)
        changed["activation_acceptance"] = None
        rejected(changed, "bounded_g4_status_contract_activation_row")
        activation = json.loads(evidence[activation_path])
        activation["same_attempt_remote_readback_verified"] = False
        evidence[activation_path] = json.dumps(activation, sort_keys=True).encode("utf-8")
        changed = copy.deepcopy(q)
        changed["activation_acceptance"]["sha256"] = hashlib.sha256(
            evidence[activation_path]).hexdigest()
        rejected(changed, "bounded_g4_status_contract_activation_acceptance")



@pytest.mark.parametrize("stage", ["enable", "apply"])
def test_status_contract_subject_reviews_bind_each_phase_and_independence(monkeypatch, stage):
    q, _load, _evidence, _subject, _activation = _status_contract_loader_fixture(monkeypatch, stage)
    for phase in ("development", "pre-push", "post-push"):
        subject_q = copy.deepcopy(q)
        subject_q["phase"] = phase
        subject = bounded_g1b.g4_status_contract_review_subject(subject_q)
        path = (bounded_g1b.G4_STATUS_CONTRACT_ROOT / "entry-admission-v1" /
                ("independent-" + stage + "-" + phase + "-subject-review-v1.json"))
        review = {
            "schema": "emr4.g4_operation_review.v1", "status": "PASS",
            "verdict": "PASS_G4_STAGE1_STATUS_CONTRACT_EXACT_ADMISSION_SUBJECT",
            "subject_sha256": subject, "stage": stage, "phase": phase,
            "independent": True, "implementation_authorship": False,
            "blocking_findings": [], "reviewer_agent": "/root/independent-subject-reviewer",
        }

        def check(document):
            raw = bounded_g1b._canonical(document)
            row = {"path": path.as_posix(), "sha256": hashlib.sha256(raw).hexdigest()}

            def read(expected_path, digest):
                assert expected_path == path
                assert hashlib.sha256(raw).hexdigest() == digest
                return raw

            return bounded_g1b._g4_status_contract_review(
                read, row, bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT,
                subject, stage, phase)

        assert check(review) == review
        for key, value in (
            ("phase", "runtime"), ("subject_sha256", "0" * 64),
            ("independent", False), ("implementation_authorship", True),
            ("reviewer_agent", "/root"),
            ("reviewer_agent", "/root/status_contract_entry_author"),
            ("blocking_findings", ["unresolved"]),
        ):
            with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
                check(dict(review, **{key: value}))
            assert caught.value.reason_code == "bounded_g4_status_contract_independent_subject"


def _receipt_predecessor_v12_scope():
    # Accepted V12 fixture stays literal when current scope advances to V13.
    return json.loads('{"active_profile":"G4_STAGE1_LOCAL_SUCCESSOR","admission_grants_runtime_authority":false,"allowed_effects":["control_plane_edit","product_behavior_change","repository_read","task_branch_commit","task_branch_push"],"allowed_paths":["app/routers/appointments.py","app/schemas/appointments.py","stage1_demo_http.py","tests/test_stage1_bureau_projection.py"],"allowed_task_kind":"g4_stage1_local_successor","control_sha256":{"orchestration_harness/bounded_g1b.py":"c7d30a2cdb352b2065d014770d93e2e6538e470dada20567411ce62f267a733f","tests/test_g4_stage1_successor_entry.py":"1da7077984f0e7581f8485d87a45c8781443f88f4ad5e3ca458d49aa113e1484"},"excluded_effects":["unreviewed_application_or_database_runtime","unreviewed_browser_or_microphone_runtime","unreviewed_voice_child_or_network_egress","provider_invocation","real_data_access","protected_ref_movement","deployment","public_listener"],"mapping_review":{"path":"C:/Users/there/EMR4-tools/selected-bureau-correlation-binding-product-candidate-v2/independent-source-review-v2.json","sha256":"cbd927ee21017892926b16fce6029004a0e0f68fda80d5e8559904217407a3fb"},"predecessor_scope":{"sha256":"302e4a5ae9df0cee9e783fc19793975bf7e362fa5095b23686b19b92b466e1d5"},"product_sha256":{"app/routers/appointments.py":"09f919ce3ece03970de6e4ce6a555a0cff4271dca5c52c9834ed7f040d26fdcc","app/schemas/appointments.py":"05f324de7c7c01254e666c754b44631652e794ff9a3a45c87d5106478725d5a0","stage1_demo_http.py":"bc621dc44fc341e9e8ab26c6c705013f9874695d8cd407dc09f79f58250644c6","tests/test_stage1_bureau_projection.py":"0e4962a55fc807a509eeaae344776ad7876f55a44090ee557ad790a0a2e76190"},"product_vector":{"path":"C:/Users/there/EMR4-tools/selected-bureau-correlation-binding-product-candidate-v2/source-vector-v2.json","sha256":"d642264e4601a3af9d50f0131731f764d112b473b82ac74f9c535e1f6c2fc9df"},"recorded_at":"2026-10-27T00:00:00+00:00","runtime_binding_required":true,"schema_version":"ariadne.g4_stage1_successor_entry_scope.v12","selected_base":{"commit":"ee33ed7fe61b702acc013b89b03dc2dc1aa11dd9","tree":"39663edc3b87aee5980e4b0212446e365aa183ae"},"source_sha256":{"orchestration_harness/bounded_g1b.py":"c7d30a2cdb352b2065d014770d93e2e6538e470dada20567411ce62f267a733f","orchestration_harness/configuration_core.py":"f7ba7a80eb0a590f9fb71b864e6c1f9f43241d9f7d70a38da67a9243fea208e5","orchestration_harness/pinned_programme_gatekeeper.py":"c1fea9a2849068ed8e87dbe1e7cec1cc7e762fa2bc8876fc32bbda80d226cf39","orchestration_harness/programme_admission.py":"ac816a8a79b2d8222fa357777c075950927e86cf30c8a5b25ffd08a474052181","orchestration_harness/raisa_policy.py":"2dabec173bf7e39629e7036cac2d13c777e52649cea744a1fec778b5e9b9332e","orchestration_harness/trusted_git.py":"4a856bffe2b68d7c7e1875152629c9024a32679b59d9b1ed8301c368d41ff527","scripts/raisa_ariadne_recovery_preflight.py":"edfd37b30673b8544d309b532c95b3fd7c20ff592880a8a0235dfde6cfc8e7e4","tests/test_bounded_g1b.py":"bb1be86ca39232fea30c1ea84cdfb114428d57be0f8f67bf7e86daab0ba73bc5"},"voice_activation":false}\n')


def test_correlation_binding_successor_is_four_binding_paths_and_requires_acceptance(monkeypatch):
    scope = _receipt_predecessor_v12_scope()
    bounded_g1b.validate_g4_correlation_binding_scope(scope)
    assert scope["allowed_paths"] == sorted(bounded_g1b.G4_CORRELATION_BINDING_PRODUCT)
    assert set(scope["allowed_paths"]) == {
        "stage1_demo_http.py", "tests/test_stage1_bureau_projection.py",
        "app/routers/appointments.py", "app/schemas/appointments.py",
    }
    assert scope["selected_base"] == bounded_g1b.G4_CORRELATION_BINDING_BASE
    assert scope["admission_grants_runtime_authority"] is False
    for changed_field, changed_value in (
        ("selected_base", {"commit": "0" * 40, "tree": "0" * 40}),
        ("allowed_paths", scope["allowed_paths"] + ["app/other.py"]),
        ("product_sha256", {**scope["product_sha256"],
                            "stage1_demo_http.py": "0" * 64}),
        ("mapping_review", None),
        ("runtime_binding_required", False),
        ("admission_grants_runtime_authority", True),
        ("voice_activation", True),
        ("allowed_effects", scope["allowed_effects"] + ["provider_invocation"]),
        ("predecessor_scope", {"sha256": "0" * 64}),
    ):
        changed = copy.deepcopy(scope)
        changed[changed_field] = changed_value
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b.validate_g4_correlation_binding_scope(changed)
        assert caught.value.reason_code == "bounded_g4_correlation_binding_scope_boundary"

    for stage, kind, paths in (
        ("enable", "enable_g4_stage1_successor", bounded_g1b.G4_CORRELATION_BINDING_CONTROL),
        ("apply", "implement_g4_stage1_successor", bounded_g1b.G4_CORRELATION_BINDING_PRODUCT),
    ):
        q = {"schema_version": bounded_g1b.G4_CORRELATION_BINDING_SCHEMA,
             "operation_kind": kind, "stage": stage,
             "repair_sha256": {p: {} for p in paths}}
        assert bounded_g1b.operation_paths(kind, q) == paths
        operation = bounded_g1b._operation(kind, q)
        assert operation["g4_correlation_binding_source"] is True
        assert operation["paths"] == paths
        assert operation["profile"] == bounded_g1b.raisa_policy.G4_STAGE1_SUCCESSOR_PROFILE
        for replacement in (set(paths) | {"app/other.py"}, set(paths) - {next(iter(paths))}):
            with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
                bounded_g1b.operation_paths(kind, dict(
                    q, repair_sha256={p: {} for p in replacement}))
            assert caught.value.reason_code == "bounded_g4_correlation_binding_changed_paths"



def _correlation_binding_loader_fixture(monkeypatch, stage):
    """Exercise the production loader with pinned ordinary files and literal Git stubs."""
    root = Path(__file__).resolve().parents[1]
    scope = _receipt_predecessor_v12_scope()
    bounded_g1b.validate_g4_correlation_binding_scope(scope)
    target = Path("C:/synthetic-correlation-binding-target")
    source = Path("C:/synthetic-correlation-binding-source")
    product_root = Path("C:/Users/there/EMR4-tools/selected-bureau-correlation-binding-product-candidate-v2/after")
    before_files = {
        "stage1_demo_http.py": (Path("C:/Users/there/EMR4-tools/selected-bureau-correlation-binding-product-candidate-v2/before/stage1_demo_http.py"), 102636),
        "tests/test_stage1_bureau_projection.py": (Path("C:/Users/there/EMR4-tools/selected-bureau-correlation-binding-product-candidate-v2/before/tests/test_stage1_bureau_projection.py"), 6950),
        "app/routers/appointments.py": (Path("C:/Users/there/EMR4-tools/selected-bureau-correlation-binding-product-candidate-v2/before/app/routers/appointments.py"), 381168),
        "app/schemas/appointments.py": (Path("C:/Users/there/EMR4-tools/selected-bureau-correlation-binding-product-candidate-v2/before/app/schemas/appointments.py"), 67758),
    }
    after_lengths = {
        "stage1_demo_http.py": 103141,
        "tests/test_stage1_bureau_projection.py": 15590,
        "app/routers/appointments.py": 381555,
        "app/schemas/appointments.py": 67919,
    }
    before_product = {}
    after_product = {}
    for path in sorted(bounded_g1b.G4_CORRELATION_BINDING_PRODUCT):
        before_product[path] = before_files[path][0].read_bytes()
        after_product[path] = (product_root / path).read_bytes()
        assert len(before_product[path]) == before_files[path][1]
        assert len(after_product[path]) == after_lengths[path]
        assert hashlib.sha256(before_product[path]).hexdigest() == bounded_g1b.G4_CORRELATION_BINDING_BEFORE_SHA[path]
        assert hashlib.sha256(after_product[path]).hexdigest() == bounded_g1b.G4_CORRELATION_BINDING_PRODUCT_SHA[path]

    evidence = {}
    for path, digest in (
        (bounded_g1b.G4_CORRELATION_BINDING_VECTOR, bounded_g1b.G4_CORRELATION_BINDING_VECTOR_SHA),
        (bounded_g1b.G4_CORRELATION_BINDING_SOURCE_REVIEW, bounded_g1b.G4_CORRELATION_BINDING_SOURCE_REVIEW_SHA),
    ):
        raw = path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == digest
        evidence[path] = raw
    vector = json.loads(evidence[bounded_g1b.G4_CORRELATION_BINDING_VECTOR])
    selected = (bounded_g1b.G4_CORRELATION_BINDING_CONTROL if stage == "enable"
                else bounded_g1b.G4_CORRELATION_BINDING_PRODUCT)
    inputs = (bounded_g1b.CONFIGURATION_PATHS |
              {bounded_g1b.STATE, bounded_g1b.GATES, bounded_g1b.OVERLAY,
               bounded_g1b.AGENTS, bounded_g1b.G4_STAGE1_INTERACTIVE_SCOPE,
               bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE,
               bounded_g1b.G4_STAGE1_SUCCESSOR_TEST, bounded_g1b.G4_CI_WORKFLOW} |
              bounded_g1b.SOURCE_PATHS | bounded_g1b.CONTROLLER_PATHS |
              (bounded_g1b.G4_CORRELATION_BINDING_PRODUCT if stage == "apply" else set()))
    payload = {path: b"synthetic-v12-payload:" + path.encode("utf-8") for path in inputs}
    for path in sorted(bounded_g1b.SOURCE_PATHS | bounded_g1b.CONTROLLER_PATHS):
        historical_root = Path('C:/Users/there/EMR4-tools/selected-patient-request-receipt-correction-v1/entry-control-preparation-v1/before') if path == bounded_g1b.G4_AUDIT_CODE else root
        payload[path] = (historical_root / path).read_bytes()
        assert hashlib.sha256(payload[path]).hexdigest() == scope["source_sha256"][path]
    payload[bounded_g1b.OVERLAY] = (root / bounded_g1b.OVERLAY).read_bytes()
    payload[bounded_g1b.G4_STAGE1_SUCCESSOR_TEST] = (Path('C:/Users/there/EMR4-tools/selected-patient-request-receipt-correction-v1/entry-control-preparation-v1/before') / bounded_g1b.G4_STAGE1_SUCCESSOR_TEST).read_bytes()
    assert hashlib.sha256(payload[bounded_g1b.G4_STAGE1_SUCCESSOR_TEST]).hexdigest() == scope["control_sha256"][bounded_g1b.G4_STAGE1_SUCCESSOR_TEST]
    payload[bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE] = bounded_g1b._canonical(scope) + b"\n"
    if stage == "apply":
        payload.update(after_product)
    predecessor = bounded_g1b._canonical(_status_contract_scope()) + b"\n"
    assert hashlib.sha256(predecessor).hexdigest() == scope["predecessor_scope"]["sha256"]
    base_commit = (bounded_g1b.G4_CORRELATION_BINDING_BASE["commit"] if stage == "enable"
                   else "b" * 40)
    base_tree = (bounded_g1b.G4_CORRELATION_BINDING_BASE["tree"] if stage == "enable"
                 else "c" * 40)
    committed = dict(payload)
    if stage == "enable":
        for path in selected:
            committed[path] = (predecessor if path == bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE
                               else b"synthetic-v12-before:" + path.encode("utf-8"))
    else:
        committed.update(before_product)
    q = {
        "schema_version": bounded_g1b.G4_CORRELATION_BINDING_SCHEMA,
        "operation_id": "correlation-binding-synthetic-" + stage,
        "operation_kind": ("enable_g4_stage1_successor" if stage == "enable"
                           else "implement_g4_stage1_successor"),
        "stage": stage, "phase": "development",
        "base_commit": base_commit, "base_tree": base_tree,
        "expected_head": base_commit, "expected_index_tree": base_tree,
        "candidate_tree": "d" * 40,
        "source_sha256": copy.deepcopy(scope["source_sha256"]),
        "payload_sha256": {path: hashlib.sha256(raw).hexdigest()
                           for path, raw in payload.items()},
        "repair_sha256": {
            path: {"before_sha256": hashlib.sha256(committed[path]).hexdigest(),
                   "after_sha256": hashlib.sha256(payload[path]).hexdigest()}
            for path in selected},
        "source_review": {}, "activation_acceptance": None,
        "product_vector": scope["product_vector"],
        "mapping_review": scope["mapping_review"],
    }
    activation_path = (bounded_g1b.G4_CORRELATION_BINDING_ROOT / "entry-admission-v1" /
                       "independent-enable-push-effect-review-v1.json")
    activation = None
    if stage == "apply":
        activation = {
            "status": "PASS", "verdict": "PASS_G4_STAGE1_CORRELATION_BINDING_CONTROL_PUBLICATION_EFFECT",
            "reviewer_agent": "/root/independent-enable-reviewer",
            "independent": True, "implementation_authorship": False,
            "blocking_findings": [], "stage": "enable", "phase": "push",
            "base": bounded_g1b.G4_CORRELATION_BINDING_BASE["commit"],
            "commit": base_commit, "candidate_tree": base_tree,
            "control_activation_accepted": True,
            "same_attempt_remote_readback_verified": True,
            "protected_refs_unchanged": True,
            "whole_inverse_verified_same_attempt": True,
            "published_ref": bounded_g1b.G4_STAGE1_INTERACTIVE_BACKEND_REF,
        }
        raw = json.dumps(activation, sort_keys=True).encode("utf-8")
        q["activation_acceptance"] = {
            "path": activation_path.as_posix(),
            "sha256": hashlib.sha256(raw).hexdigest()}
        evidence[activation_path] = raw
    subject_path = (bounded_g1b.G4_CORRELATION_BINDING_ROOT / "entry-admission-v1" /
                    ("independent-" + stage + "-development-subject-review-v1.json"))
    review = {
        "schema": "emr4.g4_operation_review.v1", "status": "PASS",
        "verdict": "PASS_G4_STAGE1_CORRELATION_BINDING_EXACT_ADMISSION_SUBJECT",
        "subject_sha256": bounded_g1b.g4_correlation_binding_review_subject(q),
        "stage": stage, "phase": "development",
        "independent": True, "implementation_authorship": False,
        "blocking_findings": [], "reviewer_agent": "/root/independent-subject-reviewer",
    }
    raw = json.dumps(review, sort_keys=True).encode("utf-8")
    q["source_review"] = {"path": subject_path.as_posix(),
                          "sha256": hashlib.sha256(raw).hexdigest()}
    evidence[subject_path] = raw

    def read(path, digest):
        if path in evidence:
            raw = evidence[path]
            assert hashlib.sha256(raw).hexdigest() == digest
            return raw
        for root_path in (target, source, product_root):
            if path.is_relative_to(root_path):
                relative = path.relative_to(root_path).as_posix()
                if root_path == source and relative in bounded_g1b.SOURCE_PATHS | bounded_g1b.CONTROLLER_PATHS:
                    assert digest == q["source_sha256"][relative]
                    raw = (payload[relative] if stage == "enable" and relative in selected
                           else committed[relative])
                    assert hashlib.sha256(raw).hexdigest() == digest
                    return raw
                if root_path == target:
                    assert digest == q["payload_sha256"][relative]
                    assert hashlib.sha256(payload[relative]).hexdigest() == digest
                    return payload[relative]
                assert relative in after_product
                assert digest == bounded_g1b.G4_CORRELATION_BINDING_PRODUCT_SHA[relative]
                return after_product[relative]
        raise AssertionError("unexpected synthetic read")

    def fake_git_bytes(_target, *args):
        if args == ("cat-file", "blob", bounded_g1b.G4_CORRELATION_BINDING_BASE["commit"] +
                    ":" + bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE):
            return predecessor
        if args[:3] == ("ls-tree", "-z", base_commit):
            assert args[3] == "--" and args[4] in selected
            return b"100644 blob present\x00"
        assert args[:2] == ("cat-file", "blob")
        commit, relative = args[2].split(":", 1)
        if commit == bounded_g1b.G4_CORRELATION_BINDING_BASE["commit"] and relative in (
                bounded_g1b.STATE, bounded_g1b.GATES, bounded_g1b.OVERLAY,
                bounded_g1b.AGENTS):
            return committed[relative]
        assert commit == base_commit and relative in committed
        return committed[relative]

    def fake_git(_target, *args):
        if args == ("rev-parse", bounded_g1b.G4_CORRELATION_BINDING_BASE["commit"] + "^{tree}"):
            return bounded_g1b.G4_CORRELATION_BINDING_BASE["tree"]
        assert args == ("cat-file", "commit", base_commit)
        return ("tree " + base_tree + "\nparent " +
                bounded_g1b.G4_CORRELATION_BINDING_BASE["commit"] + "\n\nsynthetic")

    monkeypatch.setattr(bounded_g1b.trusted_git, "run_git_bytes", fake_git_bytes)
    monkeypatch.setattr(bounded_g1b.trusted_git, "run_git", fake_git)
    monkeypatch.setattr(bounded_g1b.trusted_git, "attest_target_index",
                        lambda *_args, **_kwargs: {"synthetic": True})

    def load(selected_q):
        return bounded_g1b._load_g4_correlation_binding_inputs(
            None, target, source, bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT,
            Path("C:/synthetic-correlation-binding-scratch"), selected_q, read, {})
    return q, load, evidence, subject_path, activation_path


@pytest.mark.parametrize("stage", ["enable", "apply"])
def test_correlation_binding_loader_valid_baseline_and_targeted_rejections(monkeypatch, stage):
    q, load, evidence, subject_path, activation_path = _correlation_binding_loader_fixture(
        monkeypatch, stage)
    loaded = load(q)
    assert loaded.binding == q
    assert loaded.evidence["scope"]["schema_version"] == bounded_g1b.G4_CORRELATION_BINDING_SCOPE_SCHEMA
    assert loaded.evidence["review"]["subject_sha256"] == bounded_g1b.g4_correlation_binding_review_subject(q)
    policy_calls = []
    sentinel = ({"exact-correlation-branch": b"source-only"}, None)

    def selected_policy(inputs):
        policy_calls.append(inputs)
        return sentinel

    monkeypatch.setattr(bounded_g1b, "_validate_g4_correlation_binding_loaded_policy", selected_policy)
    assert bounded_g1b._validate_loaded_policy(loaded) == sentinel
    assert policy_calls == [loaded]

    def rejected(changed, reason):
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            load(changed)
        assert caught.value.reason_code == reason

    changed = copy.deepcopy(q)
    changed["phase"] = "runtime"
    rejected(changed, "bounded_g4_correlation_binding_binding_version")
    changed = copy.deepcopy(q)
    changed["product_vector"]["sha256"] = "0" * 64
    rejected(changed, "bounded_g4_correlation_binding_product_pins")
    changed = copy.deepcopy(q)
    changed["mapping_review"]["sha256"] = "0" * 64
    rejected(changed, "bounded_g4_correlation_binding_product_pins")
    changed = copy.deepcopy(q)
    changed["repair_sha256"]["app/other.py"] = {"before_sha256": "0" * 64,
                                                     "after_sha256": "1" * 64}
    rejected(changed, "bounded_g4_correlation_binding_changed_paths")
    changed = copy.deepcopy(q)
    changed["source_sha256"]["app/other.py"] = "0" * 64
    rejected(changed, "bounded_g4_correlation_binding_sources")
    changed = copy.deepcopy(q)
    changed["source_sha256"]["orchestration_harness/bounded_g1b.py"] = "0" * 64
    rejected(changed, "bounded_g4_correlation_binding_scope_sources")
    changed = copy.deepcopy(q)
    del changed["payload_sha256"][bounded_g1b.STATE]
    rejected(changed, "bounded_g4_correlation_binding_payload_paths")
    changed = copy.deepcopy(q)
    changed["payload_sha256"]["app/other.py"] = "0" * 64
    rejected(changed, "bounded_g4_correlation_binding_payload_paths")
    changed = copy.deepcopy(q)
    first_repair = sorted(changed["repair_sha256"])[0]
    changed["repair_sha256"][first_repair] = {}
    rejected(changed, "bounded_g4_correlation_binding_change_pair")
    changed = copy.deepcopy(q)
    changed["repair_sha256"][first_repair]["after_sha256"] = "0" * 64
    rejected(changed, "bounded_g4_correlation_binding_change_preimage")
    changed = copy.deepcopy(q)
    changed["candidate_tree"] = "e" * 40
    rejected(changed, "bounded_g4_correlation_binding_independent_subject")
    review = json.loads(evidence[subject_path])
    review["phase"] = "pre-push"
    evidence[subject_path] = json.dumps(review, sort_keys=True).encode("utf-8")
    changed = copy.deepcopy(q)
    changed["source_review"]["sha256"] = hashlib.sha256(evidence[subject_path]).hexdigest()
    rejected(changed, "bounded_g4_correlation_binding_independent_subject")
    review["phase"] = "development"
    review["independent"] = False
    evidence[subject_path] = json.dumps(review, sort_keys=True).encode("utf-8")
    changed = copy.deepcopy(q)
    changed["source_review"]["sha256"] = hashlib.sha256(evidence[subject_path]).hexdigest()
    rejected(changed, "bounded_g4_correlation_binding_independent_subject")
    if stage == "enable":
        changed = copy.deepcopy(q)
        changed["base_commit"] = "0" * 40
        rejected(changed, "bounded_g4_correlation_binding_enable_base")
    else:
        changed = copy.deepcopy(q)
        changed["activation_acceptance"] = None
        rejected(changed, "bounded_g4_correlation_binding_activation_row")
        activation = json.loads(evidence[activation_path])
        activation["same_attempt_remote_readback_verified"] = False
        evidence[activation_path] = json.dumps(activation, sort_keys=True).encode("utf-8")
        changed = copy.deepcopy(q)
        changed["activation_acceptance"]["sha256"] = hashlib.sha256(
            evidence[activation_path]).hexdigest()
        rejected(changed, "bounded_g4_correlation_binding_activation_acceptance")



@pytest.mark.parametrize("stage", ["enable", "apply"])
def test_correlation_binding_subject_reviews_bind_each_phase_and_independence(monkeypatch, stage):
    q, _load, _evidence, _subject, _activation = _correlation_binding_loader_fixture(monkeypatch, stage)
    for phase in ("development", "pre-push", "post-push"):
        subject_q = copy.deepcopy(q)
        subject_q["phase"] = phase
        subject = bounded_g1b.g4_correlation_binding_review_subject(subject_q)
        path = (bounded_g1b.G4_CORRELATION_BINDING_ROOT / "entry-admission-v1" /
                ("independent-" + stage + "-" + phase + "-subject-review-v1.json"))
        review = {
            "schema": "emr4.g4_operation_review.v1", "status": "PASS",
            "verdict": "PASS_G4_STAGE1_CORRELATION_BINDING_EXACT_ADMISSION_SUBJECT",
            "subject_sha256": subject, "stage": stage, "phase": phase,
            "independent": True, "implementation_authorship": False,
            "blocking_findings": [], "reviewer_agent": "/root/independent-subject-reviewer",
        }

        def check(document):
            raw = bounded_g1b._canonical(document)
            row = {"path": path.as_posix(), "sha256": hashlib.sha256(raw).hexdigest()}

            def read(expected_path, digest):
                assert expected_path == path
                assert hashlib.sha256(raw).hexdigest() == digest
                return raw

            return bounded_g1b._g4_correlation_binding_review(
                read, row, bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT,
                subject, stage, phase)

        assert check(review) == review
        for key, value in (
            ("phase", "runtime"), ("subject_sha256", "0" * 64),
            ("independent", False), ("implementation_authorship", True),
            ("reviewer_agent", "/root"),
            ("reviewer_agent", "/root/interpret_diagnostic_author_61"),
            ("blocking_findings", ["unresolved"]),
        ):
            with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
                check(dict(review, **{key: value}))
            assert caught.value.reason_code == "bounded_g4_correlation_binding_independent_subject"


def test_receipt_successor_is_two_receipt_paths_and_requires_acceptance(monkeypatch):
    scope = _account_coexistence_preserved_receipt_v13_scope()
    bounded_g1b.validate_g4_receipt_scope(scope)
    assert scope["allowed_paths"] == sorted(bounded_g1b.G4_RECEIPT_PRODUCT)
    assert set(scope["allowed_paths"]) == {
        "app/services/patient_request_service.py", "tests/test_patient_request_submission_receipt.py",
    }
    assert scope["selected_base"] == bounded_g1b.G4_RECEIPT_BASE
    assert scope["admission_grants_runtime_authority"] is False
    for changed_field, changed_value in (
        ("selected_base", {"commit": "0" * 40, "tree": "0" * 40}),
        ("allowed_paths", scope["allowed_paths"] + ["app/other.py"]),
        ("product_sha256", {**scope["product_sha256"],
                            "app/services/patient_request_service.py": "0" * 64}),
        ("mapping_review", None),
        ("runtime_binding_required", False),
        ("admission_grants_runtime_authority", True),
        ("voice_activation", True),
        ("allowed_effects", scope["allowed_effects"] + ["provider_invocation"]),
        ("predecessor_scope", {"sha256": "0" * 64}),
    ):
        changed = copy.deepcopy(scope)
        changed[changed_field] = changed_value
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b.validate_g4_receipt_scope(changed)
        assert caught.value.reason_code == "bounded_g4_receipt_scope_boundary"

    for stage, kind, paths in (
        ("enable", "enable_g4_stage1_successor", bounded_g1b.G4_RECEIPT_CONTROL),
        ("apply", "implement_g4_stage1_successor", bounded_g1b.G4_RECEIPT_PRODUCT),
    ):
        q = {"schema_version": bounded_g1b.G4_RECEIPT_SCHEMA,
             "operation_kind": kind, "stage": stage,
             "repair_sha256": {p: {} for p in paths}}
        assert bounded_g1b.operation_paths(kind, q) == paths
        operation = bounded_g1b._operation(kind, q)
        assert operation["g4_receipt_source"] is True
        assert operation["paths"] == paths
        assert operation["profile"] == bounded_g1b.raisa_policy.G4_STAGE1_SUCCESSOR_PROFILE
        for replacement in (set(paths) | {"app/other.py"}, set(paths) - {next(iter(paths))}):
            with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
                bounded_g1b.operation_paths(kind, dict(
                    q, repair_sha256={p: {} for p in replacement}))
            assert caught.value.reason_code == "bounded_g4_receipt_changed_paths"



def test_receipt_subject_keeps_exact_sixteen_fields_and_excludes_review():
    keys = bounded_g1b.G4_RECEIPT_BINDING_KEYS
    assert len(keys) == 17 and keys == bounded_g1b.G4_BUREAU_BINDING_KEYS
    q = {key: {"marker": key} for key in keys}
    first = bounded_g1b.g4_receipt_review_subject(q)
    changed = copy.deepcopy(q)
    changed["source_review"] = {"different": True}
    assert bounded_g1b.g4_receipt_review_subject(changed) == first
    for key in keys - {"source_review"}:
        changed = copy.deepcopy(q)
        changed[key] = {"different": True}
        assert bounded_g1b.g4_receipt_review_subject(changed) != first


def test_receipt_full_policy_passes_all_configuration_documents_and_errors(monkeypatch):
    scope = _account_coexistence_preserved_receipt_v13_scope()
    payloads = {p: b"literal-document" for p in bounded_g1b.CONFIGURATION_PATHS}
    payloads[bounded_g1b.AGENTS] = b"literal-agents"
    payloads[bounded_g1b.STATE] = b'{"synthetic":true}'
    pins = {p: hashlib.sha256(raw).hexdigest() for p, raw in payloads.items()}
    calls = []
    marker = object()
    def validate(**kwargs):
        calls.append(kwargs)
        return marker
    monkeypatch.setattr(bounded_g1b.raisa_policy, "validate_recovery_configuration", validate)
    for stage, paths in (("enable", bounded_g1b.G4_RECEIPT_CONTROL), ("apply", bounded_g1b.G4_RECEIPT_PRODUCT)):
        selected = dict(payloads)
        selected.update({p: b"selected" for p in paths})
        inputs = bounded_g1b.BoundedG1BInputs({"stage": stage, "payload_sha256": pins}, {}, selected, {"scope": scope}, {})
        result, configuration = bounded_g1b._validate_g4_receipt_loaded_policy(inputs)
        assert set(result) == paths and configuration is marker
        assert calls[-1] == {
            "documents": {Path(p).name: payloads[p] for p in bounded_g1b.CONFIGURATION_PATHS},
            "expected_sha256": {Path(p).name: pins[p] for p in bounded_g1b.CONFIGURATION_PATHS},
            "agents_text": "literal-agents", "state": {"synthetic": True}}
    def fail(**kwargs):
        raise bounded_g1b.raisa_policy.RaisaPolicyError("receipt_configuration_rejected")
    monkeypatch.setattr(bounded_g1b.raisa_policy, "validate_recovery_configuration", fail)
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b._validate_g4_receipt_loaded_policy(inputs)
    assert caught.value.reason_code == "receipt_configuration_rejected"




def _account_coexistence_preserved_receipt_v13_scope():
    """Exact accepted H01 V13 fixture; active Account scope is V14."""
    return json.loads('{"active_profile":"G4_STAGE1_LOCAL_SUCCESSOR","admission_grants_runtime_authority":false,"allowed_effects":["control_plane_edit","product_behavior_change","repository_read","task_branch_commit","task_branch_push"],"allowed_paths":["app/services/patient_request_service.py","tests/test_patient_request_submission_receipt.py"],"allowed_task_kind":"g4_stage1_local_successor","control_sha256":{"orchestration_harness/bounded_g1b.py":"c13087ba56251d912e8b15b5f5a2745bbf07375c48370370d975946c4293a2d2","tests/test_g4_stage1_successor_entry.py":"69f5500cac1f921f33c0087b3126cc71ec25c5d0c046effc1da4cd69bf5022cf"},"excluded_effects":["unreviewed_application_or_database_runtime","unreviewed_browser_or_microphone_runtime","unreviewed_voice_child_or_network_egress","provider_invocation","real_data_access","protected_ref_movement","deployment","public_listener"],"mapping_review":{"path":"C:/Users/there/EMR4-tools/selected-patient-request-receipt-correction-v1/independent-source-review-v1.json","sha256":"f56a9d73abf7befb38a9af3c8e056bc69806210d0608dad79101e791d41e5aae"},"predecessor_scope":{"sha256":"1e9f0f901c9522cc044bc7eb05b0cff74fe517777ff8b71376552c2f9bec22d5"},"product_sha256":{"app/services/patient_request_service.py":"e65428f02ba15feeeca0f71dcefc256eded58e4c837d906e3d63b96cb8f90484","tests/test_patient_request_submission_receipt.py":"460c2825481f47c25dbe29375c0c7a05a89a351a9cd9af8e60c3286e371e13bf"},"product_vector":{"path":"C:/Users/there/EMR4-tools/selected-patient-request-receipt-correction-v1/source-vector-v1.json","sha256":"33d28d881069dab7b6a66f1eb46a600a94409df8a9563fd9ed79022a7a21b895"},"recorded_at":"2026-10-27T00:00:00+00:00","runtime_binding_required":true,"schema_version":"ariadne.g4_stage1_successor_entry_scope.v13","selected_base":{"commit":"7232b35ed1fb9d47df26b286865ab8bb93710955","tree":"390171d8791ef2e294138d74adf821563536eb81"},"source_sha256":{"orchestration_harness/bounded_g1b.py":"c13087ba56251d912e8b15b5f5a2745bbf07375c48370370d975946c4293a2d2","orchestration_harness/configuration_core.py":"f7ba7a80eb0a590f9fb71b864e6c1f9f43241d9f7d70a38da67a9243fea208e5","orchestration_harness/pinned_programme_gatekeeper.py":"c1fea9a2849068ed8e87dbe1e7cec1cc7e762fa2bc8876fc32bbda80d226cf39","orchestration_harness/programme_admission.py":"ac816a8a79b2d8222fa357777c075950927e86cf30c8a5b25ffd08a474052181","orchestration_harness/raisa_policy.py":"2dabec173bf7e39629e7036cac2d13c777e52649cea744a1fec778b5e9b9332e","orchestration_harness/trusted_git.py":"4a856bffe2b68d7c7e1875152629c9024a32679b59d9b1ed8301c368d41ff527","scripts/raisa_ariadne_recovery_preflight.py":"edfd37b30673b8544d309b532c95b3fd7c20ff592880a8a0235dfde6cfc8e7e4","tests/test_bounded_g1b.py":"bb1be86ca39232fea30c1ea84cdfb114428d57be0f8f67bf7e86daab0ba73bc5"},"voice_activation":false}\n')


def test_account_bootstrap_scope_and_source_vector_are_exact():
    root = Path(__file__).resolve().parents[1]
    scope = _human_preserved_account_v14_scope()
    bounded_g1b.validate_g4_account_bootstrap_scope(scope)
    assert len(scope["allowed_paths"]) == 11
    assert len(scope["source_sha256"]) == 8
    assert scope["predecessor_scope"]["sha256"] == "5b2460fafa34d66f160277e527a9779a815cb69e6fb06e656d87629f71c710de"
    vector_raw = bounded_g1b.G4_ACCOUNT_BOOTSTRAP_VECTOR.read_bytes()
    assert hashlib.sha256(vector_raw).hexdigest() == bounded_g1b.G4_ACCOUNT_BOOTSTRAP_VECTOR_SHA
    vector = json.loads(vector_raw)
    bounded_g1b._validate_g4_account_bootstrap_vector(vector)
    assert sum(row["before_sha256"] is None for row in vector["rows"]) == 6
    for key, value in (
        ("allowed_paths", scope["allowed_paths"] + ["app/other.py"]),
        ("runtime_binding_required", False),
        ("admission_grants_runtime_authority", True),
        ("voice_activation", True),
        ("predecessor_scope", {"sha256": "0" * 64}),
        ("selected_base", {"commit": vector["accepted_parent_commit"], "tree": vector["accepted_parent_tree"]}),
    ):
        changed = copy.deepcopy(scope)
        changed[key] = value
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b.validate_g4_account_bootstrap_scope(changed)
        assert caught.value.reason_code == "bounded_g4_account_bootstrap_scope_boundary"
    for key, value in (("after_path", "C:/unowned.py"), ("after_bytes", True),
                       ("before_sha256", "0" * 64), ("after_sha256", "0" * 64)):
        changed = copy.deepcopy(vector)
        changed["rows"][0][key] = value
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b._validate_g4_account_bootstrap_vector(changed)
        assert caught.value.reason_code == "bounded_g4_account_bootstrap_vector"
    changed = copy.deepcopy(vector)
    changed["rows"][-1] = copy.deepcopy(changed["rows"][0])
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b._validate_g4_account_bootstrap_vector(changed)
    assert caught.value.reason_code == "bounded_g4_account_bootstrap_vector"


@pytest.mark.parametrize("stage", ["enable", "apply"])
def test_account_bootstrap_dispatch_is_exact_and_subject_preserves_abi(stage):
    kind = "enable_g4_stage1_successor" if stage == "enable" else "implement_g4_stage1_successor"
    paths = bounded_g1b.G4_ACCOUNT_BOOTSTRAP_CONTROL if stage == "enable" else bounded_g1b.G4_ACCOUNT_BOOTSTRAP_PRODUCT
    q = {key: None for key in bounded_g1b.G4_ACCOUNT_BOOTSTRAP_BINDING_KEYS}
    q.update(schema_version=bounded_g1b.G4_ACCOUNT_BOOTSTRAP_SCHEMA,
             operation_kind=kind, stage=stage,
             repair_sha256={path: {} for path in paths})
    assert len(q) == 17
    assert bounded_g1b.operation_paths(kind, q) == paths
    operation = bounded_g1b._operation(kind, q)
    assert operation["g4_account_bootstrap_source"] is True
    assert operation["paths"] == paths
    assert "g4_correlation_binding_source" not in operation
    subject = bounded_g1b.g4_account_bootstrap_review_subject(q)
    q["source_review"] = {"ignored_for_subject": True}
    assert bounded_g1b.g4_account_bootstrap_review_subject(q) == subject
    for key in set(q) - {"source_review"}:
        changed = copy.deepcopy(q)
        changed[key] = "changed-subject-field"
        assert bounded_g1b.g4_account_bootstrap_review_subject(changed) != subject
    for replacement in (set(paths) | {"app/other.py"}, set(paths) - {next(iter(paths))}):
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b.operation_paths(kind, dict(q, repair_sha256={p: {} for p in replacement}))
        assert caught.value.reason_code == "bounded_g4_account_bootstrap_changed_paths"


def test_account_bootstrap_loaded_policy_dispatch_stays_source_specific(monkeypatch):
    q = {"schema_version": bounded_g1b.G4_ACCOUNT_BOOTSTRAP_SCHEMA,
         "operation_kind": "enable_g4_stage1_successor", "stage": "enable",
         "repair_sha256": {p: {} for p in bounded_g1b.G4_ACCOUNT_BOOTSTRAP_CONTROL}}
    sentinel = ({"account-source-only": b"inert"}, None)
    monkeypatch.setattr(bounded_g1b, "_validate_g4_account_bootstrap_loaded_policy", lambda inputs: sentinel)
    inputs = bounded_g1b.BoundedG1BInputs(q, {}, {}, {}, {})
    assert bounded_g1b._validate_loaded_policy(inputs) == sentinel


def test_account_receipt_correlation_coexistence_routes_do_not_cross(monkeypatch):
    families = (
        ("account_bootstrap", bounded_g1b.G4_ACCOUNT_BOOTSTRAP_SCHEMA,
         bounded_g1b.G4_ACCOUNT_BOOTSTRAP_CONTROL, bounded_g1b.G4_ACCOUNT_BOOTSTRAP_PRODUCT,
         "_validate_g4_account_bootstrap_loaded_policy"),
        ("receipt", bounded_g1b.G4_RECEIPT_SCHEMA,
         bounded_g1b.G4_RECEIPT_CONTROL, bounded_g1b.G4_RECEIPT_PRODUCT,
         "_validate_g4_receipt_loaded_policy"),
        ("correlation_binding", bounded_g1b.G4_CORRELATION_BINDING_SCHEMA,
         bounded_g1b.G4_CORRELATION_BINDING_CONTROL, bounded_g1b.G4_CORRELATION_BINDING_PRODUCT,
         "_validate_g4_correlation_binding_loaded_policy"),
    )
    assert len({item[1] for item in families}) == 3
    assert all(not (set(left[3]) & set(right[3]))
               for index,left in enumerate(families) for right in families[index+1:])
    calls = []
    sentinels = {name: ({name: b"source-only-routing"}, None) for name,*_ in families}
    for name,_,_,_,helper in families:
        def route(inputs, family=name):
            calls.append(family)
            return sentinels[family]
        monkeypatch.setattr(bounded_g1b, helper, route)
    expected_calls = []
    for name,schema,control,product,_ in families:
        for stage,kind,paths in (("enable","enable_g4_stage1_successor",control),
                                 ("apply","implement_g4_stage1_successor",product)):
            q = {key: None for key in bounded_g1b.G4_ACCOUNT_BOOTSTRAP_BINDING_KEYS}
            q.update(schema_version=schema, operation_kind=kind, stage=stage,
                     repair_sha256={path:{} for path in paths})
            assert len(q) == 17
            operation = bounded_g1b._operation(kind,q)
            assert bounded_g1b.operation_paths(kind,q) == paths
            assert operation["paths"] == paths
            assert operation["g4_"+name+"_source"] is True
            assert all("g4_"+other+"_source" not in operation
                       for other, *_ in families if other != name)
            inputs = bounded_g1b.BoundedG1BInputs(q, {}, {}, {}, {})
            assert bounded_g1b._validate_loaded_policy(inputs) is sentinels[name]
            expected_calls.append(name)
        for other,_,_,other_product,_ in families:
            if other == name:
                continue
            crossed = dict(q,repair_sha256={path:{} for path in other_product})
            with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
                bounded_g1b.operation_paths("implement_g4_stage1_successor",crossed)
            assert caught.value.reason_code == "bounded_g4_"+name+"_changed_paths"
    assert calls == expected_calls


def test_account_v14_keeps_receipt_v13_and_correlation_v12_scopes_separate():
    root = Path(__file__).resolve().parents[1]
    account = _human_preserved_account_v14_scope()
    receipt = _account_coexistence_preserved_receipt_v13_scope()
    correlation = _receipt_predecessor_v12_scope()
    cases = ((account,bounded_g1b.validate_g4_account_bootstrap_scope,"account_bootstrap",14),
             (receipt,bounded_g1b.validate_g4_receipt_scope,"receipt",13),
             (correlation,bounded_g1b.validate_g4_correlation_binding_scope,"correlation_binding",12))
    for scope,validate,name,version in cases:
        validate(scope)
        assert scope["schema_version"] == "ariadne.g4_stage1_successor_entry_scope.v"+str(version)
        assert len(scope["source_sha256"]) == 8
        assert scope["runtime_binding_required"] is True
        assert scope["admission_grants_runtime_authority"] is False
        assert scope["voice_activation"] is False
        for other,_,_,_ in cases:
            if other is scope:
                continue
            with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
                validate(other)
            assert caught.value.reason_code == "bounded_g4_"+name+"_scope_boundary"
    assert account["predecessor_scope"] == {
        "sha256":"5b2460fafa34d66f160277e527a9779a815cb69e6fb06e656d87629f71c710de"}
    assert account["product_vector"] != receipt["product_vector"] != correlation["product_vector"]
    assert account["allowed_effects"] == receipt["allowed_effects"] == correlation["allowed_effects"]
    assert account["excluded_effects"] == receipt["excluded_effects"] == correlation["excluded_effects"]



def _human_preserved_account_v14_scope():
    """Preserved exact accepted Account14 fixture; active human scope is source-only15."""
    return json.loads('{"active_profile":"G4_STAGE1_LOCAL_SUCCESSOR","admission_grants_runtime_authority":false,"allowed_effects":["control_plane_edit","product_behavior_change","repository_read","task_branch_commit","task_branch_push"],"allowed_paths":["alembic/versions/c8d9e0f1a2b3_add_account_membership_bridge.py","alembic/versions/d9e0f1a2b3c4_add_account_bootstrap_access.py","app/dependencies.py","app/models/__init__.py","app/models/account_membership.py","app/routers/auth.py","app/schemas/auth.py","app/services/account_access.py","app/services/auth_service.py","tests/test_account_bootstrap.py","tests/test_account_membership_persistence.py"],"allowed_task_kind":"g4_stage1_local_successor","control_sha256":{"orchestration_harness/bounded_g1b.py":"cdd42a8b17e6d350f67406a953bf4fe41a8ede75978161b6a5b76118bb91a9cb","tests/test_g4_stage1_successor_entry.py":"58830214930438c9c7a408d96a1659962b09d04f5f0cd9612f87b7e25a2542b3"},"excluded_effects":["unreviewed_application_or_database_runtime","unreviewed_browser_or_microphone_runtime","unreviewed_voice_child_or_network_egress","provider_invocation","real_data_access","protected_ref_movement","deployment","public_listener"],"mapping_review":{"path":"C:/Users/there/EMR4-tools/local-mock-account-bootstrap-candidate-v1/independent-bootstrap-source-review-v1.json","sha256":"f9e6c014104ca3d3a7150a732136b4a2f3ffc677ff2557e49816401e1f482cb9"},"predecessor_scope":{"sha256":"5b2460fafa34d66f160277e527a9779a815cb69e6fb06e656d87629f71c710de"},"product_sha256":{"alembic/versions/c8d9e0f1a2b3_add_account_membership_bridge.py":"f64ccbc9d05070e1cf0dc84fa145f27229245aef96bd9bd75a2433de51e0f73e","alembic/versions/d9e0f1a2b3c4_add_account_bootstrap_access.py":"06663906d285ea147062cbadc665ccc9511906bca7bc320f8b73984808095cbc","app/dependencies.py":"0e315c88b5231bdefa768d4e7c7708dae056ead1d9902270c747b3b519fa0b46","app/models/__init__.py":"29ad2b2034b016630d2157940d829fffb294f23c1ec2fb246f87a653d81268f2","app/models/account_membership.py":"81bdc94dd58b806591807d662180c240351afc910e3e18dba0911703915c9502","app/routers/auth.py":"f5e2a87e9fca99758fec6b69a9a64dc43257fb0a41285815eed29701af3eb893","app/schemas/auth.py":"5815412abf75515ed9cb9089042404587cb54f5e7bdc87047864ddfdd7936234","app/services/account_access.py":"7c3efc21b9e437481a09bd935c87aaacd97de4f73c9c811a8430a8a7ae3c7d17","app/services/auth_service.py":"402f57c68a3f3a2c55c0215f9e746ae956c4c5f57bb9ab553dacecc8f9e6cb5d","tests/test_account_bootstrap.py":"7ac93a512dae14aa5d693b924c9e69f1351c6d9549b0673281e5f55546eaffb8","tests/test_account_membership_persistence.py":"5ced8b36fecd3a964a90efcf3d4f40a33fbe8b86a2307bd24dbd6326cb9fd506"},"product_vector":{"path":"C:/Users/there/EMR4-tools/local-mock-account-bootstrap-candidate-v1/source-vector-v1.json","sha256":"f2312b35a4187a9fe835f9fb3dac91d7938652d3048866ca0e2d8fad61186620"},"recorded_at":"2026-10-27T00:00:00+00:00","runtime_binding_required":true,"schema_version":"ariadne.g4_stage1_successor_entry_scope.v14","selected_base":{"commit":"f7a5a790bce6ff23decd06af60108a980bee3089","tree":"aed9e3032a517a99b611f1262a858f641364a585"},"source_sha256":{"orchestration_harness/bounded_g1b.py":"cdd42a8b17e6d350f67406a953bf4fe41a8ede75978161b6a5b76118bb91a9cb","orchestration_harness/configuration_core.py":"f7ba7a80eb0a590f9fb71b864e6c1f9f43241d9f7d70a38da67a9243fea208e5","orchestration_harness/pinned_programme_gatekeeper.py":"c1fea9a2849068ed8e87dbe1e7cec1cc7e762fa2bc8876fc32bbda80d226cf39","orchestration_harness/programme_admission.py":"ac816a8a79b2d8222fa357777c075950927e86cf30c8a5b25ffd08a474052181","orchestration_harness/raisa_policy.py":"2dabec173bf7e39629e7036cac2d13c777e52649cea744a1fec778b5e9b9332e","orchestration_harness/trusted_git.py":"4a856bffe2b68d7c7e1875152629c9024a32679b59d9b1ed8301c368d41ff527","scripts/raisa_ariadne_recovery_preflight.py":"edfd37b30673b8544d309b532c95b3fd7c20ff592880a8a0235dfde6cfc8e7e4","tests/test_bounded_g1b.py":"bb1be86ca39232fea30c1ea84cdfb114428d57be0f8f67bf7e86daab0ba73bc5"},"voice_activation":false}\n')


def _human_scope():
    root = Path(__file__).resolve().parents[1]
    return json.loads((root / bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE).read_bytes())


def _human_q(stage="enable", phase="development"):
    q = {key:None for key in bounded_g1b.G4_HUMAN_BINDING_KEYS}
    paths = bounded_g1b.G4_HUMAN_CONTROL if stage == "enable" else frozenset()
    q.update(schema_version=bounded_g1b.G4_HUMAN_SCHEMA, operation_id="human-source-unit",
             operation_kind="enable_g4_stage1_successor" if stage == "enable" else bounded_g1b.G4_HUMAN_ADMIT_KIND,
             stage=stage, phase=phase, repair_sha256={p:{} for p in paths},
             base_commit=bounded_g1b.G4_HUMAN_BASE["commit"],
             expected_head=bounded_g1b.G4_HUMAN_BASE["commit"],
             base_tree=bounded_g1b.G4_HUMAN_BASE["tree"],
             candidate_tree=bounded_g1b.G4_HUMAN_BASE["tree"],
             expected_index_tree=bounded_g1b.G4_HUMAN_BASE["tree"])
    return q


def test_human_external_scope_does_not_activate_voice_or_admit_product():
    scope = _human_scope()
    bounded_g1b.validate_g4_human_scope(scope)
    assert len(scope["source_sha256"]) == 8
    assert scope["allowed_paths"] == [] and scope["product_sha256"] == {}
    for key,value in (("voice_activation",True),("runtime_binding_required",False),
                      ("admission_grants_runtime_authority",True),
                      ("allowed_paths",["app/services/auth_service.py"]),
                      ("product_sha256",{"app/services/auth_service.py":"0"*64}),
                      ("allowed_effects",scope["allowed_effects"]+["provider_invocation"]),
                      ("selected_base",bounded_g1b.G4_ACCOUNT_BOOTSTRAP_BASE),
                      ("predecessor_scope",{"sha256":"0"*64}),
                      ("mapping_review",{"path":"C:/synthetic/fake-review.json","sha256":"0"*64})):
        changed = copy.deepcopy(scope);changed[key]=value
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b.validate_g4_human_scope(changed)
        assert caught.value.reason_code == "bounded_g4_human_scope_boundary"


@pytest.mark.parametrize("stage",["enable","admit"])
def test_human_external_op17_subject16_and_exact_dispatch(stage):
    q = _human_q(stage)
    assert len(q) == 17
    expected = bounded_g1b.G4_HUMAN_CONTROL if stage == "enable" else frozenset()
    assert bounded_g1b.operation_paths(q["operation_kind"],q) == expected
    assert bounded_g1b._operation(q["operation_kind"],q)["g4_human_external_source"] is True
    subject = bounded_g1b.g4_human_review_subject(q)
    q["source_review"]={"outside_subject":True}
    assert bounded_g1b.g4_human_review_subject(q) == subject
    for key in set(q)-{"source_review"}:
        changed=copy.deepcopy(q);changed[key]="changed"
        assert bounded_g1b.g4_human_review_subject(changed) != subject
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b.operation_paths(q["operation_kind"],dict(q,repair_sha256={"app/unowned.py":{}}))
    assert caught.value.reason_code == "bounded_g4_human_changed_paths"
    if stage == "admit":
        assert bounded_g1b.operation_effects(q["operation_kind"]) == {"repository_read"}


@pytest.mark.parametrize("entrypoint,phase",[("task_branch_commit","development"),
    ("task_branch_push","pre-push"),("task_branch_push","post-push"),
    ("recovery_preflight","pre-push"),("recovery_preflight","post-push")])
def test_human_external_zero_delta_cannot_be_commit_or_push(entrypoint,phase):
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b._g4_human_require_entrypoint(_human_q("admit"),entrypoint,phase)
    assert caught.value.reason_code == "bounded_g4_human_admit_entrypoint"
    bounded_g1b._g4_human_require_entrypoint(_human_q("enable"),entrypoint,phase)
    bounded_g1b._g4_human_require_entrypoint({"schema_version":bounded_g1b.G4_ACCOUNT_BOOTSTRAP_SCHEMA},entrypoint,phase)


@pytest.mark.parametrize("key,value,reason",[
    ("phase","pre-push","bounded_g4_human_admit_no_delta"),
    ("phase","post-push","bounded_g4_human_admit_no_delta"),
    ("candidate_tree","a"*40,"bounded_g4_human_admit_no_delta"),
    ("expected_head","a"*40,"bounded_g4_human_admit_no_delta"),
    ("expected_index_tree","a"*40,"bounded_g4_human_admit_no_delta"),
    ("repair_sha256",{"app/unowned.py":{}},"bounded_g4_human_changed_paths")])
def test_human_admit_rejects_delta_before_external_read(key,value,reason):
    q=_human_q("admit");q[key]=value
    def forbidden(*args):pytest.fail("invalid admission reached an input/effect seam")
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b._load_g4_human_inputs(None,Path("C:/synthetic-target"),
            Path("C:/synthetic-source"),Path("C:/synthetic-evidence"),
            Path("C:/synthetic-scratch"),q,forbidden,{})
    assert caught.value.reason_code == reason


def test_human_subject_review_requires_new_independent_exact_subject():
    evidence=bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT
    path=bounded_g1b.G4_HUMAN_ROOT/"entry-admission-v1/independent-admit-development-subject-review-v1.json"
    subject="a"*64
    review={"schema":"emr4.g4_operation_review.v1","status":"PASS",
        "verdict":"PASS_G4_STAGE1_HUMAN_EXTERNAL_EXACT_ADMISSION_SUBJECT",
        "subject_sha256":subject,"independent":True,"implementation_authorship":False,
        "blocking_findings":[],"reviewer_agent":"/root/independent-synthetic-reviewer",
        "stage":"admit","phase":"development"}
    def call(value,row=None):
        return bounded_g1b._g4_human_subject_review(
            lambda p,d:json.dumps(value).encode(),row or {"path":path.as_posix(),"sha256":"b"*64},
            evidence,subject,"admit","development")
    assert call(review)==review
    for key,value in (("subject_sha256","0"*64),("independent",False),
                      ("implementation_authorship",True),("blocking_findings",["block"]),
                      ("reviewer_agent","/root/human_bureau_join_source_author"),
                      ("reviewer_agent","/root/human_account11_topology_join_author"),
                      ("phase","pre-push"),("stage","enable"),
                      ("verdict","PASS_CURRENT_BUREAU_HUMAN_SOURCE_PREPARATION_ONLY")):
        changed=copy.deepcopy(review);changed[key]=value
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:call(changed)
        assert caught.value.reason_code == "bounded_g4_human_independent_subject"
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        call(review,{"path":(path.parent/"wrong.json").as_posix(),"sha256":"b"*64})
    assert caught.value.reason_code == "bounded_g4_human_review_path"


def test_human_account_receipt_bureau_dispatches_stay_separate(monkeypatch):
    families=[("human_external",bounded_g1b.G4_HUMAN_SCHEMA,"admit",bounded_g1b.G4_HUMAN_ADMIT_KIND,
               frozenset(),"_validate_g4_human_loaded_policy"),
              ("account_bootstrap",bounded_g1b.G4_ACCOUNT_BOOTSTRAP_SCHEMA,"apply","implement_g4_stage1_successor",
               bounded_g1b.G4_ACCOUNT_BOOTSTRAP_PRODUCT,"_validate_g4_account_bootstrap_loaded_policy"),
              ("receipt",bounded_g1b.G4_RECEIPT_SCHEMA,"apply","implement_g4_stage1_successor",
               bounded_g1b.G4_RECEIPT_PRODUCT,"_validate_g4_receipt_loaded_policy"),
              ("correlation_binding",bounded_g1b.G4_CORRELATION_BINDING_SCHEMA,"apply","implement_g4_stage1_successor",
               bounded_g1b.G4_CORRELATION_BINDING_PRODUCT,"_validate_g4_correlation_binding_loaded_policy")]
    calls=[]
    for name,schema,stage,kind,paths,helper in families:
        sentinel=({name:b"routing-only"},None)
        def route(inputs,family=name,result=sentinel):calls.append(family);return result
        monkeypatch.setattr(bounded_g1b,helper,route)
        q=_human_q();q.update(schema_version=schema,stage=stage,operation_kind=kind,
                              repair_sha256={p:{} for p in paths})
        assert bounded_g1b.operation_paths(kind,q)==paths
        result=bounded_g1b._validate_loaded_policy(bounded_g1b.BoundedG1BInputs(q,{},{},{},{}))
        assert result is sentinel
        if name != "human_external":
            with pytest.raises(bounded_g1b.BoundedG1BError):
                bounded_g1b.operation_paths(kind,dict(q,repair_sha256={}))
    assert calls==[f[0] for f in families]


def test_human_loaded_policy_keeps_real_ten_document_validator(monkeypatch):
    scope=_human_scope();pins={p:"d"*64 for p in bounded_g1b.CONFIGURATION_PATHS}
    payloads={p:("document:"+p).encode() for p in pins}
    payloads.update({bounded_g1b.AGENTS:b"literal-agents",bounded_g1b.STATE:b'{"synthetic":true}'})
    marker=object();calls=[]
    def validate(**kwargs):calls.append(kwargs);return marker
    monkeypatch.setattr(bounded_g1b.raisa_policy,"validate_recovery_configuration",validate)
    assert len(pins)==10
    for stage,paths in (("enable",bounded_g1b.G4_HUMAN_CONTROL),("admit",frozenset())):
        p=dict(payloads);p.update({key:b"owned-candidate" for key in paths})
        inputs=bounded_g1b.BoundedG1BInputs({"stage":stage,"payload_sha256":pins},{},p,{"scope":scope},{})
        result,configuration=bounded_g1b._validate_g4_human_loaded_policy(inputs)
        assert set(result)==paths and configuration is marker
        assert calls[-1]=={"documents":{Path(k).name:payloads[k] for k in pins},
            "expected_sha256":{Path(k).name:pins[k] for k in pins},
            "agents_text":"literal-agents","state":{"synthetic":True}}
    def reject(**kwargs):raise bounded_g1b.raisa_policy.RaisaPolicyError("human-config-rejected")
    monkeypatch.setattr(bounded_g1b.raisa_policy,"validate_recovery_configuration",reject)
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b._validate_g4_human_loaded_policy(inputs)
    assert caught.value.reason_code=="human-config-rejected"


def test_human_current_publication_is_exact_independent_effect_not_boolean():
    raw=bounded_g1b.G4_HUMAN_CURRENT_PUBLICATION.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==bounded_g1b.G4_HUMAN_CURRENT_PUBLICATION_SHA
    original=json.loads(raw)
    assert bounded_g1b._g4_human_current_publication(lambda p,d:raw)==original
    for key,value in (("commit","0"*40),("candidate_tree","0"*40),
        ("independent",False),("implementation_authorship",True),("blocking_findings",["blocked"]),
        ("product_publication_accepted",False),("same_attempt_remote_readback_verified",False),
        ("whole_inverse_verified_same_attempt",False),("protected_refs_unchanged",False),
        ("result_sha256","0"*64),("published_ref","refs/heads/other"),
        ("published_url","https://example.invalid/"),
        ("reviewer_agent","/root/human_bureau_join_source_author")):
        changed=copy.deepcopy(original);changed[key]=value
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b._g4_human_current_publication(lambda p,d:json.dumps(changed).encode())
        assert caught.value.reason_code=="bounded_g4_human_current_publication"


def _human_loader_fixture(monkeypatch,stage="enable",phase="development"):
    """Controlled source-flow fixture: Git/index/external source checks substituted.

    This exercises this real loader, not actual native policy/Git/runtime. It
    does not read/retest154 accepted backend bodies or unchanged speech code.
    """
    root=Path(__file__).resolve().parents[1]
    candidate=root.parent
    target=Path("C:/synthetic-human-target");source=Path("C:/synthetic-human-source")
    evidence=bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT
    scope=_human_scope()
    paths=(bounded_g1b.CONFIGURATION_PATHS | {bounded_g1b.STATE,bounded_g1b.GATES,
        bounded_g1b.OVERLAY,bounded_g1b.AGENTS,bounded_g1b.G4_STAGE1_INTERACTIVE_SCOPE,
        bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE,bounded_g1b.G4_STAGE1_SUCCESSOR_TEST,
        bounded_g1b.G4_CI_WORKFLOW} | bounded_g1b.SOURCE_PATHS | bounded_g1b.CONTROLLER_PATHS)
    before={p:("accepted:"+p).encode() for p in paths}
    for p in bounded_g1b.G4_HUMAN_CONTROL:
        before[p]=(candidate/"before"/p).read_bytes()
    after={p:before[p] for p in paths}
    for p in bounded_g1b.G4_HUMAN_CONTROL-{bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE}:
        after[p]=(root/p).read_bytes()
    scope["source_sha256"]={p:hashlib.sha256(after[p]).hexdigest()
        for p in bounded_g1b.SOURCE_PATHS|bounded_g1b.CONTROLLER_PATHS}
    scope["control_sha256"]={p:hashlib.sha256(after[p]).hexdigest()
        for p in bounded_g1b.G4_HUMAN_CONTROL-{bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE}}
    after[bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE]=bounded_g1b._canonical(scope)+b"\n"
    q=_human_q(stage,phase)
    q.update(source_sha256=scope["source_sha256"],
        payload_sha256={p:hashlib.sha256(raw).hexdigest() for p,raw in after.items()},
        product_vector=scope["product_vector"],mapping_review=scope["mapping_review"])
    if stage=="enable":
        q["candidate_tree"]="a"*40
        q["repair_sha256"]={p:{"before_sha256":bounded_g1b.G4_HUMAN_PREIMAGES[p],
            "after_sha256":q["payload_sha256"][p]} for p in bounded_g1b.G4_HUMAN_CONTROL}
        if phase!="development":
            q.update(expected_head="e"*40,expected_index_tree=q["candidate_tree"])
    else:
        q.update(base_commit="b"*40,base_tree="c"*40,candidate_tree="c"*40,
                 expected_head="b"*40,expected_index_tree="c"*40)
        activation=bounded_g1b.G4_HUMAN_ROOT/"entry-admission-v1/independent-enable-push-effect-review-v1.json"
        q["activation_acceptance"]={"path":activation.as_posix(),"sha256":"f"*64}
    subject_path=bounded_g1b.G4_HUMAN_ROOT/"entry-admission-v1"/(
        "independent-"+stage+"-"+phase+"-subject-review-v1.json")
    q["source_review"]={"path":subject_path.as_posix(),"sha256":"d"*64}
    def read(p,d):
        if p==subject_path:
            return json.dumps({"schema":"emr4.g4_operation_review.v1","status":"PASS",
                "verdict":"PASS_G4_STAGE1_HUMAN_EXTERNAL_EXACT_ADMISSION_SUBJECT",
                "subject_sha256":bounded_g1b.g4_human_review_subject(q),"independent":True,
                "implementation_authorship":False,"blocking_findings":[],
                "reviewer_agent":"/root/synthetic-independent-reviewer","stage":stage,"phase":phase}).encode()
        if stage=="admit" and p==Path(q["activation_acceptance"]["path"]):
            return json.dumps({"schema":"emr4.g4_operation_review.v1","status":"PASS",
                "verdict":"PASS_G4_STAGE1_HUMAN_EXTERNAL_CONTROL_PUBLICATION_EFFECT",
                "reviewer_agent":"/root/synthetic-independent-reviewer","independent":True,
                "implementation_authorship":False,"blocking_findings":[],"stage":"enable","phase":"push",
                "base":bounded_g1b.G4_HUMAN_BASE["commit"],"commit":q["base_commit"],
                "candidate_tree":q["base_tree"],"control_activation_accepted":True,
                "same_attempt_remote_readback_verified":True,"protected_refs_unchanged":True,
                "whole_inverse_verified_same_attempt":True,"published_ref":bounded_g1b.G4_STAGE1_INTERACTIVE_BACKEND_REF}).encode()
        relative=p.relative_to(target if p.is_relative_to(target) else source).as_posix()
        raw=after[relative]
        if hashlib.sha256(raw).hexdigest()!=d:
            raise bounded_g1b.BoundedG1BError("bounded_g1b_input_digest_changed")
        return raw
    calls=[]
    def git_bytes(_target,*args):
        assert args[:2]==("cat-file","blob")
        commit,relative=args[2].split(":",1)
        return before[relative] if commit==bounded_g1b.G4_HUMAN_BASE["commit"] else after[relative]
    def git(_target,*args):
        if args[0]=="rev-parse":return bounded_g1b.G4_HUMAN_BASE["tree"]
        assert args[:2]==("cat-file","commit")
        parent=bounded_g1b.G4_HUMAN_BASE["commit"] if stage=="admit" else q["base_commit"]
        tree=q["base_tree"] if stage=="admit" else q["candidate_tree"]
        return "tree "+tree+"\nparent "+parent+"\n\nsynthetic\n"
    def attest(_target,**kwargs):calls.append(kwargs);return {"observation_sha256":"sha256:"+"0"*64}
    monkeypatch.setattr(bounded_g1b.trusted_git,"run_git_bytes",git_bytes)
    monkeypatch.setattr(bounded_g1b.trusted_git,"run_git",git)
    monkeypatch.setattr(bounded_g1b.trusted_git,"attest_target_index",attest)
    monkeypatch.setattr(bounded_g1b,"_g4_human_external_inputs",lambda _read,_q:({"inert":True},{"preparation_only":True}))
    monkeypatch.setattr(bounded_g1b,"_g4_human_current_publication",lambda _read:{"synthetic_control_flow":True})
    def run():
        return bounded_g1b._load_g4_human_inputs(None,target,source,evidence,
            Path("C:/synthetic-human-scratch"),q,read,{})
    return run,q,after,before,calls,paths


@pytest.mark.parametrize("stage,phase",[("enable","development"),("enable","pre-push"),
    ("enable","post-push"),("admit","development")])
def test_human_loader_retains_core25_source8_and_phase_index_attestation(monkeypatch,stage,phase):
    run,q,after,before,calls,paths=_human_loader_fixture(monkeypatch,stage,phase)
    inputs=run()
    assert inputs.binding is q and len(q["source_sha256"])==8 and len(paths)==25
    assert set(inputs.payloads)==paths and inputs.payloads==after
    owned=bounded_g1b.G4_HUMAN_CONTROL if stage=="enable" else frozenset()
    attested=paths-owned if phase=="development" else paths
    assert calls==[{"attested_paths":tuple(sorted(attested)),"expected_head":q["expected_head"],
        "expected_index_tree":q["expected_index_tree"],"scratch_parent":Path("C:/synthetic-human-scratch")}]


@pytest.mark.parametrize("mode,reason",[("before","bounded_g4_human_change_preimage"),
    ("unowned","bounded_g4_human_unowned_change"),
    ("payload_extra","bounded_g4_human_payload_paths"),
    ("source_missing","bounded_g4_human_sources")])
def test_human_loader_rejects_preimage_unowned_and_closure_drift(monkeypatch,mode,reason):
    run,q,after,before,calls,paths=_human_loader_fixture(monkeypatch)
    if mode=="before":before[bounded_g1b.G4_AUDIT_CODE]=b"changed-current-controller"
    elif mode=="unowned":before[bounded_g1b.G4_CI_WORKFLOW]=b"different-committed-workflow"
    elif mode=="payload_extra":q["payload_sha256"]["app/unowned.py"]="0"*64
    else:del q["source_sha256"][bounded_g1b.G4_AUDIT_CODE]
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:run()
    assert caught.value.reason_code==reason
    assert calls==[]


@pytest.mark.parametrize("binding",[None,{},
    {"schema_version":"ariadne.g4_stage1_local_mock_account_bootstrap_operation_binding.v1",
     "operation_kind":"admit_g4_stage1_human_external_source","stage":"admit","repair_sha256":{}}])
def test_human_empty_paths_exception_requires_its_exact_family(binding):
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b.operation_paths(bounded_g1b.G4_HUMAN_ADMIT_KIND,binding)
    assert caught.value.reason_code=="bounded_g4_human_binding_kind"


@pytest.mark.parametrize("mutation,reason",[("none",None),
    ("outside","bounded_g4_human_external_source"),
    ("runtime_review","bounded_g4_human_preparation_provenance"),
    ("duplicate","bounded_g4_human_external_unique"),
    ("old_schema","bounded_g4_human_external_vector"),
    ("unaccepted","bounded_g4_human_preparation_provenance"),
    ("nested_after","bounded_g4_human_preparation_provenance")])
def test_human_external_reader_retains_exact_paths_and_inert_provenance(mutation,reason):
    # Only actual ordinary metadata is read. Source bodies are deliberate length
    # substitutions, so this is not a new source hash/native/package acceptance.
    vector=json.loads(bounded_g1b.G4_HUMAN_VECTOR.read_bytes())
    table=json.loads(Path(vector["backend_rows"]["path"]).read_bytes())
    review=json.loads(bounded_g1b.G4_HUMAN_PREPARATION_REVIEW.read_bytes())
    if mutation=="outside":vector["actors"][0]["after"]["path"]="C:/synthetic-unowned/actor.py"
    if mutation=="duplicate":vector["actors"][1]["after"]=copy.deepcopy(vector["actors"][0]["after"])
    if mutation=="runtime_review":review["runtime_accepted"]=True
    if mutation=="old_schema":vector["schema"]="emr4.selected_bureau_human_source_vector.v2"
    if mutation=="unaccepted":review["source_preparation_accepted"]=False
    if mutation=="nested_after":review["actor_inverse_evidence"][0]["after"]["sha256"]="0"*64
    metadata={bounded_g1b.G4_HUMAN_VECTOR:(json.dumps(vector,indent=2)+"\n").encode(),
        bounded_g1b.G4_HUMAN_PREPARATION_REVIEW:json.dumps(review).encode(),
        Path(vector["backend_rows"]["path"]):json.dumps(table).encode()}
    # The real fixed metadata rows are read as data only; all actor/backend
    # bodies remain explicit length substitutions in this source-flow test.
    for row in bounded_g1b.G4_HUMAN_PREPARATION_SUBJECT.values():
        path=Path(row["path"])
        if path not in metadata:metadata[path]=path.read_bytes()
    rows=[a["after"] for a in vector["actors"]]+[s["after"] for s in vector["site"]]+[vector["site_handoff"],vector["backend_rows"]]
    lengths={Path(r["path"]):r["bytes"] for r in rows}
    lengths.update({Path(r["source_path"]):r["bytes"] for r in table})
    seen=[]
    def read(path,digest):
        seen.append(path)
        if path in metadata:
            if path==Path(vector["backend_rows"]["path"]):
                # The exact serialized frozen table length is retained.
                return Path(path).read_bytes()
            return metadata[path]
        if path in lengths:return b"x"*lengths[path]
        assert path.name in {"component_recognizer.py","wav_validation.py"}
        return b"source-length-substitution"
    q=_human_q();q.update(product_vector={"path":bounded_g1b.G4_HUMAN_VECTOR.as_posix(),"sha256":bounded_g1b.G4_HUMAN_VECTOR_SHA},
        mapping_review={"path":bounded_g1b.G4_HUMAN_PREPARATION_REVIEW.as_posix(),"sha256":bounded_g1b.G4_HUMAN_PREPARATION_REVIEW_SHA})
    if reason is None:
        result=bounded_g1b._g4_human_external_inputs(read,q)
        assert result==(vector,review)
        assert all(Path(r["source_path"]) in seen for r in table)
        assert any(p.name=="component_recognizer.py" for p in seen)
        assert any(p.name=="wav_validation.py" for p in seen)
    else:
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b._g4_human_external_inputs(read,q)
        assert caught.value.reason_code==reason


def test_human_account11_metadata_joins_exact_current_base_and_nested_actor_pins():
    vector=json.loads(bounded_g1b.G4_HUMAN_VECTOR.read_bytes())
    review=json.loads(bounded_g1b.G4_HUMAN_PREPARATION_REVIEW.read_bytes())
    table=json.loads(Path(vector["backend_rows"]["path"]).read_bytes())
    assert len(table)==154
    assert vector["actual_base_binding"]["commit"]==bounded_g1b.G4_HUMAN_BASE["commit"]
    assert vector["actual_base_binding"]["tree"]==bounded_g1b.G4_HUMAN_BASE["tree"]
    assert review["subject"]==bounded_g1b.G4_HUMAN_PREPARATION_SUBJECT
    assert all(item["before"]==actor["before"] and item["after"]==actor["after"]
               for item,actor in zip(review["actor_inverse_evidence"],vector["actors"]))
    assert all(not row["relative_path"].startswith("tests/") for row in table)


@pytest.mark.parametrize("key,value",[("schema","emr4.g4_local_mock_account_bootstrap_enable_publication_effect_review.v1"),
    ("stage","enable"),("base","0"*40),("base_tree","0"*40),
    ("published_commit","0"*40),("result",{"path":"C:/fake/result.json","bytes":7776,"sha256":"0"*64})])
def test_human_current_account_apply_publication_rejects_prior_family_or_unjoined_result(key,value):
    review=json.loads(bounded_g1b.G4_HUMAN_CURRENT_PUBLICATION.read_bytes())
    review[key]=value
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b._g4_human_current_publication(lambda p,d:json.dumps(review).encode())
    assert caught.value.reason_code=="bounded_g4_human_current_publication"
# New exact invitation family; source tests only, not PostgreSQL/runtime proof.
_INVITATION_AFTERIMAGES=Path("C:/Users/there/EMR4-tools/local-mock-invitation-enable-preparation-v2/after")


def _invitation_scope():
    return json.loads((_INVITATION_AFTERIMAGES/bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE).read_bytes())


def _invitation_q(stage="enable"):
    kind="enable_g4_stage1_successor" if stage=="enable" else "implement_g4_stage1_successor"
    selected=bounded_g1b.G4_INVITATION_CONTROL if stage=="enable" else bounded_g1b.G4_INVITATION_PRODUCT
    q={key:None for key in bounded_g1b.G4_INVITATION_BINDING_KEYS}
    q.update(schema_version=bounded_g1b.G4_INVITATION_SCHEMA,operation_kind=kind,stage=stage,
             repair_sha256={p:{} for p in selected},
             product_vector={"path":bounded_g1b.G4_INVITATION_VECTOR.as_posix(),"sha256":bounded_g1b.G4_INVITATION_VECTOR_SHA},
             mapping_review={"path":bounded_g1b.G4_INVITATION_SOURCE_REVIEW.as_posix(),"sha256":bounded_g1b.G4_INVITATION_SOURCE_REVIEW_SHA})
    return q


@pytest.mark.parametrize("stage",["enable","apply"])
def test_invitation_dispatch_is_four_exact_product_paths_or_control3(stage):
    q=_invitation_q(stage);selected=bounded_g1b.G4_INVITATION_CONTROL if stage=="enable" else bounded_g1b.G4_INVITATION_PRODUCT
    assert len(q)==17 and len(selected)==(3 if stage=="enable" else 4)
    assert bounded_g1b.operation_paths(q["operation_kind"],q)==selected
    assert bounded_g1b._operation(q["operation_kind"],q)["g4_invitation_source"] is True
    assert bounded_g1b.G4_INVITATION_CAPSULE_ARTIFACT in bounded_g1b.G4_INVITATION_PRODUCT
    for wrong in (selected|{"app/unreviewed.py"},selected-{next(iter(selected))}):
        with pytest.raises(bounded_g1b.BoundedG1BError) as err:
            bounded_g1b.operation_paths(q["operation_kind"],dict(q,repair_sha256={p:{} for p in wrong}))
        assert err.value.reason_code=="bounded_g4_invitation_changed_paths"


def test_invitation_scope_preserves_base_and_runtime_authority_separation():
    scope=_invitation_scope();bounded_g1b.validate_g4_invitation_scope(scope)
    assert scope["selected_base"]=={"commit":"76356c9809c92e37d3b61989edac4390ce228510","tree":"87845dd28aac966d99659e3870a35492d5e10391"}
    assert len(scope["allowed_paths"])==4
    for key,value in (("allowed_paths",scope["allowed_paths"]+["app/extra.py"]),
       ("runtime_binding_required",False),("admission_grants_runtime_authority",True),("voice_activation",True),
       ("selected_base",bounded_g1b.G4_HUMAN_BASE),("product_vector",scope["mapping_review"])):
        changed=copy.deepcopy(scope);changed[key]=value
        with pytest.raises(bounded_g1b.BoundedG1BError) as err:bounded_g1b.validate_g4_invitation_scope(changed)
        assert err.value.reason_code=="bounded_g4_invitation_scope_boundary"


def test_invitation_vector_rejects_changed_extra_duplicate_or_outside_rows():
    vector=json.loads(bounded_g1b.G4_INVITATION_VECTOR.read_bytes())
    assert len(bounded_g1b._validate_g4_invitation_vector(vector))==4
    for mode in ("extra","duplicate","outside","digest","size","prior"):
        value=copy.deepcopy(vector)
        if mode=="extra":value["rows"].append(copy.deepcopy(value["rows"][0]))
        elif mode=="duplicate":value["rows"][-1]=copy.deepcopy(value["rows"][0])
        elif mode=="outside":value["rows"][0]["after"]["path"]="C:/unreviewed.py"
        elif mode=="digest":value["rows"][0]["after"]["sha256"]="0"*64
        elif mode=="size":value["rows"][0]["after"]["bytes"]=True
        else:value["rows"][0]["original_target_before_sha256"]="0"*64
        with pytest.raises(bounded_g1b.BoundedG1BError) as err:bounded_g1b._validate_g4_invitation_vector(value)
        assert err.value.reason_code=="bounded_g4_invitation_vector"


def test_invitation_external_reader_consumes_actual_qualified_source_review():
    q=_invitation_q();calls=[]
    def read(path,digest):
        raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==digest;calls.append(path);return raw
    vector,mapping,rows=bounded_g1b._g4_invitation_external_inputs(read,q)
    assert len(rows)==4 and mapping["product_source_accepted"] is True and mapping["runtime_accepted"] is False
    assert {Path(r["after_path"]) for r in rows}<=set(calls)
    bad=dict(q,product_vector=dict(q["product_vector"],sha256="0"*64))
    with pytest.raises(bounded_g1b.BoundedG1BError) as err:bounded_g1b._g4_invitation_external_inputs(read,bad)
    assert err.value.reason_code=="bounded_g4_invitation_product_pins"


@pytest.mark.parametrize("key,value",[("independent",False),("product_source_accepted",False),
 ("implementation_authorship",True),("verdict","PASS_RUNTIME"),("runtime_accepted",True),
 ("reviewer","/root/human_account11_topology_join_author"),("blocking_findings",["block"])])
def test_invitation_rejects_unreviewed_or_mislabelled_source(key,value):
    def read(path,digest):
        raw=path.read_bytes()
        if path==bounded_g1b.G4_INVITATION_SOURCE_REVIEW:
            row=json.loads(raw);row[key]=value;return json.dumps(row).encode()
        assert hashlib.sha256(raw).hexdigest()==digest;return raw
    with pytest.raises(bounded_g1b.BoundedG1BError) as err:bounded_g1b._g4_invitation_external_inputs(read,_invitation_q())
    assert err.value.reason_code=="bounded_g4_invitation_independent_source"


def test_invitation_dispatch_and_subject_do_not_capture_old_families(monkeypatch):
    q=_invitation_q();subject=bounded_g1b.g4_invitation_review_subject(q)
    assert bounded_g1b.g4_invitation_review_subject(dict(q,source_review={"unissued":True}))==subject
    assert bounded_g1b.g4_invitation_review_subject(dict(q,candidate_tree="changed"))!=subject
    sentinel=({"new-invitation-only":b"source-routing"},None)
    monkeypatch.setattr(bounded_g1b,"_validate_g4_invitation_loaded_policy",lambda inputs:sentinel)
    assert bounded_g1b._validate_loaded_policy(bounded_g1b.BoundedG1BInputs(q,{},{},{},{})) is sentinel
    account=dict(q,schema_version=bounded_g1b.G4_ACCOUNT_BOOTSTRAP_SCHEMA,stage="apply",operation_kind="implement_g4_stage1_successor",repair_sha256={p:{} for p in bounded_g1b.G4_ACCOUNT_BOOTSTRAP_PRODUCT})
    assert bounded_g1b.operation_paths(account["operation_kind"],account)==bounded_g1b.G4_ACCOUNT_BOOTSTRAP_PRODUCT
    human=dict(q,schema_version=bounded_g1b.G4_HUMAN_SCHEMA,stage="admit",operation_kind=bounded_g1b.G4_HUMAN_ADMIT_KIND,repair_sha256={})
    assert bounded_g1b.operation_paths(human["operation_kind"],human)==frozenset()


@pytest.mark.parametrize("key",sorted(bounded_g1b.G4_INVITATION_BINDING_KEYS-{"source_review"}))
def test_invitation_subject_binds_every_canonical_field(key):
    q=_invitation_q()
    assert len(q)==17 and len(q)-1==16
    assert bounded_g1b.g4_invitation_review_subject(dict(q,**{key:"changed"}))!=bounded_g1b.g4_invitation_review_subject(q)


@pytest.mark.parametrize("mode,reason",[("missing","bounded_g4_invitation_vector"),
    ("nested_review","bounded_g4_invitation_independent_source"),
    ("parent","bounded_g4_invitation_source_provenance"),
    ("short","bounded_g4_invitation_source_bytes")])
def test_invitation_external_join_rejects_missing_or_unreviewed_provenance(mode,reason):
    def read(path,digest):
        raw=path.read_bytes()
        if path==bounded_g1b.G4_INVITATION_VECTOR and mode in {"missing","parent"}:
            item=json.loads(raw)
            if mode=="missing":item["rows"].pop()
            if mode=="parent":item["parent_vector"]["sha256"]="0"*64
            return json.dumps(item).encode()
        if path==bounded_g1b.G4_INVITATION_SOURCE_REVIEW and mode=="nested_review":
            item=json.loads(raw);item["subject"]["product_vector"]["rows"][0]["after"]["sha256"]="0"*64
            return json.dumps(item).encode()
        if mode=="short" and path.name=="local_synthetic_invitation.py":return raw[:-1]
        return raw
    with pytest.raises(bounded_g1b.BoundedG1BError) as err:
        bounded_g1b._g4_invitation_external_inputs(read,_invitation_q())
    assert err.value.reason_code==reason


@pytest.mark.parametrize("stage",["enable","apply"])
def test_invitation_paths_reject_family_kind_and_stage_mismatch(stage):
    q=_invitation_q(stage)
    for changed in (dict(q,schema_version=bounded_g1b.G4_ACCOUNT_BOOTSTRAP_SCHEMA),
                    dict(q,stage="admit"),dict(q,operation_kind=bounded_g1b.G4_HUMAN_ADMIT_KIND)):
        with pytest.raises(bounded_g1b.BoundedG1BError) as err:
            bounded_g1b._g4_invitation_paths(q["operation_kind"],changed)
        assert err.value.reason_code=="bounded_g4_invitation_binding_kind"


def _invitation_loader_fixture(monkeypatch,stage="enable",phase="development"):
    """Synthetic control flow only; no Git, native admission, or runtime proof."""
    target=Path("C:/synthetic-invitation-target");source=Path("C:/synthetic-invitation-source")
    evidence=bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT
    scope=_invitation_scope()
    core=(bounded_g1b.CONFIGURATION_PATHS | {bounded_g1b.STATE,bounded_g1b.GATES,
        bounded_g1b.OVERLAY,bounded_g1b.AGENTS,bounded_g1b.G4_STAGE1_INTERACTIVE_SCOPE,
        bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE,bounded_g1b.G4_STAGE1_SUCCESSOR_TEST,
        bounded_g1b.G4_CI_WORKFLOW} | bounded_g1b.SOURCE_PATHS | bounded_g1b.CONTROLLER_PATHS)
    paths=core|(bounded_g1b.G4_INVITATION_PRODUCT if stage=="apply" else set())
    prior={p:("accepted:"+p).encode() for p in core}
    for p in bounded_g1b.G4_INVITATION_CONTROL:
        prior[p]=(_INVITATION_AFTERIMAGES.parent/"before"/p).read_bytes()
    after=dict(prior)
    for p in bounded_g1b.G4_INVITATION_CONTROL-{bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE}:
        after[p]=(_INVITATION_AFTERIMAGES/p).read_bytes()
    vector=json.loads(bounded_g1b.G4_INVITATION_VECTOR.read_bytes())
    rows=bounded_g1b._validate_g4_invitation_vector(vector)
    product={r["relative_path"]:Path(r["after_path"]).read_bytes() for r in rows}
    if stage=="apply":after.update(product)
    scope["source_sha256"]={p:hashlib.sha256(after[p]).hexdigest()
        for p in bounded_g1b.SOURCE_PATHS|bounded_g1b.CONTROLLER_PATHS}
    scope["control_sha256"]={p:hashlib.sha256(after[p]).hexdigest()
        for p in bounded_g1b.G4_INVITATION_CONTROL-{bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE}}
    after[bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE]=bounded_g1b._canonical(scope)+b"\n"
    installed=prior if stage=="enable" else {p:after[p] for p in core}
    q=_invitation_q(stage)
    q.update(operation_id="synthetic-invitation-source",phase=phase,
        base_commit=bounded_g1b.G4_INVITATION_BASE["commit"] if stage=="enable" else "b"*40,
        base_tree=bounded_g1b.G4_INVITATION_BASE["tree"] if stage=="enable" else "c"*40,
        candidate_tree="a"*40,source_sha256=scope["source_sha256"],
        payload_sha256={p:hashlib.sha256(raw).hexdigest() for p,raw in after.items()})
    q.update(expected_head=q["base_commit"] if phase=="development" else "e"*40,
        expected_index_tree=q["base_tree"] if phase=="development" else q["candidate_tree"])
    owned=bounded_g1b.G4_INVITATION_CONTROL if stage=="enable" else bounded_g1b.G4_INVITATION_PRODUCT
    q["repair_sha256"]={p:{"before_sha256":hashlib.sha256(installed[p]).hexdigest() if p in installed else None,
        "after_sha256":q["payload_sha256"][p]} for p in owned}
    subject_path=bounded_g1b.G4_INVITATION_ROOT/"entry-admission-v1"/(
        "independent-"+stage+"-"+phase+"-subject-review-v1.json")
    q["source_review"]={"path":subject_path.as_posix(),"sha256":"d"*64}
    activation_path=bounded_g1b.G4_INVITATION_ROOT/"entry-admission-v1/independent-enable-push-effect-review-v1.json"
    if stage=="apply":q["activation_acceptance"]={"path":activation_path.as_posix(),"sha256":"f"*64}
    review={"schema":"emr4.g4_operation_review.v1","status":"PASS",
        "verdict":"PASS_G4_STAGE1_LOCAL_SYNTHETIC_INVITATION_EXACT_ADMISSION_SUBJECT",
        "independent":True,"implementation_authorship":False,"blocking_findings":[],
        "reviewer_agent":"/root/synthetic-independent-reviewer","stage":stage,"phase":phase}
    activation={"status":"PASS","verdict":"PASS_G4_STAGE1_LOCAL_SYNTHETIC_INVITATION_CONTROL_PUBLICATION_EFFECT",
        "reviewer_agent":"/root/synthetic-independent-reviewer","independent":True,
        "implementation_authorship":False,"blocking_findings":[],"stage":"enable","phase":"push",
        "base":bounded_g1b.G4_INVITATION_BASE["commit"],"commit":q["base_commit"],
        "candidate_tree":q["base_tree"],"control_activation_accepted":True,
        "same_attempt_remote_readback_verified":True,"protected_refs_unchanged":True,
        "whole_inverse_verified_same_attempt":True,"published_ref":bounded_g1b.G4_STAGE1_INTERACTIVE_BACKEND_REF}
    def read(p,d):
        if p==subject_path:return json.dumps(dict(review,subject_sha256=bounded_g1b.g4_invitation_review_subject(q))).encode()
        if p==activation_path:return json.dumps(activation).encode()
        if p.is_relative_to(bounded_g1b.G4_INVITATION_VECTOR.parent/"after"):
            return product[p.relative_to(bounded_g1b.G4_INVITATION_VECTOR.parent/"after").as_posix()]
        relative=p.relative_to(target if p.is_relative_to(target) else source).as_posix()
        raw=after[relative]
        if hashlib.sha256(raw).hexdigest()!=d:raise bounded_g1b.BoundedG1BError("bounded_g1b_input_digest_changed")
        return raw
    def git_bytes(_target,*args):
        if args[:2]==("ls-tree","-z"):return b"present" if args[-1] in installed else b""
        assert args[:2]==("cat-file","blob")
        commit,relative=args[2].split(":",1)
        return prior[relative] if commit==bounded_g1b.G4_INVITATION_BASE["commit"] else installed[relative]
    def git(_target,*args):
        if args[0]=="rev-parse":return bounded_g1b.G4_INVITATION_BASE["tree"]
        assert args[:2]==("cat-file","commit")
        activation_commit=stage=="apply" and args[2]==q["base_commit"]
        parent=bounded_g1b.G4_INVITATION_BASE["commit"] if activation_commit else q["base_commit"]
        tree=q["base_tree"] if activation_commit else q["candidate_tree"]
        return "tree "+tree+"\nparent "+parent+"\n\nsynthetic\n"
    calls=[]
    monkeypatch.setattr(bounded_g1b.trusted_git,"run_git_bytes",git_bytes)
    monkeypatch.setattr(bounded_g1b.trusted_git,"run_git",git)
    monkeypatch.setattr(bounded_g1b.trusted_git,"attest_target_index",lambda _target,**kwargs:calls.append(kwargs) or {})
    monkeypatch.setattr(bounded_g1b,"_g4_invitation_external_inputs",lambda _read,_q:(vector,{"source_only":True},rows))
    monkeypatch.setattr(bounded_g1b,"_g4_invitation_fixture_source",lambda _read:{"synthetic_implemented_fixture_source_join":True})
    def run():
        return bounded_g1b._load_g4_invitation_inputs(None,target,source,evidence,
            Path("C:/synthetic-invitation-scratch"),q,read,{})
    return run,q,after,installed,calls,paths,review,activation


@pytest.mark.parametrize("stage,phase",[("enable","development"),("enable","pre-push"),
    ("enable","post-push"),("apply","development"),("apply","pre-push"),("apply","post-push")])
def test_invitation_loader_real_body_retains_core25_and_exact4(monkeypatch,stage,phase):
    run,q,after,installed,calls,paths,review,activation=_invitation_loader_fixture(monkeypatch,stage,phase)
    inputs=run()
    assert inputs.binding is q and inputs.payloads==after and len(paths)==(25 if stage=="enable" else 29)
    owned=bounded_g1b.G4_INVITATION_CONTROL if stage=="enable" else bounded_g1b.G4_INVITATION_PRODUCT
    assert calls==[{"attested_paths":tuple(sorted(paths-owned if phase=="development" else paths)),
        "expected_head":q["expected_head"],"expected_index_tree":q["expected_index_tree"],
        "scratch_parent":Path("C:/synthetic-invitation-scratch")}]


@pytest.mark.parametrize("mode,reason",[("base","bounded_g4_invitation_enable_base"),
    ("before","bounded_g4_invitation_change_preimage"),("unowned","bounded_g4_invitation_unowned_change"),
    ("payload_extra","bounded_g4_invitation_payload_paths"),("payload_missing","bounded_g4_invitation_payload_paths"),
    ("source_missing","bounded_g4_invitation_sources"),("review","bounded_g4_invitation_independent_subject"),
    ("review_path","bounded_g4_invitation_review_path")])
def test_invitation_loader_rejects_bad_base_paths_preimage_and_unreviewed_subject(monkeypatch,mode,reason):
    run,q,after,installed,calls,paths,review,activation=_invitation_loader_fixture(monkeypatch)
    if mode=="base":q["base_commit"]="0"*40
    elif mode=="before":installed[bounded_g1b.G4_AUDIT_CODE]=b"changed-controller"
    elif mode=="unowned":installed[bounded_g1b.G4_CI_WORKFLOW]=b"changed-unowned-workflow"
    elif mode=="payload_extra":q["payload_sha256"]["app/unreviewed.py"]="0"*64
    elif mode=="payload_missing":del q["payload_sha256"][bounded_g1b.G4_CI_WORKFLOW]
    elif mode=="source_missing":del q["source_sha256"][bounded_g1b.G4_AUDIT_CODE]
    elif mode=="review":review["independent"]=False
    else:q["source_review"]["path"]="C:/unreviewed/review.json"
    with pytest.raises(bounded_g1b.BoundedG1BError) as err:run()
    assert err.value.reason_code==reason and calls==[]


def test_invitation_apply_requires_independent_enable_publication(monkeypatch):
    run,q,after,installed,calls,paths,review,activation=_invitation_loader_fixture(monkeypatch,"apply")
    activation["control_activation_accepted"]=False
    with pytest.raises(bounded_g1b.BoundedG1BError) as err:run()
    assert err.value.reason_code=="bounded_g4_invitation_activation_acceptance" and calls==[]


@pytest.mark.parametrize("name,schema",[("HEADER","G4_HEADER_BINDING_SCHEMA"),
    ("VOICE","G4_VOICE_BINDING_SCHEMA"),("HANDOFF","G4_HANDOFF_BINDING_SCHEMA"),
    ("AUDIT","G4_AUDIT_BINDING_SCHEMA"),("INTENT","G4_INTENT_SCHEMA"),
    ("BUREAU","G4_BUREAU_SCHEMA"),("BUREAU_V9","G4_BUREAU_V9_SCHEMA"),
    ("EXACT_TIME","G4_EXACT_TIME_SCHEMA"),("STATUS_CONTRACT","G4_STATUS_CONTRACT_SCHEMA"),
    ("CORRELATION_BINDING","G4_CORRELATION_BINDING_SCHEMA"),("RECEIPT","G4_RECEIPT_SCHEMA"),
    ("ACCOUNT_BOOTSTRAP","G4_ACCOUNT_BOOTSTRAP_SCHEMA")])
@pytest.mark.parametrize("stage",["enable","apply"])
def test_invitation_predicate_allows_every_prior_successor_family_to_dispatch(name,schema,stage):
    paths=getattr(bounded_g1b,"G4_"+name+("_CONTROL" if stage=="enable" else "_PRODUCT"))
    q=dict(_invitation_q(stage),schema_version=getattr(bounded_g1b,schema),repair_sha256={p:{} for p in paths})
    assert bounded_g1b._is_g4_invitation_binding(q) is False
    assert bounded_g1b.operation_paths(q["operation_kind"],q)==paths
    operation=bounded_g1b._operation(q["operation_kind"],q)
    assert operation["paths"]==paths and "g4_invitation_source" not in operation


def test_invitation_fixture_join_reads_actual_implemented_twelve_source_outputs():
    seen=[]
    def read(path,digest):
        raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==digest;seen.append(path);return raw
    result=bounded_g1b._g4_invitation_fixture_source(read)
    assert result["review"]["implemented_fixture_writer_source_accepted"] is True
    assert result["review"]["runtime_accepted"] is False
    rows=result["vector"]["rows"]
    assert len(rows)==12 and all(Path(r["after"]["path"]) in seen for r in rows)
    assert result["vector"]["product_vector"]["sha256"]==bounded_g1b.G4_INVITATION_VECTOR_SHA


@pytest.mark.parametrize("mode,reason",[("missing","bounded_g4_invitation_fixture_vector"),
    ("outside","bounded_g4_invitation_fixture_vector"),("unreviewed","bounded_g4_invitation_independent_source"),
    ("nested","bounded_g4_invitation_independent_source"),("wrong_product","bounded_g4_invitation_fixture_vector"),
    ("short_source","bounded_g4_invitation_fixture_source_bytes")])
def test_invitation_fixture_join_rejects_missing_outside_unreviewed_or_unjoined_source(mode,reason):
    # Reader deliberately substitutes metadata, exercising validators rather
    # than claiming a hash acceptance for the mutated synthetic document.
    def read(path,digest):
        raw=path.read_bytes()
        if path==bounded_g1b.G4_INVITATION_FIXTURE_VECTOR and mode in {"missing","outside","wrong_product"}:
            item=json.loads(raw)
            if mode=="missing":item["rows"].pop()
            elif mode=="outside":item["rows"][0]["after"]["path"]="C:/unreviewed/fixture.py"
            else:item["product_vector"]["sha256"]="0"*64
            return json.dumps(item).encode()
        if path==bounded_g1b.G4_INVITATION_SOURCE_REVIEW and mode in {"unreviewed","nested"}:
            item=json.loads(raw)
            if mode=="unreviewed":item["implemented_fixture_writer_source_accepted"]=False
            else:item["subject"]["fixture_vector"]["rows"][0]["after"]["sha256"]="0"*64
            return json.dumps(item).encode()
        if mode=="short_source" and path.name=="invitation_case_fixtures.py":return raw[:-1]
        assert hashlib.sha256(raw).hexdigest()==digest
        return raw
    with pytest.raises(bounded_g1b.BoundedG1BError) as err:bounded_g1b._g4_invitation_fixture_source(read)
    assert err.value.reason_code==reason


def test_invitation_loader_calls_implemented_source_join_for_apply_only(monkeypatch):
    calls=[]
    for stage in ("enable","apply"):
        run,q,after,installed,attest,paths,review,activation=_invitation_loader_fixture(monkeypatch,stage)
        monkeypatch.setattr(bounded_g1b,"_g4_invitation_fixture_source",lambda read:calls.append(stage) or {"source_only":True})
        run()
    assert calls==["apply"]


# Account HTTP external source successor: four focused source tests. Unrun here.
def _account_http_scope():
    return json.loads((Path(__file__).resolve().parents[1] /
                       bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE).read_bytes())


def _account_http_q(stage="enable", phase="development"):
    q = {key: None for key in bounded_g1b.G4_ACCOUNT_HTTP_BINDING_KEYS}
    paths = bounded_g1b.G4_ACCOUNT_HTTP_CONTROL if stage == "enable" else frozenset()
    q.update(schema_version=bounded_g1b.G4_ACCOUNT_HTTP_SCHEMA,
        operation_id="account-http-source-unit", stage=stage, phase=phase,
        operation_kind="enable_g4_stage1_successor" if stage == "enable" else bounded_g1b.G4_ACCOUNT_HTTP_ADMIT_KIND,
        repair_sha256={p: {} for p in paths},
        base_commit=bounded_g1b.G4_ACCOUNT_HTTP_BASE["commit"],
        expected_head=bounded_g1b.G4_ACCOUNT_HTTP_BASE["commit"],
        base_tree=bounded_g1b.G4_ACCOUNT_HTTP_BASE["tree"],
        candidate_tree=bounded_g1b.G4_ACCOUNT_HTTP_BASE["tree"],
        expected_index_tree=bounded_g1b.G4_ACCOUNT_HTTP_BASE["tree"])
    return q


def test_account_http_source_scope_dispatch_and_prior_families(monkeypatch):
    scope = _account_http_scope()
    bounded_g1b.validate_g4_account_http_scope(scope)
    assert scope["allowed_paths"] == [] and scope["product_sha256"] == {}
    for key, value in (("schema_version", "ariadne.g4_stage1_successor_entry_scope.v18"),
                       ("runtime_binding_required", False),
                       ("admission_grants_runtime_authority", True), ("voice_activation", True),
                       ("allowed_paths", ["app/routers/auth.py"]),
                       ("allowed_effects", scope["allowed_effects"] + ["product_behavior_change"]),
                       ("selected_base", bounded_g1b.G4_HUMAN_BASE),
                       ("product_vector", {"path": "C:/unowned.json", "sha256": "0" * 64}),
                       ("predecessor_scope", {"sha256": "0" * 64})):
        changed = copy.deepcopy(scope); changed[key] = value
        with pytest.raises(bounded_g1b.BoundedG1BError) as err:
            bounded_g1b.validate_g4_account_http_scope(changed)
        assert err.value.reason_code == "bounded_g4_account_http_scope_boundary"
    for stage in ("enable", "admit"):
        q = _account_http_q(stage)
        paths = bounded_g1b.G4_ACCOUNT_HTTP_CONTROL if stage == "enable" else frozenset()
        assert bounded_g1b.operation_paths(q["operation_kind"], q) == paths
        assert bounded_g1b._operation(q["operation_kind"], q)["g4_account_http_external_source"] is True
        subject = bounded_g1b.g4_account_http_review_subject(q)
        assert bounded_g1b.g4_account_http_review_subject(dict(q, source_review={"unissued": True})) == subject
        for key in set(q) - {"source_review"}:
            assert bounded_g1b.g4_account_http_review_subject(dict(q, **{key: "changed"})) != subject
        for changed in (dict(q, repair_sha256={"app/unowned.py": {}}),
                        dict(q, stage="apply"), dict(q, operation_kind="implement_g4_stage1_successor")):
            with pytest.raises(bounded_g1b.BoundedG1BError):
                bounded_g1b.operation_paths(q["operation_kind"], changed)
        old = dict(q, schema_version="ariadne.g4_stage1_account_http_external_source_operation_binding.v2")
        assert not bounded_g1b._is_g4_account_http_binding(old)
        with pytest.raises(bounded_g1b.BoundedG1BError) as err:
            bounded_g1b._g4_account_http_paths(q["operation_kind"], old)
        assert err.value.reason_code == "bounded_g4_account_http_binding_kind"
    q = _account_http_q("admit")
    assert bounded_g1b.operation_effects(q["operation_kind"]) == {"repository_read"}
    sentinel = ({}, None)
    monkeypatch.setattr(bounded_g1b, "_validate_g4_account_http_loaded_policy", lambda inputs: sentinel)
    assert bounded_g1b._validate_loaded_policy(bounded_g1b.BoundedG1BInputs(q, {}, {}, {}, {})) is sentinel
    for schema, stage, kind, paths in (
        (bounded_g1b.G4_HUMAN_SCHEMA, "admit", bounded_g1b.G4_HUMAN_ADMIT_KIND, frozenset()),
        (bounded_g1b.G4_ACCOUNT_BOOTSTRAP_SCHEMA, "apply", "implement_g4_stage1_successor", bounded_g1b.G4_ACCOUNT_BOOTSTRAP_PRODUCT),
        (bounded_g1b.G4_INVITATION_SCHEMA, "apply", "implement_g4_stage1_successor", bounded_g1b.G4_INVITATION_PRODUCT)):
        prior = dict(q, schema_version=schema, stage=stage, operation_kind=kind,
                     repair_sha256={p: {} for p in paths})
        assert not bounded_g1b._is_g4_account_http_binding(prior)
        assert bounded_g1b.operation_paths(kind, prior) == paths
        assert "g4_account_http_external_source" not in bounded_g1b._operation(kind, prior)


@pytest.mark.parametrize("mode", ["valid", "vector_path", "vector_hash", "row_path", "row_hash",
    "row_missing", "duplicate", "short", "review", "review_subject", "publication", "publication_source",
    "old_vector", "prior_review", "reviewer", "authorship", "publication_schema", "publication_base",
    "publication_tree", "publication_result", "publication_ref", "publication_readback", "publication_inverse",
    "dependency_review", "dependency_subject", "dependency_author", "dependency_row",
    "publication_not_accepted", "publication_activation_confusion"])
def test_account_http_external_subject_and_accepted_publication_are_exact(mode):
    # Only these literal ordinary sources are read; provenance backend is not read.
    allowed = {bounded_g1b.G4_ACCOUNT_HTTP_VECTOR, bounded_g1b.G4_ACCOUNT_HTTP_PREPARATION_REVIEW,
               bounded_g1b.G4_ACCOUNT_HTTP_FOCUSED_REVIEW, bounded_g1b.G4_ACCOUNT_HTTP_CURRENT_PUBLICATION,
               bounded_g1b.G4_ACCOUNT_HTTP_CURRENT_ACTIVATION, bounded_g1b.G4_ACCOUNT_HTTP_DEPENDENCY_REVIEW}
    allowed |= {Path(row["path"]) for row in bounded_g1b.G4_ACCOUNT_HTTP_EXTERNAL_VECTOR["rows"]}
    q = _account_http_q()
    q.update(product_vector={"path": bounded_g1b.G4_ACCOUNT_HTTP_VECTOR.as_posix(), "sha256": bounded_g1b.G4_ACCOUNT_HTTP_VECTOR_SHA},
        mapping_review={"path": bounded_g1b.G4_ACCOUNT_HTTP_PREPARATION_REVIEW.as_posix(), "sha256": bounded_g1b.G4_ACCOUNT_HTTP_PREPARATION_REVIEW_SHA})
    calls = []
    def read(path, digest):
        assert path in allowed
        calls.append(path)
        raw = path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == digest
        if path == bounded_g1b.G4_ACCOUNT_HTTP_VECTOR and mode in {"row_path", "row_hash", "row_missing", "duplicate", "dependency_row"}:
            value = json.loads(raw)
            if mode == "row_path": value["rows"][0]["path"] = "C:/unowned.py"
            if mode == "row_hash": value["rows"][1]["sha256"] = "9ec0e20556cb9eb4b930e8c40abac85648a65539a72cb2cc7d57eeccec44cfab"
            if mode == "row_missing": value["rows"].pop()
            if mode == "dependency_row": value["rows"][3]["sha256"] = "0" * 64
            if mode == "duplicate": value["rows"][1] = value["rows"][0]
            return json.dumps(value).encode()
        if mode == "short" and path == Path(bounded_g1b.G4_ACCOUNT_HTTP_EXTERNAL_VECTOR["rows"][0]["path"]):
            return raw[:-1]
        if path == bounded_g1b.G4_ACCOUNT_HTTP_FOCUSED_REVIEW and mode in {
                "review", "review_subject", "prior_review", "reviewer", "authorship"}:
            value = json.loads(raw)
            key, changed = {
                "review": ("independent", False), "review_subject": ("fixture_sha256", "0" * 64),
                "prior_review": ("prior_review_sha256", "0" * 64),
                "reviewer": ("reviewer_agent", "/root/unreviewed"),
                "authorship": ("implementation_authorship", True)}[mode]
            value[key] = changed
            return json.dumps(value).encode()
        if path == bounded_g1b.G4_ACCOUNT_HTTP_DEPENDENCY_REVIEW and mode in {
                "dependency_review", "dependency_subject", "dependency_author"}:
            value = json.loads(raw)
            if mode == "dependency_review": value["independent"] = False
            if mode == "dependency_subject": value["product"]["sha256"] = "0" * 64
            if mode == "dependency_author": value["implementation_authorship"] = True
            return json.dumps(value).encode()
        if path == bounded_g1b.G4_ACCOUNT_HTTP_CURRENT_PUBLICATION and mode in {
                "publication", "publication_source", "publication_schema", "publication_base", "publication_tree",
                "publication_not_accepted", "publication_activation_confusion"}:
            value = json.loads(raw)
            if mode == "publication_source":
                value["source_identity"]["files"][bounded_g1b.G4_AUDIT_CODE] = "0" * 64
            else:
                key, changed = {"publication": ("commit", "0" * 40),
                    "publication_schema": ("schema", "emr4.g4_local_mock_invitation_apply_publication_effect_review.v1"),
                    "publication_base": ("base", "0" * 40),
                    "publication_tree": ("candidate_tree", "0" * 40),
                    "publication_not_accepted": ("publication_accepted", False),
                    "publication_activation_confusion": ("activation_accepted", True)}[mode]
                value[key] = changed
            return json.dumps(value).encode()
        if path == bounded_g1b.G4_ACCOUNT_HTTP_CURRENT_ACTIVATION and mode in {
                "publication_result", "publication_ref", "publication_readback", "publication_inverse"}:
            value = json.loads(raw)
            if mode == "publication_result": value["result"]["sha256"] = "0" * 64
            if mode == "publication_ref": value["published_ref"] = "refs/heads/master"
            if mode == "publication_readback": value["same_attempt_remote_readback_verified"] = False
            if mode == "publication_inverse": value["whole_inverse_verified_same_attempt"] = False
            return json.dumps(value).encode()
        return raw
    if mode == "vector_path": q["product_vector"]["path"] = "C:/unowned.json"
    if mode == "vector_hash": q["product_vector"]["sha256"] = "0" * 64
    if mode == "old_vector": q["product_vector"] = {
        "path": 'C:/Users/there/EMR4-tools/local-mock-owner-staff-login-source-preparation-v1/account-http-factory-candidate-v2/admission-preparation/source-only-successor-v1/control-candidate-v1/corrected-test-control-successor-v1/external-source-vector-v2.json',
        "sha256": "a558337e74a02880b5201ec29ece96365b1aaad5cf3e85da1a6cac21e0f5a7ed"}
    if mode == "valid":
        vector, reviews = bounded_g1b._g4_account_http_external_inputs(read, q)
        assert len(vector["rows"]) == 4 and set(reviews) == {"helper", "focused", "dependency"}
        assert bounded_g1b._g4_account_http_current_publication(read)["commit"] == bounded_g1b.G4_ACCOUNT_HTTP_BASE["commit"]
        assert set(calls) == allowed
    else:
        reason = ("bounded_g4_account_http_external_pins" if mode.startswith("vector_") or mode == "old_vector" else
                  "bounded_g4_account_http_external_vector" if mode in {"row_path", "row_hash", "row_missing", "duplicate", "dependency_row"} else
                  "bounded_g4_account_http_external_source" if mode == "short" else
                  "bounded_g4_account_http_current_publication" if mode.startswith("publication") else
                  "bounded_g4_account_http_dependency_provenance" if mode.startswith("dependency_") else
                  "bounded_g4_account_http_preparation_provenance")
        with pytest.raises(bounded_g1b.BoundedG1BError) as err:
            bounded_g1b._g4_account_http_external_inputs(read, q)
            bounded_g1b._g4_account_http_current_publication(read)
        assert err.value.reason_code == reason


def test_account_http_admit_is_preflight_only_and_reports_no_execution(monkeypatch):
    q = _account_http_q("admit")
    q["source_sha256"] = {}; q["payload_sha256"] = {}
    inputs = bounded_g1b.BoundedG1BInputs(q, {}, {}, {}, {"observation_sha256": "sha256:" + "0" * 64})
    context = bounded_g1b.BoundedG1BContext(
        target_root=Path("C:/synthetic-account-http-target"), source_root=Path("C:/synthetic-account-http-source"),
        evidence_root=bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT,
        binding_path=Path("C:/synthetic-account-http-binding.json"), expected_binding_sha256="0" * 64,
        scratch_root=Path("C:/synthetic-account-http-scratch"))
    monkeypatch.setattr(bounded_g1b, "load_bounded_g1b_inputs", lambda context: inputs)
    monkeypatch.setattr(bounded_g1b, "_validate_g4_account_http_loaded_policy", lambda inputs: ({}, None))
    manifest = bounded_g1b.build_bounded_g1b_manifest(context)
    assert manifest["allowed_paths"] == [] and manifest["intended_side_effect_classes"] == ["repository_read"]
    report = bounded_g1b.bounded_g1b_report(context=context, manifest=manifest, entrypoint="recovery_preflight", phase="development")
    assert report["policy_eligible"] is True
    assert report["execution_authorized"] is False and report["feature_work_eligible"] is False
    for entrypoint, phase in (("task_branch_commit", "development"), ("task_branch_push", "pre-push"),
                              ("task_branch_push", "post-push"), ("recovery_preflight", "pre-push")):
        decision = bounded_g1b.evaluate_bounded_g1b_operation(context=context, manifest=manifest, entrypoint=entrypoint, phase=phase)
        assert not decision.policy_admitted and decision.reason_codes == ("bounded_g4_account_http_admit_entrypoint",)
    changed = dict(manifest, intended_side_effect_classes=["repository_read", "task_branch_commit"])
    decision = bounded_g1b.evaluate_bounded_g1b_operation(context=context, manifest=changed, entrypoint="recovery_preflight", phase="development")
    assert decision.reason_codes == ("bounded_g1b_manifest_binding_mismatch",)

def _account_http_loader_fixture(monkeypatch,stage="enable",phase="development"):
    """Controlled source-flow fixture: Git/index/external source checks substituted.

    This exercises the real loader with substituted Git/index/provenance seams. It
    does not import the HTTP helper or require native HTTP runtime closure.
    """
    root=Path(__file__).resolve().parents[1]
    candidate=root.parent
    target=Path("C:/synthetic-account-http-target");source=Path("C:/synthetic-account-http-source")
    evidence=bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT
    scope=_account_http_scope()
    paths=(bounded_g1b.CONFIGURATION_PATHS | {bounded_g1b.STATE,bounded_g1b.GATES,
        bounded_g1b.OVERLAY,bounded_g1b.AGENTS,bounded_g1b.G4_STAGE1_INTERACTIVE_SCOPE,
        bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE,bounded_g1b.G4_STAGE1_SUCCESSOR_TEST,
        bounded_g1b.G4_CI_WORKFLOW} | bounded_g1b.SOURCE_PATHS | bounded_g1b.CONTROLLER_PATHS)
    before={p:("accepted:"+p).encode() for p in paths}
    for p in bounded_g1b.G4_ACCOUNT_HTTP_CONTROL:
        before[p]=(candidate/"before"/p).read_bytes()
    after={p:before[p] for p in paths}
    for p in bounded_g1b.G4_ACCOUNT_HTTP_CONTROL-{bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE}:
        after[p]=(root/p).read_bytes()
    scope["source_sha256"]={p:hashlib.sha256(after[p]).hexdigest()
        for p in bounded_g1b.SOURCE_PATHS|bounded_g1b.CONTROLLER_PATHS}
    scope["control_sha256"]={p:hashlib.sha256(after[p]).hexdigest()
        for p in bounded_g1b.G4_ACCOUNT_HTTP_CONTROL-{bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE}}
    after[bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE]=bounded_g1b._canonical(scope)+b"\n"
    q=_account_http_q(stage,phase)
    q.update(source_sha256=scope["source_sha256"],
        payload_sha256={p:hashlib.sha256(raw).hexdigest() for p,raw in after.items()},
        product_vector=scope["product_vector"],mapping_review=scope["mapping_review"])
    if stage=="enable":
        q["candidate_tree"]="a"*40
        q["repair_sha256"]={p:{"before_sha256":bounded_g1b.G4_ACCOUNT_HTTP_PREIMAGES[p],
            "after_sha256":q["payload_sha256"][p]} for p in bounded_g1b.G4_ACCOUNT_HTTP_CONTROL}
        if phase!="development":
            q.update(expected_head="e"*40,expected_index_tree=q["candidate_tree"])
    else:
        q.update(base_commit="b"*40,base_tree="c"*40,candidate_tree="c"*40,
                 expected_head="b"*40,expected_index_tree="c"*40)
        activation=bounded_g1b.G4_ACCOUNT_HTTP_ROOT/"entry-admission-v1/independent-enable-push-effect-review-v1.json"
        q["activation_acceptance"]={"path":activation.as_posix(),"sha256":"f"*64}
    subject_path=bounded_g1b.G4_ACCOUNT_HTTP_ROOT/"entry-admission-v1"/(
        "independent-"+stage+"-"+phase+"-subject-review-v1.json")
    q["source_review"]={"path":subject_path.as_posix(),"sha256":"d"*64}
    def read(p,d):
        if p==subject_path:
            return json.dumps({"schema":"emr4.g4_operation_review.v1","status":"PASS",
                "verdict":"PASS_G4_STAGE1_ACCOUNT_HTTP_EXTERNAL_EXACT_ADMISSION_SUBJECT",
                "subject_sha256":bounded_g1b.g4_account_http_review_subject(q),"independent":True,
                "implementation_authorship":False,"blocking_findings":[],
                "reviewer_agent":"/root/synthetic-independent-reviewer","stage":stage,"phase":phase}).encode()
        if stage=="admit" and p==Path(q["activation_acceptance"]["path"]):
            return json.dumps({"schema":"emr4.g4_operation_review.v1","status":"PASS",
                "verdict":"PASS_G4_STAGE1_ACCOUNT_HTTP_EXTERNAL_CONTROL_PUBLICATION_EFFECT",
                "reviewer_agent":"/root/synthetic-independent-reviewer","independent":True,
                "implementation_authorship":False,"blocking_findings":[],"stage":"enable","phase":"push",
                "base":bounded_g1b.G4_ACCOUNT_HTTP_BASE["commit"],"commit":q["base_commit"],
                "candidate_tree":q["base_tree"],"control_activation_accepted":True,
                "same_attempt_remote_readback_verified":True,"protected_refs_unchanged":True,
                "whole_inverse_verified_same_attempt":True,"published_ref":bounded_g1b.G4_STAGE1_INTERACTIVE_BACKEND_REF}).encode()
        relative=p.relative_to(target if p.is_relative_to(target) else source).as_posix()
        raw=after[relative]
        if hashlib.sha256(raw).hexdigest()!=d:
            raise bounded_g1b.BoundedG1BError("bounded_g1b_input_digest_changed")
        return raw
    calls=[]
    def git_bytes(_target,*args):
        assert args[:2]==("cat-file","blob")
        commit,relative=args[2].split(":",1)
        return before[relative] if commit==bounded_g1b.G4_ACCOUNT_HTTP_BASE["commit"] else after[relative]
    def git(_target,*args):
        if args[0]=="rev-parse":return bounded_g1b.G4_ACCOUNT_HTTP_BASE["tree"]
        assert args[:2]==("cat-file","commit")
        parent=bounded_g1b.G4_ACCOUNT_HTTP_BASE["commit"] if stage=="admit" else q["base_commit"]
        tree=q["base_tree"] if stage=="admit" else q["candidate_tree"]
        return "tree "+tree+"\nparent "+parent+"\n\nsynthetic\n"
    def attest(_target,**kwargs):calls.append(kwargs);return {"observation_sha256":"sha256:"+"0"*64}
    monkeypatch.setattr(bounded_g1b.trusted_git,"run_git_bytes",git_bytes)
    monkeypatch.setattr(bounded_g1b.trusted_git,"run_git",git)
    monkeypatch.setattr(bounded_g1b.trusted_git,"attest_target_index",attest)
    monkeypatch.setattr(bounded_g1b,"_g4_account_http_external_inputs",lambda _read,_q:({"inert":True},{"preparation_only":True}))
    monkeypatch.setattr(bounded_g1b,"_g4_account_http_current_publication",lambda _read:{"synthetic_control_flow":True})
    def run():
        return bounded_g1b._load_g4_account_http_inputs(None,target,source,evidence,
            Path("C:/synthetic-account-http-scratch"),q,read,{})
    return run,q,after,before,calls,paths,read,git


@pytest.mark.parametrize("stage,phase,mode,reason", [
    ("enable", "development", "valid", None), ("enable", "pre-push", "valid", None),
    ("enable", "post-push", "valid", None), ("admit", "development", "valid", None),
    ("enable", "development", "before", "bounded_g4_account_http_change_preimage"),
    ("enable", "development", "unowned", "bounded_g4_account_http_unowned_change"),
    ("enable", "development", "source_missing", "bounded_g4_account_http_sources"),
    ("enable", "development", "payload_extra", "bounded_g4_account_http_payload_paths"),
    ("enable", "development", "subject", "bounded_g4_account_http_independent_subject"),
    ("admit", "development", "activation", "bounded_g4_account_http_activation_acceptance"),
    ("admit", "development", "old_activation", "bounded_g4_account_http_activation_acceptance"),
    ("admit", "development", "parent", "bounded_g4_account_http_activation_parent"),
    ("admit", "development", "delta", "bounded_g4_account_http_admit_no_delta"),
    ("admit", "pre-push", "valid", "bounded_g4_account_http_admit_no_delta"),
    ("enable", "post-push", "index", "bounded_g4_account_http_committed_binding")])
def test_account_http_loader_retains_activation_source_phase_and_index_checks(monkeypatch, stage, phase, mode, reason):
    run, q, after, before, calls, paths, read, git = _account_http_loader_fixture(monkeypatch, stage, phase)
    if mode == "before": before[bounded_g1b.G4_AUDIT_CODE] = b"changed-controller"
    if mode == "unowned": before[bounded_g1b.G4_CI_WORKFLOW] = b"unowned-change"
    if mode == "source_missing": del q["source_sha256"][bounded_g1b.G4_AUDIT_CODE]
    if mode == "payload_extra": q["payload_sha256"]["app/unowned.py"] = "0" * 64
    if mode == "index": q["expected_index_tree"] = "f" * 40
    if mode == "delta": q["candidate_tree"] = "f" * 40
    if mode == "parent":
        def wrong_parent(target, *args):
            raw = git(target, *args)
            return raw.replace("parent " + bounded_g1b.G4_ACCOUNT_HTTP_BASE["commit"], "parent " + "0" * 40)
        monkeypatch.setattr(bounded_g1b.trusted_git, "run_git", wrong_parent)
    if mode in {"subject", "activation", "old_activation"}:
        # Preserve the real loader and mutate a single reviewed acceptance field.
        def changed_read(path, digest):
            raw = read(path, digest)
            if mode == "old_activation" and path.name == "independent-enable-push-effect-review-v1.json":
                return bounded_g1b.G4_ACCOUNT_HTTP_CURRENT_ACTIVATION.read_bytes()
            if path.name == ("independent-" + stage + "-" + phase + "-subject-review-v1.json") and mode == "subject":
                value = json.loads(raw); value["subject_sha256"] = "0" * 64
                return json.dumps(value).encode()
            if path.name == "independent-enable-push-effect-review-v1.json" and mode == "activation":
                value = json.loads(raw); value["implementation_authorship"] = True
                return json.dumps(value).encode()
            return raw
        def run():
            return bounded_g1b._load_g4_account_http_inputs(None, Path("C:/synthetic-account-http-target"),
                Path("C:/synthetic-account-http-source"), bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT,
                Path("C:/synthetic-account-http-scratch"), q, changed_read, {})
    if reason is not None:
        with pytest.raises(bounded_g1b.BoundedG1BError) as err: run()
        assert err.value.reason_code == reason
        if mode != "index": assert calls == []
    else:
        inputs = run()
        assert inputs.binding is q and len(q["source_sha256"]) == 8 and len(paths) == 25
        assert inputs.payloads == after
        owned = bounded_g1b.G4_ACCOUNT_HTTP_CONTROL if stage == "enable" else frozenset()
        attested = paths - owned if phase == "development" else paths
        assert calls == [{"attested_paths": tuple(sorted(attested)), "expected_head": q["expected_head"],
            "expected_index_tree": q["expected_index_tree"], "scratch_parent": Path("C:/synthetic-account-http-scratch")}]


# Schema20 additions are source-only test preparation. These exercise the exact
# selected controller predicates; synthetic Git observations below do not prove
# native admission, application behaviour or an execution authorization.
def _owner_bootstrap_scope():
    # Preserve the exact v21 fixture after the candidate scope advances to v22.
    return json.loads(_owner_staff_predecessor_control(bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE))


def _owner_bootstrap_q(stage="enable", phase="development", binding_schema=None):
    b=bounded_g1b
    schema=b.G4_OWNER_BOOTSTRAP_SCHEMA if binding_schema is None else binding_schema
    d=b._g4_owner_bootstrap_descriptor(schema)
    scope=_owner_bootstrap_scope() if d["version"]==21 else _owner_staff_scope()
    base=d["base"] if stage=="enable" else {"commit":"b"*40,"tree":"c"*40}
    candidate=base["tree"] if stage=="admit" else "a"*40
    owned=b.G4_OWNER_BOOTSTRAP_CONTROL if stage=="enable" else b.G4_OWNER_BOOTSTRAP_PRODUCT if stage=="apply" else ()
    return {"schema_version":schema,"operation_id":"owner-bootstrap-source-test",
        "operation_kind":b.G4_OWNER_BOOTSTRAP_ADMIT_KIND if stage=="admit" else
            "enable_g4_stage1_successor" if stage=="enable" else "implement_g4_stage1_successor",
        "stage":stage,"phase":phase,"base_commit":base["commit"],"base_tree":base["tree"],
        "expected_head":base["commit"] if phase=="development" else "e"*40,
        "expected_index_tree":base["tree"] if phase=="development" else candidate,
        "candidate_tree":candidate,"source_sha256":scope["source_sha256"],"payload_sha256":{},
        "repair_sha256":{p:{} for p in owned},"source_review":{},
        "activation_acceptance":None if stage=="enable" else {"path":(
            d["root"]/"entry-admission-v1/independent-enable-push-effect-review-v1.json").as_posix(),"sha256":"f"*64},
        "product_vector":scope["product_vector"],"mapping_review":scope["mapping_review"]}


def _owner_bootstrap_read(path,digest):
    raw=path.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==digest
    return raw


def test_owner_bootstrap_scope_exact_six_and_prior_schema19_dispatch():
    b=bounded_g1b;scope=_owner_bootstrap_scope()
    b.validate_g4_owner_bootstrap_scope(scope)
    for stage in ("enable","admit","apply"):
        q=_owner_bootstrap_q(stage)
        expected=b.G4_OWNER_BOOTSTRAP_CONTROL if stage=="enable" else b.G4_OWNER_BOOTSTRAP_PRODUCT if stage=="apply" else frozenset()
        assert b.operation_paths(q["operation_kind"],q)==expected
    old={"schema_version":b.G4_ACCOUNT_HTTP_SCHEMA,"stage":"admit",
        "operation_kind":b.G4_ACCOUNT_HTTP_ADMIT_KIND,"repair_sha256":{}}
    assert b.operation_paths(old["operation_kind"],old)==frozenset()
    assert b._operation(old["operation_kind"],old)["g4_account_http_external_source"] is True
    assert b.G4_ACCOUNT_HTTP_SCOPE_SCHEMA=="ariadne.g4_stage1_successor_entry_scope.v19"
    assert not b._is_g4_owner_bootstrap_binding(old)
    for schema,expected in ((b.G4_BUREAU_V9_SCHEMA,b.G4_BUREAU_V9_PRODUCT),
                            (b.G4_ACCOUNT_BOOTSTRAP_SCHEMA,b.G4_ACCOUNT_BOOTSTRAP_PRODUCT)):
        prior={"schema_version":schema,"stage":"apply","operation_kind":"implement_g4_stage1_successor",
               "repair_sha256":{p:{} for p in expected}}
        assert b.operation_paths(prior["operation_kind"],prior)==expected


@pytest.mark.parametrize("mutation",["extra","base","predecessor","review","runtime","product"])
def test_owner_bootstrap_scope_rejects_widening_or_wrong_baseline(mutation):
    b=bounded_g1b;scope=_owner_bootstrap_scope()
    if mutation=="extra":scope["allowed_paths"].append("app/unowned.py")
    if mutation=="base":scope["selected_base"]["commit"]="0"*40
    if mutation=="predecessor":scope["predecessor_scope"]["sha256"]="0"*64
    if mutation=="review":scope["mapping_review"]["sha256"]="0"*64
    if mutation=="runtime":scope["admission_grants_runtime_authority"]=True
    if mutation=="product":scope["product_sha256"]["stage1_account_http_adapter.py"]="0"*64
    with pytest.raises(b.BoundedG1BError) as err:b.validate_g4_owner_bootstrap_scope(scope)
    assert err.value.reason_code=="bounded_g4_owner_bootstrap_scope_boundary"


@pytest.mark.parametrize("mutation,reason",[(None,None),("extra","bounded_g4_owner_bootstrap_external_vector"),
    ("duplicate","bounded_g4_owner_bootstrap_external_vector"),("namespace","bounded_g4_owner_bootstrap_external_vector"),
    ("file","bounded_g4_owner_bootstrap_external_vector"),("maps","bounded_g4_owner_bootstrap_source_maps"),
    ("map_duplicate","bounded_g4_owner_bootstrap_source_maps"),("review_pin","bounded_g4_owner_bootstrap_external_pins"),
    ("review_authorship","bounded_g4_owner_bootstrap_independent_source")])
def test_owner_bootstrap_external_exact_subject_and_separate_maps(mutation,reason):
    b=bounded_g1b;q=_owner_bootstrap_q("admit")
    if mutation=="review_pin":q["mapping_review"]["sha256"]="0"*64
    def read(path,digest):
        raw=_owner_bootstrap_read(path,digest)
        # Substitute one JSON field AFTER independently checking its pinned
        # ordinary baseline, to isolate the named controller predicate.
        if path==b.G4_OWNER_BOOTSTRAP_VECTOR and mutation in {"extra","duplicate","namespace","file"}:
            value=json.loads(raw)
            if mutation=="extra":value["files"].append(copy.deepcopy(value["files"][0]))
            if mutation=="duplicate":value["files"][1]=copy.deepcopy(value["files"][0])
            if mutation=="namespace":value["files"][0]["namespace"]="SITE"
            if mutation=="file":value["files"][0]["after"]["path"]="C:/unowned.py"
            return json.dumps(value).encode()
        if path==b.G4_OWNER_BOOTSTRAP_MAPS and mutation in {"maps","map_duplicate"}:
            value=json.loads(raw)
            if mutation=="maps":value["backend_count"]=156
            else:value["site_rows"][1]=copy.deepcopy(value["site_rows"][0])
            return json.dumps(value).encode()
        if path==b.G4_OWNER_BOOTSTRAP_PREPARATION_REVIEW and mutation=="review_authorship":
            value=json.loads(raw);value["reviewer"]["implementation_authored"]=True
            return json.dumps(value).encode()
        return raw
    if reason:
        with pytest.raises(b.BoundedG1BError) as err:b._g4_owner_bootstrap_external_inputs(read,q)
        assert err.value.reason_code==reason
    else:
        vector,review=b._g4_owner_bootstrap_external_inputs(read,q)
        assert len(vector["files"])==15 and review["execution_authorized"] is False


@pytest.mark.parametrize("entrypoint,phase",[("recovery_preflight","development"),
    ("task_branch_commit","development"),("task_branch_push","pre-push"),("recovery_preflight","post-push")])
def test_owner_bootstrap_admit_entrypoint_cannot_publish_or_execute(entrypoint,phase):
    b=bounded_g1b;q=_owner_bootstrap_q("admit")
    if (entrypoint,phase)==("recovery_preflight","development"):
        b._g4_owner_bootstrap_require_entrypoint(q,entrypoint,phase)
        assert b.operation_effects(q["operation_kind"])==frozenset({"repository_read"})
        assert "admission grants no runtime" in " ".join(b.G4_OWNER_BOOTSTRAP_LIMITS)
    else:
        with pytest.raises(b.BoundedG1BError) as err:b._g4_owner_bootstrap_require_entrypoint(q,entrypoint,phase)
        assert err.value.reason_code=="bounded_g4_owner_bootstrap_admit_entrypoint"


def _owner_bootstrap_loader_fixture(monkeypatch,stage,phase,binding_schema=None):
    b=bounded_g1b;root=Path(__file__).resolve().parents[1]
    schema=b.G4_OWNER_BOOTSTRAP_SCHEMA if binding_schema is None else binding_schema
    d=b._g4_owner_bootstrap_descriptor(schema)
    target=Path("C:/synthetic-seeded-target");source=Path("C:/synthetic-seeded-source")
    paths=(b.CONFIGURATION_PATHS|{b.STATE,b.GATES,b.OVERLAY,b.AGENTS,b.G4_STAGE1_INTERACTIVE_SCOPE,
        b.G4_STAGE1_SUCCESSOR_SCOPE,b.G4_STAGE1_SUCCESSOR_TEST,b.G4_CI_WORKFLOW}|b.SOURCE_PATHS|b.CONTROLLER_PATHS)
    original={p:("accepted:"+p).encode() for p in paths}
    for p in b.G4_OWNER_BOOTSTRAP_CONTROL:original[p]=_pinned_predecessor_control(p) if d["version"]==21 else _owner_staff_predecessor_control(p)
    installed=dict(original)
    for p in b.G4_OWNER_BOOTSTRAP_CONTROL:installed[p]=(root/p).read_bytes()
    after=dict(installed)
    if stage=="apply" and d["version"]==22:
        paths|=b.G4_OWNER_BOOTSTRAP_PRODUCT
        p="stage1_account_http_adapter.py";r=d["product_rows"][p]
        after[p]=_owner_bootstrap_read(Path(r["path"]),r["sha256"])
        installed[p]=_owner_bootstrap_read(Path("C:/Users/there/EMR4-tools/local-mock-owner-practice-bootstrap-source-v1/stage1_account_http_adapter.py"),d["before_sha"][p])
    elif stage=="apply":
            paths|=b.G4_OWNER_BOOTSTRAP_PRODUCT
            for p,logical in b.G4_OWNER_BOOTSTRAP_PRODUCT_LOGICAL.items():
                row=b.G4_OWNER_BOOTSTRAP_EXTERNAL_ROWS[logical][1]
                after[p]=_owner_bootstrap_read(Path(row["path"]),row["sha256"])
            vector=json.loads(_owner_bootstrap_read(b.G4_OWNER_BOOTSTRAP_VECTOR,b.G4_OWNER_BOOTSTRAP_VECTOR_SHA))
            for p,logical in b.G4_OWNER_BOOTSTRAP_PRODUCT_LOGICAL.items():
                if d["before_sha"][p] is None:continue
                entry=next(r for r in vector["files"] if r["logical_path"]==logical)
                row=entry["accepted_input"]
                old_path=Path(row.get("source_path",row.get("path")))
                installed[p]=_owner_bootstrap_read(old_path,d["before_sha"][p])
    # Bind the deliberately synthetic ordinary controls to the actual candidate
    # controller/test bytes, without invoking the whole-policy/config loader.
    scope=_owner_bootstrap_scope() if d["version"]==21 else _owner_staff_scope()
    scope["source_sha256"]={p:hashlib.sha256(after[p]).hexdigest() for p in b.SOURCE_PATHS|b.CONTROLLER_PATHS}
    scope["control_sha256"]={p:hashlib.sha256(after[p]).hexdigest()
        for p in b.G4_OWNER_BOOTSTRAP_CONTROL-{b.G4_STAGE1_SUCCESSOR_SCOPE}}
    after[b.G4_STAGE1_SUCCESSOR_SCOPE]=b._canonical(scope)+b"\n"
    if stage!="enable":installed[b.G4_STAGE1_SUCCESSOR_SCOPE]=after[b.G4_STAGE1_SUCCESSOR_SCOPE]
    q=_owner_bootstrap_q(stage,phase,binding_schema=schema)
    q["source_sha256"]={p:hashlib.sha256(after[p]).hexdigest() for p in b.SOURCE_PATHS|b.CONTROLLER_PATHS}
    q["payload_sha256"]={p:hashlib.sha256(after[p]).hexdigest() for p in paths}
    owned=b._g4_owner_bootstrap_paths(q["operation_kind"],q)
    for p in owned:
        before=d["preimages"][p] if stage=="enable" else d["before_sha"][p]
        q["repair_sha256"][p]={"before_sha256":before,"after_sha256":q["payload_sha256"][p]}
    subject=d["root"]/"entry-admission-v1"/("independent-"+stage+"-"+phase+"-subject-review-v1.json")
    q["source_review"]={"path":subject.as_posix(),"sha256":"d"*64}
    external={Path(row["path"]):(p,d["product_sha"][p],d["product_bytes"][p])
        for p,row in d["product_rows"].items()}
    assert len(external)==1 and {row[0] for row in external.values()}==b.G4_OWNER_BOOTSTRAP_PRODUCT
    external_seen=set()
    def read(path,digest):
        if path==subject:
            return json.dumps({"schema":"emr4.g4_operation_review.v1","status":"PASS",
                "verdict":"PASS_G4_STAGE1_OWNER_BOOTSTRAP_EXACT_ADMISSION_SUBJECT","subject_sha256":b.g4_owner_bootstrap_review_subject(q),
                "independent":True,"implementation_authorship":False,"blocking_findings":[],
                "reviewer_agent":"/root/synthetic-independent-reviewer","stage":stage,"phase":phase}).encode()
        if stage!="enable" and path==Path(q["activation_acceptance"]["path"]):
            return json.dumps({"schema":"emr4.g4_operation_review.v1","status":"PASS",
                "verdict":"PASS_G4_STAGE1_OWNER_BOOTSTRAP_CONTROL_PUBLICATION_EFFECT","independent":True,
                "implementation_authorship":False,"blocking_findings":[],"reviewer_agent":"/root/synthetic-independent-reviewer",
                "stage":"enable","phase":"push","base":d["base"]["commit"],"commit":q["base_commit"],
                "candidate_tree":q["base_tree"],"control_activation_accepted":True,"same_attempt_remote_readback_verified":True,
                "protected_refs_unchanged":True,"whole_inverse_verified_same_attempt":True,"published_ref":b.G4_STAGE1_INTERACTIVE_BACKEND_REF}).encode()
        if path in external:
            relative,expected,size=external[path]
            assert (stage=="apply" or d["version"]==22) and digest==expected
            raw=after[relative] if stage=="apply" else _owner_bootstrap_read(path,digest)
            assert len(raw)==size and hashlib.sha256(raw).hexdigest()==expected
            external_seen.add(relative)
            return raw
        if d["version"]==22 and path in {Path(r["path"]) for k,r in b.G4_OWNER_STAFF_INVITATION_ROWS.items() if k!="factory"}:
            return _owner_bootstrap_read(path,digest)
        assert path.is_relative_to(target) or path.is_relative_to(source), "unbound synthetic read"
        relative=path.relative_to(target if path.is_relative_to(target) else source).as_posix()
        raw=after[relative]
        assert hashlib.sha256(raw).hexdigest()==digest
        return raw
    read.external_seen=external_seen
    def git_bytes(_target,*args):
        if args[0]=="ls-tree":return b"tracked" if args[-1] in (original if stage=="enable" else installed) else b""
        assert args[:2]==("cat-file","blob")
        commit,p=args[2].split(":",1)
        return (original if commit==d["base"]["commit"] else installed)[p]
    def git(_target,*args):
        if args[0]=="rev-parse":return d["base"]["tree"]
        parent=d["base"]["commit"] if args[2]==q["base_commit"] and stage!="enable" else q["base_commit"]
        tree=q["base_tree"] if args[2]==q["base_commit"] and stage!="enable" else q["candidate_tree"]
        return "tree "+tree+"\nparent "+parent+"\n\nsynthetic\n"
    observations=[]
    monkeypatch.setattr(b.trusted_git,"run_git_bytes",git_bytes)
    monkeypatch.setattr(b.trusted_git,"run_git",git)
    monkeypatch.setattr(b.trusted_git,"attest_target_index",lambda *a,**k:observations.append(k) or {"observation_sha256":"sha256:"+"0"*64})
    if d["version"]==21:
        monkeypatch.setattr(b,"_g4_owner_bootstrap_external_inputs",lambda *a:({"synthetic_source_join":True},{}))
    def run(reader=read):return b._load_g4_owner_bootstrap_inputs(None,target,source,b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT,
        Path("C:/synthetic-seeded-scratch"),q,reader,{})
    return run,q,read,observations


@pytest.mark.parametrize("stage,phase",[("enable","development"),("enable","pre-push"),
    ("admit","development"),("apply","development"),("apply","pre-push"),("apply","post-push")])
def test_owner_bootstrap_loader_exact_stages_reach_selected_index_predicate(monkeypatch,stage,phase):
    run,q,read,observations=_owner_bootstrap_loader_fixture(monkeypatch,stage,phase)
    result=run()
    assert result.binding is q and len(observations)==1
    assert read.external_seen==(bounded_g1b.G4_OWNER_BOOTSTRAP_PRODUCT if stage=="apply" else set())
    assert set(q["repair_sha256"])==(bounded_g1b.G4_OWNER_BOOTSTRAP_CONTROL if stage=="enable" else
        bounded_g1b.G4_OWNER_BOOTSTRAP_PRODUCT if stage=="apply" else set())
    assert bounded_g1b._operation(q["operation_kind"],q)["g4_owner_bootstrap_source"] is True


@pytest.mark.parametrize("phase,delta",[("development",True),("pre-push",False)])
def test_owner_bootstrap_admit_loader_rejects_delta_and_publication_phase(monkeypatch,phase,delta):
    b=bounded_g1b;run,q,read,observations=_owner_bootstrap_loader_fixture(monkeypatch,"admit",phase)
    if delta:q["candidate_tree"]="a"*40
    with pytest.raises(b.BoundedG1BError) as err:run()
    assert err.value.reason_code=="bounded_g4_owner_bootstrap_admit_no_delta" and observations==[]


def test_owner_bootstrap_admit_report_has_no_runtime_authority(monkeypatch):
    b=bounded_g1b;q=_owner_bootstrap_q("admit")
    inputs=b.BoundedG1BInputs(q,{},{},{},{"observation_sha256":"sha256:"+"0"*64})
    context=b.BoundedG1BContext(target_root=Path("C:/synthetic-seeded-target"),
        source_root=Path("C:/synthetic-seeded-source"),evidence_root=b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT,
        binding_path=Path("C:/synthetic-seeded-binding.json"),expected_binding_sha256="0"*64,
        scratch_root=Path("C:/synthetic-seeded-scratch"))
    monkeypatch.setattr(b,"load_bounded_g1b_inputs",lambda context:inputs)
    monkeypatch.setattr(b,"_validate_g4_owner_bootstrap_loaded_policy",lambda inputs:({},None))
    manifest=b.build_bounded_g1b_manifest(context)
    report=b.bounded_g1b_report(context=context,manifest=manifest,entrypoint="recovery_preflight",phase="development")
    assert manifest["allowed_paths"]==[] and manifest["intended_side_effect_classes"]==["repository_read"]
    assert report["policy_eligible"] is True and report["execution_authorized"] is False
    assert report["feature_work_eligible"] is False


@pytest.mark.parametrize("mode,reason",[("extra","bounded_g4_owner_bootstrap_changed_paths"),
    ("preimage","bounded_g4_owner_bootstrap_change_preimage"),("activation","bounded_g4_owner_bootstrap_activation_acceptance"),
    ("subject","bounded_g4_owner_bootstrap_independent_subject"),("stage_review","bounded_g4_owner_bootstrap_independent_subject")])
def test_owner_bootstrap_apply_cannot_reuse_admit_or_wrong_product_acceptance(monkeypatch,mode,reason):
    b=bounded_g1b;run,q,read,observations=_owner_bootstrap_loader_fixture(monkeypatch,"apply","development")
    if mode=="extra":q["repair_sha256"]["backend_child_text_v1.py"]={}
    if mode=="preimage":q["repair_sha256"]["stage1_account_http_adapter.py"]["before_sha256"]=None
    def changed(path,digest):
        raw=read(path,digest)
        if path.name=="independent-enable-push-effect-review-v1.json" and mode=="activation":
            value=json.loads(raw);value["control_activation_accepted"]=False;return json.dumps(value).encode()
        if path.name=="independent-apply-development-subject-review-v1.json" and mode in {"subject","stage_review"}:
            value=json.loads(raw)
            if mode=="subject":value["subject_sha256"]="0"*64
            else:value["stage"]="admit"
            return json.dumps(value).encode()
        return raw
    with pytest.raises(b.BoundedG1BError) as err:run(changed)
    assert err.value.reason_code==reason and observations==[]



@pytest.mark.parametrize("mutation,reason", [
    ("factory", "bounded_g4_owner_bootstrap_external_vector"),
    ("unchanged_row", "bounded_g4_owner_bootstrap_external_vector"),
    ("unchanged_map", "bounded_g4_owner_bootstrap_source_maps"),
    ("reused_review", "bounded_g4_owner_bootstrap_independent_source"),
])
def test_owner_bootstrap_rejects_changed_pins_and_prior_join_review(mutation, reason):
    b = bounded_g1b
    q = _owner_bootstrap_q("admit")
    def read(path, digest):
        raw = _owner_bootstrap_read(path, digest)
        if path == b.G4_OWNER_BOOTSTRAP_VECTOR and mutation in {"factory", "unchanged_row"}:
            value = json.loads(raw)
            logical = "backend/stage1_account_http_adapter.py" if mutation == "factory" else "stage1_demo_http.py"
            row = next(row for row in value["files"] if row["logical_path"] == logical)
            row["after"]["sha256"] = "0" * 64
            return json.dumps(value).encode()
        if path == b.G4_OWNER_BOOTSTRAP_MAPS and mutation == "unchanged_map":
            value = json.loads(raw)
            # Map digest is verified by the real reader; synthetic substitution
            # changes a row count so the structural predicate rejects it.
            value["site_rows"].pop()
            return json.dumps(value).encode()
        if path == b.G4_OWNER_BOOTSTRAP_PREPARATION_REVIEW and mutation == "reused_review":
            value = json.loads(raw)
            value["schema"] = "emr4.seeded_login_coherent_integration_independent_source_review.v1"
            return json.dumps(value).encode()
        return raw
    with pytest.raises(b.BoundedG1BError) as err:
        b._g4_owner_bootstrap_external_inputs(read, q)
    assert err.value.reason_code == reason


def test_owner_bootstrap_rejects_consumed_prior_subject_path():
    b = bounded_g1b
    row = {"path": (b.G4_SEEDED_LOGIN_ROOT / "entry-admission-v1" /
                    "independent-admit-development-subject-review-v1.json").as_posix(),
           "sha256": "0" * 64}
    with pytest.raises(b.BoundedG1BError) as err:
        b._g4_owner_bootstrap_subject_review(lambda *_: b"", row,
            b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT, "0" * 64, "admit", "development")
    assert err.value.reason_code == "bounded_g4_owner_bootstrap_review_path"


def test_owner_bootstrap_scope_excludes_runtime_and_provider_effects():
    b = bounded_g1b
    scope = _owner_bootstrap_scope()
    assert scope["admission_grants_runtime_authority"] is False
    assert scope["runtime_binding_required"] is True
    assert {"provider_invocation", "real_data_access", "public_listener", "deployment",
            "protected_ref_movement"}.issubset(scope["excluded_effects"])
    scope["allowed_effects"].append("provider_invocation")
    with pytest.raises(b.BoundedG1BError) as err:
        b.validate_g4_owner_bootstrap_scope(scope)
    assert err.value.reason_code == "bounded_g4_owner_bootstrap_scope_boundary"


# V22 source-only tests. Real selected file/hash reads are separated from
# deliberately synthetic Git/index/review frames; neither is live admission.
def _owner_staff_scope():
    # Keep schema22 tests on their actual accepted fixture after scope advances.
    path=Path("C:/Users/there/EMR4-tools/owner-staff-invitation-apply01-source")/bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE
    raw=path.read_bytes()
    assert hashlib.sha256(raw).hexdigest()=="ae103d71b20acb2233a7b3958ab08c57c4ea30d0b03a3ae48e930d4bc77b4edd"
    return json.loads(raw)


def _owner_staff_predecessor_control(path):
    root=Path("C:/Users/there/EMR4-tools/owner-bootstrap-apply01-source")
    raw=(root/path).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==bounded_g1b.G4_OWNER_STAFF_INVITATION_PREIMAGES[path]
    return raw


@pytest.mark.parametrize("schema", ["legacy", "invitation"])
@pytest.mark.parametrize("stage", ["enable", "admit", "apply"])
def test_owner_staff_closed_family_dispatch_preserves_legacy(schema,stage):
    b=bounded_g1b
    version=b.G4_OWNER_BOOTSTRAP_SCHEMA if schema=="legacy" else b.G4_OWNER_STAFF_INVITATION_SCHEMA
    q=_owner_bootstrap_q(stage,binding_schema=version)
    expected=b.G4_ACCOUNT_HTTP_CONTROL if stage=="enable" else b.G4_OWNER_BOOTSTRAP_PRODUCT if stage=="apply" else frozenset()
    assert b.operation_paths(q["operation_kind"],q)==expected
    operation=b._operation(q["operation_kind"],q)
    assert operation["profile"]==b.raisa_policy.G4_STAGE1_SUCCESSOR_PROFILE
    assert operation["g4_owner_bootstrap_source"] is True
    assert "admission grants no runtime" in " ".join(operation["limits"])
    assert b.G4_OWNER_BOOTSTRAP_SCHEMA=="ariadne.g4_stage1_owner_bootstrap_operation_binding.v1"
    assert b.G4_OWNER_BOOTSTRAP_SCOPE_SCHEMA=="ariadne.g4_stage1_successor_entry_scope.v21"
    assert b.G4_OWNER_BOOTSTRAP_PRODUCT_SHA["stage1_account_http_adapter.py"]=="03a22a0ef86eda1303fc1c9d43e3e4e2e79036a33e364dd35d62d4f3526d6a45"
    if stage=="admit":assert b.operation_effects(q["operation_kind"])==frozenset({"repository_read"})


@pytest.mark.parametrize("mode", ["unknown", "cross_kind", "cross_vector", "cross_scope"])
def test_owner_staff_schema_kind_and_subject_never_fall_back(mode):
    b=bounded_g1b;q=_owner_bootstrap_q("admit",binding_schema=b.G4_OWNER_STAFF_INVITATION_SCHEMA)
    if mode=="unknown":q["schema_version"]="ariadne.g4_stage1_owner_bootstrap_operation_binding.v999"
    if mode=="cross_kind":q["operation_kind"]=b.G4_SEEDED_LOGIN_ADMIT_KIND
    if mode in {"unknown","cross_kind"}:
        with pytest.raises(b.BoundedG1BError) as err:b.operation_paths(q["operation_kind"],q)
        assert err.value.reason_code=="bounded_g4_owner_bootstrap_binding_kind"
    elif mode=="cross_vector":
        q["product_vector"]={"path":b.G4_OWNER_BOOTSTRAP_VECTOR.as_posix(),"sha256":b.G4_OWNER_BOOTSTRAP_VECTOR_SHA}
        with pytest.raises(b.BoundedG1BError) as err:b._g4_owner_bootstrap_external_inputs(_owner_bootstrap_read,q)
        assert err.value.reason_code=="bounded_g4_owner_bootstrap_external_pins"
    else:
        scope=_owner_staff_scope();scope["schema_version"]=b.G4_OWNER_BOOTSTRAP_SCOPE_SCHEMA
        with pytest.raises(b.BoundedG1BError) as err:b.validate_g4_owner_bootstrap_scope(scope)
        assert err.value.reason_code=="bounded_g4_owner_bootstrap_scope_boundary"


@pytest.mark.parametrize("mutation", [None,"factory","vector","review","base","predecessor","runtime","unowned","source_control","provider"])
def test_owner_staff_scope_exact_or_refuses_named_widening(mutation):
    b=bounded_g1b;s=_owner_staff_scope()
    if mutation=="factory":s["product_sha256"]["stage1_account_http_adapter.py"]="0"*64
    if mutation=="vector":s["product_vector"]["sha256"]="0"*64
    if mutation=="review":s["mapping_review"]["sha256"]="0"*64
    if mutation=="base":s["selected_base"]["commit"]="0"*40
    if mutation=="predecessor":s["predecessor_scope"]["sha256"]="0"*64
    if mutation=="runtime":s["admission_grants_runtime_authority"]=True
    if mutation=="unowned":s["allowed_paths"].append("app/unowned.py")
    if mutation=="source_control":s["control_sha256"][b.G4_AUDIT_CODE]="0"*64
    if mutation=="provider":s["allowed_effects"].append("provider_invocation")
    if mutation:
        with pytest.raises(b.BoundedG1BError) as err:b.validate_g4_owner_bootstrap_scope(s)
        assert err.value.reason_code==("bounded_g4_owner_bootstrap_source_vector" if mutation=="source_control" else "bounded_g4_owner_bootstrap_scope_boundary")
    else:
        assert b.validate_g4_owner_bootstrap_scope(s)==s["source_sha256"]
        assert s["allowed_paths"]==["stage1_account_http_adapter.py"]
        assert s["runtime_binding_required"] is True and s["admission_grants_runtime_authority"] is False


@pytest.mark.parametrize("mutation,reason", [(None,None),
    ("factory","bounded_g4_owner_bootstrap_external_vector"),
    ("test","bounded_g4_owner_bootstrap_external_vector"),
    ("bytes","bounded_g4_owner_bootstrap_external_source"),
    ("base","bounded_g4_owner_bootstrap_independent_source"),
    ("preimage","bounded_g4_owner_bootstrap_independent_source"),
    ("review_source","bounded_g4_owner_bootstrap_independent_source"),
    ("author","bounded_g4_owner_bootstrap_independent_source"),
    ("root","bounded_g4_owner_bootstrap_independent_source"),
    ("authorship","bounded_g4_owner_bootstrap_independent_source"),
    ("runtime","bounded_g4_owner_bootstrap_independent_source")])
def test_owner_staff_minimum_four_external_pins_and_actual_acceptance(mutation,reason):
    b=bounded_g1b;q=_owner_bootstrap_q("admit",binding_schema=b.G4_OWNER_STAFF_INVITATION_SCHEMA)
    rows=b.G4_OWNER_STAFF_INVITATION_ROWS;seen=[]
    def read(path,digest):
        raw=_owner_bootstrap_read(path,digest);seen.append(path)
        if mutation=="bytes" and path==Path(rows["factory"]["path"]):return raw+b"\n"
        value=None
        if path==Path(rows["vector"]["path"]) and mutation in {"factory","test"}:
            value=json.loads(raw);value["factory" if mutation=="factory" else "tests"]["sha256"]="0"*64
        if path==Path(rows["review"]["path"]) and mutation in {"base","preimage","review_source","author","root","authorship","runtime"}:
            value=json.loads(raw)
            if mutation=="base":value["current_product_base"]["commit"]="0"*40
            if mutation=="preimage":value["current_product_base"]["factory_sha256"]="0"*64
            if mutation=="review_source":value["source_accepted"]=False
            if mutation=="author":value["reviewer_agent"]="/root/owner_signup_guard_successor_sol"
            if mutation=="root":value["reviewer_agent"]="/root"
            if mutation=="authorship":value["implementation_authorship"]=True
            if mutation=="runtime":value["runtime_admitted"]=True
        if value is not None:
            # Deliberately substitute after real baseline pin verification, keep
            # byte count to isolate semantic predicate rather than size failure.
            changed=json.dumps(value,separators=(",",":")).encode()
            assert len(changed)<=len(raw)
            return changed+b" "*(len(raw)-len(changed))
        return raw
    if reason:
        with pytest.raises(b.BoundedG1BError) as err:b._g4_owner_bootstrap_external_inputs(read,q)
        assert err.value.reason_code==reason
    else:
        vector,review=b._g4_owner_bootstrap_external_inputs(read,q)
        assert vector["factory"]==rows["factory"] and review["source_accepted"] is True
        assert set(seen)=={Path(r["path"]) for r in rows.values()} and len(seen)==4


@pytest.mark.parametrize("stage,phase", [("enable","development"),("enable","pre-push"),
    ("admit","development"),("apply","development"),("apply","pre-push"),("apply","post-push")])
def test_owner_staff_full_loader_preserves_existing_stage_boundaries(monkeypatch,stage,phase):
    b=bounded_g1b
    run,q,read,observations=_owner_bootstrap_loader_fixture(monkeypatch,stage,phase,b.G4_OWNER_STAFF_INVITATION_SCHEMA)
    loaded=run()
    assert loaded.binding is q and len(observations)==1
    assert loaded.evidence["mapping"]["source_accepted"] is True
    assert read.external_seen==b.G4_OWNER_BOOTSTRAP_PRODUCT
    assert set(q["repair_sha256"])==(b.G4_ACCOUNT_HTTP_CONTROL if stage=="enable" else b.G4_OWNER_BOOTSTRAP_PRODUCT if stage=="apply" else set())


@pytest.mark.parametrize("mode,reason", [
    ("enable_base","bounded_g4_owner_bootstrap_enable_base"),
    ("preimage","bounded_g4_owner_bootstrap_change_preimage"),
    ("parent","bounded_g4_owner_bootstrap_activation_parent"),
    ("author","bounded_g4_owner_bootstrap_activation_acceptance"),
    ("protected","bounded_g4_owner_bootstrap_activation_acceptance"),
    ("control_acceptance","bounded_g4_owner_bootstrap_activation_acceptance"),
    ("unowned","bounded_g4_owner_bootstrap_unowned_change"),
    ("subject_author","bounded_g4_owner_bootstrap_independent_subject")])
def test_owner_staff_loader_rejects_base_preimage_publication_and_unowned_drift(monkeypatch,mode,reason):
    b=bounded_g1b;stage="enable" if mode=="enable_base" else "apply"
    run,q,read,observations=_owner_bootstrap_loader_fixture(monkeypatch,stage,"development",b.G4_OWNER_STAFF_INVITATION_SCHEMA)
    if mode=="enable_base":q["base_commit"]="0"*40
    if mode=="preimage":q["repair_sha256"]["stage1_account_http_adapter.py"]["before_sha256"]="0"*64
    original_git=b.trusted_git.run_git;original_bytes=b.trusted_git.run_git_bytes
    if mode=="parent":
        def git(target,*args):
            value=original_git(target,*args)
            return value.replace("parent "+b.G4_OWNER_STAFF_INVITATION_BASE["commit"],"parent "+"0"*40) if args[:2]==("cat-file","commit") else value
        monkeypatch.setattr(b.trusted_git,"run_git",git)
    if mode=="unowned":
        def git_bytes(target,*args):
            raw=original_bytes(target,*args)
            return raw+b"unowned" if args[:2]==("cat-file","blob") and args[2]==q["base_commit"]+":"+b.AGENTS else raw
        monkeypatch.setattr(b.trusted_git,"run_git_bytes",git_bytes)
    def changed(path,digest):
        raw=read(path,digest)
        if path.name=="independent-enable-push-effect-review-v1.json" and mode in {"author","protected","control_acceptance"}:
            v=json.loads(raw)
            if mode=="author":v["reviewer_agent"]="/root/owner_signup_guard_successor_sol"
            if mode=="protected":v["protected_refs_unchanged"]=False
            if mode=="control_acceptance":v["control_activation_accepted"]=False
            return json.dumps(v).encode()
        if path.name=="independent-apply-development-subject-review-v1.json" and mode=="subject_author":
            v=json.loads(raw);v["reviewer_agent"]="/root/owner_signup_guard_successor_sol";return json.dumps(v).encode()
        return raw
    with pytest.raises(b.BoundedG1BError) as err:run(changed)
    assert err.value.reason_code==reason and observations==[]


@pytest.mark.parametrize("mode", ["delta","phase"])
def test_owner_staff_admit_zero_delta_before_any_index_observation(monkeypatch,mode):
    b=bounded_g1b
    run,q,read,observations=_owner_bootstrap_loader_fixture(monkeypatch,"admit","development",b.G4_OWNER_STAFF_INVITATION_SCHEMA)
    if mode=="delta":q["candidate_tree"]="a"*40
    else:q["phase"]="pre-push"
    with pytest.raises(b.BoundedG1BError) as err:run()
    assert err.value.reason_code=="bounded_g4_owner_bootstrap_admit_no_delta" and observations==[]


@pytest.mark.parametrize("entrypoint,phase", [("recovery_preflight","development"),
    ("task_branch_commit","development"),("task_branch_push","pre-push"),("recovery_preflight","post-push")])
def test_owner_staff_admit_requires_preflight_only(entrypoint,phase):
    b=bounded_g1b;q=_owner_bootstrap_q("admit",binding_schema=b.G4_OWNER_STAFF_INVITATION_SCHEMA)
    if (entrypoint,phase)==("recovery_preflight","development"):
        b._g4_owner_bootstrap_require_entrypoint(q,entrypoint,phase)
    else:
        with pytest.raises(b.BoundedG1BError) as err:b._g4_owner_bootstrap_require_entrypoint(q,entrypoint,phase)
        assert err.value.reason_code=="bounded_g4_owner_bootstrap_admit_entrypoint"


# Point admission tests are source preparation only, separate from point product
# tests. Substituted reads below isolate authority predicates; they are not an
# opaque-index/native-publication or application execution proof.
_POINT_ADMISSION_CANDIDATE = Path("C:/Users/there/EMR4-tools/bureau-point-move-config-coherence-source-v2/candidate")

_POINT_COHERENCE_REAL_ROOT = Path('C:/Users/there/EMR4-tools/point-move-enable01-source')
_POINT_COHERENCE_REAL_ROWS = {'orchestration/programme/current-state.json': {'bytes': 47962, 'sha256': 'f32ea528d9efab7e45df9d4ce4770dc9094483641d332ebee052ec436634388b'}, 'orchestration/harness_settings/autonomous_continuation.yaml': {'bytes': 8277, 'sha256': '0a205c109383ed64c6c87435b259bbdd5a1989f834de6f505385bbf6c52bbd0d'}, 'orchestration/harness_settings/cost_controls.yaml': {'bytes': 1274, 'sha256': '9ed7844a22dfafa33c064cb1c26ca62779cc08f2195b93c3c7f436417cb0473f'}, 'orchestration/harness_settings/deepseek_cost_calibration.yaml': {'bytes': 1449, 'sha256': 'd84c35cb0aeea0e5a47f91845b6c5775b1af1ff489ba777a3ce33ea1c386f307'}, 'orchestration/harness_settings/direction_collaboration.yaml': {'bytes': 1450, 'sha256': 'd54f0e6719b42b3cb641406cd35d138437726f344a6d22636226a119353e6bf9'}, 'orchestration/harness_settings/evidence_led_workflow.yaml': {'bytes': 3931, 'sha256': '1e07de52436019029751bdc82547693a9cc2ed5182e856b3b7b96c9f5cfded8b'}, 'orchestration/harness_settings/operating_model.yaml': {'bytes': 7190, 'sha256': '0181a3b007f800cc7b610d8f16a9ac551daf7345da15232e464f40dda1e3ca6f'}, 'orchestration/harness_settings/programme_recovery.yaml': {'bytes': 78022, 'sha256': '46491d0e87ad8c5570b5feffac764cfb68a2fd25b1881891d3454fad17959112'}, 'orchestration/harness_settings/project.yaml': {'bytes': 1469, 'sha256': 'a3835edf35116088ef1808e2590c0b7ab837171ab40457b51f96f8519a235f84'}, 'orchestration/harness_settings/security_review_protocol.yaml': {'bytes': 2848, 'sha256': '861e5f577b98e8e3928333d28b8fade24d7e214f0cd666961f665fbce153dc70'}, 'orchestration/harness_settings/verifier_execution_policy.yaml': {'bytes': 6315, 'sha256': '92721606167a0bcb6b65d40e62061d9aaba25b2e57e72d9a2ee0445d51d5258d'}, 'AGENTS.md': {'bytes': 33600, 'sha256': 'f2c078d3877ac8a7659a614a049021df6d211d7a61934be927268f56b4b36a62'}, 'orchestration/programme/gates.yaml': {'bytes': 21258, 'sha256': '16206eaa4ee6af4785d9c2bff9e68c9e277da88eda714fc85b5227394d03228d'}}


def _point_scope():
    return json.loads((_POINT_ADMISSION_CANDIDATE / bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE).read_bytes())


def _point_q(stage="enable"):
    b=bounded_g1b;scope=_point_scope()
    owned=b.G4_POINT_MOVE_CONTROL if stage=="enable" else frozenset(b.G4_POINT_MOVE_PRODUCT_SHA) if stage=="apply" else frozenset()
    return {"schema_version":b.G4_POINT_MOVE_FIVE_SCHEMA,"operation_id":"point-source-test",
        "operation_kind":b.G4_OWNER_BOOTSTRAP_ADMIT_KIND if stage=="admit" else
            "enable_g4_stage1_successor" if stage=="enable" else "implement_g4_stage1_successor",
        "stage":stage,"phase":"development","base_commit":b.G4_POINT_MOVE_BASE["commit"],
        "base_tree":b.G4_POINT_MOVE_BASE["tree"],"expected_head":b.G4_POINT_MOVE_BASE["commit"],
        "expected_index_tree":b.G4_POINT_MOVE_BASE["tree"],"candidate_tree":b.G4_POINT_MOVE_BASE["tree"],
        "source_sha256":scope["source_sha256"],"payload_sha256":{},
        "repair_sha256":{p:{} for p in owned},"source_review":{},"activation_acceptance":None,
        "product_vector":scope["product_vector"],"mapping_review":scope["mapping_review"]}


def test_point_descriptor_exact_paths_and_old_version_populations_remain_closed():
    b=bounded_g1b
    expected={"scripts/reception_one_bureau_typed_plan_protocol.py",
        "orchestration/continuity/reception-one-bureau-typed-plan-protocol/plan-draft.schema.json",
        "orchestration/continuity/reception-one-bureau-typed-plan-protocol/operator-catalog.json",
        "orchestration/continuity/reception-one-bureau-typed-plan-protocol/execution-result.schema.json",
        "tests/test_reception_one_bureau_model_first_contract.py",
        "app/services/reception_one_proposal_runtime.py","app/routers/appointments.py",
        "tests/test_reception_one_point_move_bridge_contract.py",
        "orchestration/continuity/reception-one-bureau-typed-plan-protocol/operator-catalog.schema.json"}
    assert set(b.G4_POINT_MOVE_PRODUCT_SHA)==expected
    assert b.G4_POINT_MOVE_BEFORE_SHA["tests/test_reception_one_bureau_model_first_contract.py"] is None
    assert b.G4_POINT_MOVE_BEFORE_SHA["tests/test_reception_one_point_move_bridge_contract.py"] is None
    assert expected.issubset(raisa_policy.G4_STAGE1_SUCCESSOR_PRODUCT_PATHS)
    for schema in (b.G4_OWNER_BOOTSTRAP_SCHEMA,b.G4_OWNER_STAFF_INVITATION_SCHEMA):
        assert set(b._g4_owner_bootstrap_descriptor(schema)["product_sha"])=={"stage1_account_http_adapter.py"}
    assert b._g4_owner_bootstrap_paths("enable_g4_stage1_successor",_point_q())==b.G4_POINT_MOVE_CONTROL
    assert b._g4_owner_bootstrap_paths("implement_g4_stage1_successor",_point_q("apply"))==expected
    assert b._g4_owner_bootstrap_paths(b.G4_OWNER_BOOTSTRAP_ADMIT_KIND,_point_q("admit"))==set()
    q=_point_q();q["schema_version"]="ariadne.g4_stage1_owner_bootstrap_operation_binding.v99"
    with pytest.raises(b.BoundedG1BError):b._g4_owner_bootstrap_paths(q["operation_kind"],q)
    q=_point_q("apply");q["repair_sha256"]["stage1_account_http_adapter.py"]={}
    with pytest.raises(b.BoundedG1BError):b._g4_owner_bootstrap_paths(q["operation_kind"],q)


@pytest.mark.parametrize("field,value",[("runtime_binding_required",False),
    ("admission_grants_runtime_authority",True),("voice_activation",True),
    ("allowed_task_kind","feature_implementation"),("selected_base",{"commit":"0"*40,"tree":"0"*40}),
    ("allowed_paths",["stage1_account_http_adapter.py"])])
def test_point_scope_keeps_gate_task_runtime_base_and_population_closed(field,value):
    b=bounded_g1b;scope=_point_scope();assert b.validate_g4_owner_bootstrap_scope(scope)==scope["source_sha256"]
    scope[field]=value
    with pytest.raises(b.BoundedG1BError):b.validate_g4_owner_bootstrap_scope(scope)


@pytest.mark.parametrize("mutation,reason",[(None,None),("lineage","bounded_g4_point_move_external_vector"),
    ("rows","bounded_g4_point_move_original_vector"),("authorship","bounded_g4_point_move_independent_source"),
    ("runtime","bounded_g4_point_move_independent_source"),("bytes","bounded_g4_point_move_external_source")])
def test_point_external_authority_joins_reject_substituted_lineage_and_acceptance(mutation,reason):
    b=bounded_g1b;q=_point_q();seen=[]
    def read(path,digest):
        raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==digest;seen.append(path)
        value=json.loads(raw) if path.suffix==".json" else None
        if path==Path(b.G4_POINT_MOVE_VECTOR["path"]) and mutation=="lineage":value["published_base"]["commit"]="0"*40
        elif path.name=="source-vector.json" and mutation=="rows":value["rows"][0]["before_sha256"]="0"*64
        elif path==Path(b.G4_POINT_MOVE_MAPPING["path"]) and mutation in {"authorship","runtime"}:
            value["independent_of_implementation" if mutation=="authorship" else "runtime_accepted"] = mutation=="runtime"
        elif mutation=="bytes" and path==Path(b.G4_POINT_MOVE_PRODUCT_ROWS["app/routers/appointments.py"]["path"]):return raw+b"changed"
        else:return raw
        return json.dumps(value).encode()
    if reason:
        with pytest.raises(b.BoundedG1BError) as err:b._g4_owner_bootstrap_external_inputs(read,q)
        assert err.value.reason_code==reason
    else:
        vector,review=b._g4_owner_bootstrap_external_inputs(read,q)
        assert len(vector["rows"])==9 and review["source_candidate_accepted"] is True
        assert len(seen)==12


@pytest.mark.parametrize("entrypoint,phase",[("task_branch_commit","development"),
    ("task_branch_push","pre-push"),("recovery_preflight","post-push")])
def test_point_admit_retains_preflight_development_only(entrypoint,phase):
    b=bounded_g1b;q=_point_q("admit")
    b._g4_owner_bootstrap_require_entrypoint(q,"recovery_preflight","development")
    with pytest.raises(b.BoundedG1BError) as err:b._g4_owner_bootstrap_require_entrypoint(q,entrypoint,phase)
    assert err.value.reason_code=="bounded_g4_owner_bootstrap_admit_entrypoint"


def test_point_subject_covers_plan_sources_population_and_phase():
    b=bounded_g1b;q=_point_q();original=b.g4_owner_bootstrap_review_subject(q)
    for field,value in [("phase","pre-push"),("candidate_tree","a"*40),
        ("mapping_review",{"path":"other","sha256":"0"*64}),
        ("source_sha256",{}),("repair_sha256",{})]:
        changed=copy.deepcopy(q);changed[field]=value
        assert b.g4_owner_bootstrap_review_subject(changed)!=original


# Revised nine-path full-loader fixture. All Git/index and phase-review effects
# are explicit inert substitutes. Passing these tests would establish only the
# actual loader's predicates over this substituted state, never native Git,
# controller publication, a lease or point/backend runtime acceptance.
def _point_loader_fixture(monkeypatch, stage="enable", phase="development"):
    b=bounded_g1b;d=b._g4_owner_bootstrap_descriptor(b.G4_POINT_MOVE_FIVE_SCHEMA)
    target=Path("C:/synthetic-point-target");source=Path("C:/synthetic-point-source")
    paths=(b.CONFIGURATION_PATHS|{b.STATE,b.GATES,b.OVERLAY,b.AGENTS,b.G4_STAGE1_INTERACTIVE_SCOPE,
        b.G4_STAGE1_SUCCESSOR_SCOPE,b.G4_STAGE1_SUCCESSOR_TEST,b.G4_CI_WORKFLOW}|b.SOURCE_PATHS|b.CONTROLLER_PATHS)
    original={p:("accepted:"+p).encode() for p in paths}
    predecessor=Path("C:/Users/there/EMR4-tools/owner-staff-invitation-apply01-source")
    for p in d["control"]:
        raw=(predecessor/p).read_bytes();assert hashlib.sha256(raw).hexdigest()==d["preimages"][p]
        original[p]=raw
    installed=dict(original);after=dict(original)
    for p in d["control"]:after[p]=(_POINT_ADMISSION_CANDIDATE/p).read_bytes()
    if stage!="enable":
        for p in d["control"]:installed[p]=after[p]
    vector=json.loads(Path(d["vector"]["path"]).read_bytes())
    if stage=="apply":
        paths|=frozenset(d["product_sha"])
        for row in vector["rows"]:
            p=row["relative_path"];before=row["published_before"]
            if not before["absent"]:
                raw=Path(before["path"]).read_bytes();assert hashlib.sha256(raw).hexdigest()==d["before_sha"][p]
                installed[p]=raw
            after[p]=Path(row["after"]["path"]).read_bytes()
    scope=_point_scope()
    scope["source_sha256"]={p:hashlib.sha256(after[p]).hexdigest() for p in b.SOURCE_PATHS|b.CONTROLLER_PATHS}
    scope["control_sha256"]={p:hashlib.sha256(after[p]).hexdigest() for p in d["control"]-{b.G4_STAGE1_SUCCESSOR_SCOPE}}
    after[b.G4_STAGE1_SUCCESSOR_SCOPE]=b._canonical(scope)+b"\n"
    if stage!="enable":installed[b.G4_STAGE1_SUCCESSOR_SCOPE]=after[b.G4_STAGE1_SUCCESSOR_SCOPE]
    q=_point_q(stage);q["phase"]=phase
    if stage!="enable":q.update(base_commit="b"*40,base_tree="c"*40)
    q["candidate_tree"]=q["base_tree"] if stage=="admit" else "a"*40
    q["expected_head"]=q["base_commit"] if phase=="development" else "e"*40
    q["expected_index_tree"]=q["base_tree"] if phase=="development" else q["candidate_tree"]
    q["source_sha256"]=scope["source_sha256"]
    q["payload_sha256"]={p:hashlib.sha256(after[p]).hexdigest() for p in paths}
    owned=b._g4_owner_bootstrap_paths(q["operation_kind"],q)
    q["repair_sha256"]={p:{"before_sha256":d["preimages"][p] if stage=="enable" else d["before_sha"][p],
        "after_sha256":q["payload_sha256"][p]} for p in owned}
    subject=d["root"]/"entry-admission-v1"/("independent-"+stage+"-"+phase+"-subject-review-v1.json")
    q["source_review"]={"path":subject.as_posix(),"sha256":"d"*64}
    if stage!="enable":q["activation_acceptance"]={"path":(d["root"]/
        "entry-admission-v1/independent-enable-push-effect-review-v1.json").as_posix(),"sha256":"f"*64}
    external={Path(r["path"]):p for p,r in d["product_rows"].items()}
    seen=set()
    def read(path,digest):
        if path==subject:
            return json.dumps({"schema":"emr4.g4_operation_review.v1","status":"PASS",
                "verdict":"PASS_G4_STAGE1_OWNER_BOOTSTRAP_EXACT_ADMISSION_SUBJECT",
                "subject_sha256":b.g4_owner_bootstrap_review_subject(q),"independent":True,
                "implementation_authorship":False,"blocking_findings":[],
                "reviewer_agent":"/root/synthetic-independent-point-reviewer","stage":stage,"phase":phase}).encode()
        if stage!="enable" and q["activation_acceptance"] is not None and path==Path(q["activation_acceptance"]["path"]):
            return json.dumps({"schema":"emr4.g4_operation_review.v1","status":"PASS",
                "verdict":"PASS_G4_STAGE1_OWNER_BOOTSTRAP_CONTROL_PUBLICATION_EFFECT",
                "independent":True,"implementation_authorship":False,"blocking_findings":[],
                "reviewer_agent":"/root/synthetic-independent-point-reviewer","stage":"enable","phase":"push",
                "base":d["base"]["commit"],"commit":q["base_commit"],"candidate_tree":q["base_tree"],
                "control_activation_accepted":True,"same_attempt_remote_readback_verified":True,
                "protected_refs_unchanged":True,"whole_inverse_verified_same_attempt":True,
                "published_ref":b.G4_STAGE1_INTERACTIVE_BACKEND_REF}).encode()
        if not path.is_relative_to(target) and not path.is_relative_to(source):
            raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==digest
            if path in external:seen.add(external[path])
            return raw
        relative=path.relative_to(target if path.is_relative_to(target) else source).as_posix()
        raw=after[relative];assert hashlib.sha256(raw).hexdigest()==digest
        return raw
    def git_bytes(_target,*args):
        if args[0]=="ls-tree":return b"tracked" if args[-1] in (original if stage=="enable" else installed) else b""
        assert args[:2]==("cat-file","blob")
        commit,p=args[2].split(":",1)
        return (original if commit==d["base"]["commit"] else installed)[p]
    def git(_target,*args):
        if args[0]=="rev-parse":return d["base"]["tree"]
        parent=d["base"]["commit"] if args[2]==q["base_commit"] and stage!="enable" else q["base_commit"]
        tree=q["base_tree"] if args[2]==q["base_commit"] and stage!="enable" else q["candidate_tree"]
        return "tree "+tree+"\nparent "+parent+"\n\nsynthetic\n"
    observations=[]
    monkeypatch.setattr(b.trusted_git,"run_git_bytes",git_bytes)
    monkeypatch.setattr(b.trusted_git,"run_git",git)
    monkeypatch.setattr(b.trusted_git,"attest_target_index",lambda *a,**k:observations.append(k) or {"observation_sha256":"sha256:"+"0"*64})
    def run(reader=read):return b._load_g4_owner_bootstrap_inputs(None,target,source,
        b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT,Path("C:/synthetic-point-scratch"),q,reader,{})
    read.external_seen=seen
    return run,q,read,observations


@pytest.mark.parametrize("stage,phase",[("enable","development"),("enable","pre-push"),
    ("enable","post-push"),("admit","development"),("apply","development"),
    ("apply","pre-push"),("apply","post-push")])
def test_point_full_loader_exact_nine_path_candidate_with_synthetic_observations(monkeypatch,stage,phase):
    b=bounded_g1b;run,q,read,observations=_point_loader_fixture(monkeypatch,stage,phase)
    loaded=run()
    assert loaded.binding is q and len(observations)==1
    assert loaded.evidence["mapping"]["source_candidate_accepted"] is True
    assert read.external_seen==set(b.G4_POINT_MOVE_PRODUCT_SHA)
    assert observations[0]["expected_head"]==q["expected_head"]
    assert set(q["repair_sha256"])==(b.G4_POINT_MOVE_CONTROL if stage=="enable" else
        set(b.G4_POINT_MOVE_PRODUCT_SHA) if stage=="apply" else set())


@pytest.mark.parametrize("mutation,reason",[("extra","bounded_g4_owner_bootstrap_changed_paths"),
    ("missing","bounded_g4_owner_bootstrap_changed_paths"),("case","bounded_g4_owner_bootstrap_changed_paths"),
    ("unknown_field","bounded_g4_owner_bootstrap_binding_schema"),
    ("unknown_version","bounded_g4_owner_bootstrap_binding_version"),
    ("null_payload","bounded_g4_owner_bootstrap_payload_paths"),
    ("null_candidate","bounded_g4_owner_bootstrap_git_identity"),
    ("preimage","bounded_g4_owner_bootstrap_change_preimage"),
    ("head","bounded_g4_owner_bootstrap_development_binding"),
    ("index","bounded_g4_owner_bootstrap_development_binding"),
    ("admit_delta","bounded_g4_owner_bootstrap_admit_no_delta"),
    ("admit_phase","bounded_g4_owner_bootstrap_admit_no_delta")])
def test_point_full_loader_rejects_population_draft_preimage_and_phase_mismatch(monkeypatch,mutation,reason):
    b=bounded_g1b;stage="admit" if mutation.startswith("admit_") else "apply"
    run,q,read,observations=_point_loader_fixture(monkeypatch,stage)
    if mutation=="extra":q["repair_sha256"]["extra.py"]={}
    if mutation=="missing":q["repair_sha256"].pop("app/routers/appointments.py")
    if mutation=="case":q["repair_sha256"]["APP/routers/appointments.py"]=q["repair_sha256"].pop("app/routers/appointments.py")
    if mutation=="unknown_field":q["unbound_field"]=True
    if mutation=="unknown_version":q["schema_version"]="ariadne.g4_stage1_owner_bootstrap_operation_binding.v99"
    if mutation=="null_payload":q["payload_sha256"]=None
    if mutation=="null_candidate":q["candidate_tree"]=None
    if mutation=="preimage":q["repair_sha256"]["app/routers/appointments.py"]["before_sha256"]="0"*64
    if mutation=="head":q["expected_head"]="0"*40
    if mutation=="index":q["expected_index_tree"]="0"*40
    if mutation=="admit_delta":q["candidate_tree"]="a"*40
    if mutation=="admit_phase":q["phase"]="pre-push"
    with pytest.raises(b.BoundedG1BError) as err:run()
    assert err.value.reason_code==reason


@pytest.mark.parametrize("mutation,reason",[("subject_author","bounded_g4_owner_bootstrap_independent_subject"),
    ("subject_stale","bounded_g4_owner_bootstrap_independent_subject"),
    ("activation_author","bounded_g4_owner_bootstrap_activation_acceptance"),
    ("activation_wrong","bounded_g4_owner_bootstrap_activation_acceptance"),
    ("activation_missing","bounded_g4_owner_bootstrap_activation_row"),
    ("activation_parent","bounded_g4_owner_bootstrap_activation_parent"),
    ("source_bytes","bounded_g4_owner_bootstrap_installed_source"),
    ("unowned","bounded_g4_owner_bootstrap_unowned_change"),
    ("test_membership","bounded_g4_owner_bootstrap_change_preimage")])
def test_point_full_loader_preserves_source_subject_activation_and_committed_membership(monkeypatch,mutation,reason):
    b=bounded_g1b;run,q,read,observations=_point_loader_fixture(monkeypatch,"apply")
    if mutation=="activation_missing":q["activation_acceptance"]=None
    original_bytes=b.trusted_git.run_git_bytes;original_git=b.trusted_git.run_git
    def git_bytes(target,*args):
        if mutation=="test_membership" and args[0]=="ls-tree" and args[-1]=="tests/test_reception_one_bureau_model_first_contract.py":return b"tracked"
        if mutation=="test_membership" and args[:2]==("cat-file","blob") and args[2].endswith(":tests/test_reception_one_bureau_model_first_contract.py"):return b"unexpected committed test"
        raw=original_bytes(target,*args)
        if mutation=="source_bytes" and args[:2]==("cat-file","blob") and args[2]==q["base_commit"]+":"+b.G4_AUDIT_CODE:return raw+b"changed"
        if mutation=="unowned" and args[:2]==("cat-file","blob") and args[2]==q["base_commit"]+":"+b.AGENTS:return raw+b"changed"
        return raw
    def git(target,*args):
        raw=original_git(target,*args)
        if mutation=="activation_parent" and args[:2]==("cat-file","commit") and args[2]==q["base_commit"]:return raw.replace("parent "+b.G4_POINT_MOVE_BASE["commit"],"parent "+"0"*40)
        return raw
    monkeypatch.setattr(b.trusted_git,"run_git_bytes",git_bytes);monkeypatch.setattr(b.trusted_git,"run_git",git)
    def changed(path,digest):
        raw=read(path,digest)
        if path.name.startswith("independent-apply-") and mutation in {"subject_author","subject_stale"}:
            value=json.loads(raw)
            value["reviewer_agent" if mutation=="subject_author" else "subject_sha256"]="/root/invitation_product_publication_source_review_sol" if mutation=="subject_author" else "0"*64
            return json.dumps(value).encode()
        if path.name=="independent-enable-push-effect-review-v1.json" and mutation in {"activation_author","activation_wrong"}:
            value=json.loads(raw)
            if mutation=="activation_author":value["reviewer_agent"]="/root/invitation_product_publication_source_review_sol"
            else:value["protected_refs_unchanged"]=False
            return json.dumps(value).encode()
        return raw
    with pytest.raises(b.BoundedG1BError) as err:run(changed)
    assert err.value.reason_code==reason


# Real semantic configuration boundary, with ordinary pinned documents only.
# Git/index/phase receipts in _point_loader_fixture remain explicit substitutes.
def _point_coherence_real_documents():
    values={}
    for p,row in _POINT_COHERENCE_REAL_ROWS.items():
        raw=(_POINT_COHERENCE_REAL_ROOT/p).read_bytes()
        assert len(raw)==row["bytes"] and hashlib.sha256(raw).hexdigest()==row["sha256"]
        values[p]=raw
    assert set(bounded_g1b.CONFIGURATION_PATHS).issubset(values)
    return values


def _point_coherence_policy_inputs(mutation):
    b=bounded_g1b;payloads=_point_coherence_real_documents()
    for p in b.G4_POINT_MOVE_CONTROL:payloads[p]=(_POINT_ADMISSION_CANDIDATE/p).read_bytes()
    if mutation=="legacy30":payloads[b.OVERLAY]=(_POINT_COHERENCE_REAL_ROOT/b.OVERLAY).read_bytes()
    if mutation in {"extra","missing","effect","eligibility"}:
        raw=payloads[b.OVERLAY];start=raw.index(b"  G4_STAGE1_LOCAL_SUCCESSOR:\n")
        end=raw.index(b"scope_policy:\n",start);profile=raw[start:end]
        if mutation=="extra":profile=profile.replace(b"    autonomous_task_selection: false\n",b"    - extra/unowned.py\n    autonomous_task_selection: false\n",1)
        if mutation=="missing":profile=profile.replace(b"    - orchestration/continuity/reception-one-bureau-typed-plan-protocol/operator-catalog.schema.json\n",b"",1)
        if mutation=="effect":profile=profile.replace(b"    - task_branch_push\n",b"",1)
        if mutation=="eligibility":profile=profile.replace(b"    provider_calls_eligible: false\n",b"    provider_calls_eligible: true\n",1)
        assert profile!=raw[start:end];payloads[b.OVERLAY]=raw[:start]+profile+raw[end:]
    if mutation=="state_eligibility":
        state=json.loads(payloads[b.STATE]);state["feature_work_eligible"]=True
        payloads[b.STATE]=json.dumps(state).encode()
    q=_point_q();q["payload_sha256"]={p:hashlib.sha256(raw).hexdigest() for p,raw in payloads.items()}
    return b.BoundedG1BInputs(q,{},payloads,{"scope":_point_scope()}, {})


@pytest.mark.parametrize("mutation",["legacy30","exact35","extra","missing","effect","eligibility","state_eligibility"])
def test_point_real_configuration_requires_exact35_and_closed_authority(mutation, monkeypatch):
    # Historical v24 fixture retains exact35, not the new v25 profile.
    monkeypatch.setattr(raisa_policy,"G4_STAGE1_SUCCESSOR_PRODUCT_PATHS",_MODEL_REPLY_PREDECESSOR_PATHS)
    b=bounded_g1b;inputs=_point_coherence_policy_inputs(mutation)
    if mutation!="exact35":
        with pytest.raises(b.BoundedG1BError) as err:b._validate_g4_owner_bootstrap_loaded_policy(inputs)
        assert err.value.reason_code=="configuration_g4_stage1_successor_profile_invalid"
    else:
        owned,validated=b._validate_g4_owner_bootstrap_loaded_policy(inputs)
        assert set(owned)==b.G4_POINT_MOVE_CONTROL and len(owned)==5
        documents={name:json.loads(raw) for name,raw in validated.documents}
        profile=documents["programme_recovery.yaml"]["profiles"][raisa_policy.G4_STAGE1_SUCCESSOR_PROFILE]
        assert profile==raisa_policy.g4_stage1_successor_profile()
        assert profile["allowed_paths"]==list(raisa_policy.G4_STAGE1_SUCCESSOR_PRODUCT_PATHS)
        assert len(profile["allowed_paths"])==35
        assert json.loads(inputs.payloads[b.STATE])["feature_work_eligible"] is False
        assert profile["provider_calls_eligible"] is False and profile["protected_ref_movement_eligible"] is False


@pytest.mark.parametrize("mutation",["exact","predecessor","missing","extra","effect"])
def test_point_overlay_transition_is_one_exact_append(mutation):
    b=bounded_g1b;before=(_POINT_COHERENCE_REAL_ROOT/b.OVERLAY).read_bytes()
    after=(_POINT_ADMISSION_CANDIDATE/b.OVERLAY).read_bytes()
    if mutation=="predecessor":before+=b"# drift\n"
    if mutation=="missing":after=after.replace(b.G4_POINT_MOVE_OVERLAY_APPEND,b"",1)
    if mutation=="extra":after+=b"# extra\n"
    if mutation=="effect":after=after.replace(b"    provider_calls_eligible: false\n",b"    provider_calls_eligible: true\n",1)
    if mutation=="exact":assert b._validate_g4_point_move_overlay_transition(before,after) is None
    else:
        with pytest.raises(b.BoundedG1BError) as err:b._validate_g4_point_move_overlay_transition(before,after)
        assert err.value.reason_code=="bounded_g4_point_move_overlay_transition"


@pytest.mark.parametrize("stage,mutation,reason",[
    ("enable","missing","bounded_g4_owner_bootstrap_changed_paths"),
    ("enable","extra","bounded_g4_owner_bootstrap_changed_paths"),
    ("enable","preimage","bounded_g4_owner_bootstrap_change_preimage"),
    ("admit","delta","bounded_g4_owner_bootstrap_changed_paths"),
    ("apply","delta","bounded_g4_owner_bootstrap_changed_paths"),
    ("admit","installed","bounded_g4_owner_bootstrap_unowned_change"),
    ("apply","installed","bounded_g4_owner_bootstrap_unowned_change"),
    ("enable","unknown_family","bounded_g4_owner_bootstrap_binding_version")])
def test_point_fifth_control_stage_ownership_and_installed_preservation(monkeypatch,stage,mutation,reason):
    b=bounded_g1b;run,q,read,observations=_point_loader_fixture(monkeypatch,stage)
    if mutation=="missing":q["repair_sha256"].pop(b.OVERLAY)
    if mutation in {"extra","delta"}:q["repair_sha256"][b.OVERLAY if mutation=="delta" else "extra/unowned.py"]={}
    if mutation=="preimage":q["repair_sha256"][b.OVERLAY]["before_sha256"]="0"*64
    if mutation=="unknown_family":q["schema_version"]="ariadne.g4_stage1_owner_bootstrap_operation_binding.v99"
    original=b.trusted_git.run_git_bytes
    def changed(target,*args):
        value=original(target,*args)
        if mutation=="installed" and args[:2]==("cat-file","blob") and args[2]==q["base_commit"]+":"+b.OVERLAY:return value+b"# installed drift\n"
        return value
    monkeypatch.setattr(b.trusted_git,"run_git_bytes",changed)
    with pytest.raises(b.BoundedG1BError) as err:run()
    assert err.value.reason_code==reason
    assert observations==[]


# Known v4/v24 generation isolates new subjects from consumed v3 canonical paths.
# All authority records here are explicit inert unit fixtures, never receipts.
def test_point_v4_descriptor_preserves_frozen_populations_and_roots():
    b=bounded_g1b;old=b._g4_owner_bootstrap_descriptor(b.G4_POINT_MOVE_SCHEMA)
    new=b._g4_owner_bootstrap_descriptor(b.G4_POINT_MOVE_FIVE_SCHEMA)
    assert old["version"]==23 and new["version"]==24
    assert old["scope_schema"]=="ariadne.g4_stage1_successor_entry_scope.v23"
    assert new["scope_schema"]=="ariadne.g4_stage1_successor_entry_scope.v24"
    assert old["control"]==b.G4_POINT_MOVE_V3_CONTROL and len(old["control"])==4
    assert new["control"]==old["control"]|{b.OVERLAY} and len(new["control"])==5
    assert old["preimages"]==b.G4_POINT_MOVE_V3_PREIMAGES and b.OVERLAY not in old["preimages"]
    assert new["preimages"][b.OVERLAY]==b.G4_POINT_MOVE_OVERLAY_BEFORE_SHA
    assert old["root"]==b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT/"bureau-point-move-successor-v1"
    assert new["root"]==b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT/"bureau-point-move-five-control-successor-v1"
    assert old["root"]!=new["root"] and old["product_sha"]==new["product_sha"]
    for schema in (b.G4_OWNER_BOOTSTRAP_SCHEMA,b.G4_OWNER_STAFF_INVITATION_SCHEMA):
        d=b._g4_owner_bootstrap_descriptor(schema)
        assert len(d.get("control",b.G4_OWNER_BOOTSTRAP_CONTROL))==3
        assert set(d["product_sha"])=={"stage1_account_http_adapter.py"}
    for schema,controls in [(b.G4_POINT_MOVE_SCHEMA,old["control"]),(b.G4_POINT_MOVE_FIVE_SCHEMA,new["control"])]:
        for stage in ("enable","admit","apply"):
            q=_point_q(stage);q["schema_version"]=schema
            expected=controls if stage=="enable" else set(new["product_sha"]) if stage=="apply" else set()
            q["repair_sha256"]={p:{} for p in expected}
            assert b._g4_owner_bootstrap_paths(q["operation_kind"],q)==expected


def _point_v4_subject_fixture(stage,phase):
    b=bounded_g1b;d=b._g4_owner_bootstrap_descriptor(b.G4_POINT_MOVE_FIVE_SCHEMA)
    expected=d["root"]/"entry-admission-v1"/("independent-"+stage+"-"+phase+"-subject-review-v1.json")
    value={"schema":"emr4.g4_operation_review.v1","status":"PASS",
        "verdict":"PASS_G4_STAGE1_OWNER_BOOTSTRAP_EXACT_ADMISSION_SUBJECT",
        "subject_sha256":"a"*64,"independent":True,"implementation_authorship":False,
        "blocking_findings":[],"reviewer_agent":"/root/synthetic-independent-point-reviewer",
        "stage":stage,"phase":phase}
    seen=[]
    def read(path,digest):
        assert path==expected and digest=="b"*64
        seen.append(path);return json.dumps(value).encode()
    row={"path":expected.as_posix(),"sha256":"b"*64}
    def run():return b._g4_owner_bootstrap_subject_review(read,row,b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT,
        "a"*64,stage,phase,b.G4_POINT_MOVE_FIVE_SCHEMA)
    return run,row,value,seen,expected


@pytest.mark.parametrize("stage,phase",[("enable","development"),("enable","pre-push"),
    ("enable","post-push"),("admit","development"),("apply","development"),
    ("apply","pre-push"),("apply","post-push")])
def test_point_v4_canonical_phase_paths_are_distinct_without_writes(stage,phase):
    b=bounded_g1b;run,row,value,seen,expected=_point_v4_subject_fixture(stage,phase)
    assert run()==value and seen==[expected]
    old=b._g4_owner_bootstrap_descriptor(b.G4_POINT_MOVE_SCHEMA)["root"]/"entry-admission-v1"/expected.name
    assert old!=expected and expected.is_relative_to(b.G4_POINT_MOVE_FIVE_ROOT)
    # The consumer only reads the fixed canonical path; this fixture performs no save/write.


@pytest.mark.parametrize("mutation,reason",[("old_path","bounded_g4_owner_bootstrap_review_path"),
    ("arbitrary_path","bounded_g4_owner_bootstrap_review_path"),
    ("old_subject","bounded_g4_owner_bootstrap_independent_subject"),
    ("stage","bounded_g4_owner_bootstrap_independent_subject"),
    ("phase","bounded_g4_owner_bootstrap_independent_subject")])
def test_point_v4_rejects_old_subject_and_arbitrary_phase_paths(mutation,reason):
    b=bounded_g1b;run,row,value,seen,expected=_point_v4_subject_fixture("enable","development")
    if mutation=="old_path":row["path"]=(b.G4_POINT_MOVE_V3_ROOT/"entry-admission-v1"/expected.name).as_posix()
    if mutation=="arbitrary_path":row["path"]=(expected.parent/"arbitrary-review.json").as_posix()
    if mutation=="old_subject":value["subject_sha256"]="208a6484af44ed9fe75ef8c46f6ad13435480b5aaf6ccae3e3e16d234042e373"
    if mutation=="stage":value["stage"]="apply"
    if mutation=="phase":value["phase"]="pre-push"
    with pytest.raises(b.BoundedG1BError) as err:run()
    assert err.value.reason_code==reason
    assert seen==([] if mutation.endswith("path") else [expected])


@pytest.mark.parametrize("mutation,reason",[("v3_five","bounded_g4_owner_bootstrap_changed_paths"),
    ("unknown_version","bounded_g4_owner_bootstrap_binding_version"),
    ("path_override","bounded_g4_owner_bootstrap_binding_schema")])
def test_point_v4_loader_rejects_generation_mixing_and_path_override(monkeypatch,mutation,reason):
    b=bounded_g1b;run,q,read,observations=_point_loader_fixture(monkeypatch,"enable")
    if mutation=="v3_five":q["schema_version"]=b.G4_POINT_MOVE_SCHEMA
    if mutation=="unknown_version":q["schema_version"]="ariadne.g4_stage1_owner_bootstrap_operation_binding.v99"
    if mutation=="path_override":q["subject_review_path"]="arbitrary-review.json"
    with pytest.raises(b.BoundedG1BError) as err:run()
    assert err.value.reason_code==reason and observations==[]


def test_point_v4_scope_rejects_old_generation_with_five_control_hashes():
    b=bounded_g1b;scope=_point_scope()
    assert b.validate_g4_owner_bootstrap_scope(scope)==scope["source_sha256"]
    scope["schema_version"]=b.G4_POINT_MOVE_SCOPE_SCHEMA
    with pytest.raises(b.BoundedG1BError) as err:b.validate_g4_owner_bootstrap_scope(scope)
    assert err.value.reason_code=="bounded_g4_owner_bootstrap_control_sources"


def test_point_v4_real_configuration_dispatch_has_exact_five_owned_controls(monkeypatch):
    # Historical v24 fixture retains exact35, not the new v25 profile.
    monkeypatch.setattr(raisa_policy,"G4_STAGE1_SUCCESSOR_PRODUCT_PATHS",_MODEL_REPLY_PREDECESSOR_PATHS)
    b=bounded_g1b;inputs=_point_coherence_policy_inputs("exact35")
    assert inputs.binding["schema_version"]==b.G4_POINT_MOVE_FIVE_SCHEMA
    assert inputs.evidence["scope"]["schema_version"]==b.G4_POINT_MOVE_FIVE_SCOPE_SCHEMA
    owned,validated=b._validate_g4_owner_bootstrap_loaded_policy(inputs)
    assert set(owned)==b.G4_POINT_MOVE_CONTROL and len(owned)==5
    documents={name:json.loads(raw) for name,raw in validated.documents}
    assert documents["programme_recovery.yaml"]["profiles"][raisa_policy.G4_STAGE1_SUCCESSOR_PROFILE]==raisa_policy.g4_stage1_successor_profile()


# Source-only successor test fixtures: no actual controller/Git/runtime evidence.
_MODEL_REPLY_PREDECESSOR_PATHS = tuple(p for p in raisa_policy.G4_STAGE1_SUCCESSOR_PRODUCT_PATHS if p != 'app/services/reception_one_isolated_vertex_planner.py')
_MODEL_REPLY_CANDIDATE = Path('C:/Users/there/EMR4-tools/bureau-model-reply-carrier-enable-preparation-v1/sol-candidate-v1/candidate')


def _model_reply_unlatch(monkeypatch):
    # Explicit fixture substitution only; operative source stays INERT.
    monkeypatch.setattr(bounded_g1b,"G4_MODEL_REPLY_TEMPLATE_INERT",False)


def test_model_reply_successor_inert_and_old_descriptor_preserved(monkeypatch):
    b=bounded_g1b
    monkeypatch.setattr(b,"G4_MODEL_REPLY_TEMPLATE_INERT",True)
    with pytest.raises(b.BoundedG1BError) as err:b._g4_owner_bootstrap_descriptor(b.G4_MODEL_REPLY_SCHEMA)
    assert err.value.reason_code=="bounded_g4_model_reply_source_inert"
    assert b._g4_owner_bootstrap_descriptor(b.G4_POINT_MOVE_FIVE_SCHEMA)["version"]==24
    _model_reply_unlatch(monkeypatch);d=b._g4_owner_bootstrap_descriptor(b.G4_MODEL_REPLY_SCHEMA)
    assert d["version"]==25 and len(d["product_sha"])==2 and len(d["control"])==5
    assert set(d["product_sha"])==set(['app/services/reception_one_isolated_vertex_planner.py', 'tests/test_reception_one_point_move_bridge_contract.py'])
    assert d["preimages"][b.G4_STAGE1_SUCCESSOR_SCOPE]=='be62b21c139dfa2f03751d3bbe7d11dd6cf314696cbcb6df538f1bb77a0a0586'
    assert d["before_sha"]['app/services/reception_one_isolated_vertex_planner.py']=='525cf851818031799bd43ce737575711943b2fa231e7627739504ef6b31ef956'
    assert d["root"]!=b._g4_owner_bootstrap_descriptor(b.G4_POINT_MOVE_FIVE_SCHEMA)["root"]
    assert len(_MODEL_REPLY_PREDECESSOR_PATHS)==35


@pytest.mark.parametrize("stage",["enable","admit","apply"])
def test_model_reply_exact_stage_ownership_and_extra_path_refusal(monkeypatch,stage):
    b=bounded_g1b;_model_reply_unlatch(monkeypatch);d=b._g4_owner_bootstrap_descriptor(b.G4_MODEL_REPLY_SCHEMA)
    kind={"enable":"enable_g4_stage1_successor","admit":b.G4_OWNER_BOOTSTRAP_ADMIT_KIND,"apply":"implement_g4_stage1_successor"}[stage]
    paths=d["control"] if stage=="enable" else set(d["product_sha"]) if stage=="apply" else set()
    q={"schema_version":b.G4_MODEL_REPLY_SCHEMA,"stage":stage,"operation_kind":kind,"repair_sha256":dict.fromkeys(paths,{})}
    assert b._g4_owner_bootstrap_paths(kind,q)==paths
    q["repair_sha256"]["app/extra.py"]={}
    with pytest.raises(b.BoundedG1BError):b._g4_owner_bootstrap_paths(kind,q)


def test_model_reply_scope_profile36_and_runtime_closures(monkeypatch):
    b=bounded_g1b;_model_reply_unlatch(monkeypatch)
    scope=json.loads((_MODEL_REPLY_CANDIDATE/b.G4_STAGE1_SUCCESSOR_SCOPE).read_bytes())
    assert b.validate_g4_owner_bootstrap_scope(scope)==scope["source_sha256"]
    assert len(raisa_policy.G4_STAGE1_SUCCESSOR_PRODUCT_PATHS)==36
    assert 'app/services/reception_one_isolated_vertex_planner.py' in raisa_policy.G4_STAGE1_SUCCESSOR_PRODUCT_PATHS
    assert scope["runtime_binding_required"] is True and scope["admission_grants_runtime_authority"] is False
    assert scope["voice_activation"] is False and "provider_invocation" in scope["excluded_effects"]
    for field,value in [("allowed_paths",scope["allowed_paths"]+["app/extra.py"]),("voice_activation",True),("runtime_binding_required",False),("admission_grants_runtime_authority",True)]:
        changed=copy.deepcopy(scope);changed[field]=value
        with pytest.raises(b.BoundedG1BError):b.validate_g4_owner_bootstrap_scope(changed)


def test_model_reply_external_source_and_review_byte_substitution_refuse(monkeypatch):
    b=bounded_g1b;_model_reply_unlatch(monkeypatch);d=b._g4_owner_bootstrap_descriptor(b.G4_MODEL_REPLY_SCHEMA)
    q={"product_vector":d["vector"],"mapping_review":d["mapping"]}
    def read(path,digest):
        raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==digest;return raw
    vector,review=b._g4_model_reply_external_inputs(read,q)
    assert review["source_accepted"] is True and review["execution_authorized"] is False
    assert review["blocking_findings"]==[] and len(vector["candidate_afterimages"])==2
    def changed(path,digest):
        raw=read(path,digest)
        return raw+b" " if path==Path(b.G4_MODEL_REPLY_REVIEW["path"]) else raw
    with pytest.raises(b.BoundedG1BError):b._g4_model_reply_external_inputs(changed,q)


def test_model_reply_overlay_exact_append_and_extra_change_refusal():
    b=bounded_g1b;before=Path('C:/Users/there/EMR4-tools/point-move-product-apply01-source/orchestration/harness_settings/programme_recovery.yaml').read_bytes();after=(_MODEL_REPLY_CANDIDATE/b.OVERLAY).read_bytes()
    b._validate_g4_model_reply_overlay_transition(before,after)
    with pytest.raises(b.BoundedG1BError):b._validate_g4_model_reply_overlay_transition(before,after+b"\n")
