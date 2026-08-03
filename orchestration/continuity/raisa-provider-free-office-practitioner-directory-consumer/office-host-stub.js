(() => {
  "use strict";
  const root = document.getElementById("directory-root");
  const expected = (root && root.dataset.expectedHost) || "";
  const platform = expected === "word_online" ? "OfficeOnline" : "PC";
  globalThis.Office = Object.freeze({
    onReady(callback) {
      window.queueMicrotask(() => callback({ host: "Word", platform }));
    },
  });
})();
