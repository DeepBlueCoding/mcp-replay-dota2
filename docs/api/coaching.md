# AI Coaching Features

This MCP server includes AI-powered coaching analysis that provides professional-level Dota 2 insights when the client supports MCP sampling.

## How It Works

The server uses **MCP Sampling** - a protocol feature where the server requests the client's LLM to generate analysis based on structured prompts. This enables rich, contextual coaching without requiring additional API calls.

```
┌─────────────────┐     1. Tool call        ┌─────────────────┐
│                 │ ────────────────────>   │                 │
│   MCP Client    │                         │   MCP Server    │
│  (Claude, etc)  │     2. Raw data +       │  (Dota2 Coach)  │
│                 │ <────────────────────   │                 │
│                 │     sampling request    │                 │
│                 │                         │                 │
│   LLM analyzes  │     3. Analysis         │                 │
│   with prompts  │ ────────────────────>   │                 │
│                 │                         │                 │
│                 │     4. Final response   │                 │
│                 │ <────────────────────   │                 │
└─────────────────┘     with coaching       └─────────────────┘
```

## Client Feature Support

| Client | Tools | Resources | Sampling | Coaching Analysis |
|--------|:-----:|:---------:|:--------:|:-----------------:|
| **Claude Desktop** | ✅ | ✅ | ✅ | ✅ Full |
| **Claude Code CLI** | ✅ | ✅ | ✅ | ✅ Full |
| **Cursor** | ✅ | ✅ | ❌ | ⚠️ Data only |
| **Windsurf** | ✅ | ✅ | ❌ | ⚠️ Data only |
| **Zed** | ✅ | ✅ | ❌ | ⚠️ Data only |
| **Continue.dev** | ✅ | ✅ | ❌ | ⚠️ Data only |
| **LangChain** | ✅ | ✅ | ⚠️ Manual | ⚠️ Requires setup |
| **OpenAI API** | ✅ | ❌ | ❌ | ⚠️ Data only |
| **Custom MCP SDK** | ✅ | ✅ | ⚠️ Optional | Depends on impl |

**Legend:**
- ✅ Full: Feature fully supported with automatic coaching
- ⚠️ Data only: Raw data returned, no AI coaching analysis
- ⚠️ Manual/Requires setup: Possible but requires custom implementation

## Tools with Coaching Analysis

The following tools include AI coaching when sampling is available:

| Tool | Coaching Focus |
|------|----------------|
| `get_hero_performance` | Position-appropriate performance evaluation, ability effectiveness |
| `get_hero_deaths` | Death pattern analysis, preventable vs unavoidable deaths |
| `get_lane_summary` | Laning phase evaluation, CS benchmarks, lane winner analysis |
| `get_teamfights` | Teamfight breakdown, initiation quality, target priority |

## Response Comparison

### With Sampling (Claude Desktop, Claude Code)

```json
{
  "success": true,
  "match_id": 8461956309,
  "hero": "batrider",
  "total_kills": 5,
  "total_deaths": 3,
  "total_assists": 12,
  "ability_summary": [
    {"ability": "batrider_flaming_lasso", "total_casts": 8, "hero_hits": 7, "hit_rate": 87.5}
  ],
  "fights": [...],
  "coaching_analysis": "**Rating: Good**\n\nBatrider's Lasso usage was effective with 87.5% hit rate across 8 casts. Key observations:\n\n**Strengths:**\n- 7/8 Lassos hit priority targets\n- Strong kill participation (5K/12A in teamfights)\n- Initiated 3 winning teamfights\n\n**Areas for Improvement:**\n- Died 3 times, 2 were preventable (caught farming without vision)\n- Consider Lasso timing - 2 casts were on already-disabled targets\n\n**Actionable Advice:**\n1. Check minimap before Blink-Lasso initiations\n2. Coordinate with team to avoid overlapping disables"
}
```

### Without Sampling (Cursor, Windsurf, etc.)

