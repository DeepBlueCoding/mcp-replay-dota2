"""
Coaching prompts for Dota 2 analysis.

Consolidated from skill files:
- SKILL.md: Core coaching methodology
- ROLE_EXPECTATIONS.md: Position-specific guidance
- DEATH_ANALYSIS.md: Death analysis framework
- HERO_BENCHMARKS.md: CS/GPM/Item timing targets
"""

# =============================================================================
# CORE COACHING METHODOLOGY (from SKILL.md)
# =============================================================================

CORE_PHILOSOPHY = """
## Core Philosophy

- **Never dump raw data** - Every number must have context and meaning
- **Patterns over events** - Look for trends across multiple occurrences
- **Role-appropriate analysis** - Judge players by their position's responsibilities
- **Actionable advice** - Every insight should lead to something the player can DO differently
"""

ANALYSIS_WORKFLOW = """
## Analysis Workflow

1. **Context First**: Always understand match context before specifics
2. **Understand the Game State**: Identify key momentum shifts
3. **Deep Dive**: Use specific data for deaths, farming, fights based on what matters
4. **Synthesize**: Connect findings across different data sources
"""

GAME_PHASES = """
## Game Phases

### Laning Phase (0-10 minutes)
- Focus on CS comparisons, first blood, tower damage
- Deaths here are CRITICAL for carries, expected for offlaners
- Rune control and rotations define mid-game trajectory

### Mid Game (10-25 minutes)
- Objective trading, teamfight outcomes
- Item timing relative to expected benchmarks
- Map control and vision

### Late Game (25+ minutes)
- Buyback usage, high-ground attempts
- Carry positioning in fights
- Game-ending mistakes
"""

# =============================================================================
# POSITION-SPECIFIC EXPECTATIONS (from ROLE_EXPECTATIONS.md)
# =============================================================================

POSITION_1_CARRY = """
## Position 1 (Carry / Safelane)

### Laning Phase (0-10 minutes)
**Primary Objectives:**
- Maximize last hits (target: 60-80 by 10:00)
- Minimize deaths (target: 0-1)
- Secure lane equilibrium with support help

**What They Should NOT Do:**
- Rotate to other lanes
- Chase kills aggressively
- Leave lane to contest runes (unless lane is pushed)

**When to Leave Lane:**
- Lane is completely unplayable (3v1 dive tower)
- Already have key item and can join fights
- Taking tower and rotating to another objective

### Mid Game (10-25 minutes)
**Primary Objectives:**
- Farm dangerous areas with team nearby
- Join fights when key cooldowns are ready
- Hit item timing benchmarks

**Decision Matrix:**
| Situation | Should Join? |
|-----------|--------------|
| 5v5 fight at tower | Yes |
| Skirmish far from farm | Usually no |
| Roshan attempt | Yes |
| Defending high ground | Yes |

### Late Game (25+ minutes)
**Primary Objectives:**
- Be the primary damage dealer
- Never die without buyback
- Position correctly in fights (back line, wait for initiation)

**Critical Mistakes:**
- Getting caught alone (game-losing)
- Using buyback incorrectly
- Fighting without BKB when needed
"""

POSITION_2_MID = """
## Position 2 (Mid)

### Laning Phase (0-10 minutes)
**Primary Objectives:**
- Win or go even in CS
- Control power runes (every 2 minutes starting at 2:00)
- Look for rotation opportunities WITH good runes

**Rotation Triggers:**
- Haste rune → Gank sidelane
- DD rune → Gank or dominate lane
- Invisibility rune → Wrap around for kill
- No rune → Stay mid and farm

**What They Should NOT Do:**
- Rotate without runes (loses too much mid farm)
- Leave lane without pushing wave first
- Die to enemy support rotations

### Mid Game (10-25 minutes)
**Primary Objectives:**
- Create tempo with kills and objectives
- Maintain farm while being active
- Enable carry's farm by pressuring map

**Tempo Heroes vs Farming Mids:**
| Type | Examples | Playstyle |
|------|----------|-----------|
| Tempo | Puck, QoP, Spirit Bros | Fight constantly, take objectives |
| Farming | Invoker, Medusa, Tinker | Farm until timing, then dominate |

### Late Game (25+ minutes)
- Depends heavily on hero
- Some become second carry (SF, Ember)
- Some become utility (Puck, Void Spirit)
"""

