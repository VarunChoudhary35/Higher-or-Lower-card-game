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
- Starts the game by creating the first active card for the player.
- Returns a token that must be used for the first guess.
- This endpoint is only used to begin the game and does not itself evaluate a comparison.

**Request:**
- Method: `GET`
- Path: `/first`
- No request body.

**Response:**
- Status: `200 OK`
- Content-Type: `application/json`
- Body:
  - `token` (string): unique token for the first turn.
  - `first` (object): the card currently shown to the player.

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
- Evaluates one turn of the game.
- Compares the currently visible card with a newly revealed card.
- Returns whether the player's guess was correct, along with the card that should become the next visible card.

**Request:**
- Method: `POST`
- Path: `/guess`
- Content-Type: `application/json`
- Body:
  - `token` (string): the token returned by `/first` or by the previous `/guess` response.
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
  - `first` (object): the card shown to the player before the guess for the current turn.
  - `second` (object): the card revealed after the guess for the current turn.
  - `result` (boolean or string):
    - `true` if the guess was correct
    - `false` if the guess was incorrect
    - `"draw"` if both cards had equal value
  - `next_token` (string): a fresh token for the next turn.
  - `next_card` (object): the same card as `second`, which becomes the visible card for the next turn.

**Example Response:**

```json
{
  "first": { "value": "7", "suit": "HEARTS" },
  "second": { "value": "JACK", "suit": "SPADES" },
  "result": true,
  "next_token": "4b9e6b6f-2d54-4cc8-9d91-b8c1fb1f8d10",
  "next_card": { "value": "JACK", "suit": "SPADES" }
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

## Game Flow Semantics

The API is intentionally stateful and supports an indefinite sequence of turns.

- The first turn begins with `GET /first`, which returns an initial visible card and a token.
- Each subsequent turn uses the `next_token` returned by the previous `/guess` response.
- For each turn, the server compares the current visible card with one newly revealed card.
- After the comparison, the revealed card becomes the new visible card for the next turn.
- The client should display the returned `next_card` and send the returned `next_token` on the following guess.

This means the game is not based on a fixed deck or a finite number of rounds. The player can continue making guesses indefinitely.

## Notes for Deployment

- The web app should run on the port specified by the hosting platform using the environment variable `PORT`.
- The `Procfile` runs the app with `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 30`.
- The UI uses the `/first` and `/guess` endpoints to manage each round.
- Tokens are stored in memory and are single-use.

## Usage Flow

1. Browser loads `/`.
2. Client calls `GET /first` to start the first turn.
3. The API returns a visible card and a token.
4. The user chooses `higher` or `lower`.
5. The client sends `POST /guess` with that token and the chosen guess.
6. The API compares the visible card with a newly revealed card and returns:
   - the result of the comparison
   - the revealed card for the current turn
   - a fresh token for the next turn
   - the revealed card again as `next_card` for the next turn
7. The client displays the returned `next_card` and sends the returned `next_token` with the next guess.
8. Steps 4–7 repeat indefinitely.
