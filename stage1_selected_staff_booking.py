"""Default-off selected-session booking caller. SOURCE/ADMISSION PROPOSAL ONLY."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import date, datetime, timezone
import json
import re
import secrets
from typing import Awaitable, Callable

from stage1_seeded_login import COOKIE, SeededLoginController, _Denied, _Unavailable, _reply
from stage1_patient_browser import _uuid
from stage1_staff_booking_context import _pairs


@dataclass(frozen=True, repr=False)
class SelectedStaffBookingBinding:
    practice_id: str
    fixture_day: date
    exchange: Callable[..., Awaitable]
    enabled: bool = False


_SELECTED_RECEIVE_STAGES = frozenset({"SITE_RECEIVE_ENTRY", "SITE_RECEIVE_GUARDS", "SITE_RECEIVE_CLAIM", "SITE_RECEIVE_CURRENT", "SITE_RECEIVE_PRE_CALLBACK", "SITE_RECEIVE_CALLBACK", "SITE_RECEIVE_POST_SAME", "SITE_RECEIVE_POST_CURRENT", "SITE_RECEIVE_RELEASE"})
_SELECTED_RECEIVE_STATUSES = frozenset({"NOT_OBSERVED", "NOT_RETURNED", "HTTP_200", "HTTP_400", "HTTP_401", "HTTP_403", "HTTP_404", "HTTP_409", "HTTP_422", "HTTP_500", "HTTP_503", "HTTP_OTHER", "UNAVAILABLE"})


def _new_selected_receive_progress():
    try:
        return {'stage':'SITE_RECEIVE_ENTRY','callback_status':'NOT_OBSERVED'}
    except BaseException:
        return None


def _selected_receive_stage(progress, stage):
    try:
        if type(progress) is dict and stage in _SELECTED_RECEIVE_STAGES:
            progress['stage'] = stage
    except BaseException:
        pass


def _selected_receive_status(progress, status):
    try:
        if type(progress) is dict and status in _SELECTED_RECEIVE_STATUSES:
            progress['callback_status'] = status
    except BaseException:
        pass


class SelectedStaffBookingController:
    """SITE keeps opaque refs only; backend owns source, key and signed body."""
    def __init__(self, controller, binding):
        if (type(controller) is not SeededLoginController
                or type(binding) is not SelectedStaffBookingBinding or binding.enabled is not True
                or not _uuid(binding.practice_id) or type(binding.fixture_day) is not date
                or not callable(binding.exchange)):
            raise ValueError('selected staff booking disabled')
        self.controller, self.binding, self._closed = controller, binding, False
        self._states = []
        self._native_owner = None
        self._receive_diagnostic = None

    def _remember_receive_failure(self, progress, error):
        try:
            if type(progress) is not dict or self._receive_diagnostic is not None:
                return
            stage = progress.get('stage')
            stage = stage if stage in _SELECTED_RECEIVE_STAGES else 'SITE_RECEIVE_ENTRY'
            status = progress.get('callback_status')
            status = status if status in _SELECTED_RECEIVE_STATUSES else 'UNAVAILABLE'
            caught = type(error)
            kind = ('_Denied' if caught is _Denied else '_Unavailable' if caught is _Unavailable else
                'KeyError' if caught is KeyError else 'TypeError' if caught is TypeError else
                'ValueError' if caught is ValueError else 'UnicodeError' if isinstance(error, UnicodeError) else
                'OverflowError' if caught is OverflowError else
                'CancelledError' if isinstance(error, asyncio.CancelledError) else 'Other')
            self._receive_diagnostic = (stage,kind,status)
        except BaseException:
            pass

    def selected_receive_diagnostic_snapshot(self):
        retained = self._receive_diagnostic
        if retained is None:
            return {'state':'NO_FAILURE_RECORDED','stage':'NONE','refusal_class':None,
                'callback_status':'NOT_OBSERVED'}
        stage,kind,status = retained
        return {'state':'REFUSED','stage':stage,'refusal_class':kind,'callback_status':status}

    async def handle(self, request, action):
        key = request.cookies.get(COOKIE, '')
        value = self.controller.sessions.get(key)
        state = None
        try:
            if (self._closed or value is None or request.method != 'POST' or request.url.query
                    or request.headers.get('authorization') is not None
                    or request.headers.get('origin') != request.app.state.seeded_login_origin
                    or request.headers.get('content-type') != 'application/json'
                    or not secrets.compare_digest(request.headers.get('x-csrf-token',''), value.csrf)
                    or action not in {'capture','status','select','confirm','readback'}):
                raise _Denied()
            async with value.lock:
                self.controller._require_current(key, value)
                chunks, size = [], 0
                async for chunk in request.stream():
                    size += len(chunk)
                    if size > 4096:
                        raise _Denied()
                    chunks.append(chunk)
                self.controller._require_current(key, value)
                try:
                    body = json.loads(b''.join(chunks), object_pairs_hook=_pairs,
                        parse_constant=lambda _x: (_ for _ in ()).throw(ValueError()))
                except (ValueError, UnicodeDecodeError):
                    raise _Denied() from None
                shapes = {'capture':{'patient_id','date','duration_minutes','instruction','manual'},
                    'status':set(), 'select':{'slot_ref'}, 'confirm':{'proposal_ref'}, 'readback':set()}
                if type(body) is not dict or set(body) != shapes[action]:
                    raise _Denied()
                tenant, selected, staff = value.tenant, value.selected, value.staff_session
                if not tenant or type(selected) is not dict:
                    raise _Denied()
                selected_copy = dict(selected)
                def local_identity():
                    self.controller._require_current(key, value)
                    if (self._closed or value.tenant != tenant or value.selected is not selected
                            or value.selected != selected_copy or value.staff_session is not staff):
                        raise _Denied()
                    return True
                local_identity()
                role = await self.controller._current(value, key=key, expected=value)
                local_identity()
                authority = value.patient_current_authority
                if (role != 'InvitedReceptionist' or type(authority) is not dict
                        or set(authority) != {'account_id','membership_id','user_id','practice_id','role','authority_generation'}
                        or authority['practice_id'] != self.binding.practice_id
                        or selected_copy.get('practice_id') != self.binding.practice_id
                        or authority['role'] != 'Receptionist' or type(authority['authority_generation']) is not int):
                    raise _Denied()
                authority = dict(authority)
                state = next((s for s in self._states if s['value'] is value), None)
                if state is None:
                    if action != 'capture':
                        raise _Denied()
                    state = {'value':value, 'tenant':tenant, 'selected':selected_copy, 'authority':authority,
                        'session_ref':secrets.token_urlsafe(24), 'capture_id':None, 'sent':False,
                        'uncertain':False, 'expires':None, 'view':None, 'retired':False,
                        'received':False, 'packet':None, 'retired_capture_ids':set()}
                    self._states.append(state)
                if (state['retired'] or state['tenant'] != tenant or state['selected'] != selected_copy
                        or state['authority'] != authority):
                    state['retired'] = True
                    raise _Denied()
                def same():
                    local_identity()
                    if state['retired'] or value.patient_current_authority != authority:
                        raise _Denied()
                    if action in {'select','confirm'} and (state['expires'] is None
                            or datetime.now(timezone.utc) >= state['expires']):
                        raise _Denied()
                    return True
                if action == 'capture':
                    if (state['sent'] or state['uncertain'] or not _uuid(body['patient_id'])
                            or body['date'] != self.binding.fixture_day.isoformat()
                            or type(body['duration_minutes']) is not int or body['duration_minutes'] != 30
                            or type(body['manual']) is not bool or type(body['instruction']) is not str
                            or not 1 <= len(body['instruction']) <= 512 or not body['instruction'].strip()):
                        raise _Denied()
                    # Retire the prior capture before any replacement await; its replies cannot bind the new one.
                    if state['capture_id'] is not None:
                        state['retired_capture_ids'].add(state['capture_id'])
                    # A deliberate new capture has its own one-use receive latch, private packet and original expiry.
                    state['capture_id'], state['expires'], state['view'] = None, None, None
                    state['received'], state['packet'] = False, None
                elif state['capture_id'] is None:
                    raise _Denied()
                if action == 'confirm':
                    if state['sent'] or state['uncertain']:
                        raise _Denied()
                    # Even cancellation/context loss after dispatch never grants retry.
                    state['sent'], state['uncertain'] = True, True
                private = {'op':action, 'selected':authority, 'session_ref':state['session_ref'], **body}
                if action != 'capture':
                    private['capture_id'] = state['capture_id']
                same()
                response = await self.controller._call(self.binding.exchange,
                    tenant_bearer=tenant, body=private, current=same)
                same()
                role_after = await self.controller._current(value, key=key, expected=value)
                same()
                if role_after != role or value.patient_current_authority != authority:
                    raise _Denied()
                if action == 'capture':
                    packet = response.pop('_private_capture', None)
                    if (type(packet) is not dict or set(packet) != {'capture_id','frame_sha256','frame'}
                            or packet['capture_id'] != response.get('capture_id')
                            or type(packet['frame_sha256']) is not str
                            or re.fullmatch(r'[0-9a-f]{64}', packet['frame_sha256']) is None
                            or type(packet['frame']) is not dict):
                        raise _Denied()
                    state['packet'] = packet
                required = {'state','capture_id','expires_at','patient','practitioner','date',
                    'duration_minutes','timezone','choices','review','receipt','readback'}
                if (type(response) is not dict or set(response) != required
                        or response['state'] not in {'awaiting_reply','choice','clarification','review','expired','uncertain','confirmed'}
                        or type(response['capture_id']) is not str
                        or re.fullmatch(r'[A-Za-z0-9_-]{32}', response['capture_id']) is None
                        or response['date'] != self.binding.fixture_day.isoformat()
                        or type(response['duration_minutes']) is not int or response['duration_minutes'] != 30
                        or type(response['choices']) is not list or len(response['choices']) > 8):
                    raise _Denied()
                expiry = datetime.fromisoformat(response['expires_at'].replace('Z','+00:00'))
                if expiry.tzinfo is None or (state['expires'] is not None and expiry != state['expires']):
                    raise _Denied()
                if action != 'capture' and response['capture_id'] != state['capture_id']:
                    raise _Denied()
                state['capture_id'], state['expires'], state['view'] = response['capture_id'], expiry, response
                if (action == 'capture' and body['manual'] is False and response['state'] == 'awaiting_reply'
                        and self._native_owner is not None):
                    self._native_owner.notify(self, state['capture_id'])
                if response['state'] == 'confirmed':
                    state['uncertain'] = False
                return _reply(response)
        except asyncio.CancelledError:
            raise
        except (_Denied, _Unavailable, KeyError, TypeError, ValueError, OverflowError):
            # No retry or outcome-query claim. Original command/key stay backend-private.
            return _reply({'state':'uncertain' if state is not None and state['sent'] else 'unavailable',
                'detail':'Booking outcome unresolved; do not resend.' if state is not None and state['sent']
                    else 'Selected booking unavailable.'}, 403)

    def take_staff_booking_capture_v1(self, capture_id):
        """Trusted host read of the retained packet; never an HTTP operation."""
        state = next((s for s in self._states if s['capture_id'] == capture_id), None)
        if state is None or self._closed or state['retired'] or state['sent']:
            raise _Denied()
        value = state['value']
        key = next((k for k,v in self.controller.sessions.items() if v is value), None)
        self.controller._require_current(key, value)
        if (value.tenant != state['tenant'] or value.selected != state['selected']
                or value.patient_current_authority != state['authority']
                or state['expires'] is None or datetime.now(timezone.utc) >= state['expires']):
            raise _Denied()
        return json.loads(json.dumps(state['packet']))

    async def receive_staff_booking_reply_v1(self, capture_id, frame_sha256, raw_response):
        """Private trusted caller only. Public schemas have no receive/raw/provenance fields."""
        _receive_progress = _new_selected_receive_progress()
        try:
            import base64
            _selected_receive_stage(_receive_progress, 'SITE_RECEIVE_GUARDS')
            if type(raw_response) is not bytes or not 1 <= len(raw_response) <= 32768:
                raise _Denied()
            state = next((s for s in self._states if s['capture_id'] == capture_id), None)
            if state is None or state.get('received') or state['sent']:
                raise _Denied()
            value = state['value']
            key = next((k for k,v in self.controller.sessions.items() if v is value), None)
            async with value.lock:
                _selected_receive_stage(_receive_progress, 'SITE_RECEIVE_CURRENT')
                packet = self.take_staff_booking_capture_v1(capture_id)
                if frame_sha256 != packet['frame_sha256']:
                    raise _Denied()
                role = await self.controller._current(value, key=key, expected=value)
                if role != 'InvitedReceptionist':
                    raise _Denied()
                def same():
                    self.take_staff_booking_capture_v1(capture_id)
                    return True
                _selected_receive_stage(_receive_progress, 'SITE_RECEIVE_PRE_CALLBACK')
                same()
                # Authoritative claim is under value.lock after current/expiry checks and the /me await.
                if (self._closed or state['retired'] or state['value'] is not value
                        or state['capture_id'] != capture_id or capture_id in state['retired_capture_ids']
                        or state['received'] or state['sent'] or state['uncertain']
                        or state['packet'] is None or state['packet']['capture_id'] != capture_id
                        or state['packet']['frame_sha256'] != frame_sha256
                        or state['expires'] is None or datetime.now(timezone.utc) >= state['expires']):
                    raise _Denied()
                # No await separates the claim from the sole receive dispatch; response loss never permits retry.
                state['received'] = True
                async def observed_exchange(**kwargs):
                    _selected_receive_stage(_receive_progress, 'SITE_RECEIVE_CALLBACK')
                    _selected_receive_status(_receive_progress, 'NOT_RETURNED')
                    response = await self.binding.exchange(**kwargs)
                    try:
                        status = response.status_code
                        category = {200:'HTTP_200',400:'HTTP_400',401:'HTTP_401',403:'HTTP_403',
                            404:'HTTP_404',409:'HTTP_409',422:'HTTP_422',500:'HTTP_500',
                            503:'HTTP_503'}.get(status,'HTTP_OTHER') if type(status) is int else 'HTTP_OTHER'
                        _selected_receive_status(_receive_progress, category)
                    except BaseException:
                        _selected_receive_status(_receive_progress, 'UNAVAILABLE')
                    return response
                answer = await self.controller._call(observed_exchange,
                    tenant_bearer=state['tenant'], current=same, body={
                        'op':'receive','selected':state['authority'],'session_ref':state['session_ref'],
                        'capture_id':capture_id,'frame_sha256':frame_sha256,
                        'raw_b64':base64.b64encode(raw_response).decode('ascii')})
                _selected_receive_stage(_receive_progress, 'SITE_RECEIVE_POST_SAME')
                same()
                _selected_receive_stage(_receive_progress, 'SITE_RECEIVE_POST_CURRENT')
                role_after = await self.controller._current(value, key=key, expected=value)
                _selected_receive_stage(_receive_progress, 'SITE_RECEIVE_RELEASE')
                same()
                if role_after != role:
                    raise _Denied()
                # The next authenticated status operation projects this state to the UI.
                return answer
        except BaseException as error:
            self._remember_receive_failure(_receive_progress, error)
            raise

    async def close(self):
        self._closed = True
        for state in self._states:
            state['retired'] = True
            # Retain opaque refs and uncertainty until the owner releases this controller.


class SelectedStaffNativeOwner:
    """Default-off harness adapter. Root alone owns actual native generation."""
    SCHEMA = 'emr4.selected_staff_native_private.v1'
    PATH = '/_stage1/selected-staff-native-v1'
    INPUT = 'model-input.selected-staff-v1.json'
    READY = 'capture-ready.selected-staff.json'

    def __init__(self, config):
        import hashlib
        if (type(config) is not dict or set(config) != {
                'schema','attempt_id','implementation_generation','policy_digest','authoring_manifest','capability'}
                or config['schema'] != self.SCHEMA
                or any(type(config[k]) is not str or not 1 <= len(config[k]) <= 128
                    for k in ('attempt_id','implementation_generation'))
                or any(type(config[k]) is not str or re.fullmatch(r'[0-9a-f]{64}', config[k]) is None
                    for k in ('policy_digest','capability'))):
            raise ValueError('selected native configuration invalid')
        manifest = config['authoring_manifest']
        if (type(manifest) is not dict or set(manifest) != {
                'dispatch_id','worker_role','input_template_sha256','response_filename','max_raw_bytes'}
                or type(manifest['dispatch_id']) is not str or not 1 <= len(manifest['dispatch_id']) <= 128
                or manifest['worker_role'] != 'untrusted_model_semantic_packet_author'
                or re.fullmatch(r'[0-9a-f]{64}', manifest['input_template_sha256']) is None
                or manifest['response_filename'] != '01-selected-staff.semantic-packet.response.utf8.json'
                or type(manifest['max_raw_bytes']) is not int or manifest['max_raw_bytes'] != 32768):
            raise ValueError('selected native manifest invalid')
        self.config = json.loads(json.dumps(config))
        self.capture_event, self.received_event = asyncio.Event(), asyncio.Event()
        self._controller = None
        self._capture_id, self._descriptor, self._assert_live = None, None, None
        self._publication_claimed = self._receive_claimed = self._closed = False
        self._state, self._raw_sha256, self._provenance = 'PENDING', None, None
        self._operations, self._lock = set(), asyncio.Lock()

    @staticmethod
    def _canonical(value):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',',':'),
                          allow_nan=False).encode('utf-8')

    def _remember_receive_failure(self, progress, error):
        try:
            controller = self._controller
            if type(controller) is SelectedStaffBookingController and controller._native_owner is self:
                controller._remember_receive_failure(progress, error)
        except BaseException:
            pass

    def selected_receive_diagnostic_snapshot(self):
        controller = self._controller
        if type(controller) is not SelectedStaffBookingController or controller._native_owner is not self:
            return {'state':'UNAVAILABLE','stage':'UNAVAILABLE','refusal_class':None,
                'callback_status':'UNAVAILABLE'}
        return controller.selected_receive_diagnostic_snapshot()

    def bind(self, controller, *, current):
        if (self._controller is not None or self._closed or type(controller) is not SelectedStaffBookingController
                or controller._native_owner is not None or not callable(current) or current() is not True):
            raise _Denied()
        self._controller = controller
        controller._native_owner = self

    def notify(self, controller, capture_id):
        if self._closed or controller is not self._controller:
            raise _Denied()
        controller.take_staff_booking_capture_v1(capture_id)
        # First nonmanual capture only. Reselection never automatically buys another dispatch.
        if self._capture_id is None:
            self._capture_id = capture_id
            self.capture_event.set()

    async def render_input(self, q, work, renderer):
        from pathlib import Path
        import hashlib
        if self._closed or self._publication_claimed or self._controller is None or not callable(renderer):
            raise _Denied()
        self._publication_claimed = True
        controller, capture_id = self._controller, self._capture_id
        state = next((s for s in controller._states if s['capture_id'] == capture_id), None)
        if state is None:
            raise _Denied()
        value = state['value']
        key = next((k for k,v in controller.controller.sessions.items() if v is value), None)
        async with value.lock:
            role = await controller.controller._current(value, key=key, expected=value)
            if role != 'InvitedReceptionist':
                raise _Denied()
            packet = controller.take_staff_booking_capture_v1(capture_id)
            def assert_live(expected):
                actual = controller.take_staff_booking_capture_v1(capture_id)
                if (self._closed or state['received'] or state['sent']
                        or state['uncertain'] or self._canonical(actual) != self._canonical(packet)
                        or self._canonical(expected) != self._canonical(packet)):
                    raise _Denied()
                return True
            assert_live(packet)
            descriptor, content = renderer(q, json.loads(json.dumps(packet)), work, assert_live)
            work = Path(work)
            target, ready = work/self.INPUT, work/self.READY
            pending, pending_ready = work/(self.INPUT+'.pending'), work/(self.READY+'.pending')
            ready_bytes = self._canonical(descriptor)
            if (type(content) is not bytes or not 0 < len(content) <= 131072 or len(ready_bytes) > 16384
                    or descriptor['input'] != {'path':target.as_posix(),'bytes':len(content),
                                               'sha256':hashlib.sha256(content).hexdigest()}
                    or any(p.exists() for p in (target,ready,pending,pending_ready))):
                raise _Denied()
            created, published, primary, failures = [], False, None, []
            try:
                for path, raw in ((pending,content),(pending_ready,ready_bytes)):
                    with path.open('xb') as stream:
                        created.append(path)
                        stream.write(raw)
                assert_live(packet)
                pending.rename(target)
                created.remove(pending)
                created.append(target)
                assert_live(packet)
                # No await separates the current check and visible-ready publication.
                pending_ready.rename(ready)
                created.remove(pending_ready)
                self._descriptor, self._assert_live, self._state = descriptor, assert_live, 'CAPTURED'
                published = True
                return descriptor
            except BaseException as error:
                primary = error
            finally:
                if not published:
                    self._closed = True
                    for path in reversed(created):
                        try:
                            path.unlink()
                        except BaseException as error:
                            failures.append(error)
                if primary is not None and failures:
                    raise BaseExceptionGroup('selected native publication and cleanup failed', [primary,*failures])
                if primary is not None:
                    raise primary
                if failures:
                    raise BaseExceptionGroup('selected native publication cleanup failed', failures)

    def _reply(self):
        return {'schema':'emr4.selected_staff_native_control_reply.v1',
            'capture_id':self._capture_id,
            'frame_sha256':None if self._descriptor is None else self._descriptor['frame_sha256'],
            'input_sha256':None if self._descriptor is None else self._descriptor['input']['sha256'],
            'raw_sha256':self._raw_sha256, 'state':self._state}

    async def handle_private(self, request, *, origin):
        _receive_progress = None
        try:
            import base64
            import hashlib
            if (self._closed or request.client is None or request.client.host != '127.0.0.1'
                    or request.url.query or request.headers.get('origin') != origin
                    or request.headers.get('content-type') != 'application/json'
                    or not secrets.compare_digest(request.headers.get('x-selected-staff-native-capability',''),
                                                   self.config['capability'])):
                raise _Denied()
            chunks, size = [], 0
            async for chunk in request.stream():
                size += len(chunk)
                if size > 61440:
                    raise _Denied()
                chunks.append(chunk)
            body = json.loads(b''.join(chunks), object_pairs_hook=_pairs,
                              parse_constant=lambda _x: (_ for _ in ()).throw(ValueError()))
            common = {'schema','operation','attempt_id','implementation_generation','policy_digest'}
            extra = {'capture':set(), 'receive':{'capture_id','frame_sha256','raw_bytes','raw_sha256',
                        'raw_utf8_base64','authoring_provenance'}, 'status':{'capture_id','frame_sha256'},
                        'cancel':{'capture_id','frame_sha256','reason'}}
            if type(body) is dict and body.get('operation') == 'receive':
                _receive_progress = _new_selected_receive_progress()
                _selected_receive_stage(_receive_progress, 'SITE_RECEIVE_GUARDS')
            if (type(body) is not dict or body.get('schema') != 'emr4.selected_staff_native_handoff.v1'
                    or body.get('operation') not in extra or set(body) != common | extra[body['operation']]
                    or any(body[k] != self.config[k] for k in ('attempt_id','implementation_generation','policy_digest'))):
                raise _Denied()
            operation = body['operation']
            raw = None
            async with self._lock:
                if operation in self._operations or self._descriptor is None or self._controller is None:
                    raise _Denied()
                self._operations.add(operation)
                cap = self._controller.take_staff_booking_capture_v1(self._capture_id)
                if operation != 'capture' and (body['capture_id'] != cap['capture_id']
                        or body['frame_sha256'] != cap['frame_sha256']):
                    raise _Denied()
                if operation in ('capture','receive'):
                    self._assert_live(cap)
                if operation == 'cancel':
                    if body['reason'] not in ('cancelled','superseded') or self._receive_claimed:
                        raise _Denied()
                    # Native-handoff cancellation only. Never erase or replay a command.
                    self._state = body['reason'].upper()
                    return _reply(self._reply())
                if operation != 'receive':
                    return _reply(self._reply())
                manifest, proof = self.config['authoring_manifest'], body['authoring_provenance']
                if (self._receive_claimed or self._state != 'CAPTURED'
                        or type(proof) is not dict or set(proof) != {
                            'dispatch_id','input_sha256','output_path','output_bytes','output_sha256'}
                        or proof['dispatch_id'] != manifest['dispatch_id']
                        or proof['input_sha256'] != self._descriptor['input']['sha256']
                        or proof['output_path'] != manifest['response_filename']
                        or type(body['raw_bytes']) is not int or not 1 <= body['raw_bytes'] <= 32768
                        or proof['output_bytes'] != body['raw_bytes'] or proof['output_sha256'] != body['raw_sha256']):
                    raise _Denied()
                raw = base64.b64decode(body['raw_utf8_base64'], validate=True)
                raw.decode('utf-8', errors='strict')
                if (raw.startswith(b'\xef\xbb\xbf') or len(raw) != body['raw_bytes']
                        or hashlib.sha256(raw).hexdigest() != body['raw_sha256']
                        or base64.b64encode(raw).decode('ascii') != body['raw_utf8_base64']):
                    raise _Denied()
                self._assert_live(cap)
                # Consumed before the sole awaited callback. Response loss cannot reopen it.
                _selected_receive_stage(_receive_progress, 'SITE_RECEIVE_CLAIM')
                self._receive_claimed = True
                self._raw_sha256, self._provenance, self._state = body['raw_sha256'], dict(proof), 'UNCERTAIN'
            try:
                await self._controller.receive_staff_booking_reply_v1(
                    cap['capture_id'],cap['frame_sha256'],raw)
                self._state = 'DELIVERED'
                self.received_event.set()
                return _reply(self._reply())
            finally:
                raw = None
        except BaseException as error:
            self._remember_receive_failure(_receive_progress, error)
            raise

    async def close(self):
        self._closed = True
        self.config['capability'] = None
        # Capture/input/raw hashes and uncertainty remain for this owned lifetime.