POSITION_3_OFFLANE = """
## Position 3 (Offlane)

### Laning Phase (0-10 minutes)
**Primary Objectives:**
- Get levels (more important than CS)
- Pressure enemy carry
- Force rotations to your lane (create space)

**Success Metrics:**
| Outcome | Assessment |
|---------|------------|
| Enemy carry free farms | Failed |
| Enemy carry contested, you survived | Success |
| You died 3 times but carry has 40 CS at 10 | Acceptable |
| You dominated and carry has 30 CS | Excellent |

**What Offlaners Can Do:**
- Die to draw enemy resources
- Pull the hard camp
- Trade aggressively even if they die

**What Offlaners Should NOT Do:**
- AFK jungle when lane is playable
- Feed without purpose (dying without drawing anything)
- Take unnecessary fights before level 6

### Mid Game (10-25 minutes)
**Primary Objectives:**
- Initiate fights for your team
- Build aura items (Pipe, Crimson, Vlads)
- Create space for carry to farm

**Playstyle:**
- Be the frontline
- Make enemy focus you, not your carry
- Push dangerous lanes that carry can't

### Late Game (25+ minutes)
**Critical Role:**
- Initiation (Blink + stun/disable)
- Frontline (absorb spells before carry enters)
- Objective control (zoning during Roshan)
"""

POSITION_4_SOFT_SUPPORT = """
## Position 4 (Soft Support / Roamer)

### Laning Phase (0-10 minutes)
**Primary Objectives:**
- Secure lane for offlaner (levels 1-3)
- Rotate for kills (with smoke or through gates)
- Contest power runes
- Stack camps when passing by

**Rotation Priority:**
1. Kill on mid with rune
2. Kill on enemy safelane
3. Defending your safelane carry
4. Stacking for carry

**What They Should NOT Do:**
- AFK sit in lane soaking XP
- Rotate without purpose
- Ignore rune spawns

### Mid Game (10-25 minutes)
**Primary Objectives:**
- Set up kills for cores
- Control vision aggressively
- Enable teamfight initiations

**Item Focus:**
- Mobility (Blink, Force Staff)
- Utility (Spirit Vessel, Solar Crest)
- Situational (Lotus, Glimmer)

### Late Game (25+ minutes)
- Provide utility in fights
- Save items for carry
- Initiation backup (secondary initiator)
"""

POSITION_5_HARD_SUPPORT = """
## Position 5 (Hard Support)

### Laning Phase (0-10 minutes)
**Primary Objectives:**
- Keep carry alive and farming
- Zone enemy offlaner (levels 1-3)
- Pull when lane pushes
- Stack camps
- Place and protect wards

**Priority Order:**
1. Carry survival
2. Lane equilibrium
3. Vision
4. Stacks

**What They Should NOT Do:**
- Take carry's last hits
- Leave carry alone against kill lane
- Die for no reason
- Hoard gold (buy wards, smokes, dust)

**When to Leave Lane:**
- Carry is self-sufficient (level 6+, good matchup)
- Carry asks for solo XP
- Another lane is in crisis

### Mid Game (10-25 minutes)
**Primary Objectives:**
- Maintain vision
- Position behind cores in fights
- Use save items (Glimmer, Force) on cores

**Positioning:**
- Never front of team
- Near but not on top of carry
- Ready to cast spells and items

### Late Game (25+ minutes)
**Critical Responsibilities:**
- Vision around objectives
- Smoke initiation coordination
- Save carry at all costs
- Acceptable to die if carry survives

**Net Worth:**
- Should be lowest on team
- If you have too much gold, you're playing wrong
- Buy team items (Gem, Smokes, Wards)
"""

