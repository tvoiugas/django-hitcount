/**
 * Legacy companion for {% insert_hit_count_js_variables for [object] %}.
 *
 * Kept (despite the name) for sites that still include it: it no longer needs
 * jQuery. New code should use {% insert_hit_count_js for [object] %} instead.
 *
 * Reads the global `hitcountJS` written by the template tag and POSTs the hit.
 * The CSRF token is read from the "csrftoken" cookie, so the view rendering
 * the page must set it (e.g. with @ensure_csrf_cookie).
 */
(function () {
  function getCookie(name) {
    var cookies = document.cookie ? document.cookie.split(";") : [];
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        return decodeURIComponent(cookie.substring(name.length + 1));
      }
    }
    return null;
  }

  function countHit() {
    if (typeof hitcountJS === "undefined") {
      // loaded on every page: only do something if a hit is to be counted
      return;
    }

    fetch(hitcountJS.hitcountURL, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": getCookie("csrftoken") || "",
        "X-Requested-With": "XMLHttpRequest"
      },
      body: "hitcountPK=" + encodeURIComponent(hitcountJS.hitcountPK)
    }).then(function (response) {
      return response.json();
    }).then(function (data) {
      console.log(data); // just so you can see the response
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", countHit);
  } else {
    countHit();
  }
})();
