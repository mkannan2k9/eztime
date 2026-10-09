# EZTime

A small open-source web app that shows local mean solar time for your longitude. The clock runs in the browser, and the server only estimates your longitude and sends a single offset.

Live site: https://eztime.pythonanywhere.com

## What it shows

Local mean solar time is the time kept by an imaginary Sun that moves at a steady speed. The Earth turns 15 degrees of longitude per hour, which is 4 minutes per degree, so:

```
solar time = UTC + (longitude x 4 minutes) east positive, west negative
```


For example, Singapore at about 103.8 degrees east is roughly 6 hours 55 minutes ahead of UTC in solar time, while its civil time zone is UTC+8.

This is not your civil time zone. It ignores daylight saving and the equation of time, so it can differ from your watch and from a sundial.

## Features

- Clock: a live solar-time clock for your approximate location.
- Full screen clock: a large, distraction-free display.
- Calculator: enter any longitude, or use your device location (read in your browser only).
- About page: explains the calculation and its limits.
- Plain design: system fonts, no third-party assets, strict Content-Security-Policy.

## How it works

1. The server reads the visitor's IP address (`X-Real-IP`, falling back to the connection address) and validates it.
2. It asks the free [ip-api.com](https://ip-api.com/) service for an approximate longitude, city and country.
3. Results are cached in memory for one hour (failed lookups for five minutes) and cleared on restart. The cache is never written to disk.
4. The server calculates `offset = round(longitude x 240)` seconds and renders the page with that offset.
5. `clock.js` computes `Date.now() + offset` once per second, so the display stays accurate without more requests.

If a lookup fails, the page says so and links to the calculator.

### Routes

| Route | Method | Purpose |
|---|---|---|
| `/` | GET | Solar time clock |
| `/fullscreenclock/` | GET | Full screen clock |
| `/customcalc/` | GET | Longitude calculator |
| `/whatisthis/` | GET | About the calculation |
| `/privacy/` | GET | Privacy Policy |
| `/terms/` | GET | Terms of Use |
| `/logoo/` | GET | Site icon |
| `/termsandconditions/`, `/termsandconditionswebsite/`, `/blog/` | GET | Redirect to the current pages |

## Getting started

Requirements: Python 3.10 or newer.

```bash
git clone <your-repository-url>
cd <your-repository-folder>
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python flask_app.py
```

Open http://127.0.0.1:5000. When you run the app locally, your address is a private one, so the IP lookup fails and the home page shows the "could not determine location" message. Use the calculator to try the clock locally.

## Configuration

EZTime needs no API keys. The settings at the top of `flask_app.py` are:

| Setting | Default | Meaning |
|---|---|---|
| `BANNED_IPS` | empty set | IP addresses to block with a 403 |
| `CACHE_SECONDS` | 3600 | How long a successful lookup is cached |
| `FAILED_CACHE_SECONDS` | 300 | How long a failed lookup is cached |
| `LOOKUP_URL` | `http://ip-api.com/json/` | Geolocation endpoint |

## Deployment (PythonAnywhere)

1. Upload the project and create a virtualenv.
2. Install dependencies inside that virtualenv: `pip install -U -r requirements.txt`.
3. Set the virtualenv path in the **Web** tab.
4. In the WSGI file, import the app:

   ```python
   from flask_app import app as application
   ```

5. Reload the web app.

On PythonAnywhere the `X-Real-IP` header carries the visitor's address, which the app uses for the lookup.

## Project structure
```
flask_app.py Flask app and IP lookup
requirements.txt Python dependencies
static/
style.css Site styles
clock.js Live clock
calc.js Calculator
templates/
base.html Shared layout
time.html Clock page
fulltime.html Full screen clock
custom_calc.html Longitude calculator
whatisthis.html About page
privacy.html Privacy Policy
terms.html Terms of Use
eztime-logo.png Site icon
```


## Privacy and limitations

- The home page sends the visitor's IP address to ip-api.com to estimate a location. The free plan of that service works over plain HTTP and is intended for non-commercial use, with a limit of 45 requests per minute. See the in-app [Privacy Policy](templates/privacy.html) for details.
- IP-based locations can be off by many kilometres, and are often wrong on mobile networks or VPNs.
- The calculator's device-location button uses your browser's location prompt, and the result stays in your browser.
- Solar time is informational. Do not use it for navigation, safety, legal or financial decisions.

## AI Use Declaration

The original code for this project was written by the author. It was later cleaned up, and its comments were added, with the help of AI tools. This README was also written with AI. The author reviewed the project and is responsible for its contents.

## Contributing

Issues and pull requests are welcome. For larger changes, please open an issue first to discuss what you would like to change.

## License

Released under the [MIT License](LICENSE).

## Author

Created by [Kannan Murugapandian](https://kannan.bearblog.dev).
