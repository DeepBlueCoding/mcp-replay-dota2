# MCP Prompts

??? info "AI Summary"

    MCP Prompts are reusable analysis templates that clients can invoke. Unlike tools (which execute code and return data), prompts return structured instructions for the LLM to follow. Each prompt focuses on a specific domain: draft analysis, hero performance, death patterns, laning, teamfights, itemization, and game turning points.

## Overview

MCP Prompts provide pre-built analysis templates for common Dota 2 coaching scenarios. Each prompt:

- **Returns structured instructions** for the LLM to follow
- **Focuses on one domain** - no scope creep into unrelated analysis
- **Includes benchmarks and frameworks** specific to Dota 2

!!! note "Prompts vs Tools vs Sampling"

    | Feature | Purpose | When to Use |
    |---------|---------|-------------|
    | **Tools** | Execute code, return data | Get match data, hero stats, fights |
    | **Prompts** | Guide LLM analysis | Structure analysis of provided data |
    | **Sampling** | Server-requested LLM calls | Automatic coaching in tool responses |

## Available Prompts

### analyze_draft

Analyzes a draft for lane matchups, synergies, and counter picks.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `radiant_picks` | string | Yes | Radiant's picked heroes |
| `dire_picks` | string | Yes | Dire's picked heroes |
| `radiant_bans` | string | No | Radiant's banned heroes |
| `dire_bans` | string | No | Dire's banned heroes |

**Analysis Sections:**

1. **Lane Matchups** - Who wins each lane (safelane, mid, offlane) based on hero matchups
2. **Draft Synergies** - How heroes complement each other per team
3. **Counter Picks** - Which picks counter enemy heroes and how
4. **Draft Weaknesses** - What each draft lacks
5. **Ban Analysis** - Why heroes were banned (if bans provided)
6. **Draft Grade** - A/B/C/D rating with justification

!!! warning "Focused Analysis"
    This prompt explicitly excludes teamfight combo analysis and item timing predictions. Those belong in `analyze_teamfight` and `compare_itemization` respectively.

**Example Usage:**
```
/dota2-match-analysis:analyze_draft
radiant_picks: "Juggernaut, Shadow Fiend, Earthshaker, Shadow Demon, Pugna"
dire_picks: "Medusa, Pangolier, Magnus, Naga Siren, Disruptor"
radiant_bans: "Chen, Sand King, Enchantress"
dire_bans: "Bane, Centaur, Anti-Mage"
```

---

### review_hero_performance

Reviews a player's performance with position-specific coaching feedback.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `hero` | string | Yes | Hero played |
| `position` | string | Yes | Position (1-5) |
| `kda` | string | Yes | K/D/A stats |
| `cs_at_10` | string | No | CS at 10 minutes |
| `gpm` | string | No | Gold per minute |
| `item_timings` | string | No | Key item timings |
| `fight_participation` | string | No | Fight participation % |

**Analysis Sections:**

1. **Overall Rating** - Poor / Acceptable / Good / Excellent
2. **Benchmark Comparison** - Stats vs position expectations
3. **Key Issues** - What went wrong (2-3 points)
4. **Actionable Improvements** - What to do differently (2-3 points)
5. **Positives** - What was done well (1-2 points)

**Position Benchmarks:**

| Position | CS@10 Target | Primary Metrics |
|----------|--------------|-----------------|
| Pos 1 | 65-80 | CS, GPM, item timings |
| Pos 2 | 60-75 | CS, kill participation |
| Pos 3 | N/A | Space creation, not farm |
| Pos 4/5 | N/A | Impact, not net worth |

---

### analyze_deaths

Analyzes death patterns to identify preventable mistakes.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `deaths_list` | string | Yes | List of deaths with times/details |
| `focus_hero` | string | No | Hero to focus analysis on |

**5-Question Framework:**

Each death is evaluated against:

1. **Was Vision Available?** - Ward coverage, minimap awareness, smoke gank?
2. **Power Spike Timing?** - Before/after level 6? Key item? Cooldowns?
3. **Objective Trade?** - Did death enable Roshan/towers/space?
4. **Buyback Usage?** - Available? Used correctly? Wasted?
5. **Item Timing Impact?** - How much did death delay key items?

