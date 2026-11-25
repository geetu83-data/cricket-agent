"""Cricket API client for live scores, player stats, and match data.

Uses CricAPI (cricapi.com) - 100 free requests/day.
Get your free API key at: https://cricapi.com/
"""

import os
import requests
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CRICAPI_BASE_URL = "https://api.cricapi.com/v1"


class CricketClient:
    """Client for CricAPI."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("CRICKET_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Cricket API key required. Get one free at https://cricapi.com/ "
                "and set CRICKET_API_KEY environment variable."
            )

    def _request(self, endpoint: str, params: dict | None = None) -> dict:
        """Make a request to CricAPI."""
        params = params or {}
        params["apikey"] = self.api_key

        try:
            response = requests.get(
                f"{CRICAPI_BASE_URL}/{endpoint}",
                params=params,
                timeout=15,
                verify=False
            )
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "failure":
                return {"error": data.get("reason", "API request failed")}
            return data
        except requests.exceptions.RequestException as e:
            return {"error": f"Cricket API request failed: {str(e)}"}

    def get_current_matches(self) -> dict:
        """Get current/live matches."""
        return self._request("currentMatches")

    def get_match_info(self, match_id: str) -> dict:
        """Get detailed info about a specific match."""
        return self._request("match_info", {"id": match_id})

    def get_series_list(self) -> dict:
        """Get list of cricket series."""
        return self._request("series")

    def get_series_info(self, series_id: str) -> dict:
        """Get info about a specific series."""
        return self._request("series_info", {"id": series_id})

    def search_players(self, name: str) -> dict:
        """Search for players by name."""
        return self._request("players", {"search": name})

    def get_player_info(self, player_id: str) -> dict:
        """Get detailed player info."""
        return self._request("players_info", {"id": player_id})


_client: CricketClient | None = None


def get_client() -> CricketClient:
    """Get or create Cricket API client."""
    global _client
    if _client is None:
        _client = CricketClient()
    return _client


def get_live_matches() -> dict:
    """Get all current/live cricket matches."""
    client = get_client()
    result = client.get_current_matches()

    if "error" in result:
        return result

    matches = result.get("data", [])

    live_matches = []
    upcoming_matches = []
    completed_matches = []

    for match in matches[:20]:
        match_data = {
            "match_id": match.get("id"),
            "name": match.get("name"),
            "status": match.get("status"),
            "venue": match.get("venue"),
            "date": match.get("date"),
            "teams": match.get("teams", []),
            "score": match.get("score", []),
            "series": match.get("series"),
            "match_type": match.get("matchType"),
        }

        if match.get("matchStarted") and not match.get("matchEnded"):
            live_matches.append(match_data)
        elif not match.get("matchStarted"):
            upcoming_matches.append(match_data)
        else:
            completed_matches.append(match_data)

    return {
        "live_count": len(live_matches),
        "live_matches": live_matches[:5],
        "upcoming_count": len(upcoming_matches),
        "upcoming_matches": upcoming_matches[:5],
        "recent_completed": completed_matches[:3],
    }


def get_match_details(match_id: str) -> dict:
    """Get detailed info about a specific match."""
    client = get_client()
    result = client.get_match_info(match_id)

    if "error" in result:
        return result

    data = result.get("data", {})
    return {
        "match_id": data.get("id"),
        "name": data.get("name"),
        "status": data.get("status"),
        "venue": data.get("venue"),
        "date": data.get("date"),
        "teams": data.get("teams", []),
        "score": data.get("score", []),
        "toss": {
            "winner": data.get("tossWinner"),
            "decision": data.get("tossChoice"),
        },
        "match_type": data.get("matchType"),
        "series": data.get("series"),
    }


def get_player_stats(player_name: str) -> dict:
    """Search for a player and get their stats."""
    client = get_client()

    # First search for the player
    search_result = client.search_players(player_name)
    if "error" in search_result:
        return search_result

    players = search_result.get("data", [])
    if not players:
        return {"error": f"No player found with name '{player_name}'"}

    # Get the first matching player's details
    player = players[0]
    player_id = player.get("id")

    # Get detailed info
    info_result = client.get_player_info(player_id)
    if "error" in info_result:
        return {
            "player_id": player_id,
            "name": player.get("name"),
            "country": player.get("country"),
            "note": "Detailed stats not available",
        }

    data = info_result.get("data", {})
    return {
        "player_id": data.get("id"),
        "name": data.get("name"),
        "country": data.get("country"),
        "role": data.get("role"),
        "batting_style": data.get("battingStyle"),
        "bowling_style": data.get("bowlingStyle"),
        "date_of_birth": data.get("dateOfBirth"),
        "stats": data.get("stats", []),
        "current_teams": data.get("teams", []),
    }


def get_series_list() -> dict:
    """Get list of ongoing and upcoming cricket series."""
    client = get_client()
    result = client.get_series_list()

    if "error" in result:
        return result

    series = result.get("data", [])
    return {
        "count": len(series),
        "series": [
            {
                "series_id": s.get("id"),
                "name": s.get("name"),
                "start_date": s.get("startDate"),
                "end_date": s.get("endDate"),
                "odi_count": s.get("odi", 0),
                "t20_count": s.get("t20", 0),
                "test_count": s.get("test", 0),
            }
            for s in series[:15]
        ]
    }


