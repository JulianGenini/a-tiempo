# A Tiempo?

#### Video Demo: TODO

## Description

A Tiempo? is a bilingual Flask web application for exploring the historical
performance of flights observed at Argentine airports. It includes 417,278 records
from December 23, 2024 through July 29, 2026 and works locally after installation.
The data is historical, not predictive, and does not provide live flight status.

Users can search by flight number, route or airline and choose the last 90 days, last
365 days or the complete dataset. Reports show:

- observations and cancellation rates;
- the typical (median) difference from the published schedule;
- results within or outside a 30-minute threshold;
- monthly trends and commonly recorded aircraft models.

The comparison page places two or three flights, routes or airlines side by side for
the same period. The complete interface is available in English and Spanish.

## Technologies

The project follows the same web stack introduced in CS50x. Python and Flask handle
the application routes and prepare the information shown on each page. SQL is used
to read an SQLite database through CS50's `SQL` helper. Jinja templates generate the
HTML, while CSS, Bootstrap and a small amount of JavaScript provide the design and
browser interactions.

All searches use the database included in the repository, so the application does
not depend on an external API or a separate database server. Bootstrap is also stored
locally. After the two Python packages in `requirements.txt` have been installed, the
site can therefore run without an Internet connection.

## How the analysis works

For departures, the application compares actual takeoff time (ATD) with scheduled
departure time (STD). For inbound arrivals, it compares actual landing time (ATA)
with scheduled arrival time (STA). A result is considered within the analysis
threshold when it is no more than 30 minutes late.

These are runway events, not airline punctuality measurements based on gate or
off-block times. Departure differences may include taxi-out time, while arrival
results describe landing rather than arrival at the gate.

Only records explicitly marked `Cancelled` count as cancellations. `NO OPERA`
records are excluded from rate denominators, while `DIVERTED` records count as
analysed flights outside the threshold. Records without a valid event time and
differences earlier than six hours are excluded. Reports with fewer than ten usable
observations are labelled as having insufficient data.

The typical difference is the median rather than the average. The values are sorted
and the middle one is selected, so an isolated very long delay does not distort the
number shown to the user. If there is an even number of values, the two middle values
are averaged. Monthly results repeat the same rules for each calendar month.

Flight numbers sometimes appear more than once on the same date because the same
number can be reused later in a daily rotation. The application keeps the earliest
scheduled observation for each date, identifies whether that flight is most commonly
observed as a departure or arrival, and removes directions that appear only once when
recurring directions exist. This choice is made using the complete history before the
selected 90-day or 365-day filter is applied. As a result, changing the period changes
the sample but does not unexpectedly change which service the flight number means.

Route searches first look for a departure observed at the requested origin. If none
exists, the application looks for an arrival observed at the destination. This is
useful for international inbound routes whose foreign departure is outside the
Argentina-only dataset. Airline reports use recorded departures.

## Project structure

`app.py` is the entry point. It creates the Flask application, opens
`database/flights.db`, validates the values received from each form and defines the
home, flight, route, airline, comparison, methodology and error routes. It passes the
result of each search to the appropriate template.

`analytics.py` contains the database queries and calculations. Its functions select
the observations for a search, calculate cancellation and timing rates, group records
by month, list the available routes and summarize aircraft models. Keeping these
functions outside `app.py` makes the routes shorter and separates page handling from
data analysis.

`localization.py` stores the English and Spanish interface text in one dictionary. It
also contains small helpers for dates, thousands separators and decimal separators.
Both languages use the same Flask routes, SQL queries and templates; the `lang`
parameter only changes the text and formatting.

Inside `templates/`, `layout.html` provides the shared navigation, dataset notice and
footer. `home.html`, `report.html`, `compare.html` and `error.html` contain the pages
rendered by Flask. `methodology.html` selects either `methodology_en.html` or
`methodology_es.html`, which hold the longer explanation in each language. Template
inheritance avoids repeating the full HTML document on every page.

Inside `static/`, `styles.css` contains the responsive visual design and
`script.js` contains two small interactions: it updates the examples on the comparison
form and controls the dialog that lists routes. `favicon.svg` is the site icon. The
`vendor/` directory contains the local Bootstrap CSS and JavaScript used by the
navigation bar and the search tabs.

`database/flights.db` is the prepared SQLite database used by the application.
`database/schema.sql` documents its normalized tables, relationships, indexes and
readable view. The schema is included so the organization of the data can be examined,
but the populated database is already ready to use.

`requirements.txt` lists Flask and the CS50 library, the only Python packages that
must be installed. Queries are parameterized through CS50's `SQL` helper, keeping
visitor input separate from SQL statements.

## How to run the project

From a terminal in the project directory, install the two dependencies once:

```bash
pip install -r requirements.txt
```

Then start Flask in the same way as the CS50 Finance project:

```bash
flask run
```

Because the entry point is named `app.py`, Flask finds it automatically; no `--app`
option or custom command is needed. Open the URL printed in the terminal, normally
`http://127.0.0.1:5000`. Stop the server with `Ctrl-C`.

## Design decisions

The interface uses a shared layout so navigation, language controls and the footer
remain consistent. Separate routes for flight, route and airline searches make each
validation path explicit. The forms use `GET` because a report only reads data and its
parameters can be kept in a link. SQL values are passed with `?` placeholders through
`db.execute` instead of being inserted into query strings.

The monthly charts and aircraft bars are ordinary HTML elements styled with CSS.
This avoids adding a charting framework for a small visual feature and keeps the code
within the HTML, CSS and JavaScript covered by CS50. JavaScript only improves two
interactions; searches, reports and validation continue to work through Flask forms.

English is the default language. Spanish pages add `lang=es` to their links and form
submissions. This approach avoids duplicating routes or calculations, although it
requires all visible interface phrases to have both translations.

## Data source and limitations

The database was prepared from the public Failbondi dump at
<https://failbondi.fail/api/dump>. Its source code is available at
<https://github.com/catdevnull/flybondi.fail>.

The original dump and importer are not included, so the preparation process cannot
be reproduced from this repository alone. The source may contain incomplete or
inaccurate records and covers only services observed at Argentine airports. Results
describe the included historical observations and should not be used as operational
travel information.

## Acknowledgements

Historical data was obtained from Failbondi. OpenAI Codex assisted with database
preparation, code, testing, design and documentation, as disclosed in source-code
comments in accordance with the CS50 academic honesty policy.