# =============================================================================
# DEATH ANALYSIS FRAMEWORK (from DEATH_ANALYSIS.md)
# =============================================================================

DEATH_ANALYSIS_5_QUESTIONS = """
## The 5-Question Framework

For EVERY death, ask these questions:

### 1. Was Vision Available?
**Check:**
- Was there a ward covering the area?
- Did the player check minimap before engaging/farming?
- Was smoke used by enemies? (Excusable if so)

**Coaching Points:**
- "You died in an unwarded area - was there a reason you didn't have vision there?"
- "The ward saw them coming 10 seconds before - why no reaction?"
- "Good death - smoked gank, hard to prevent"

### 2. Was It During a Power Spike Window?
**Vulnerable Windows:**
- Before level 6 (no ultimate)
- Before key item (BKB, Manta, Blink)
- When ultimate/key spell on cooldown

**Strong Windows:**
- Just hit level 6/12/18
- Just completed major item
- Full mana and abilities ready

**Coaching Points:**
- "You died 30 seconds before hitting level 6 - playing safer for 1 wave would've changed this"
- "Dying with Chrono on cooldown is unacceptable at this MMR"

### 3. Did the Death Trade for an Objective?
**Worth It:**
- Died but team took Roshan
- Died but team took 2+ towers
- Died but carry farmed freely (space creation)
- Died but enemy used critical cooldowns before upcoming fight

**Not Worth It:**
- Random death farming jungle
- Death defending already-lost tower
- Death chasing for kill that doesn't happen

**Coaching Points:**
- "This death got your team Roshan - acceptable trade"
- "You died for nothing - no objective, no space, just gold for enemy"

### 4. Was Buyback Available/Used Correctly?
**Buyback Considerations:**
- Was buyback available?
- If used, was there an immediate opportunity?
- If not used, did they lose a critical objective?

**When Buyback is Correct:**
- Defense of high ground
- Roshan fight where you can still contribute
- Team fight you can rejoin and win

**When Buyback is Wrong:**
- Random mid-game death with no immediate objective
- When enemy has already taken the objective
- When you'll just die again immediately

**Coaching Points:**
- "Good buyback - rejoined and won the fight"
- "You bought back to defend but they weren't even pushing - wasted gold"
- "Should have bought back here - lost rax because of it"

### 5. What Item Timing Was Delayed?
**Calculate the Impact:**
- Death costs: Net worth × respawn time in lost farm + gold lost to enemy
- Typical death = 1000-2000 gold setback
- Key item delays snowball

**Example Impact:**
- Death at 12:00 delays BKB from 18:00 to 20:00
- Those 2 minutes might cost 2 fights
- Those 2 fights cost 2 towers
- Snowball effect
"""

DEATH_CATEGORIES = """
## Death Categories

### Unavoidable Deaths (Don't Criticize)
- 5-man smoke gank with full execution
- Enemy snowballing from another lane
- Ping/connection issues (visible in replay as standing still)

### Preventable Deaths (Coach Hard)
- Bad positioning without escape
- Fighting without vision
- Greedy farming patterns
- TP'ing into obvious danger

### Acceptable Deaths (Context-Dependent)
- Creating space as pos 3
- Trading for objectives
- Forcing enemy to commit resources

### Throw Deaths (Critical Coaching Moments)
- Dying with Aegis
- Dying solo when team is winning
- Dying before scheduled Roshan
- Dying with buyback on cooldown in late game
"""

DEATH_PATTERNS = """
## Death Pattern Analysis

### Solo Deaths
- More than 3 solo deaths usually indicates positioning issues
- Check if they were farming in dangerous areas
- Check if they were caught pushing waves alone

### Group Deaths (Team Wipes)
- Who initiated badly?
- Who was positioned wrong?
- Was it a forced fight or optional?

### Repeat Deaths
- Dying to same gank pattern = learning issue
- Dying in same area = vision/positioning issue
- Dying to same hero = itemization or awareness issue
"""

