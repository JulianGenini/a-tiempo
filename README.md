# A Tiempo?

#### Video Demo: TODO

#### Description

A Tiempo? is a local web application for exploring how flight services observed at
Argentine airports performed against their published schedules. It answers historical
questions about runway timing, typical differences and comparisons between routes or
airlines. It uses 417,278 observations stored in an included SQLite database, covering
December 23, 2024 through July 29, 2026.

The project was created for CS50x and combines Python, SQL, Flask, HTML, CSS and
JavaScript. Historical searches use only local files and need no Internet connection
after installation. The fixed dataset is descriptive rather than predictive and does
not show current flight status.

## Main features

The home page lets a visitor search by flight number, route or airline. Because the
source can repeat a number during a daily rotation, a flight-number report keeps the
earliest scheduled event per date. It then selects the recurring movement type and
removes one-date directions when recurrent routes exist. This canonical choice uses
the complete stored history before the selected period is applied, so changing the
period changes the sample without changing which event the number represents.

A route report prefers a departure observed at its origin. If an international
inbound route has no observed departure because its origin is outside Argentina, the
application uses the arrival recorded at its Argentine destination. Airline reports
use recorded departures. The Compare page places two or three flights, routes or
airlines side by side for the same period. When a comparison mixes departures and
inbound arrivals, the page explains their different observed events and shared
30-minute threshold.

Reports show usable observations, timing and cancellation rates, average and median
differences, monthly history and commonly recorded aircraft models. Aircraft details
are historical context, not a future assignment. Visitors can select the final 90
days, final 365 days or all stored history.

## Project files

`app.py` creates the Flask application and its page routes. It validates GET
parameters, calls `analytics.py` and passes results to Jinja templates.

`analytics.py` contains SQL queries and calculations. It normalizes searches, chooses
the observable event, calculates metrics and summarizes months, routes and aircraft.
It mainly uses loops, lists, dictionaries, sets and conditionals.

The `templates` directory contains the shared layout and the home, report, compare,
methodology and error pages. `static/styles.css` defines the responsive visual design.
Bootstrap is stored locally in `static/vendor` and supports the navigation and search
tabs. `static/script.js` updates comparison examples and opens or closes the route-list
dialog. `static/favicon.svg` contains the project icon.

`database/flights.db` is the prepared SQLite database used by the application.
`database/schema.sql` documents its normalized tables, foreign keys, indexes and the
readable `flight_details` view; it does not populate the database. `requirements.txt`
lists the Python dependencies. The `tests` directory contains unit tests for the
calculations and integration tests for Flask routes. `.github/workflows/tests.yml`
runs those tests on configured GitHub branches.

## How the analysis works

The browser submits a GET form, a Flask route validates its values, and
`analytics.py` runs a parameterized query with CS50's `SQL` helper. Query parameters
keep visitor input separate from the SQL statement. Python then calculates the report
and Flask renders the finished HTML with Jinja.

For departures, the project compares actual takeoff time (ATD) with scheduled
departure time (STD) and counts a result as within the project threshold when it is
no more than 30 minutes late. The source has no departure off-block times, so this is
not the airline metric based on AOBT and SOBT: taxi-out time remains in the
difference. For inbound arrivals, it compares landing time (ATA) with scheduled
arrival time (STA) and uses the same 30-minute threshold. Arrival results describe
runway landing, not arrival at the gate.

Only the explicit source status `Cancelled` counts as a cancellation. `NO OPERA` is
kept separate and removed from both rate denominators. Records without usable times
do not enter timing calculations, and absolute differences above six hours are
excluded as likely source errors. Reports with fewer than ten usable observations
receive an “Insufficient data” label. Placeholder airport values such as `--I`, `-AR`
and `-BR` are not displayed as routes, although a record can still contribute to
timing metrics when its times are valid.

## Data source and limitations

The prepared database came from a Failbondi dump. The original raw dump and the
importer used during database preparation are not included in this repository, so the
data-preparation step cannot be reproduced from the submitted files alone. The
included schema documents the final structure, while the database provides the fixed
records needed to run the project.

The source does not guarantee completeness or accuracy. The dataset contains only
services observed at Argentine airports, and the reconstruction rules make
conservative choices when source rows are repeated or incomplete. Results describe
past observations and are not a promise of future performance. Travelers should
always confirm operational information with their airline or airport.

## Installation and tests

Python 3.11 or later is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app run
```

Open `http://127.0.0.1:5000`. Run the automated tests with:

```bash
python -m unittest discover -s tests -v
```

## Design decisions

The interface uses an airport-information style with a dark navigation bar, warm
background and signal-yellow accent. Monthly histories use HTML and CSS bars instead
of a charting library, keeping the project local and easier to inspect. A shared
layout avoids repeating navigation and footer markup, while separate Flask routes
keep each type of search explicit.

## Acknowledgements

Historical data was obtained from a prepared Failbondi dump. OpenAI Codex assisted
with database preparation, code, testing, design and documentation. That assistance
is disclosed in source-code comments in accordance with the CS50 academic honesty
policy.
