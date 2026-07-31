# Observed public Aeropuertos Argentina API reference

**Research date:** July 29, 2026  
**Status:** Working reference, not official documentation  
**Public site:** [aeropuertosargentina.com](https://www.aeropuertosargentina.com/en)

## Purpose and limits

This document records endpoints declared or used by the public Aeropuertos Argentina
website. It does not describe administrative, authenticated or private systems.

The research used:

- low-volume observation of requests made by public pages;
- static inspection of service and configuration bundles published by the site;
- low-volume GET requests to those same public routes;
- comparison with the public
  [Failbondi collector](https://github.com/catdevnull/flybondi.fail/blob/master/trigger/scrap-aerolineas.ts).

No write endpoint, private credential, reservation, payment system or personal data was
tested.

## Base URL and access

Observed base URL:

```text
https://webaa-api-h4d5amdfcze7hthn.a02.azurefd.net/web-prod/v1
```

The tested GET requests worked without cookies, tokens or API keys. The current
frontend adds `Accept-Language`. Older community code included a `Key` header, but it
was not required in the tests and should not be copied.

The server restricts browser CORS to the official website, so calls from this project
must be made by the Flask backend. Responses were observed with a 60-second public
cache and an ETag. No public rate-limit policy, OpenAPI specification, developer
portal, SLA or data license was found.

Public accessibility does not by itself grant permission for persistent collection or
redistribution.

## Main endpoints

| Method | Endpoint | Observed purpose |
|---|---|---|
| `GET` | `/api-aa/all-flights` | Current or recent flight status |
| `GET` | `/api-aa/flights-fth` | Future flight schedules |
| `GET` | `/api-aa/all-airports` | Airport search catalog |
| `GET` | `/api-aa/all-airports-by-id` | Airport detail by IATA |
| `GET` | `/airports` | Airports managed by the company |
| `GET` | `/airlines` | Airline catalog |
| `GET` | `/api-aa/climates` | Current weather |

## Current and recent flights

### `GET /api-aa/all-flights`

This is the main source for the public departure and arrival boards.

```http
GET /web-prod/v1/api-aa/all-flights?c=900&idarpt=AEP&movtp=D&f=29-07-2026
```

Observed parameters:

| Parameter | Format | Meaning |
|---|---|---|
| `c` | integer | Maximum returned records |
| `idarpt` | IATA | Airport whose board is requested |
| `movtp` | `D` or `A` | Departure or arrival |
| `f` | `DD-MM-YYYY` | Requested date |
| `flight` | text | Full flight number, such as `AR 1400` |
| `destorig` | IATA | Destination for departures or origin for arrivals |
| `idairline` | airline IATA | Airline filter |
| `h` | unknown | Declared by the public client but not confirmed |
| `dosdias` | boolean, unknown | Declared for a possible two-day search |

The response is a JSON array. Important fields include:

| Field | Observed meaning |
|---|---|
| `id` | Source flight-instance identifier |
| `stda` | Scheduled time |
| `etda` | Estimated time |
| `atda` | Actual time |
| `arpt` | Airport whose board was requested |
| `mov` | `D` departure or `A` arrival |
| `nro` | Flight number |
| `idaerolinea`, `aerolinea` | Airline code and name |
| `IATAdestorig`, `destorig` | Destination/origin code and name |
| `estes`, `estin`, `estbr` | Spanish, English and Portuguese status |
| `matricula`, `acftype`, `acft_body` | Aircraft information |
| `gate`, `posicion`, `checkins`, `belt` | Operational fields |
| `id_flight_reg` | Domestic, international or regional category |
| `pasajeros` | Passenger text, frequently missing |
| `rot` | Related or rotating flight |

Observed historical status values include `Took off`, `Landed`, `Cancelled`,
`Delayed`, `Rescheduled`, `DIVERTED`, `On Time` and other operational text.

This endpoint is not a dependable historical archive. Complete results were observed
for approximately two prior days, with no complete result three days back. Retention
is undocumented and may change.

The time strings usually use `DD/MM HH:mm` without a year or time zone. A board for one
date can contain a flight scheduled the previous day. Any collector should keep the
original text and carefully normalize it to `America/Argentina/Buenos_Aires`.

## Future schedules

### `GET /api-aa/flights-fth`

The public website uses this endpoint for dates further in the future. It describes
schedules, not historical performance.

```http
GET /web-prod/v1/api-aa/flights-fth?id_arpt=AEP&movtp=D&c=20&from=05%2F08%2F2026&to=06%2F08%2F2026
```

Observed parameters include `id_arpt`, `movtp`, `c`, `from`, `to`, `flight`,
`destorig`, `id_airline`, `h` and `dosdias`.

Observed response fields include:

```text
day, stda, stdate, id_arpt, mov_tp, flight, id_airline,
id_arpt_dest_orig, via, flight_type, id_acft_tp,
min_date, max_date, checkins, belt, gate, stand, f1...f7
```

It does not contain actual times or completed status values.

## Airport catalogs

### `GET /api-aa/all-airports`

The flight search uses this older airport catalog. Without parameters it returned 106
airports in the test; `all=true` returned 740.

Fields include:

```text
id, country, aeropuerto, oaci, latitud, longitud, descripcion,
nombre, swLat, swLong, neLat, nwLong, admTams
```

`id` is the IATA code. The exact contractual meaning of `admTams` is not documented.

### `GET /api-aa/all-airports-by-id`

```http
GET /web-prod/v1/api-aa/all-airports-by-id?all=true&idarpt=AEP
```

Observed parameters are `all` and `idarpt`.

### `GET /airports`

This newer paginated catalog provides richer details for airports operated by the
company.

| Parameter | Example | Meaning |
|---|---|---|
| `pageSize` | `15` | Page size |
| `page` | `1` | Page |
| `orderBy` | `id-ASC` | Field and direction |
| `like` | `iata-AEP` | Field-value search syntax |
| `active` | `true` | Active records only |

The response contains `data` and `totalCount`. Airport objects can include IATA,
name, city, province, coordinates, telephone numbers, descriptions, airlines,
parking, shops and assets.

## Airlines

### `GET /airlines`

Observed parameters include `pageSize`, `page`, `like`, `airportId` and `active`.
The response is paginated with `data` and `totalCount`. Fields include `id`, `iata`,
`name`, `web`, `phone`, `email`, `airports` and `assetDocument`.

`airportId` expects the internal numeric identifier from `/airports`, not an IATA code.

## Current weather

### `GET /api-aa/climates`

```http
GET /web-prod/v1/api-aa/climates?id_arpt=AEP
```

`id_arpt` is an airport IATA code. The endpoint returns current, not historical,
weather. Observed fields include:

```text
arpt, texto, textoen, textobr, temp, tempunit, tempf,
aptemp, rhumit, winddir, windspeed, pres, icono
```

## Other observed public GET endpoints

| Endpoint | Content |
|---|---|
| `/alerts` | Current alerts |
| `/currencies` | Currency rates displayed by the site |
| `/parkings` | Parking catalog and prices |
| `/shops` | Shop catalog |
| `/shopcategories` | Shop categories |
| `/news` and `/news/{id}` | News and detail |
| `/faqs` | Frequently asked questions |
| `/trafficreports` | Aggregate traffic reports |
| `/officialorganizations` | Organizations at airports |
| `/online-store/categories` | Store categories by airport |
| `/online-store/products` | Products by category |
| `/api-aa/tenders` | Public tenders |

Common pagination patterns include:

```text
pageSize=N
page=N
active=true
orderBy=field-ASC
orderBy=field-DESC
like=field-value
```

Paginated endpoints normally return:

```json
{
  "data": [],
  "totalCount": 0
}
```

## Write endpoints outside this project's scope

The public client declares POST routes including:

```text
/contact/queries
/contact/fbo
/contact/investors
/contact/press
/contact/parking-reserves
/contact/request-for-assistance
/api-aa/offers
/recaptcha/recaptcha-v3
```

These routes were not tested. They transmit forms, personal information or commercial
requests and have no role in A Tiempo?.

## Related systems

TAMS Organismos is an ASP.NET Web Forms application that posts back to itself using
`__VIEWSTATE` and `__EVENTVALIDATION`. It is not a JSON API and should not be
automated as a data source.

The ADA chatbot, store, parking, VIP and contact forms are transactional surfaces.
Older results from `api.aa2000.com.ar` are not current documentation for the modern
API. Azure CDN blob URLs serve documents and assets, not flight information.

## Appropriate client behavior

For a low-volume academic client:

1. Make requests from the backend because of CORS.
2. Request data only when the visitor explicitly asks for current status.
3. Send an honest User-Agent and a short timeout.
4. Handle timeouts, connection errors and unexpected JSON without breaking the app.
5. Do not send private headers, keys or personal information.
6. Display the source's disclaimer and tell users to confirm with the airline.
7. Do not assume public access grants a redistribution license.

The A Tiempo? application follows this limited approach. It does not run a persistent
collector and does not save live responses.

## Conditions and risk

Aeropuertos Argentina states that flight information is informational, may come from
internal and external sources, can be incomplete or out of date, and should be
confirmed with the airline or airport.

Source:
[Aeropuertos Argentina disclaimer](https://www.aeropuertosargentina.com/es/limitacion-de-responsabilidad).

The site's `robots.txt` does not define a data license or API usage limits. A
persistent collector should request written permission, an allowed request frequency,
publication terms and a supported developer channel.

## Maintenance

This API is internal to the public site and may change without notice. A future review
should confirm the base URL, `/api-aa/all-flights` parameters, response schema, CORS,
authentication and terms of use.

**Observed frontend build:** `ak14yuXwXJRsfU0VVPAOP`  
**Last verification:** July 29, 2026
