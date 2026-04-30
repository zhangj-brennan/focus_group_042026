(function () {
  function createScrollyEmbed(el, index) {
    const src = el.getAttribute("data-src");
    if (!src) return;

    const iframe = document.createElement("iframe");

    iframe.src = src;
    iframe.title = el.getAttribute("data-title") || "Scrolly embed";
    iframe.id = el.id || `scrolly-embed-${index}`;
    iframe.scrolling = "no";
    iframe.frameBorder = "0";

    iframe.style.width = "100%";
    iframe.style.border = "0";
    iframe.style.display = "block";
    iframe.style.overflow = "hidden";
    iframe.style.minHeight = "400px";

    el.innerHTML = "";
    el.appendChild(iframe);
  }

  function init() {
    document.querySelectorAll(".scrolly-embed").forEach(createScrollyEmbed);
  }

  window.addEventListener("message", function (event) {
    if (!event.data || event.data.type !== "resize-scrolly") return;

    document.querySelectorAll(".scrolly-embed iframe").forEach(function (iframe) {
      if (iframe.contentWindow === event.source) {
        iframe.style.height = event.data.height + "px";
      }
    });
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();