```json
{
  "success": true,
  "match_id": 8461956309,
  "hero": "batrider",
  "total_kills": 5,
  "total_deaths": 3,
  "total_assists": 12,
  "ability_summary": [
    {"ability": "batrider_flaming_lasso", "total_casts": 8, "hero_hits": 7, "hit_rate": 87.5}
  ],
  "fights": [...],
  "coaching_analysis": null
}
```

When `coaching_analysis` is `null`, the client's LLM can still interpret the raw data, but won't have access to the specialized Dota 2 coaching prompts embedded in the server.

## Coaching Knowledge Base

The server includes comprehensive Dota 2 coaching knowledge loaded from persona files in `data/personas/`.

### Coaching Persona

The AI adopts the perspective of a senior Dota 2 analyst with professional play experience (TI qualifiers, 11k peak MMR). The persona is defined in `data/personas/coaching_persona.md`.

**Analysis Principles:**

- **Lead with Insight, Support with Data** - Don't just report numbers, interpret what they mean
- **Identify the Core Issue** - Surface the fundamental problem, not symptoms
- **Actionable Takeaways** - Specific, implementable changes (2-3 maximum)

**Communication Style:**

- Direct and specific - timestamps, hero names, ability names
- Focus on the "why" not just the "what"
- Never blame teammates - focus on what the player could control
- Distinguish execution errors from decision errors

### Analysis Workflow

Every analysis follows this framework:

