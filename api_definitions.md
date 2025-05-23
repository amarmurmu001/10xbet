# API Endpoint Definitions

This document outlines the conceptual structure for HTTP API endpoints related to a sports betting application.

## Endpoint 1: Fetch Available Matches and Odds

*   **Purpose:** To provide clients with a list of current or upcoming matches and their associated betting odds.
*   **HTTP Method:** `GET`
*   **URL Path:** `/api/matches`
    *   *Alternative/More Specific Path:* `/api/sports/{sport_name}/matches` (e.g., `/api/sports/cricket/matches`)
    *   *Filtering (Optional Query Parameters):*
        *   `?date=YYYY-MM-DD` (e.g., `?date=2024-12-25`)
        *   `?status=upcoming` (other values: `live`, `finished`)
        *   `?sport=cricket` (if using the generic `/api/matches` path)

*   **Request Payload:** None. Query parameters can be used for filtering as noted above.

*   **Response Payload (Success - 200 OK):**
    *   A list of match objects. Each match object should include its details (inspired by `models.py`) and a list of its associated odd objects (inspired by `models.py`).
    *   **Data Types:**
        *   `matches`: List of Objects
        *   `match_id`: String (or Integer)
        *   `team1`: String
        *   `team2`: String
        *   `start_time`: String (ISO 8601 datetime format)
        *   `sport`: String
        *   `odds`: List of Objects
        *   `odd_id`: String (or Integer)
        *   `market_name`: String
        *   `outcome`: String
        *   `value`: Float
        *   `is_active`: Boolean
        *   `last_updated`: String (ISO 8601 datetime format)
    *   **Example:**
        ```json
        {
          "matches": [
            {
              "match_id": "match123",
              "team1": "Team A",
              "team2": "Team B",
              "start_time": "2024-12-25T14:00:00Z",
              "sport": "cricket",
              "odds": [
                {
                  "odd_id": "odd001",
                  "match_id": "match123", // Implicitly known, but can be included
                  "market_name": "Match Winner",
                  "outcome": "Team A",
                  "value": 1.85,
                  "is_active": true,
                  "last_updated": "2024-12-25T10:30:00Z"
                },
                {
                  "odd_id": "odd002",
                  "match_id": "match123", // Implicitly known
                  "market_name": "Match Winner",
                  "outcome": "Team B",
                  "value": 2.10,
                  "is_active": true,
                  "last_updated": "2024-12-25T10:30:00Z"
                }
                // ... more odds for this match
              ]
            },
            {
              "match_id": "match456",
              "team1": "Team C",
              "team2": "Team D",
              "start_time": "2024-12-26T18:00:00Z",
              "sport": "football",
              "odds": [
                // ... odds for this match
              ]
            }
            // ... more matches
          ]
        }
        ```

*   **Response Payload (Error - e.g., 500 Internal Server Error):**
    *   **Data Types:**
        *   `error`: String
    *   **Example:**
        ```json
        {
          "error": "Failed to fetch matches due to an internal server issue."
        }
        ```

## Endpoint 2: Submit a Bet

*   **Purpose:** To allow an authenticated user to place a bet.
*   **HTTP Method:** `POST`
*   **URL Path:** `/api/bets`

*   **Request Payload:**
    *   Details of the bet being placed.
    *   **Data Types:**
        *   `user_id`: String (or Integer, typically extracted from authentication token on the server-side, but can be in payload if necessary for some architectures)
        *   `selections`: List of Objects
        *   `odd_id`: String (or Integer)
        *   `stake_amount`: Float (should be positive)
    *   **Example:**
        ```json
        {
          "user_id": "user789", // Can be omitted if derived from auth token
          "selections": [
            {
              "odd_id": "odd001",
              "stake_amount": 10.00
            }
            // For simplicity, one selection per request.
            // A multi-selection request might represent a parlay/accumulator bet.
            // {
            //   "odd_id": "odd005",
            //   "stake_amount": 5.00 // Or stake might be applied to the whole parlay
            // }
          ]
        }
        ```

*   **Response Payload (Success - 201 Created):**
    *   Confirmation of the bet placement, including the bet details (inspired by `models.py`).
    *   **Data Types:**
        *   `message`: String
        *   `bet`: Object
        *   `bet_id`: String (or Integer)
        *   `user_id`: String (or Integer)
        *   `match_id`: String (or Integer)
        *   `odd_id`: String (or Integer)
        *   `stake_amount`: Float
        *   `potential_winnings`: Float
        *   `timestamp`: String (ISO 8601 datetime format)
        *   `status`: String (e.g., "pending", "accepted", "processing")
    *   **Example:**
        ```json
        {
          "message": "Bet placed successfully",
          "bet": {
            "bet_id": "betABC",
            "user_id": "user789",
            "match_id": "match123", // Derived by the backend from odd_id
            "odd_id": "odd001",
            "stake_amount": 10.00,
            "potential_winnings": 18.50, // Calculated as stake_amount * odd_value
            "timestamp": "2024-12-25T11:45:10Z",
            "status": "pending"
          }
        }
        ```

*   **Response Payload (Error - 400 Bad Request - Invalid input):**
    *   Provides details about what was wrong with the request.
    *   **Data Types:**
        *   `error`: String
        *   `details`: Object (keys can vary based on the specific errors)
    *   **Example:**
        ```json
        {
          "error": "Invalid bet data",
          "details": {
            "selections[0].odd_id": "This odd is no longer available or does not exist.",
            "selections[0].stake_amount": "Stake must be a positive value greater than 0."
            // Could also be a general error like "Insufficient account balance."
          }
        }
        ```

*   **Response Payload (Error - 401 Unauthorized - User not authenticated):**
    *   Indicates the user needs to authenticate.
    *   **Data Types:**
        *   `error`: String
    *   **Example:**
        ```json
        {
          "error": "User not authenticated. Please login to place a bet."
        }
        ```

*   **Response Payload (Error - 403 Forbidden - User authenticated but not authorized):**
    *   Indicates the user is authenticated but lacks permission for this action (e.g., account suspended).
    *   **Data Types:**
        *   `error`: String
    *   **Example:**
        ```json
        {
          "error": "User account is suspended. Bet placement not allowed."
        }
        ```

*   **Response Payload (Error - 422 Unprocessable Entity - Business logic error):**
    *   Indicates the request was well-formed but could not be processed due to business rules.
    *   **Data Types:**
        *   `error`: String
        *   `details`: (Optional) String or Object providing more context.
    *   **Example (e.g., odd value changed, bet cannot be accepted at old value):**
        ```json
        {
          "error": "Odd value has changed. Please review and resubmit if you agree to the new odds.",
          "details": {
            "odd_id": "odd001",
            "new_value": 1.75,
            "old_value": 1.85
          }
        }
        ```
    *   **Example (e.g., insufficient balance):**
        ```json
        {
          "error": "Insufficient account balance to place this bet."
        }
        ```

*   **Response Payload (Error - 500 Internal Server Error - Bet processing failed):**
    *   A generic server-side error.
    *   **Data Types:**
        *   `error`: String
    *   **Example:**
        ```json
        {
          "error": "Failed to place bet due to an internal server error. Please try again later."
        }
        ```

This structure provides a clear definition for each endpoint, including request/response formats and common error handling.
