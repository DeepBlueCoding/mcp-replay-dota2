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

The server includes comprehensive Dota 2 coaching knowledge:

### Position-Specific Expectations

Each position (1-5) has different success metrics:

| Position | Primary Metrics | Acceptable Deaths |
|----------|-----------------|-------------------|
| **Pos 1 (Carry)** | CS@10 (65-80), Item timings | 0-1 before 10:00 |
| **Pos 2 (Mid)** | CS@10 (60-75), Rune control | 0-2 before 10:00 |
| **Pos 3 (Offlane)** | Enemy carry CS disruption | 2-3 acceptable if creating space |
| **Pos 4 (Soft Support)** | Kill participation, Rotations | Context-dependent |
| **Pos 5 (Hard Support)** | Vision uptime, Save usage | Acceptable if saving cores |

### Death Analysis Framework

The coaching analyzes deaths using a 5-question framework:

1. **Was vision available?** - Ward coverage, minimap awareness
2. **Power spike window?** - Pre-6, pre-BKB vulnerability
3. **Did it trade for objectives?** - Roshan, towers, space creation
4. **Buyback usage?** - Correct/incorrect buyback decisions
5. **Item timing impact?** - How much did death delay key items

### CS/GPM Benchmarks

```
Position 1 (Carry) CS Targets:
┌────────┬──────┬────────────┬──────┬───────────┐
│ Minute │ Poor │ Acceptable │ Good │ Excellent │
├────────┼──────┼────────────┼──────┼───────────┤
│ 5      │ <30  │ 30-40      │ 40-50│ 50+       │
│ 10     │ <50  │ 50-65      │ 65-80│ 80+       │
│ 15     │ <80  │ 80-110     │110-140│ 140+     │
│ 20     │ <120 │ 120-160    │160-200│ 200+     │
└────────┴──────┴────────────┴──────┴───────────┘
```

### Fight Analysis

Teamfights are evaluated on:

- **Initiation quality** - Planned vs reactive, ability readiness
- **Target priority** - Were high-value targets focused?
- **Ability usage** - Key ultimates, CC chaining, save items
- **Trade value** - What did each team gain/lose?

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
