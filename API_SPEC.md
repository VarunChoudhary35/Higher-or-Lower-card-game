# Higher or Lower Card Game API Specification

This document describes the public API for the Flask web version of the Higher or Lower card game.
The service exposes endpoints for starting a round, submitting a guess, and checking health.

## Base URL

The base URL for the deployed service is the root of the Railway project, for example:

```text
https://higher-or-lower-card-game-production.up.railway.app
```

## Endpoints

### 1. `GET /`

**Purpose:**
- Returns the HTML game UI.

**Request:**
- Method: `GET`
- Path: `/`
- No request body.

**Response:**
- Status: `200 OK`
- Content-Type: `text/html`
- Body: HTML content for the browser UI.

### 2. `GET /first`

**Purpose:**
- Start a new round by drawing the first card.
- Generates a unique token to associate the first card with the next guess.

**Request:**
- Method: `GET`
- Path: `/first`
- No request body.

**Response:**
- Status: `200 OK`
- Content-Type: `application/json`
- Body:
  - `token` (string): unique round token.
  - `first` (object): first card drawn.

**Example Response:**

```json
{
  "token": "b1f1c8d2-8a14-4ceb-ac37-1e3a3e9c0d7a",
  "first": {
    "value": "7",
    "suit": "HEARTS"
  }
}
```

### 3. `POST /guess`

**Purpose:**
- Submit the player's guess for the next card in the current round.
- Evaluates whether the second card is higher, lower, or equal to the first card.

**Request:**
- Method: `POST`
- Path: `/guess`
- Content-Type: `application/json`
- Body:
  - `token` (string): the round token returned from `/first`
  - `guess` (string): either `higher` or `lower`

**Example Request:**

```json
{
  "token": "b1f1c8d2-8a14-4ceb-ac37-1e3a3e9c0d7a",
  "guess": "higher"
}
```

**Successful Response:**
- Status: `200 OK`
- Content-Type: `application/json`
- Body:
  - `first` (object): the first card drawn.
  - `second` (object): the second card drawn.
  - `result` (string): one of:
    - `true` — guess was correct
    - `false` — guess was incorrect
    - `draw` — both cards had equal value

**Example Response:**

```json
{
  "first": { "value": "7", "suit": "HEARTS" },
  "second": { "value": "JACK", "suit": "SPADES" },
  "result": true
}
```

**Error Responses:**
- Status: `400 Bad Request`
- Content-Type: `application/json`
- Body:
  - `error` (string): description of the problem.

**Example Invalid Request Response:**

```json
{
  "error": "missing token or invalid guess"
}
```

### 4. `GET /health`

**Purpose:**
- A simple health check endpoint for load balancers or deployment platforms.

**Request:**
- Method: `GET`
- Path: `/health`
- No request body.

**Response:**
- Status: `200 OK`
- Content-Type: `application/json`
- Body:
  - `status` (string): always `ok`

**Example Response:**

```json
{
  "status": "ok"
}
```

## Card Value Rules

The API compares card values using this ranking:

- `2` through `10` use numeric value
- `JACK` = 11
- `QUEEN` = 12
- `KING` = 13
- `ACE` = 14

A guess of `higher` is correct if the second card value is greater than the first card value.
A guess of `lower` is correct if the second card value is less than the first card value.
If the values are equal, the response is `draw`.

## Error Handling

- Invalid or missing `token` in `/guess` returns `400 Bad Request`.
- Invalid `guess` value in `/guess` returns `400 Bad Request`.
- If `/first` fails to draw enough cards from the API, the app falls back to a local card list.

## Notes for Deployment

- The web app should run on the port specified by the hosting platform using the environment variable `PORT`.
- The `Procfile` should expose the web process using `gunicorn app:app --bind 0.0.0.0:$PORT`.
- The UI uses the `/first` and `/guess` endpoints to manage each round.

## Usage Flow

1. Browser loads `/`.
2. Client calls `GET /first`.
3. User chooses `higher` or `lower`.
4. Client sends `POST /guess`.
5. UI displays the `second` card and the result.
