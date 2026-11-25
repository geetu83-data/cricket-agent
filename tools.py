"""Tool definitions for the Cricket Agent."""

TOOLS = [
    {
        "name": "get_live_matches",
        "description": "Get current live cricket matches, upcoming matches, and recent results. Use this for questions about what matches are happening now, today's cricket, or upcoming games.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_match_details",
        "description": "Get detailed information about a specific cricket match including scores, teams, venue, and toss details. Requires match_id from get_live_matches.",
        "input_schema": {
            "type": "object",
            "properties": {
                "match_id": {
                    "type": "string",
                    "description": "The match ID (get this from get_live_matches first)"
                }
            },
            "required": ["match_id"]
        }
    },
    {
        "name": "get_player_stats",
        "description": "Get information and stats about a cricket player. Use for questions about player careers, batting/bowling styles, which country they play for.",
        "input_schema": {
            "type": "object",
            "properties": {
                "player_name": {
                    "type": "string",
                    "description": "Name of the player (e.g., 'Virat Kohli', 'Ben Stokes')"
                }
            },
            "required": ["player_name"]
        }
    },
    {
        "name": "get_series_list",
        "description": "Get list of ongoing and upcoming cricket series/tournaments like IPL, World Cup, Ashes, etc.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "compare_players",
        "description": "Compare two cricket players side by side - their stats, playing styles, and careers.",
        "input_schema": {
            "type": "object",
            "properties": {
                "player1_name": {
                    "type": "string",
                    "description": "First player's name"
                },
                "player2_name": {
                    "type": "string",
                    "description": "Second player's name"
                }
            },
            "required": ["player1_name", "player2_name"]
        }
    }
]
