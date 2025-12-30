"""
MCP Prompt definitions for Dota 2 coaching.

These prompts are exposed to MCP clients as reusable templates.
Unlike tools (which execute code), prompts are templates the client
can fill in and send to the LLM.
"""


def register_prompts(mcp):
    """Register all MCP prompts with the server."""

    @mcp.prompt
    def analyze_draft(
        radiant_picks: str,
        dire_picks: str,
        radiant_bans: str = "",
        dire_bans: str = "",
    ) -> str:
        """
        Analyze a Dota 2 draft for lane matchups, synergies, counters, and itemization.

        Use the dota2://heroes/all resource for detailed counter matchups.
        """
        bans_section = ""
        if radiant_bans or dire_bans:
            bans_section = f"""
## Bans
- Radiant bans: {radiant_bans or 'None specified'}
- Dire bans: {dire_bans or 'None specified'}
"""

        return f"""Analyze this Dota 2 draft:

## Picks
- Radiant: {radiant_picks}
- Dire: {dire_picks}
{bans_section}
## Analysis Required

1. **Lane Matchups**: Who wins each lane and why?

2. **Draft Synergies**: Key combos and how heroes complement each other.

3. **Counter Picks**: Which picks counter enemy heroes? Who got countered?

4. **Itemization Implications**:
   - **Required counter-items**: Items the draft FORCES enemies to buy
     (e.g., Diffusal vs Medusa, MKB vs PA/WR/evasion, Spirit Vessel vs healers,
     BKB vs heavy magic damage, Linken's vs single-target ultimates like LC/Doom)
   - **Natural item buyers**: Heroes who naturally build counter-items anyway
     (e.g., Pangolier already builds Diffusal, Troll already builds MKB)
   - **Build disruption**: How forced items delay core timings
     (e.g., forcing Linken's on AM delays Manta by 3-4 min)

5. **Expected Item Timings**: Based on lane matchups, estimate key item timings
   (good lane = faster timing, bad lane = delayed timing)

6. **Draft Weaknesses**: What does each draft lack? What would counter it?

7. **Draft Grade**: A/B/C/D for each team with brief justification."""

    @mcp.prompt
    def review_hero_performance(
        hero: str,
        position: str,
        kda: str,
        cs_at_10: str = "",
        gpm: str = "",
        item_timings: str = "",
        fight_participation: str = "",
    ) -> str:
        """
        Review a hero's performance with coaching feedback.

        Evaluates against role-specific expectations (cores by farm/timings,
        supports by impact/saves).
        """
        stats_lines = [f"- K/D/A: {kda}"]
        if cs_at_10:
            stats_lines.append(f"- CS at 10 min: {cs_at_10}")
        if gpm:
            stats_lines.append(f"- GPM: {gpm}")
        if item_timings:
            stats_lines.append(f"- Key item timings: {item_timings}")
        if fight_participation:
            stats_lines.append(f"- Fight participation: {fight_participation}")

        stats_section = "\n".join(stats_lines)

        return f"""Review this player's performance. Judge by ROLE expectations.

**Hero**: {hero} (Position {position})

**Stats**:
{stats_section}

Provide:
1. **Rating** (Poor/Acceptable/Good/Excellent) with justification
2. **Key Issues** - What went wrong?
3. **Improvements** - What to do differently next game?
4. **Positives** - What they did well"""

    @mcp.prompt
    def analyze_deaths(
        deaths_list: str,
        focus_hero: str = "",
    ) -> str:
        """
        Analyze death patterns to identify preventable mistakes.
        """
        focus_section = ""
        if focus_hero:
            focus_section = f"\n**Focus on**: {focus_hero}'s deaths\n"

        return f"""Analyze these deaths for coaching insights:

{deaths_list}
{focus_section}
For key deaths, consider: vision available? power spike timing? objective trade?
buyback usage? item timing delay?

Provide:
1. **Most Impactful Deaths** - Which mattered most and why?
2. **Patterns** - Repeated issues (same area, same killer, solo deaths)?
3. **Categories** - Classify as: Unavoidable / Preventable / Acceptable / Throw
4. **Advice** - How to reduce preventable deaths

Judge by role: carry deaths are catastrophic, offlane deaths may be acceptable."""

    @mcp.prompt
    def review_laning_phase(
        lane_results: str,
        hero_cs_stats: str,
    ) -> str:
        """
        Review the laning phase (0-10 minutes) with coaching feedback.
        """
        return f"""Review this laning phase (0-10 min):

**Lane Results**: {lane_results}

**Hero Stats at 10 min**:
{hero_cs_stats}

Provide:
1. **Lane Outcomes** - Who won each lane? Draft advantage or execution?
2. **Critical Lane** - Which lane mattered most for game outcome?
3. **CS Analysis** - Compare pos1 vs enemy pos3 (offlaner's job is to disrupt carry farm)
4. **Key Mistakes** - What swung lanes? Deaths, rotations, pulls?
5. **Improvements** - What could losing lanes do differently?"""

    @mcp.prompt
    def analyze_teamfight(
        fight_time: str,
        participants: str,
        death_sequence: str,
        fight_winner: str = "",
    ) -> str:
        """
        Analyze a teamfight for coaching insights.
        """
        winner_section = ""
        if fight_winner:
            winner_section = f" | Winner: {fight_winner}"

        return f"""Analyze this teamfight:

**Time**: {fight_time} | **Participants**: {participants}{winner_section}

**Death Sequence**:
{death_sequence}

Provide:
1. **Initiation** - Who started? Planned (smoke/blink) or reactive? Right timing?
2. **Target Priority** - Correct focus? High-value targets killed first?
3. **Ability Usage** - Key ultimates effective? Disables chained? Saves used well?
4. **Positioning** - Who was out of position?
5. **Objective Context** - Fighting for Roshan/tower? Objective taken after? HG defense?"""

    @mcp.prompt
    def compare_itemization(
        hero: str,
        items_built: str,
        enemy_heroes: str,
        game_context: str = "",
    ) -> str:
        """
        Analyze item choices and suggest alternatives.
        """
        context_section = ""
        if game_context:
            context_section = f"\n**Context**: {game_context}"

        return f"""Analyze this item build:

**Hero**: {hero}
**Items**: {items_built}
**Enemy Team**: {enemy_heroes}{context_section}

Provide:
1. **Required Counter-Items** - Did they buy what the enemy draft forces?
   (Diffusal vs Medusa, MKB vs evasion, BKB vs magic damage, Linken's vs LC/Doom)
2. **Timing** - Were items completed on time? Any critical delays?
3. **Build Disruption** - Did forced items delay core timings? Was it worth it?
4. **Missing Items** - What should they have bought but didn't?
5. **Build Order** - Should any items have been prioritized earlier/later?"""

    @mcp.prompt
    def game_turning_points(
        gold_lead_timeline: str,
        key_events: str,
    ) -> str:
        """
        Identify and analyze the turning points of a match.
        """
        return f"""Identify turning points in this match:

**Gold Lead Timeline**: {gold_lead_timeline}

**Key Events**:
{key_events}

Provide:
1. **Major Swings** (2-4 moments) - What happened? Fight, Roshan, pickoff, high ground?
2. **Gold/Map Impact** - How much gold swing? Who got map control after?
3. **Preventable?** - Which swings were mistakes vs good plays by opponent?
4. **Decisive Moment** - Which single moment decided the game outcome?"""
