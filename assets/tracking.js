/**
 * The Ritual Journal Collective — Tracking
 * Plausible analytics + product link UTM injection
 */

var PLAUSIBLE_URL = "https://plausible.io/api/event";
var SITE_DOMAIN = "theritualjournalcollective.com";

function sendPlausibleEvent(name, props) {
  if (!navigator.sendBeacon) return;
  navigator.sendBeacon(
    PLAUSIBLE_URL,
    JSON.stringify({
      n: name,
      u: window.location.href,
      d: SITE_DOMAIN,
      r: document.referrer || null,
      p: props ? JSON.stringify(props) : undefined,
    }),
  );
}

function getArticleSlug() {
  var parts = window.location.pathname.split("/");
  var last = parts[parts.length - 1].replace(".html", "");
  return last || "homepage";
}

// Product link click tracking
document.addEventListener(
  "click",
  function (e) {
    var link = e.target.closest("a[href]");
    if (!link) return;
    var href = link.getAttribute("href") || "";
    var isProduct =
      href.includes("gumroad.com") ||
      href.includes("buy.stripe.com") ||
      href.includes("howmindswork.org");
    if (!isProduct) return;
    sendPlausibleEvent("product_click", {
      article: getArticleSlug(),
      product_url: href.split("?")[0],
      utm_campaign: getArticleSlug(),
    });
  },
  true,
);

// UTM injection + pageview on load
document.addEventListener("DOMContentLoaded", function () {
  var slug = getArticleSlug();

  // Inject UTM params into all product links
  document
    .querySelectorAll(
      'a[href*="gumroad.com"], a[href*="buy.stripe.com"], a[href*="howmindswork.org"]',
    )
    .forEach(function (link) {
      try {
        var url = new URL(link.href, window.location.origin);
        url.searchParams.set("utm_source", "trjc");
        url.searchParams.set("utm_medium", "blog");
        url.searchParams.set("utm_campaign", slug);
        link.href = url.toString();
      } catch (err) {
        // skip malformed URLs
      }
    });

  // Send pageview
  sendPlausibleEvent("pageview", { slug: slug });

  // Scroll depth tracking
  var scrollDepths = { 25: false, 50: false, 75: false, 100: false };
  window.addEventListener(
    "scroll",
    function () {
      var scrollPct = Math.round(
        (window.scrollY /
          (document.documentElement.scrollHeight - window.innerHeight)) *
          100,
      );
      [25, 50, 75, 100].forEach(function (depth) {
        if (!scrollDepths[depth] && scrollPct >= depth) {
          scrollDepths[depth] = true;
          sendPlausibleEvent("scroll_depth", {
            depth: depth,
            article: getArticleSlug(),
          });
        }
      });
    },
    { passive: true },
  );

  // Time on page (30s = engaged reader, 2min = deep read)
  setTimeout(function () {
    sendPlausibleEvent("time_30s", { article: getArticleSlug() });
  }, 30000);
  setTimeout(function () {
    sendPlausibleEvent("time_2min", { article: getArticleSlug() });
  }, 120000);
});
