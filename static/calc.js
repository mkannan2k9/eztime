(function () {
  var input = document.getElementById("lon");
  var out = document.getElementById("result");
  var err = document.getElementById("error");
  var btn = document.getElementById("use-location");
  var status = document.getElementById("loc-status");
  if (!input || !out) { return; }

  var days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  var months = ["January", "February", "March", "April", "May", "June", "July",
                "August", "September", "October", "November", "December"];

  function pad(n) { return n < 10 ? "0" + n : String(n); }

  function formatOffset(sec) {
    var sign = sec >= 0 ? "+" : "-";
    var a = Math.abs(sec);
    return sign + pad(Math.floor(a / 3600)) + ":" + pad(Math.floor((a % 3600) / 60)) + ":" + pad(a % 60);
  }

  function render() {
    var v = parseFloat(input.value);
    if (input.value.trim() === "") {
      out.hidden = true; err.textContent = ""; return;
    }
    if (isNaN(v) || v < -180 || v > 180) {
      out.hidden = true;
      err.textContent = "Enter a longitude between -180 and 180.";
      return;
    }
    err.textContent = "";
    var offset = Math.round(v * 240);
    var d = new Date(Date.now() + offset * 1000);
    document.getElementById("res-offset").textContent = formatOffset(offset);
    document.getElementById("res-time").textContent =
      pad(d.getUTCHours()) + ":" + pad(d.getUTCMinutes()) + ":" + pad(d.getUTCSeconds());
    document.getElementById("res-date").textContent =
      days[d.getUTCDay()] + " " + d.getUTCDate() + " " + months[d.getUTCMonth()] + " " + d.getUTCFullYear();
    document.getElementById("res-working").textContent =
      v + " degrees x 4 minutes = " + (v * 4).toFixed(4) + " minutes from UTC";
    out.hidden = false;
  }

  function loop() { render(); setTimeout(loop, 1000 - (Date.now() % 1000) + 5); }

  input.addEventListener("input", render);

  if (btn) {
    btn.addEventListener("click", function () {
      if (!navigator.geolocation) {
        status.textContent = "Your browser does not support location.";
        return;
      }
      status.textContent = "Requesting your location...";
      navigator.geolocation.getCurrentPosition(function (pos) {
        input.value = pos.coords.longitude.toFixed(4);
        status.textContent = "Location read in your browser. It is not sent to EZTime.";
        render();
      }, function () {
        status.textContent = "Could not get your location. Enter a longitude instead.";
      }, { timeout: 10000 });
    });
  }
  loop();
})();
