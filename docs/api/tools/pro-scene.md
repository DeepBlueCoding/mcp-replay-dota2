# Pro Scene Tools

These tools query professional Dota 2 data from OpenDota.

## search_pro_player

Fuzzy search for pro players by name or alias.

```python
search_pro_player(query="yatoro", max_results=5)
```

**Returns:**
```json
{
  "success": true,
  "query": "yatoro",
  "total_results": 1,
  "results": [
    {"id": 311360822, "name": "Yatoro", "matched_alias": "Yatoro", "similarity": 1.0}
  ]
}
```

---

## search_team

Fuzzy search for teams by name or tag.

```python
search_team(query="spirit", max_results=5)
```

**Returns:**
```json
{
  "success": true,
  "query": "spirit",
  "total_results": 2,
  "results": [
    {"id": 8599101, "name": "Team Spirit", "matched_alias": "spirit", "similarity": 0.95}
  ]
}
```

---

## get_pro_player

Get pro player details by account ID.

```python
get_pro_player(account_id=311360822)
```

**Returns:**
```json
{
  "success": true,
  "player": {
    "account_id": 311360822,
    "name": "Yatoro",
    "personaname": "Yatoro",
    "team_id": 8599101,
    "team_name": "Team Spirit",
    "country_code": "UA",
    "fantasy_role": 1,
    "is_active": true,
    "aliases": ["yatoro", "raddan"]
  }
}
```

---

## get_pro_player_by_name

Get pro player details by name (uses fuzzy search).

```python
get_pro_player_by_name(name="Yatoro")
```

---

## get_team

Get team details by team ID.

```python
get_team(team_id=8599101)
```

**Returns:**
```json
{
  "success": true,
  "team": {
    "team_id": 8599101,
    "name": "Team Spirit",
    "tag": "Spirit",
    "rating": 1500.0,
    "wins": 450,
    "losses": 200,
    "aliases": ["ts", "spirit"]
  },
  "roster": [
    {"account_id": 311360822, "player_name": "Yatoro", "games_played": 300, "wins": 200, "is_current": true}
  ]
}
```

---

## get_team_by_name

Get team details by name (uses fuzzy search).

```python
get_team_by_name(name="Team Spirit")
```

---

## get_team_matches

Get recent matches for a team with series grouping.

```python
get_team_matches(team_id=8599101, limit=20)
```

**Returns:**
```json
{
  "success": true,
  "team_id": 8599101,
  "team_name": "Team Spirit",
  "total_matches": 20,
  "series": [
    {
      "series_id": 123,
      "series_type": "bo3",
      "games_in_series": 2,
      "wins_needed": 2,
      "radiant_team_id": 8599101,
      "dire_team_id": 7391077,
      "winner_team_id": 8599101,
      "league_name": "ESL One"
    }
  ],
  "matches": [...]
}
```

---

## get_leagues

Get all leagues/tournaments, optionally filtered by tier.

```python
get_leagues(tier="premium")  # "premium", "professional", "amateur", or None for all
```

**Returns:**
```json
{
  "success": true,
  "total_leagues": 15,
  "leagues": [
    {"league_id": 15728, "name": "The International 2023", "tier": "premium"}
  ]
}
```

---

## get_pro_matches

Get recent professional matches with series grouping. By default returns ALL matches including low-tier leagues - use filters to narrow down results.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | int | Maximum matches to return (default: 100) |
| `tier` | string | Filter by league tier: `"premium"` (TI, Majors), `"professional"`, or `"amateur"` |
| `team1_name` | string | Filter by first team (fuzzy match). Alone: returns all matches for that team |
| `team2_name` | string | Filter by second team (fuzzy match). With team1: returns head-to-head matches |
| `league_name` | string | Fuzzy match on league name with alias expansion (see below) |
| `days_back` | int | Only return matches from the last N days |

**Team Filtering:**

- **Single team** (`team1_name` only): Returns all matches involving that team (either radiant or dire)
- **Head-to-head** (`team1_name` + `team2_name`): Returns only matches where both teams played against each other, regardless of which side (radiant/dire) they were on

**League Name Fuzzy Search:**

The `league_name` parameter supports fuzzy matching with common abbreviations:

| Query | Matches |
|-------|---------|
| `"TI 2025"` | "The International 2025" |
| `"ESL"` | "ESL One Kuala Lumpur", "ESL One Birmingham" |
| `"DPC"` | "Dota Pro Circuit" leagues |
| `"blast"` or `"slam"` | "BLAST Slam V" |
| `"dreamleague"` | "DreamLeague Season 24" |
| `"PGL"` | "PGL Wallachia Season 6" |
| `"wallachia"` | "PGL Wallachia Season 6" |
| `"riyadh"` | "Riyadh Masters 2025" |
| `"bali"` | "Bali Major 2025" |

