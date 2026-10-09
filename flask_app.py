import ipaddress
import time
from datetime import datetime, timedelta, timezone

import requests
from flask import Flask, abort, redirect, render_template, request, send_file, url_for
import os

app = Flask(__name__)

# Add IP addresses here (as strings) to block them.
BANNED_IPS = set()

LOOKUP_URL = "http://ip-api.com/json/"  # the free plan is HTTP only
CACHE_SECONDS = 3600
FAILED_CACHE_SECONDS = 300
CACHE_MAX_ENTRIES = 2000
_cache = {}


def client_ip():
    raw = request.headers.get("X-Real-IP") or request.remote_addr or ""
    try:
        return str(ipaddress.ip_address(raw.strip()))
    except ValueError:
        return None


def lookup_location(ip):
    """Returns {"lon": float, "place": str} or None. Cached in memory only."""
    now = time.time()
    hit = _cache.get(ip)
    if hit and hit[0] > now:
        return hit[1]
    result = None
    try:
        resp = requests.get(
            LOOKUP_URL + ip,
            params={"fields": "status,lon,city,country"},
            timeout=4,
        )
        data = resp.json()
        if data.get("status") == "success" and isinstance(data.get("lon"), (int, float)):
            place = ", ".join(p for p in (data.get("city"), data.get("country")) if p)
            result = {"lon": float(data["lon"]), "place": place or "Unknown"}
    except (requests.RequestException, ValueError):
        result = None
    if len(_cache) >= CACHE_MAX_ENTRIES:
        _cache.clear()
    ttl = CACHE_SECONDS if result else FAILED_CACHE_SECONDS
    _cache[ip] = (now + ttl, result)
    return result


def format_offset(seconds):
    sign = "+" if seconds >= 0 else "-"
    hours, rest = divmod(abs(seconds), 3600)
    minutes, secs = divmod(rest, 60)
    return "%s%02d:%02d:%02d" % (sign, hours, minutes, secs)


def solar_context():
    ip = client_ip()
    info = lookup_location(ip) if ip else None
    if not info or not -180 <= info["lon"] <= 180:
        return {"ok": False}
    lon = info["lon"]
    offset = round(lon * 240)  # 4 minutes of time per degree = 240 seconds
    now = datetime.now(timezone.utc) + timedelta(seconds=offset)
    return {
        "ok": True,
        "offset_seconds": offset,
        "offset_text": format_offset(offset),
        "longitude_text": "%.4f\u00b0 %s" % (abs(lon), "E" if lon >= 0 else "W"),
        "place": info["place"],
        "clock": now.strftime("%H:%M:%S"),
        "date_text": "%s %d %s %d" % (now.strftime("%A"), now.day, now.strftime("%B"), now.year),
    }


@app.before_request
def block_banned():
    ip = client_ip()
    if ip and ip in BANNED_IPS:
        abort(403)


@app.after_request
def security_headers(resp):
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Permissions-Policy"] = "geolocation=(self), camera=(), microphone=()"
    resp.headers["Content-Security-Policy"] = (
        "default-src 'self'; img-src 'self' data:; frame-ancestors 'none'; "
        "form-action 'self'; base-uri 'none'"
    )
    if request.endpoint != "static":
        resp.headers["Cache-Control"] = "private, no-store"
    return resp


@app.route("/")
def home():
    return render_template("time.html", **solar_context())


@app.route("/fullscreenclock/")
def fullscreenclock():
    return render_template("fulltime.html", **solar_context())


@app.route("/customcalc/")
def customcalc():
    return render_template("custom_calc.html")


@app.route("/whatisthis/")
def whatisthis():
    return render_template("whatisthis.html")


@app.route("/terms/")
def terms():
    return render_template("terms.html")


@app.route("/privacy/")
def privacy():
    return render_template("privacy.html")


@app.route("/logoo/")
def logo():
    path = os.path.join(app.root_path, "templates", "eztime-logo.png")
    if not os.path.exists(path):
        abort(404)
    return send_file(path, mimetype="image/png", max_age=86400)


# Old URLs keep working.
@app.route("/termsandconditions/")
@app.route("/termsandconditionswebsite/")
def old_terms():
    return redirect(url_for("terms"), code=301)


@app.route("/blog/")
def old_blog():
    return redirect(url_for("whatisthis"), code=301)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
