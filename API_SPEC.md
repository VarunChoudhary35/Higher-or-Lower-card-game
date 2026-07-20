# Higher or Lower Card Game API Specification

This document describes the API implemented by the Flask web app in this project.
The service exposes endpoints for starting a round, submitting a guess, and checking health.

## Base URL

The base URL for the deployed service is the root of the Railway project, for example:

```text
https://higher-or-lower-card-game-production.up.railway.app
```

## Endpoints

### 1. `GET /`

**Purpose:**
- Returns the HTML game UI rendered from the Flask template.

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
- Starts a new round by drawing two cards.
- Generates a unique token that links the first card to the next guess.

**Request:**
- Method: `GET`
- Path: `/first`
- No request body.

**Response:**
- Status: `200 OK`
- Content-Type: `application/json`
- Body:
  - `token` (string): unique round token.
  - `first` (object): the first card drawn.

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
- Submits the player's guess for the next card in the current round.
- Evaluates whether the second card is higher, lower, or equal to the first card.

**Request:**
- Method: `POST`
- Path: `/guess`
- Content-Type: `application/json`
- Body:
  - `token` (string): the round token returned by `/first`
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
  - `result` (boolean or string):
    - `true` if the guess was correct
    - `false` if the guess was incorrect
    - `"draw"` if both cards had equal value
  - `next_token` (string): a fresh round token for the next turn.
  - `next_first` (object): the first card for the next round.

**Example Response:**

```json
{
  "first": { "value": "7", "suit": "HEARTS" },
  "second": { "value": "JACK", "suit": "SPADES" },
  "result": true,
  "next_token": "4b9e6b6f-2d54-4cc8-9d91-b8c1fb1f8d10",
  "next_first": { "value": "10", "suit": "CLUBS" }
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

**Example Expired or Invalid Token Response:**

```json
{
  "error": "invalid or expired token"
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
If the values are equal, the response is `"draw"`.

## Error Handling

- Missing or invalid `token` in `/guess` returns `400 Bad Request`.
- Invalid `guess` value in `/guess` returns `400 Bad Request`.
- An invalid or expired token also returns `400 Bad Request`.
- If the external card API fails or returns an invalid payload, the app falls back to a built-in local card list.

## Notes for Deployment

- The web app should run on the port specified by the hosting platform using the environment variable `PORT`.
- The `Procfile` runs the app with `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 30`.
- The UI uses the `/first` and `/guess` endpoints to manage each round.
- Tokens are stored in memory and are single-use.

## Usage Flow

1. Browser loads `/`.
2. Client calls `GET /first` to start the first round.
3. User chooses `higher` or `lower`.
4. Client sends `POST /guess` with the current token.
5. The API returns the result, the second card, and a `next_token` plus `next_first` for the following round.
6. The client can continue the game using the returned `next_token` and `next_first` without calling `/first` again.