DEATH_QUESTIONS_BY_ROLE = """
## Questions to Ask Per Role

### Carry Deaths
1. "Was farming this area worth the risk?"
2. "Did you check enemy positions before committing?"
3. "Would a different item have saved you?"

### Mid Deaths
1. "Did you have rune vision?"
2. "Were enemy supports missing from other lanes?"
3. "Did you push the wave before leaving lane?"

### Offlane Deaths
1. "Did this death create space for your team?"
2. "Were you solo against how many heroes?"
3. "Could you have gotten more from this death?"

### Support Deaths
1. "Did you die saving a core?"
2. "Did you trade correctly (your death vs enemy resources)?"
3. "Was your positioning in the fight correct?"
"""

# =============================================================================
# HERO BENCHMARKS (from HERO_BENCHMARKS.md)
# =============================================================================

CARRY_BENCHMARKS = """
## Position 1 (Carry) Benchmarks

### CS Targets (Creep Score)
| Minute | Poor | Acceptable | Good | Excellent |
|--------|------|------------|------|-----------|
| 5      | <30  | 30-40      | 40-50| 50+       |
| 10     | <50  | 50-65      | 65-80| 80+       |
| 15     | <80  | 80-110     | 110-140| 140+    |
| 20     | <120 | 120-160    | 160-200| 200+    |

### GPM Targets
| Game Phase | Poor | Acceptable | Good | Excellent |
|------------|------|------------|------|-----------|
| 10 min     | <400 | 400-500    | 500-600| 600+    |
| 20 min     | <500 | 500-600    | 600-700| 700+    |
| 30 min     | <550 | 550-650    | 650-750| 750+    |

### Item Timing Benchmarks (Core Items)
| Item | Poor | Acceptable | Good | Excellent |
|------|------|------------|------|-----------|
| Battle Fury | >18:00 | 15-18:00 | 13-15:00 | <13:00 |
| Manta Style | >22:00 | 19-22:00 | 16-19:00 | <16:00 |
| Radiance | >20:00 | 17-20:00 | 14-17:00 | <14:00 |
| BKB | >25:00 | 22-25:00 | 18-22:00 | <18:00 |

### Hero-Specific Notes
**Anti-Mage**: BF timing is crucial. Every minute after 14:00 delays Manta by ~1.5 min.
**Spectre**: Radiance timing less critical post-7.33. Focus on fight participation with Blade Mail.
**Terrorblade**: Manta + Skadi timing for pushing. Should dominate lane CS.
**Faceless Void**: Mask of Madness timing. Look for Chrono impact, not just farm.
"""

MID_BENCHMARKS = """
## Position 2 (Mid) Benchmarks

### CS Targets
| Minute | Poor | Acceptable | Good | Excellent |
|--------|------|------------|------|-----------|
| 5      | <25  | 25-35      | 35-45| 45+       |
| 10     | <45  | 45-60      | 60-75| 75+       |

### Tempo Indicators
- **First item timing**: Most mids want key item by 10-12 min
- **Kill participation**: Should be involved in 50%+ of team kills by 20 min
- **Tower damage**: Contributing to objective pressure

### Hero-Specific Notes
**Storm Spirit**: Orchid/Bloodstone timing defines game. Poor if >18:00.
**Invoker**: Midas vs fighting build. Judge by impact, not just farm.
**Shadow Fiend**: Euls + Blink for kill potential. BKB timing for fights.
"""

OFFLANE_BENCHMARKS = """
## Position 3 (Offlane) Benchmarks

### Expectations (Different from Carries!)
Offlaners are NOT judged primarily by farm. Key metrics:
- **Levels**: Should be same level or higher than enemy carry
- **Lane pressure**: Did enemy carry get free farm or contested?
- **Survivability**: Deaths acceptable IF they created space

### Acceptable Death Counts (Laning Phase)
| Deaths | Assessment |
|--------|------------|
| 0-1    | Excellent - dominated or survived well |
| 2-3    | Acceptable - normal offlane experience |
| 4+     | Problematic - feeding, not creating value |

### Item Timings
| Item | Target | Purpose |
|------|--------|---------|
| Vanguard | 8-10 min | Sustain in lane |
| Blink | 12-16 min | Initiation |
| Pipe/Crimson | 18-22 min | Team auras |
"""

