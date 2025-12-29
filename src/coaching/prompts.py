"""
Coaching prompts for Dota 2 analysis.

Constants used by server instructions and sampling prompts.
Personas are loaded from data/personas/ directory.
"""

from .personas import get_coaching_persona, get_position_framework

# =============================================================================
# COACHING PERSONA (loaded from file)
# =============================================================================


def _get_persona() -> str:
    """Load coaching persona, with fallback for missing file."""
    try:
        return get_coaching_persona()
    except FileNotFoundError:
        return _FALLBACK_PERSONA


_FALLBACK_PERSONA = """
You are a professional Dota 2 coach and analyst with extensive competitive experience.
Focus on actionable advice, patterns over events, and role-appropriate analysis.
"""

# Backwards compatibility export
COACHING_PERSONA = _get_persona()

# =============================================================================
# CORE METHODOLOGY (used by server instructions)
# =============================================================================

CORE_PHILOSOPHY = """
## Core Philosophy

- **Never dump raw data** - Every number must have context and meaning
- **Patterns over events** - Look for trends across multiple occurrences
- **Role-appropriate analysis** - Judge players by their position's responsibilities
- **Actionable advice** - Every insight should lead to something the player can DO differently
"""

ANALYSIS_WORKFLOW = """
## Analysis Approach

1. **Win condition** - What does each draft want to do? Who has the timing advantage?
2. **Execution check** - Did they play their draft? Or did they deviate?
3. **The inflection point** - Find THE moment the game turned (there's always one)
4. **The "why"** - Don't just describe events, explain why they mattered
5. **Counterfactual** - What could the losing side have done differently?
"""

# =============================================================================
# ROLE EXPECTATIONS (consolidated from 5 position constants)
# =============================================================================

ROLE_EXPECTATIONS = """
## Role Expectations

**Position 1 (Carry)**: Maximize CS, minimize deaths. Never rotate early.
Join fights only with key items/ultimates ready. Late game: never die without buyback.

**Position 2 (Mid)**: Win CS, control power runes. Rotate only WITH good runes (haste/DD/invis).
Create tempo mid-game. Some become second carry, some become utility.

**Position 3 (Offlane)**: Disrupt enemy carry's farm (compare their CS vs yours).
Deaths acceptable if they drew resources. Mid-game: initiate, build auras, frontline.

**Position 4 (Soft Support)**: Secure offlane levels 1-3, then rotate with smoke/runes.
Stack camps. Mid-game: set up kills, aggressive vision, mobility items.

**Position 5 (Hard Support)**: Keep carry alive, zone offlaner, pull, stack, ward.
Lowest net worth expected. Die to save cores if needed.
"""

# =============================================================================
# LANE RECOVERY FRAMEWORK
# =============================================================================

LANE_RECOVERY = """
## Lane Recovery

When a lane is lost, evaluate the response:

**Carry (pos 1) losing lane:**
- Expected response: Jungle transition at level 5-6 with minimal items
- Red flag: Staying in lane dying repeatedly instead of rotating
- Support should stack and create jungle space

**Mid (pos 2) losing lane:**
- Expected response: Stack-farming, rune control, rotate with power runes
- Red flag: Forcing fights without level/item advantage
- Should focus on getting back into the game via jungle/stacks

**Offlane (pos 3) losing lane:**
- Expected response: Secure levels, pressure when possible, don't feed
- Sometimes acceptable: Dying is fine if enemy carry had to commit resources
- Red flag: Feeding without creating any pressure

**Key Question**: Did the losing lane adapt their gameplan?
"""

# =============================================================================
# DEATH ANALYSIS (simplified)
# =============================================================================

DEATH_FRAMEWORK = """
## Death Analysis

For each death, ask:
1. **Vision** - Ward coverage? Smoke gank (excusable)?
2. **Timing** - Before key level/item? Ult on cooldown?
3. **Trade** - Got objective? Created space? Or died for nothing?
4. **Buyback** - Available? Used correctly?
5. **Impact** - How much did this delay key items?
"""

DEATH_CATEGORIES = """
## Death Categories

**Unavoidable**: Smoke gank, enemy snowballing, connection issues
**Preventable**: Bad positioning, no vision, greedy farming, TP into danger
**Acceptable**: Space creation (pos 3), trading for objectives, forcing cooldowns
**Throw**: Dying with Aegis, solo death while winning, before Roshan, no buyback late
"""

DEATH_PATTERNS = """
## Death Patterns

**Solo deaths** (3+): Positioning issue, farming dangerous areas
**Team wipes**: Who initiated badly? Forced or optional fight?
**Repeat deaths**: Same pattern = learning issue, same area = vision issue, same hero = itemization issue
"""

# =============================================================================
# FIGHT ANALYSIS (simplified)
# =============================================================================

FIGHT_ANALYSIS = """
## Fight Analysis

### Before the Fight
- **Setup**: Smoke? Vision advantage? Waiting for key cooldown?
- **Numbers**: 5v5 or someone missing? Who arrived late?
- **Resources**: Aegis? Buybacks available? Key items completed?

### During the Fight
- **Initiation**: Who started? Good target? Chained disables?
- **Ability Timing**: Key ults used well? (Black Hole, RP, Ravage)
- **Focus Fire**: Did they focus the right target or spread damage?
- **Saves/Counters**: Defensive saves used? (Glimmer, Force, BKB)

### After the Fight
- **Objective Trade**: Did the winner take Roshan/tower/barracks?
- **Death Timers**: Long respawns = push opportunity
- **Buyback Status**: Who used buyback? Was it necessary?

### Key Question
Was this fight NECESSARY? Or did they force a bad engagement?
"""

