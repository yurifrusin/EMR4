"""Authored source-only DOM/synthesis mock; deliberately not run in preparation."""
import base64
from pathlib import Path
import shutil
import subprocess

import pytest


def test_spoken_reply_requires_exact_local_voice_and_fresh_visible_result():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node needed for a later independently admitted mock run")
    source = (Path(__file__).resolve().parents[1] / "static" / "demo" /
              "stage1-local-voice.js").read_text(encoding="utf-8")
    assert "const QUALIFIED_LOCAL_SPEECH_VOICE = null;" in source
    qualified = source.replace(
        "const QUALIFIED_LOCAL_SPEECH_VOICE = null;",
        'const QUALIFIED_LOCAL_SPEECH_VOICE = {voiceURI:"local:test", name:"Local Test", lang:"en-AU"};',
    )
    script = r"""
import assert from 'node:assert/strict';
const tick = () => new Promise(resolve => setImmediate(resolve));
const load = async raw => (await import('data:text/javascript;base64,' +
  Buffer.from(raw, 'base64').toString('base64'))).initSpokenReply;
const original = process.argv[1], qualified = process.argv[2];
function harness(local = true) {
  const elements = Object.fromEntries(['spoken-reply','spoken-availability','status'].map(id =>
    [id, {id,disabled:false,textContent:'',listeners:{},
      addEventListener(name,fn){this.listeners[name]=fn;}}]));
  const events = {}, calls = {speak:[],cancel:0};
  const voice = {voiceURI:'local:test',name:'Local Test',lang:'en-AU',localService:local};
  let session = {persona:'staff',csrf:'scope-a'}, serverSession = session,
    serverAvailable = true, deferred;
  const timers = new Map(); let nextTimer = 0;
  globalThis.setInterval = fn => {const id=++nextTimer;timers.set(id,{fn,interval:true});return id;};
  globalThis.clearInterval = id => timers.delete(id);
  globalThis.setTimeout = fn => {const id=++nextTimer;timers.set(id,{fn,interval:false});return id;};
  globalThis.clearTimeout = id => timers.delete(id);
  globalThis.document = {hidden:false,getElementById:id=>elements[id],
    addEventListener:(name,fn)=>{events[name]=fn;}};
  globalThis.window = {speechSynthesis:{getVoices:()=>[voice],
    cancel(){calls.cancel++;},speak(u){calls.speak.push(u);},addEventListener(){}},
    addEventListener:(name,fn)=>{events[name]=fn;}};
  globalThis.SpeechSynthesisUtterance = class {constructor(text){this.text=text;}};
  globalThis.fetch = async () => deferred || {ok:serverAvailable,json:async()=>serverSession};
  return {elements,events,calls,getSession:()=>session,setSession:v=>{session=v;},
    setServerSession:v=>{serverSession=v;},expire:()=>{serverAvailable=false;},
    delay:v=>{deferred=v;},click:()=>elements['spoken-reply'].listeners.click(),
    tickWatch:()=>{for(const item of [...timers.values()]) if(item.interval) item.fn();},
    activeTimers:()=>timers.size};
}
// Default source cannot select an installed or browser-default voice.
{
  const h=harness(); const reply=(await load(original))(h.getSession);
  h.elements.status.textContent='Verified booking'; reply.offer('Verified booking');
  assert.equal(h.elements['spoken-reply'].disabled,true);
  h.click(); await tick(); assert.equal(h.calls.speak.length,0);
}
// A matching name and URI with localService=false is still rejected.
{
  const h=harness(false); const reply=(await load(qualified))(h.getSession);
  h.elements.status.textContent='Verified booking'; reply.offer('Verified booking');
  h.click(); await tick(); assert.equal(h.calls.speak.length,0);
}
// With an exact mock-local identity, speech requires the explicit click and
// uses the same currently visible message after a fresh session check.
{
  const h=harness(); const reply=(await load(qualified))(h.getSession);
  h.elements.status.textContent='Booked 2026-10-15 at 14:00 Australia/Brisbane';
  reply.offer(h.elements.status.textContent);
  assert.equal(h.calls.speak.length,0);
  h.click(); await tick(); await tick();
  assert.equal(h.calls.speak.length,1);
  assert.equal(h.calls.speak[0].text,h.elements.status.textContent);
  reply.stop(); assert.ok(h.calls.cancel >= 1);
  const stale=h.calls.speak[0]; stale.onend();
  assert.equal(h.calls.speak.length,1);
}
// Changed session and hidden page stop speech; delayed session replies cannot
// revive a superseded utterance or submit any appointment action.
{
  const h=harness(); const reply=(await load(qualified))(h.getSession);
  h.elements.status.textContent='Moved same appointment to 2026-10-15 at 15:00 Australia/Brisbane';
  reply.offer(h.elements.status.textContent);
  let release; h.delay(new Promise(resolve=>{release=resolve;})); h.click();
  reply.stop(); release({ok:true,json:async()=>({persona:'staff',csrf:'scope-a'})});
  await tick(); await tick(); assert.equal(h.calls.speak.length,0);
  h.delay(null); reply.offer(h.elements.status.textContent); h.setSession({persona:'staff',csrf:'scope-b'});
  h.click(); await tick(); assert.equal(h.calls.speak.length,0);
  h.setSession({persona:'staff',csrf:'scope-a'}); reply.offer(h.elements.status.textContent);
  document.hidden=true; h.events.visibilitychange();
  h.click(); await tick(); assert.equal(h.calls.speak.length,0);
  h.events.pagehide(); assert.equal(h.calls.speak.length,0);
}
// Server scope can change without a DOM event or a state.session assignment.
// The active watcher must cancel and dispose, and its late callback cannot revive speech.
{
  const h=harness(); const reply=(await load(qualified))(h.getSession);
  h.elements.status.textContent='Booked 2026-10-15 at 14:00 Australia/Brisbane';
  reply.offer(h.elements.status.textContent); h.click(); await tick(); await tick();
  assert.equal(h.calls.speak.length,1); assert.equal(h.activeTimers(),2);
  const old=h.calls.speak[0];
  h.setServerSession({persona:'staff',csrf:'scope-b'});
  h.tickWatch(); await tick(); await tick();
  assert.ok(h.calls.cancel>=1); assert.equal(h.activeTimers(),0);
  old.onend(); assert.equal(h.calls.speak.length,1);
  reply.stop(); assert.equal(h.activeTimers(),0);
}
// Expired/unavailable server session during speech is also fail-closed.
{
  const h=harness(); const reply=(await load(qualified))(h.getSession);
  h.elements.status.textContent='Moved same appointment to 2026-10-15 at 15:00 Australia/Brisbane';
  reply.offer(h.elements.status.textContent); h.click(); await tick(); await tick();
  assert.equal(h.calls.speak.length,1);
  h.expire(); h.tickWatch(); await tick(); await tick();
  assert.ok(h.calls.cancel>=1); assert.equal(h.activeTimers(),0);
  h.calls.speak[0].onerror(); assert.equal(h.calls.speak.length,1);
}
"""
    before = base64.b64encode(source.encode()).decode()
    after = base64.b64encode(qualified.encode()).decode()
    subprocess.run([node, "--input-type=module", "-e", script, before, after],
                   check=True, capture_output=True, text=True, timeout=15)