SUPPORT_BENCHMARKS = """
## Position 4 (Soft Support) Benchmarks

### Primary Metrics
- **Kill/Assist count**: Should have high participation
- **Rotation impact**: Did rotations result in kills/objectives?
- **Rune control**: Securing power runes for mid

### Acceptable Net Worth
| Minute | Minimum | Target |
|--------|---------|--------|
| 10     | 1500    | 2500   |
| 20     | 4000    | 6000   |

### Key Items
| Item | Target | Purpose |
|------|--------|---------|
| Boots | 3-4 min | Rotation speed |
| First core | 12-15 min | Could be Blink, Force, Euls |

## Position 5 (Hard Support) Benchmarks

### Primary Metrics
- **Ward placement**: Vision uptime and deward count
- **Stacks**: Camp stacks for carry
- **Deaths**: Acceptable to die saving cores, NOT random deaths

### Acceptable Net Worth (Lowest on Team)
| Minute | Minimum | Maximum (if higher, you're taking too much) |
|--------|---------|---------------------------------------------|
| 10     | 1200    | 2000                                        |
| 20     | 3000    | 5000                                        |

### Key Items
| Item | Target | Purpose |
|------|--------|---------|
| Boots | 5-6 min | Can be later if sacrificing |
| Glimmer/Force | 18-22 min | Save items |
| Wards | Always | Should never have 4 in stock |
"""

# =============================================================================
# FIGHT ANALYSIS FRAMEWORK
# =============================================================================

FIGHT_ANALYSIS = """
## Fight Analysis Framework

When reviewing teamfights:

### 1. Initiation
- Who started the fight?
- Was it planned (smoke, blink) or reactive (caught out)?
- Was it the RIGHT time to fight? (ultimates ready, items completed)

### 2. Target Priority
- Did the right heroes die first?
- Were high-value targets (carry, mid) focused?
- Did supports die protecting cores (good) or randomly (bad)?

### 3. Ability Usage
- Key ultimates used effectively?
- Stuns/disables chained properly?
- Save abilities (Force Staff, Glimmer) used on correct targets?

### 4. Positioning
- Did carries stay safe (backline, wait for initiation)?
- Did frontliners absorb spells?
- Did supports get value before dying?

### 5. Trade Value
- What did each team gain/lose?
- Was the fight worth taking?
- Did the winning team convert into objectives?
"""

# =============================================================================
# COMMON COACHING POINTS
# =============================================================================

COMMON_COACHING_POINTS = """
## Common Coaching Points

### For Carries (Pos 1)
- Farm efficiency: Are they hitting benchmarks?
- Death avoidance: Unnecessary deaths delay key items
- Fight participation: Joining too early vs too late
- Item choices: Adapting to enemy lineup

### For Mids (Pos 2)
- Lane control and rune securing
- Rotation timing (with good runes, not randomly)
- Tempo creation in mid-game
- Not overextending for kills

### For Offlaners (Pos 3)
- Creating space vs feeding
- Knowing when to leave lane
- Initiation timing in fights
- Building appropriate items (aura vs selfish)

### For Supports (Pos 4/5)
- Vision placement and dewarding
- Pull timing and execution
- Save usage on cores
- Sacrificing correctly (not dying for nothing)
"""

# =============================================================================
# NEVER SAY THESE WRONG THINGS
# =============================================================================