1. **Win Condition** - What does each draft want to do? Timing advantage?
2. **Execution Check** - Did they play their draft or deviate?
3. **Inflection Point** - THE moment the game turned (there's always one)
4. **The "Why"** - Explain why events mattered, not just describe them
5. **Counterfactual** - What could the losing side have done differently?

### Position-Specific Frameworks

Position-specific analysis frameworks are loaded from `data/personas/` when available. These provide detailed phase-by-phase guidance for each role.

| Position | Framework File | Status |
|----------|----------------|--------|
| **Pos 1 (Carry)** | `pos1_carry.md` | ✅ Available |
| **Pos 2 (Mid)** | `pos2_mid.md` | 🔜 Planned |
| **Pos 3 (Offlane)** | `pos3_offlane.md` | 🔜 Planned |
| **Pos 4 (Soft Support)** | `pos4_soft_support.md` | 🔜 Planned |
| **Pos 5 (Hard Support)** | `pos5_hard_support.md` | 🔜 Planned |

### Position 1 (Carry) Framework

The carry framework (`data/personas/pos1_carry.md`) provides comprehensive phase-by-phase analysis:

**Laning (0-10 min):**

- Lane equilibrium management (creep aggro, wave positioning)
- Lane dynamics assessment (2v1, 1v2, etc.)
- Recognizing when laning phase ends (offlaner level 6)

**Farming (7-25 min):**

- Farming pattern: Wave → Jungle → Wave → Jungle
- Timer awareness (stack at :40-:45, XP shrines at 14/21 min)
- Item timing benchmarks:

| Item | Good Timing | Struggling |
|------|-------------|------------|
| Maelstrom | 11-13 min | 16+ min |
| Battlefury | 12-14 min | 18+ min |
| BKB | 18-20 min | 24+ min |

**Transition (20-35 min):**

- Active vs Passive farming (the #1 carry mistake)
- Pre-BKB: Only join convenient cleanup kills
- Post-BKB: Farm near team, 60%+ kill participation target
- 20-30 second rule before TPing back

**Closing (25-45 min):**

- "Aegis is a timer, not insurance" - push immediately
- No-throw mentality: end with 2-3 deaths, not 7-8
- Second Aegis = game should end

### Basic Role Expectations

| Position | Primary Focus | Key Metrics |
|----------|---------------|-------------|
| **Pos 1 (Carry)** | Maximize farm efficiency, minimize deaths | Item timings, kill participation post-BKB |
| **Pos 2 (Mid)** | Win CS, control power runes | Rotate only WITH good runes (haste/DD/invis) |
| **Pos 3 (Offlane)** | Disrupt enemy carry's farm | Deaths acceptable if they drew resources |
| **Pos 4 (Soft Support)** | Secure offlane levels 1-3, then rotate | Stack camps, set up kills, aggressive vision |
| **Pos 5 (Hard Support)** | Keep carry alive, zone offlaner | Lowest net worth expected, die to save cores |

### Death Analysis Framework

For each death, the coaching asks:

1. **Vision** - Ward coverage? Smoke gank (excusable)?
2. **Timing** - Before key level/item? Ult on cooldown?
3. **Trade** - Got objective? Created space? Or died for nothing?
4. **Buyback** - Available? Used correctly?
5. **Impact** - How much did this delay key items?

**Death Categories:**

- **Unavoidable**: Smoke gank, enemy snowballing
- **Preventable**: Bad positioning, no vision, greedy farming
- **Acceptable**: Space creation (pos 3), trading for objectives
- **Throw**: Dying with Aegis, solo death while winning, no buyback late

### Lane Recovery Framework

When a lane is lost, the coaching evaluates the response:

| Role | Expected Response | Red Flag |
|------|-------------------|----------|
| **Carry** | Jungle transition at level 5-6 | Staying in lane dying repeatedly |
| **Mid** | Stack-farming, rune control | Forcing fights without advantage |
| **Offlane** | Secure levels, pressure when possible | Feeding without creating any pressure |

### Fight Analysis (Before/During/After)

**Before the Fight:**
- Setup (smoke, vision advantage, key cooldowns ready)
- Numbers (5v5 or someone missing?)
- Resources (Aegis, buybacks, key items)

**During the Fight:**
- Initiation (who started, chained disables)
- Ability timing (key ults used well)
- Focus fire (right target or spread damage)
- Saves/counters (defensive saves used)

**After the Fight:**
- Objective trade (Roshan/tower/barracks taken)
- Death timers (push opportunity)
- Buyback status (who used, was it necessary)

**Key Question:** Was this fight NECESSARY?

### Late Game Framework (30+ minutes)

**Buyback Discipline:**
- Core heroes: NEVER die without buyback available after 35 minutes
- Team fight with buybacks ready = acceptable risk

**Risk Assessment:**
- **Ahead**: Only take fights you NEED (Roshan, high ground, defending)
- **Behind**: Must take calculated risks to comeback
- **Even**: Map control and Roshan become deciding factors

**Common Late Game Throws:**
- Solo pickoff on carry without buyback
- Fighting without key ultimate
- Pushing high ground without Aegis when ahead

## Implementing Sampling in Custom Clients

If building a custom MCP client, implement the sampling handler:

```python
from mcp import ClientSession

async def handle_sampling_request(request):
    """Handle server's request to sample from client's LLM."""
    prompt = request.messages[0].content

    # Send to your LLM
    response = await your_llm.generate(
        prompt=prompt,
        max_tokens=request.max_tokens or 600
    )

    return SamplingResult(text=response.text)

# Register handler
session.on_sampling_request = handle_sampling_request
```

## Fallback Behavior

The server gracefully handles clients without sampling:

```python
# Server-side logic (simplified)
async def get_hero_performance(...):
    # Always compute raw data
    response = compute_performance_data(...)

    # Try sampling if available
    coaching = await try_coaching_analysis(ctx, prompt)
    response.coaching_analysis = coaching  # None if sampling unavailable

    return response
```

- **No exceptions** thrown if sampling unavailable
- **No degraded data** - raw statistics always complete
- **No fallback prompts** - coaching is simply omitted
- Client's LLM can still interpret raw data using its own knowledge

## Best Practices

### For Users

1. **Use Claude Desktop or Claude Code** for full coaching experience
2. **Ask specific questions** - "How did Batrider's Lassos perform?" triggers ability-filtered analysis
3. **Don't chain tools** - `get_hero_performance` includes everything; no need for additional calls

### For Developers

1. **Implement sampling** in custom clients for full coaching
2. **Handle null coaching_analysis** gracefully in UIs
3. **Don't duplicate prompts** - let the server's coaching handle interpretation
