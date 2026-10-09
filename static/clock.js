(function () {
  var clock = document.getElementById("clock");
  if (!clock) { return; }
  var offset = parseInt(clock.getAttribute("data-offset"), 10);
  if (isNaN(offset)) { return; }
  var dateEl = document.getElementById("date");
  var days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  var months = ["January", "February", "March", "April", "May", "June", "July",
                "August", "September", "October", "November", "December"];

  function pad(n) { return n < 10 ? "0" + n : String(n); }

  function tick() {
    var d = new Date(Date.now() + offset * 1000);
    clock.textContent = pad(d.getUTCHours()) + ":" + pad(d.getUTCMinutes()) + ":" + pad(d.getUTCSeconds());
    if (dateEl) {
      dateEl.textContent = days[d.getUTCDay()] + " " + d.getUTCDate() + " " +
        months[d.getUTCMonth()] + " " + d.getUTCFullYear();
    }
    setTimeout(tick, 1000 - (Date.now() % 1000) + 5);
  }
  tick();
})();
