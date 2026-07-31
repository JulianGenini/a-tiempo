# A Tiempo?

#### Video Demo: TODO

#### Description

A Tiempo? is a local web application that helps passengers explore how services
observed at Argentine airports performed against their published schedules. A current
flight board can tell a traveler what is happening today, but it cannot answer broader
questions: How often did this service use the runway close to schedule? What was its
typical time difference? Does one route look different from another? This project
answers those questions using 417,278 historical airport observations stored in an
included SQLite database.

The project was created as a final project for CS50x. It combines Python, SQL, Flask,
HTML, CSS and JavaScript while deliberately keeping the code close to concepts taught
in the course. It does not require PostgreSQL, Docker or an Internet connection for
historical analysis. All application features use the included database and work
without an Internet connection.

## Main features

Home is the main starting point. A visitor can enter a flight number, select an
origin and destination, choose an airline, or start a comparison. Each choice opens
the relevant historical report.

Reports prefer departures at the searched origin. International inbound routes whose
foreign origin is outside the dataset use the arrival recorded at their Argentine
destination. Reports show the usable sample, percentage within the applicable timing
threshold, cancellation rate, average time difference, median time difference and a
monthly history drawn with regular HTML and CSS. They also show the
aircraft models most commonly recorded in that selection. Aircraft information is
historical context, not a confirmation of the equipment assigned to a future flight.

For flight-number searches, the application keeps the earliest scheduled event for
each date and then selects the recurring movement type. This addresses a source-data
issue where a number can be repeated across later events in the same daily rotation.
When recurrent routes exist, it also removes directions seen on only one date as
isolated source anomalies. Route searches prefer a departure and fall back to an
arrival for inbound international services. Airline searches use departures.

The Compare page places two or three items of the same type side by side. For example,
a visitor can compare AEP-COR with AEP-MDZ, or compare airline codes AR, FO and WJ.

The interface always states that the database covers December 23, 2024 through July
29, 2026. This is important because the application describes a fixed historical
dataset; it does not show or imply current operational status.

## Project files

`app.py` creates the Flask application and defines its routes. Each route reads values
from a standard GET form, validates them, asks `analytics.py` for data and passes the
result to a Jinja template. The file also contains the simple rules used to parse
comparison items and display user-friendly error pages.

`analytics.py` contains the SQL queries and calculations. It searches the normalized
database, chooses the observable event, reconstructs one daily observation for a flight
number, calculates medians with a sorted Python list and builds monthly groups. The functions use
ordinary loops, lists, dictionaries and conditionals so their behavior can be followed
line by line.

The `templates` directory contains the Jinja HTML pages. `layout.html` defines the
shared navigation and footer. The other templates cover the home page, report,
comparison, methodology and error states. `static/styles.css` contains a
simple responsive design. Bootstrap 5.3.8 is stored locally in `static/vendor` and is
used for the responsive navigation; the rest of the design is original CSS.
`static/script.js` uses one basic DOM event to update the examples shown in the
comparison form.

`database/flights.db` is the included SQLite database. `database/schema.sql`
documents its tables, foreign keys, indexes and readable `flight_details` view. The
database is normalized into flights, airports, airlines, aircraft and flight statuses.
The `tests` directory contains `unittest` tests for calculations and Flask
routes.

## How the code works

The complete request cycle follows the same pattern used in CS50:

1. The browser submits a GET form, such as `/route?origin=AEP&destination=COR`.
2. A Flask route reads the values with `request.args`.
3. The route validates the values and calls a function in `analytics.py`.
4. That function runs a parameterized SQL query using CS50's `SQL` helper.
5. Python loops over the returned rows and calculates the required metrics.
6. Flask calls `render_template`, and Jinja places the values into HTML.
7. The browser receives and displays the finished page.

Parameterized queries are important because visitor input is passed separately from
the SQL statement. The database therefore treats input as data instead of executable
SQL.

## Schedule-performance rules

The default period is the final 365 days in the database. Visitors can instead choose
90 days or all history. A departure is within the project threshold when its actual
takeoff time is no more than 30 minutes after STD. An inbound arrival is within its
threshold when its landing time is no more than 15 minutes after STA. Cancelled flights
do not enter that timing calculation.

Only the explicit source status `Cancelled` counts as a cancellation. `NO OPERA` is
kept as an independent “not operating” status. It is not counted as cancelled, within
the applicable threshold or delayed and is removed from both rate denominators.

Some source records contain impossible date differences. A Tiempo? excludes delays
whose absolute value exceeds six hours from time-difference calculations, while
showing the number of excluded values. Reports with fewer than ten usable observations
receive an “Insufficient data” label.

The source also contains placeholder airport values such as `--I`, `-AR` and `-BR`.
They are not displayed as routes. A record can still contribute to timing metrics when
its times are valid, while the report states that its counterpart IATA code is missing.

Departure results compare actual takeoff time (ATD) with scheduled departure time
(STD). The raw dump contains no departure
off-block times: the `blockoff` field is empty in all 269,377 departure records.
Therefore, this is not the same as the airline operational metric based on AOBT and
SOBT, and taxi-out time remains in the displayed difference. The 30-minute project
threshold accounts for this limitation without pretending to reproduce the airline
D15 metric. Arrival results compare landing time (ATA) with scheduled arrival time
(STA); they do not measure arrival at the gate.

## Installation and use

Python 3.11 or later is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app run
```

Then open `http://127.0.0.1:5000`.

Run the automated tests with:

```bash
python -m unittest discover -s tests -v
```

## Design decisions and limitations

The application uses a restrained airport-information style: a dark petroleum
navigation bar, warm background, signal-yellow accent and compact data tables. A
small plane symbol inside a yellow airport-style sign acts as the project mark; it is
regular HTML text styled with CSS, not an external image. The home page puts a clear
explanation, database summary and search controls in the first screen. A locally
stored Bootstrap navbar and Bootstrap tabs make navigation and search responsive
without introducing a frontend framework architecture. Rankings, monthly trends,
comparisons and methodology topics are contained in bordered cards so visitors can
scan the page easily. Ranking items link directly to their reports, allowing someone
to discover the application without already knowing a flight number. Green, amber
and red are reserved for performance labels. IATA codes, dates and percentages use a
system monospace font. Charts are simple HTML bars rather than a JavaScript charting
library, keeping the implementation understandable and independent of external
assets.

The dataset covers December 23, 2024 through July 29, 2026. It came from a Failbondi
dump based on public Aeropuertos Argentina flight information. The source does not
guarantee completeness or accuracy. The application prefers departure records and
uses arrivals for inbound international routes when their foreign departure is not
observed. It applies a conservative daily reconstruction to flight-number searches. It is
descriptive rather than predictive. Travelers should always confirm operational
information with their airline or airport.

Questions an evaluator might ask include: How does a SQL JOIN connect a flight to its
airline? Why are query parameters safer than string formatting? Why does a flight-number
search keep one event per date? Why is ATD–STD different from AOBT–SOBT? How is an
even-sized median calculated? Why is NO OPERA not a cancellation? Why are differences
above six hours excluded? Each answer is documented in the corresponding short function
or in the Methodology page.

## Acknowledgements

Historical data was obtained from a Failbondi dump and originated from public
Aeropuertos Argentina information. OpenAI Codex assisted with database preparation,
code, testing, design and documentation. That assistance is cited in source-code
comments in accordance with the CS50 academic honesty policy.