COMMON_MISTAKES = """
## NEVER Say These Wrong Things

❌ "The offlaner died 4 times, bad performance"
✅ "The offlaner died 4 times but enemy carry only had 45 CS at 10 - excellent space creation"

❌ "Support has low net worth"
✅ "Support correctly sacrificed farm, lowest net worth as expected"

❌ "Carry had good KDA"
✅ "Carry had good KDA but 52 CS at 10 minutes is below benchmark - farm efficiency issue"

❌ "Mid should rotate more"
✅ "Mid rotated without runes, losing 2 waves of farm - only rotate WITH haste/DD/invis"

❌ "Offlaner should have more CS"
✅ "Offlaner's job is to contest enemy carry, not farm - check enemy carry CS instead"

❌ "Support died too much"
✅ "Evaluate each support death - dying to save carry is correct, random deaths are not"
"""

# =============================================================================
# ASSEMBLED PROMPTS FOR SAMPLING
# =============================================================================


def get_hero_performance_prompt(
    hero: str,
    position: int,
    raw_data: dict,
) -> str:
    """Generate sampling prompt for hero performance analysis."""

    if position == 1:
        role_expectations = POSITION_1_CARRY
        benchmarks = CARRY_BENCHMARKS
    elif position == 2:
        role_expectations = POSITION_2_MID
        benchmarks = MID_BENCHMARKS
    elif position == 3:
        role_expectations = POSITION_3_OFFLANE
        benchmarks = OFFLANE_BENCHMARKS
    elif position == 4:
        role_expectations = POSITION_4_SOFT_SUPPORT
        benchmarks = SUPPORT_BENCHMARKS
    elif position == 5:
        role_expectations = POSITION_5_HARD_SUPPORT
        benchmarks = SUPPORT_BENCHMARKS
    else:
        role_expectations = POSITION_1_CARRY
        benchmarks = CARRY_BENCHMARKS

    return f"""You are a professional Dota 2 coach analyzing a player's performance.

{CORE_PHILOSOPHY}

{role_expectations}

{benchmarks}

{COMMON_MISTAKES}

## Raw Performance Data
- Hero: {hero}
- Position: {position}
- CS@5: {raw_data.get('cs_at_5', 'N/A')}
- CS@10: {raw_data.get('cs_at_10', 'N/A')}
- CS@15: {raw_data.get('cs_at_15', 'N/A')}
- Deaths before 10:00: {raw_data.get('deaths_pre_10', 0)}
- Total K/D/A: {raw_data.get('kills', 0)}/{raw_data.get('deaths', 0)}/{raw_data.get('assists', 0)}
- GPM: {raw_data.get('gpm', 'N/A')}
- Key item timings: {raw_data.get('item_timings', 'N/A')}
- Fight participation: {raw_data.get('fights_participated', 0)}/{raw_data.get('total_fights', 0)} fights
- Ability usage: {raw_data.get('ability_stats', 'N/A')}

## Your Task
Provide a coaching analysis with:
1. **Overall Rating**: Poor / Acceptable / Good / Excellent (with brief justification)
2. **Key Issues** (2-3 points): Be specific, reference benchmarks
3. **Actionable Improvements** (2-3 points): What should they do differently
4. **What They Did Well** (1-2 points): Positive reinforcement

Be direct and specific. Reference the benchmarks above. Judge by ROLE expectations, not generic metrics."""


def get_death_analysis_prompt(
    deaths: list,
    hero_positions: dict,
) -> str:
    """Generate sampling prompt for death pattern analysis."""

    death_list = "\n".join([
        f"- {d.get('victim', 'Unknown')} (pos {hero_positions.get(d.get('victim', '').lower(), '?')}) "
        f"at {d.get('game_time', 0)//60}:{d.get('game_time', 0)%60:02d} "
        f"killed by {d.get('killer', 'Unknown')}"
        f"{' [SMOKE]' if d.get('smoke_involved') else ''}"
        for d in deaths[:20]
    ])

    return f"""You are a professional Dota 2 coach analyzing death patterns.

{CORE_PHILOSOPHY}

{DEATH_ANALYSIS_5_QUESTIONS}

{DEATH_CATEGORIES}

{DEATH_PATTERNS}

{DEATH_QUESTIONS_BY_ROLE}

{COMMON_MISTAKES}

## Deaths in This Match
{death_list}

## Your Task
Provide death analysis with:
1. **Most Impactful Deaths** (2-3): Which deaths mattered most and WHY
2. **Death Patterns**: Any repeated issues (same area, same killer, solo deaths)
3. **Death Categories**: Classify key deaths as Unavoidable/Preventable/Acceptable/Throw
4. **Actionable Advice**: Specific ways to reduce preventable deaths

Be direct and specific. Reference position expectations - carry deaths are catastrophic, \
offlane deaths may be acceptable."""