# =============================================================================
# COMMON MISTAKES (keep - prevents bad analysis)
# =============================================================================

COMMON_MISTAKES = """
## NEVER Say These Wrong Things

### Role Misunderstandings
❌ "The offlaner died 4 times, bad performance"
✅ "The offlaner died 4 times but enemy carry only had 45 CS at 10 - space created"

❌ "Support has low net worth"
✅ "Support correctly sacrificed farm, lowest net worth as expected"

❌ "Carry had good KDA"
✅ "Carry had good KDA but 52 CS at 10 min is poor - farm efficiency issue"

❌ "Mid should rotate more"
✅ "Mid rotated without runes, lost 2 waves - only rotate WITH haste/DD/invis"

❌ "Offlaner should have more CS"
✅ "Offlaner's job is to disrupt enemy carry - check enemy carry CS instead"

### Strategic Mistakes
❌ "They should have pushed high ground"
✅ "They had Aegis but 2 heroes were dead - wait for full team + Aegis"

❌ "They lost the teamfight"
✅ "They lost the teamfight but traded for Roshan - net positive"

❌ "Bad item choice"
✅ "BKB would have prevented 3 of their 4 deaths this fight - itemization issue"

### Late Game Analysis
❌ "Carry was farming when team died"
✅ "Carry was farming but team forced fight without him - communication/timing issue"

❌ "They threw the game"
✅ "At 45:00 with no buybacks, they took a fight they didn't need - risk management"
"""

# =============================================================================
# LATE GAME FRAMEWORK
# =============================================================================

LATE_GAME_FRAMEWORK = """
## Late Game Analysis (30+ minutes)

**Buyback Discipline:**
- Core heroes: NEVER die without buyback available after 35 minutes
- If died without buyback → analyze why they were in that position
- Team fight with buybacks ready = acceptable risk

**Objective Priority:**
1. Aegis timing - fights with Aegis vs without
2. Barracks status - mega creeps pressure
3. Vision control - high ground ward battles

**Risk Assessment:**
- Ahead: Only take fights you NEED (Roshan, high ground, defending)
- Behind: Must take calculated risks to comeback
- Even: Map control and Roshan become deciding factors

**Common Late Game Throws:**
- Solo pickoff on carry without buyback
- Fighting without key ultimate (Black Hole, RP, etc.)
- Pushing high ground without Aegis when ahead
- Not respecting enemy's powerspike timing
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
    kills = raw_data.get('kills', 0)
    deaths = raw_data.get('deaths', 0)
    assists = raw_data.get('assists', 0)
    fights_in = raw_data.get('fights_participated', 0)
    fights_total = raw_data.get('total_fights', 0)
    abilities = raw_data.get('ability_stats', 'N/A')

    persona = _get_persona()
    position_framework = get_position_framework(position) or ""

    # Include position-specific framework if available
    framework_section = ""
    if position_framework:
        framework_section = f"\n\n## Position-Specific Analysis\n{position_framework}"

    return f"""{persona}
{ROLE_EXPECTATIONS}
{COMMON_MISTAKES}{framework_section}

**Hero**: {hero} (Position {position})
**Stats**: K/D/A {kills}/{deaths}/{assists}
**Fights**: {fights_in}/{fights_total}
**Abilities**: {abilities}

Provide: Rating (Poor/Acceptable/Good/Excellent), Key Issues, Improvements, Positives.
Judge by ROLE expectations and position-specific framework if provided."""


def get_death_analysis_prompt(
    deaths: list,
    hero_positions: dict,
) -> str:
    """Generate sampling prompt for death pattern analysis."""
    death_list = "\n".join([
        f"- {d.get('victim', 'Unknown')} (pos {hero_positions.get(d.get('victim', '').lower(), '?')}) "
        f"at {int(d.get('game_time', 0))//60}:{int(d.get('game_time', 0))%60:02d} "
        f"killed by {d.get('killer', 'Unknown')}"
        for d in deaths[:20]
    ])

    return f"""{_get_persona()}
{DEATH_FRAMEWORK}
{DEATH_CATEGORIES}
{DEATH_PATTERNS}
{COMMON_MISTAKES}

**Deaths**:
{death_list}

Provide: Most Impactful Deaths, Patterns, Categories (Unavoidable/Preventable/Acceptable/Throw), Advice."""


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

    top = lane_data.get('top_winner', '?')
    mid = lane_data.get('mid_winner', '?')
    bot = lane_data.get('bot_winner', '?')
    rad = lane_data.get('radiant_score', 'N/A')
    dire = lane_data.get('dire_score', 'N/A')

    return f"""{_get_persona()}
{ROLE_EXPECTATIONS}
{LANE_RECOVERY}
{COMMON_MISTAKES}

**Lane Winners**: Top={top}, Mid={mid}, Bot={bot}
**Scores**: Radiant {rad} vs Dire {dire}

**Hero Stats at 10 min**:
{hero_summary}

Provide: Lane Outcomes (who won and why), Critical Lane, Key Mistakes, Improvements.
Compare pos1 CS vs enemy pos3 to judge offlaner impact."""


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

    start = fight_data.get('start_time_str', '?')
    end = fight_data.get('end_time_str', '?')
    dur = fight_data.get('duration', 0)
    total = fight_data.get('total_deaths', 0)
    parts = ', '.join(fight_data.get('participants', []))

    return f"""{_get_persona()}
{FIGHT_ANALYSIS}
{COMMON_MISTAKES}

**Fight**: {start} - {end} ({dur:.1f}s)
**Deaths**: {total}
**Participants**: {parts}

**Death Sequence**:
{death_sequence}

Provide: Initiation, Target Priority, Key Moments, Objective Context."""
