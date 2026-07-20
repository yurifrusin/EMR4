/* EMR4 Diary Office.js bootstrap.
 *
 * The Diary remains an Office dialog when launched normally. A deliberately
 * narrow loopback-only capability lets the native browser Diary run without an
 * external Office.js fetch during provider-disabled local acceptance.
 */
(function bootstrapDiaryOffice() {
  "use strict";

  const params = new URLSearchParams(window.location.search);
  const isLoopback = ["127.0.0.1", "localhost"].includes(window.location.hostname);
  const standalone = isLoopback && params.get("standalone_diary") === "true";
  if (standalone) {
    window.Office = Object.freeze({
      context: Object.freeze({}),
      EventType: Object.freeze({}),
      onReady(callback) {
        return Promise.resolve().then(() => callback({ host: null, platform: null }));
      }
    });
    return;
  }

  document.write(
    '<script type="text/javascript" src="https://appsforoffice.microsoft.com/lib/1/hosted/office.js"><\/script>'
  );
})();