Partial names also work: `"wallachia 6"` matches "PGL Wallachia Season 6".

**Data Blending:** When team filters are provided, this tool automatically blends data from two sources:

1. **Team-specific endpoint** (`/teams/{id}/matches`) - captures matches that OpenDota's `/proMatches` often misses (e.g., major tournaments like SLAM)
2. **General pro matches** (`/proMatches`) - provides broader coverage

This ensures comprehensive results when searching for specific teams.

```python
# Get top-tier tournament matches only
get_pro_matches(tier="premium")

# Find all matches for a specific team
get_pro_matches(team1_name="Tundra", days_back=7)

# Find head-to-head matches between two teams
get_pro_matches(team1_name="Team Spirit", team2_name="OG")

# Head-to-head at a specific tournament (fuzzy league name)
get_pro_matches(team1_name="Spirit", team2_name="OG", league_name="TI 2025")

# Find matches using abbreviations
get_pro_matches(league_name="TI 2025")      # The International 2025
get_pro_matches(league_name="PGL")          # PGL tournaments
get_pro_matches(league_name="wallachia 6")  # PGL Wallachia Season 6
get_pro_matches(league_name="ESL")          # ESL One tournaments

# Combine filters: team matches at premium tournaments
get_pro_matches(tier="premium", team1_name="Team Spirit", days_back=30)
```

**Returns:**
```json
{
  "success": true,
  "total_matches": 100,
  "series": [...],
  "matches": [
    {
      "match_id": 8461956309,
      "radiant_team_id": 8291895,
      "radiant_team_name": "XG",
      "dire_team_id": 8894818,
      "dire_team_name": "FLCN",
      "radiant_win": false,
      "duration": 4672,
      "league_name": "Elite League"
    }
  ]
}
```

---

## get_tournament_series

Get tournament series with bracket/game details. Use for tournament progression analysis: series results, Bo3/Bo5 outcomes, team advancement.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `league_name` | string | Filter by league/tournament name (fuzzy match with alias expansion) |
| `league_id` | int | Filter by specific league ID |
| `team_name` | string | Filter series involving this team (fuzzy match) |
| `limit` | int | Maximum series to return (default: 20) |
| `days_back` | int | Only return series from the last N days |

**League Name Fuzzy Search:**

Same alias expansion as `get_pro_matches` - "TI" matches "The International", "ESL" matches ESL tournaments, etc.

```python
# Get recent series from a tournament
get_tournament_series(league_name="TI 2025", limit=10)

# Get all series involving a specific team
get_tournament_series(team_name="Team Spirit", days_back=30)

# Get series from a specific league ID
get_tournament_series(league_id=15728)

# Combine filters: team at a specific tournament
get_tournament_series(league_name="ESL One", team_name="Tundra")
```

**Returns:**
```json
{
  "success": true,
  "total_series": 5,
  "series": [
    {
      "series_id": 12345,
      "series_type": "bo3",
      "radiant_team_id": 8599101,
      "radiant_team_name": "Team Spirit",
      "dire_team_id": 7391077,
      "dire_team_name": "Tundra Esports",
      "radiant_wins": 2,
      "dire_wins": 1,
      "winner_team_id": 8599101,
      "winner_team_name": "Team Spirit",
      "league_id": 15728,
      "league_name": "The International 2024",
      "games": [
        {
          "match_id": 8461956309,
          "game_number": 1,
          "radiant_win": true,
          "duration": 2847
        },
        {
          "match_id": 8461956310,
          "game_number": 2,
          "radiant_win": false,
          "duration": 3102
        },
        {
          "match_id": 8461956311,
          "game_number": 3,
          "radiant_win": true,
          "duration": 2456
        }
      ]
    }
  ]
}
```

**Key Fields:**

| Field | Description |
|-------|-------------|
| `series_type` | `"bo1"`, `"bo3"`, or `"bo5"` |
| `radiant_wins` / `dire_wins` | Games won by each team in the series |
| `winner_team_id` | Team that won the series |
| `games` | Array of individual matches with results |

!!! tip "Series vs Matches"
    Use `get_tournament_series` for bracket analysis (who advanced, series scores). Use `get_pro_matches` for individual match details.

---

## get_league_matches

Get matches from a specific league with series grouping.

```python
get_league_matches(league_id=15728, limit=50)
```

**Returns:**
```json
{
  "success": true,
  "league_id": 15728,
  "league_name": "The International 2023",
  "total_matches": 50,
  "series": [...],
  "matches": [...]
}
```