**Analysis Sections:**

1. **Most Impactful Deaths** - Which deaths mattered most (2-3)
2. **Death Patterns** - Repeated issues, same area, same killer
3. **Death Categories** - Unavoidable / Preventable / Acceptable / Throw
4. **Actionable Advice** - How to reduce preventable deaths

---

### review_laning_phase

Reviews the laning phase (0-10 minutes) with coaching feedback.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `lane_results` | string | Yes | Lane winner summary |
| `hero_cs_stats` | string | Yes | CS stats at 10 min for all heroes |

**CS Benchmarks:**

| Position | Poor | Acceptable | Good | Excellent |
|----------|------|------------|------|-----------|
| Pos 1 | <50 | 50-65 | 65-80 | 80+ |
| Pos 2 | <45 | 45-60 | 60-75 | 75+ |
| Pos 3 | Judged by space creation, not CS |

**Analysis Sections:**

1. **Lane Outcomes** - Who won each lane and why
2. **Critical Lane** - Which lane mattered most
3. **Benchmark Performance** - Which cores hit targets
4. **Key Mistakes** - What swung lanes
5. **Improvement Advice** - What losing lanes could do differently

---

### analyze_teamfight

Analyzes a specific teamfight for coaching insights.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `fight_time` | string | Yes | Game time of fight |
| `participants` | string | Yes | Heroes involved |
| `death_sequence` | string | Yes | Order of deaths |
| `fight_winner` | string | No | Which team won |

**Analysis Sections:**

1. **Initiation** - Who started, planned vs reactive, timing
2. **Target Priority** - Were right heroes focused?
3. **Ability Usage** - Key ults, CC chaining, saves
4. **Positioning** - Carries safe? Frontliners absorbing?
5. **Trade Value** - What each team gained/lost
6. **Coaching Points** - What each side could improve

---

### compare_itemization

Analyzes item choices and suggests alternatives.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `hero` | string | Yes | Hero being analyzed |
| `items_built` | string | Yes | Items the player built |
| `enemy_heroes` | string | Yes | Enemy team composition |
| `game_context` | string | No | Additional context (ahead/behind, etc.) |

**Analysis Sections:**

1. **Build Assessment** - Is build appropriate for this game?
2. **Timing Analysis** - Were items completed at good times?
3. **Alternative Items** - What could have been better?
4. **Item Ordering** - Was build order optimal?
5. **Situational Purchases** - BKB timing, detection, defensive items

---

### game_turning_points

Identifies and analyzes match turning points.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `gold_lead_timeline` | string | Yes | Gold lead changes over time |
| `key_events` | string | Yes | Major events (fights, objectives) |

**Analysis Sections:**

1. **Major Turning Points** - 2-4 moments that swung the game
2. **Momentum Shifts** - How each turning point changed trajectory
3. **Preventable Swings** - Which could have been avoided
4. **Decisive Moment** - Single most important moment
5. **Lessons** - What each team should learn

---

## Usage with Claude Code

Prompts appear in Claude Code's autocomplete when you type `/`:

```
/dota2-match-analysis:analyze_draft
/dota2-match-analysis:review_hero_performance
/dota2-match-analysis:analyze_deaths
...
```

The prompt will guide Claude to focus on the specific analysis domain without scope creep.

## Usage with Other Clients

MCP prompts are exposed via the MCP protocol's prompt listing. Clients can:

1. List available prompts: `list_prompts()`
2. Get prompt template: `get_prompt(name, arguments)`
3. Fill in arguments and send to LLM

```python
# Example with MCP SDK
prompts = await session.list_prompts()
draft_prompt = await session.get_prompt(
    "analyze_draft",
    arguments={
        "radiant_picks": "Juggernaut, Shadow Fiend",
        "dire_picks": "Medusa, Pangolier"
    }
)
# draft_prompt contains the filled template to send to your LLM
```
