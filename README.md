# A Tiempo?

#### Video Demo: https://youtu.be/3yXCROBEeno?si=cTByjVZUfGXx91Z

## Description

A Tiempo? is a bilingual Flask application for exploring the historical performance
of flights observed at Argentine airports. Its included SQLite database contains
417,278 records from December 23, 2024 through July 29, 2026. The data is historical,
not predictive, and does not provide live flight status.

Users can search by flight number, route or airline and select the last 90 days, last
365 days or the complete dataset. Reports show observation and cancellation rates,
the median difference from the published schedule, results against a 30-minute
threshold, monthly trends and recorded aircraft models. The comparison page places
two or three searches side by side. The complete interface is available in English
and Spanish.

Departures compare actual and scheduled takeoff times; inbound arrivals compare
actual and scheduled landing times. These are runway events, not airline punctuality
measurements based on gate or off-block times. Only `CANCELLED` records count as
cancellations. `NO OPERA` is excluded from rate denominators, while `DIVERTED` counts
as analysed but outside the threshold. Invalid times and differences earlier than six
hours are excluded. Reports with fewer than ten usable observations are labelled as
having insufficient data.

Flight numbers can repeat during a daily rotation, so the application keeps the
earliest scheduled observation per date and selects its recurring movement from the
complete history before applying the requested period. Route searches prefer a
departure from the origin and fall back to an arrival at the destination when the
foreign departure is outside the Argentine dataset. These choices keep the meaning
of a report consistent across time periods.

## Project files

- `app.py` creates the Flask application, validates form values and defines the home,
  report, comparison, methodology and error routes.
- `analytics.py` contains the parameterized SQL queries and calculations for timing,
  cancellations, monthly results, routes and aircraft.
- `localization.py` stores the English and Spanish text and formats dates and numbers.
- `templates/layout.html` provides the shared page structure. `home.html`,
  `report.html`, `compare.html` and `error.html` render the application pages.
  `methodology.html` loads the longer explanation from `methodology_en.html` or
  `methodology_es.html`.
- `static/styles.css` defines the responsive design, `script.js` handles the small
  browser interactions and `favicon.svg` is the site icon. `static/vendor/` contains
  Bootstrap locally.
- `database/flights.db` is the prepared dataset. `database/schema.sql` documents its
  tables, relationships, indexes and readable view.
- `requirements.txt` lists Flask and CS50, the two required Python packages.

## Running the project

Python 3.11 or later is recommended. From the project directory, run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app run
```

Then open `http://127.0.0.1:5000`. The database and Bootstrap files are local, so the
application does not require an Internet connection after installation.

## Design decisions

The application separates request handling in `app.py` from queries and calculations
in `analytics.py`. Both languages share the same routes, templates and analysis;
`lang=es` changes only text and formatting. Report forms use `GET` because searches
only read data and their URLs can be shared. SQL values are passed as parameters
rather than inserted into query strings.

Monthly charts and aircraft bars are HTML elements styled with CSS. JavaScript
only enhances the comparison form and route-list dialog; searches and validation
continue to work through Flask.

## Data source and limitations

The database was prepared from the public [Failbondi
dump](https://failbondi.fail/api/dump); Failbondi's [source code is available on
GitHub](https://github.com/catdevnull/flybondi.fail). The original dump and importer
are not included. The source may be incomplete or inaccurate and covers only flights
observed at Argentine airports. Results should not be used as operational travel
information.

## Acknowledgements

Historical data was obtained from Failbondi. OpenAI Codex assisted with database
preparation, code, design and documentation, as disclosed in source-code comments
under the CS50 academic honesty policy.