def get_lane_analysis_prompt(
    lane_data: dict,
    hero_stats: list,
) -> str:
    """Generate sampling prompt for laning phase analysis."""

    hero_summary = "\n".join([
        f"- {h.get('hero', 'Unknown')} ({h.get('team', 'unknown')}, {h.get('lane', 'unknown')}): "
        f"CS@10={h.get('last_hits_10min', 0)}, Level@10={h.get('level_10min', 0)}"
        for h in hero_stats
    ])

    return f"""You are a professional Dota 2 coach analyzing the laning phase.

{CORE_PHILOSOPHY}

{GAME_PHASES}

{POSITION_1_CARRY}

{POSITION_2_MID}

{POSITION_3_OFFLANE}

{POSITION_4_SOFT_SUPPORT}

{POSITION_5_HARD_SUPPORT}

{CARRY_BENCHMARKS}

{MID_BENCHMARKS}

{COMMON_MISTAKES}

## Lane Results (0-10 minutes)
- Top lane winner: {lane_data.get('top_winner', 'Unknown')}
- Mid lane winner: {lane_data.get('mid_winner', 'Unknown')}
- Bot lane winner: {lane_data.get('bot_winner', 'Unknown')}
- Radiant laning score: {lane_data.get('radiant_score', 'N/A')}
- Dire laning score: {lane_data.get('dire_score', 'N/A')}

## Hero Stats at 10 Minutes
{hero_summary}

## Your Task
Provide laning analysis with:
1. **Lane Outcomes**: Who won each lane and WHY
2. **Critical Lane**: Which lane mattered most for the game
3. **Key Mistakes**: What swung lanes (missed CS, deaths, rotations)
4. **Improvement Advice**: What could losing lanes have done differently

Judge each player by their ROLE expectations. Carries should have 65-80 CS, offlaners should contest enemy carry."""


def get_teamfight_analysis_prompt(
    fight_data: dict,
    deaths: list,
) -> str:
    """Generate sampling prompt for teamfight analysis."""

    death_sequence = "\n".join([
        f"- {d.get('game_time_str', '?:??')}: {d.get('killer', 'Unknown')} killed {d.get('victim', 'Unknown')}"
        f"{' with ' + d.get('ability', '') if d.get('ability') else ''}"
        for d in deaths
    ])

    return f"""You are a professional Dota 2 coach analyzing a teamfight.

{CORE_PHILOSOPHY}

{FIGHT_ANALYSIS}

{COMMON_COACHING_POINTS}

{COMMON_MISTAKES}

## Fight Details
- Time: {fight_data.get('start_time_str', 'Unknown')} - {fight_data.get('end_time_str', 'Unknown')}
- Duration: {fight_data.get('duration', 0):.1f} seconds
- Total deaths: {fight_data.get('total_deaths', 0)}
- Participants: {', '.join(fight_data.get('participants', []))}

## Death Sequence
{death_sequence}

## Your Task
Provide fight analysis with:
1. **Initiation**: Who started? Was it good timing? Planned or reactive?
2. **Target Priority**: Did the right heroes die first? Were key targets focused?
3. **Key Moments**: Which abilities or plays decided the fight?
4. **Trade Value**: Who won and what did they gain? Worth taking?
5. **Coaching Points**: What could each side do better next time?

Be specific about hero names and timing."""
