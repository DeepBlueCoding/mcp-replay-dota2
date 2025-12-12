"""Tests for Pydantic model validation to catch type errors early.

These tests ensure that:
1. All response models accept correct types
2. Models auto-convert floats to ints (via CoercedInt type)
3. Tool outputs are validated through Pydantic classes
"""

import pytest
from pydantic import ValidationError

from src.models.combat_log import (
    AbilityUsage,
    BarracksKill,
    CombatLogEvent,
    CombatLogResponse,
    FightCombatLogResponse,
    FightHighlights,
    FightParticipation,
    HeroCombatAnalysisResponse,
    HeroDeath,
    HeroDeathsResponse,
    ItemPurchase,
    ItemPurchasesResponse,
    KillStreak,
    MultiHeroAbility,
    ObjectiveKillsResponse,
    RoshanKill,
    RunePickup,
    RunePickupsResponse,
    TeamWipe,
    TormentorKill,
    TowerKill,
)
from src.models.pro_scene import (
    LeagueInfo,
    LeaguesResponse,
    PlayerSearchResponse,
    ProMatchesResponse,
    ProMatchSummary,
    ProPlayerInfo,
    ProPlayerResponse,
    RosterEntry,
    SearchResult,
    SeriesSummary,
    TeamInfo,
    TeamResponse,
    TeamSearchResponse,
)
from src.models.tool_responses import (
    CampStack,
    CampStacksResponse,
    CSAtMinuteResponse,
    FightDeath,
    FightDeathDetail,
    FightDetailResponse,
    FightListResponse,
    FightReplayResponse,
    FightSnapshot,
    FightSnapshotHero,
    FightSummary,
    HeroCSData,
    HeroLaneStats,
    HeroPositionTimeline,
    HeroSnapshot,
    HeroStats,
    JungleSummaryResponse,
    KDASnapshot,
    LaneSummaryResponse,
    LaneWinners,
    MatchHeroesResponse,
    MatchTimelineResponse,
    PlayerStatsAtMinute,
    PlayerTimeline,
    PositionPoint,
    PositionTimelineResponse,
    StatsAtMinuteResponse,
    TeamGraphs,
    TeamScores,
)
from src.services.models.farming_data import (
    CampClear,
    CreepKill,
    FarmingPatternResponse,
    FarmingSummary,
    FarmingTransitions,
    ItemTiming,
    LevelTiming,
    MapPositionSnapshot,
    MinuteFarmingData,
    MultiCampClear,
)
from src.services.models.rotation_data import (
    HeroRotationStats,
    PowerRuneEvent,
    Rotation,
    RotationAnalysisResponse,
    RotationOutcome,
    RotationSummary,
    RuneCorrelation,
    RuneRotations,
    WisdomRuneEvent,
)
from src.utils.constants_fetcher import constants_fetcher

# =============================================================================
# Test: CoercedInt auto-converts floats to ints
# =============================================================================


class TestCoercedIntConversion:
    """Test that CoercedInt fields auto-convert floats to ints."""

    def test_player_timeline_converts_float_net_worth(self):
        """PlayerTimeline.net_worth should auto-convert floats to ints."""
        timeline = PlayerTimeline(
            hero="antimage",
            team="radiant",
            net_worth=[72.21094, 92.77344, 104.79375],
            hero_damage=[0.0, 0.0, 0.0],
            kda_timeline=[],
        )
        assert timeline.net_worth == [72, 92, 104]
        assert timeline.hero_damage == [0, 0, 0]

    def test_player_timeline_accepts_int_net_worth(self):
        """PlayerTimeline should accept integer net_worth values."""
        timeline = PlayerTimeline(
            hero="antimage",
            team="radiant",
            net_worth=[72, 92, 104],
            hero_damage=[0, 0, 0],
            kda_timeline=[],
        )
        assert timeline.net_worth == [72, 92, 104]

    def test_team_graphs_converts_float_values(self):
        """TeamGraphs XP/gold fields should auto-convert floats to ints."""
        graphs = TeamGraphs(
            radiant_xp=[100.5, 200.9],
            dire_xp=[150.1, 250.7],
            radiant_gold=[500.3, 600.8],
            dire_gold=[550.2, 650.6],
        )
        assert graphs.radiant_xp == [100, 200]
        assert graphs.dire_xp == [150, 250]
        assert graphs.radiant_gold == [500, 600]
        assert graphs.dire_gold == [550, 650]

    def test_team_graphs_accepts_int_values(self):
        """TeamGraphs should accept integer values."""
        graphs = TeamGraphs(
            radiant_xp=[100, 200],
            dire_xp=[150, 250],
            radiant_gold=[500, 600],
            dire_gold=[550, 650],
        )
        assert graphs.radiant_xp == [100, 200]

    def test_kda_snapshot_converts_float_kills(self):
        """KDASnapshot kills/deaths/assists should auto-convert floats to ints."""
        snapshot = KDASnapshot(
            game_time=300.0,
            kills=1.9,
            deaths=0.1,
            assists=2.7,
            level=5.5,
        )
        assert snapshot.kills == 1
        assert snapshot.deaths == 0
        assert snapshot.assists == 2
        assert snapshot.level == 5

    def test_player_stats_at_minute_converts_float_net_worth(self):
        """PlayerStatsAtMinute.net_worth should auto-convert floats to ints."""
        stats = PlayerStatsAtMinute(
            hero="antimage",
            team="radiant",
            net_worth=5000.75,
            hero_damage=1000.5,
            kills=2.9,
            deaths=1.1,
            assists=3.7,
            level=10.5,
        )
        assert stats.net_worth == 5000
        assert stats.hero_damage == 1000
        assert stats.kills == 2
        assert stats.deaths == 1
        assert stats.assists == 3
        assert stats.level == 10

    def test_hero_snapshot_converts_float_health(self):
        """HeroSnapshot.health/mana should auto-convert floats to ints."""
        snapshot = HeroSnapshot(
            hero="antimage",
            team="radiant",
            player_id=0,
            x=0.0,
            y=0.0,
            health=1000.5,
            max_health=2000.9,
            mana=500.3,
            max_mana=1000.7,
            level=10.2,
            alive=True,
        )
        assert snapshot.health == 1000
        assert snapshot.max_health == 2000
        assert snapshot.mana == 500
        assert snapshot.max_mana == 1000
        assert snapshot.level == 10

    def test_hero_cs_data_converts_float_last_hits(self):
        """HeroCSData.last_hits/denies/gold/level should auto-convert floats to ints."""
        cs_data = HeroCSData(
            hero="antimage",
            team="radiant",
            last_hits=50.9,
            denies=5.1,
            gold=2000.5,
            level=8.7,
        )
        assert cs_data.last_hits == 50
        assert cs_data.denies == 5
        assert cs_data.gold == 2000
        assert cs_data.level == 8

    def test_minute_farming_data_converts_float_gold(self):
        """MinuteFarmingData.gold/last_hits/level should auto-convert floats to ints."""
        farming_data = MinuteFarmingData(
            minute=10,
            gold=5000.5,
            last_hits=100.9,
            level=10.3,
        )
        assert farming_data.minute == 10
        assert farming_data.gold == 5000
        assert farming_data.last_hits == 100
        assert farming_data.level == 10

    def test_combat_log_event_converts_float_value(self):
        """CombatLogEvent.value should auto-convert floats to ints."""
        event = CombatLogEvent(
            type="DAMAGE",
            game_time=300.0,
            game_time_str="5:00",
            attacker="antimage",
            attacker_is_hero=True,
            target="axe",
            target_is_hero=True,
            value=150.75,
        )
        assert event.value == 150


# =============================================================================
# Test: Match Timeline Response Models
# =============================================================================


class TestMatchTimelineModels:
    """Tests for match timeline-related models."""

    def test_match_timeline_response_success(self):
        """MatchTimelineResponse should accept valid data."""
        response = MatchTimelineResponse(
            success=True,
            match_id=12345,
            players=[
                PlayerTimeline(
                    hero="antimage",
                    team="radiant",
                    net_worth=[100, 200, 300],
                    hero_damage=[0, 50, 100],
                    kda_timeline=[
                        KDASnapshot(game_time=60.0, kills=0, deaths=0, assists=0, level=2)
                    ],
                )
            ],
            team_graphs=TeamGraphs(
                radiant_xp=[100, 200],
                dire_xp=[150, 250],
                radiant_gold=[500, 600],
                dire_gold=[550, 650],
            ),
        )
        assert response.success is True
        assert len(response.players) == 1

    def test_stats_at_minute_response_success(self):
        """StatsAtMinuteResponse should accept valid data."""
        response = StatsAtMinuteResponse(
            success=True,
            match_id=12345,
            minute=10,
            players=[
                PlayerStatsAtMinute(
                    hero="antimage",
                    team="radiant",
                    net_worth=5000,
                    hero_damage=1000,
                    kills=1,
                    deaths=0,
                    assists=2,
                    level=10,
                )
            ],
        )
        assert response.minute == 10


# =============================================================================
# Test: Combat Log Response Models
# =============================================================================


class TestCombatLogModels:
    """Tests for combat log-related models."""

    def test_hero_deaths_response_success(self):
        """HeroDeathsResponse should accept valid death data."""
        response = HeroDeathsResponse(
            success=True,
            match_id=12345,
            total_deaths=1,
            deaths=[
                HeroDeath(
                    game_time=288.0,
                    game_time_str="4:48",
                    killer="disruptor",
                    victim="earthshaker",
                    killer_is_hero=True,
                    ability="disruptor_thunder_strike",
                    position_x=1000.0,
                    position_y=-2000.0,
                    location_description="radiant_safelane",
                )
            ],
        )
        assert response.total_deaths == 1

    def test_combat_log_response_success(self):
        """CombatLogResponse should accept valid event data."""
        response = CombatLogResponse(
            success=True,
            match_id=12345,
            total_events=1,
            events=[
                CombatLogEvent(
                    type="DAMAGE",
                    game_time=300.0,
                    game_time_str="5:00",
                    attacker="antimage",
                    attacker_is_hero=True,
                    target="axe",
                    target_is_hero=True,
                    value=150,
                )
            ],
        )
        assert response.total_events == 1

    def test_objective_kills_response_success(self):
        """ObjectiveKillsResponse should accept valid objective data."""
        response = ObjectiveKillsResponse(
            success=True,
            match_id=12345,
            roshan_kills=[
                RoshanKill(
                    game_time=1200.0,
                    game_time_str="20:00",
                    killer="ursa",
                    team="radiant",
                    kill_number=1,
                )
            ],
            tormentor_kills=[
                TormentorKill(
                    game_time=1500.0,
                    game_time_str="25:00",
                    killer="sven",
                    team="dire",
                    side="dire",
                )
            ],
            tower_kills=[
                TowerKill(
                    game_time=900.0,
                    game_time_str="15:00",
                    tower="radiant_t1_mid",
                    team="radiant",
                    tier=1,
                    lane="mid",
                    killer="pugna",
                    killer_is_hero=True,
                )
            ],
            barracks_kills=[
                BarracksKill(
                    game_time=2400.0,
                    game_time_str="40:00",
                    barracks="radiant_melee_mid",
                    team="radiant",
                    lane="mid",
                    type="melee",
                    killer="lycan",
                    killer_is_hero=True,
                )
            ],
        )
        assert len(response.roshan_kills) == 1

    def test_item_purchases_response_success(self):
        """ItemPurchasesResponse should accept valid purchase data."""
        response = ItemPurchasesResponse(
            success=True,
            match_id=12345,
            total_purchases=1,
            purchases=[
                ItemPurchase(
                    game_time=600.0,
                    game_time_str="10:00",
                    hero="antimage",
                    item="item_bfury",
                )
            ],
        )
        assert response.total_purchases == 1

    def test_rune_pickups_response_success(self):
        """RunePickupsResponse should accept valid rune data."""
        response = RunePickupsResponse(
            success=True,
            match_id=12345,
            total_pickups=1,
            pickups=[
                RunePickup(
                    game_time=360.0,
                    game_time_str="6:00",
                    hero="zeus",
                    rune_type="double_damage",
                )
            ],
        )
        assert response.total_pickups == 1


# =============================================================================
# Test: Fight Response Models
# =============================================================================


class TestFightModels:
    """Tests for fight-related models."""

    def test_fight_list_response_success(self):
        """FightListResponse should accept valid fight data."""
        response = FightListResponse(
            success=True,
            match_id=12345,
            total_fights=1,
            teamfights=1,
            skirmishes=0,
            total_deaths=3,
            fights=[
                FightSummary(
                    fight_id="fight_300",
                    start_time=300.0,
                    start_time_str="5:00",
                    end_time=320.0,
                    end_time_str="5:20",
                    duration_seconds=20.0,
                    total_deaths=3,
                    is_teamfight=True,
                    participants=["antimage", "axe", "zeus"],
                    deaths=[
                        FightDeath(
                            game_time=305.0,
                            game_time_str="5:05",
                            killer="antimage",
                            victim="axe",
                            ability="antimage_mana_void",
                        )
                    ],
                )
            ],
        )
        assert response.total_fights == 1

    def test_fight_detail_response_success(self):
        """FightDetailResponse should accept valid fight detail data."""
        response = FightDetailResponse(
            success=True,
            match_id=12345,
            fight_id="fight_300",
            start_time=300.0,
            start_time_str="5:00",
            start_time_seconds=300.0,
            end_time=320.0,
            end_time_str="5:20",
            end_time_seconds=320.0,
            duration_seconds=20.0,
            is_teamfight=True,
            total_deaths=3,
            participants=["antimage", "axe"],
            deaths=[
                FightDeathDetail(
                    game_time=305.0,
                    game_time_str="5:05",
                    killer="antimage",
                    killer_is_hero=True,
                    victim="axe",
                    ability="antimage_mana_void",
                    position_x=1000.0,
                    position_y=-2000.0,
                )
            ],
        )
        assert response.fight_id == "fight_300"

    def test_fight_replay_response_success(self):
        """FightReplayResponse should accept valid replay snapshot data."""
        response = FightReplayResponse(
            success=True,
            match_id=12345,
            start_tick=1000,
            end_tick=2000,
            start_time=300.0,
            start_time_str="5:00",
            end_time=320.0,
            end_time_str="5:20",
            interval_seconds=0.5,
            total_snapshots=1,
            snapshots=[
                FightSnapshot(
                    tick=1000,
                    game_time=300.0,
                    game_time_str="5:00",
                    heroes=[
                        FightSnapshotHero(
                            hero="antimage",
                            team="radiant",
                            x=1000.0,
                            y=-2000.0,
                            health=1500,
                            max_health=2000,
                            alive=True,
                        )
                    ],
                )
            ],
        )
        assert response.total_snapshots == 1


# =============================================================================
# Test: Hero Combat Analysis Models
# =============================================================================


class TestHeroCombatAnalysisModels:
    """Tests for hero combat analysis models."""

    def test_hero_combat_analysis_response_success(self):
        """HeroCombatAnalysisResponse should accept valid analysis data."""
        response = HeroCombatAnalysisResponse(
            success=True,
            match_id=12345,
            hero="jakiro",
            total_fights=5,
            total_teamfights=3,
            total_kills=2,
            total_deaths=1,
            total_assists=8,
            ability_summary=[
                AbilityUsage(
                    ability="jakiro_ice_path",
                    total_casts=12,
                    hero_hits=8,
                    hit_rate=66.7,
                )
            ],
            fights=[
                FightParticipation(
                    fight_id="fight_300",
                    fight_start=300.0,
                    fight_start_str="5:00",
                    fight_end=320.0,
                    fight_end_str="5:20",
                    is_teamfight=True,
                    kills=1,
                    deaths=0,
                    assists=3,
                    abilities_used=[
                        AbilityUsage(
                            ability="jakiro_ice_path",
                            total_casts=3,
                            hero_hits=2,
                            hit_rate=66.7,
                        )
                    ],
                    damage_dealt=1500,
                    damage_received=500,
                )
            ],
        )
        assert response.total_fights == 5

    def test_fight_combat_log_response_with_highlights(self):
        """FightCombatLogResponse should accept valid highlights."""
        response = FightCombatLogResponse(
            success=True,
            match_id=12345,
            hero="faceless_void",
            fight_start=1800.0,
            fight_start_str="30:00",
            fight_end=1830.0,
            fight_end_str="30:30",
            duration=30.0,
            participants=["faceless_void", "crystal_maiden", "antimage", "axe", "zeus"],
            total_events=50,
            events=[],
            highlights=FightHighlights(
                multi_hero_abilities=[
                    MultiHeroAbility(
                        game_time=1805.0,
                        game_time_str="30:05",
                        ability="faceless_void_chronosphere",
                        ability_display="Chronosphere",
                        caster="faceless_void",
                        targets=["antimage", "axe", "zeus"],
                        hero_count=3,
                    )
                ],
                kill_streaks=[
                    KillStreak(
                        game_time=1815.0,
                        game_time_str="30:15",
                        hero="faceless_void",
                        streak_type="triple_kill",
                        kills=3,
                        victims=["antimage", "axe", "zeus"],
                    )
                ],
                team_wipes=[
                    TeamWipe(
                        game_time=1820.0,
                        game_time_str="30:20",
                        team_wiped="dire",
                        duration=15.0,
                        killer_team="radiant",
                    )
                ],
            ),
        )
        assert response.highlights is not None
        assert len(response.highlights.multi_hero_abilities) == 1


# =============================================================================
# Test: Analysis Tool Models
# =============================================================================


class TestAnalysisModels:
    """Tests for analysis tool models."""

    def test_camp_stacks_response_success(self):
        """CampStacksResponse should accept valid stack data."""
        response = CampStacksResponse(
            success=True,
            match_id=12345,
            hero_filter="chen",
            total_stacks=3,
            stacks=[
                CampStack(
                    game_time=420.0,
                    game_time_str="7:00",
                    stacker="chen",
                    camp_type="ancient",
                    stack_count=4,
                )
            ],
        )
        assert response.total_stacks == 3

    def test_jungle_summary_response_success(self):
        """JungleSummaryResponse should accept valid summary data."""
        response = JungleSummaryResponse(
            success=True,
            match_id=12345,
            total_stacks=10,
            stacks_by_hero={"chen": 5, "crystal_maiden": 3, "rubick": 2},
            stack_efficiency_per_10min={"chen": 2.5, "crystal_maiden": 1.5, "rubick": 1.0},
        )
        assert response.total_stacks == 10

    def test_lane_summary_response_success(self):
        """LaneSummaryResponse should accept valid lane data."""
        response = LaneSummaryResponse(
            success=True,
            match_id=12345,
            lane_winners=LaneWinners(top="radiant", mid="even", bot="dire"),
            team_scores=TeamScores(radiant=2.5, dire=1.5),
            hero_stats=[
                HeroLaneStats(
                    hero="antimage",
                    lane="safe_lane",
                    role="core",
                    team="radiant",
                    last_hits_5min=35,
                    last_hits_10min=80,
                    denies_5min=5,
                    denies_10min=12,
                    gold_5min=1500,
                    gold_10min=4000,
                    level_5min=5,
                    level_10min=10,
                )
            ],
        )
        assert response.lane_winners.top == "radiant"

    def test_cs_at_minute_response_success(self):
        """CSAtMinuteResponse should accept valid CS data."""
        response = CSAtMinuteResponse(
            success=True,
            match_id=12345,
            minute=10,
            heroes=[
                HeroCSData(
                    hero="antimage",
                    team="radiant",
                    last_hits=80,
                    denies=12,
                    gold=4000,
                    level=10,
                )
            ],
        )
        assert response.minute == 10

    def test_position_timeline_response_success(self):
        """PositionTimelineResponse should accept valid position data."""
        response = PositionTimelineResponse(
            success=True,
            match_id=12345,
            start_time=0.0,
            end_time=600.0,
            interval_seconds=1.0,
            hero_filter="antimage",
            heroes=[
                HeroPositionTimeline(
                    hero="antimage",
                    team="radiant",
                    positions=[
                        PositionPoint(tick=1000, game_time=60.0, x=1000.0, y=-2000.0)
                    ],
                )
            ],
        )
        assert response.hero_filter == "antimage"


# =============================================================================
# Test: Farming Pattern Models
# =============================================================================


class TestFarmingPatternModels:
    """Tests for farming pattern models."""

    def test_farming_pattern_response_success(self):
        """FarmingPatternResponse should accept valid farming data."""
        response = FarmingPatternResponse(
            success=True,
            match_id=12345,
            hero="antimage",
            start_minute=0,
            end_minute=10,
            level_timings=[
                LevelTiming(level=6, time=420.0, time_str="7:00")
            ],
            item_timings=[
                ItemTiming(item="item_bfury", time=840.0, time_str="14:00")
            ],
            minutes=[
                MinuteFarmingData(
                    minute=5,
                    position_at_start=MapPositionSnapshot(x=1000.0, y=-2000.0, area="radiant_safelane"),
                    position_at_end=MapPositionSnapshot(x=2000.0, y=-3000.0, area="dire_jungle"),
                    camp_sequence=[
                        CampClear(
                            time_str="5:30",
                            camp="large_centaur",
                            tier="hard",
                            area="dire_jungle",
                        )
                    ],
                    lane_creeps_killed=5,
                    camps_cleared=2,
                    gold=2500,
                    last_hits=40,
                    level=6,
                )
            ],
            transitions=FarmingTransitions(
                first_jungle_kill_time=300.0,
                first_jungle_kill_str="5:00",
            ),
            summary=FarmingSummary(
                total_lane_creeps=35,
                total_neutral_creeps=15,
                jungle_percentage=30.0,
                gpm=550.0,
                cs_per_min=8.0,
                camps_cleared={"large_centaur": 3, "medium_wolf": 2},
            ),
            creep_kills=[
                CreepKill(
                    game_time=300.0,
                    game_time_str="5:00",
                    creep_name="npc_dota_neutral_centaur_khan",
                    creep_type="neutral",
                    neutral_camp="large_centaur",
                    camp_tier="hard",
                    position_x=2000.0,
                    position_y=-3000.0,
                    map_area="dire_jungle",
                )
            ],
            multi_camp_clears=[
                MultiCampClear(
                    time_str="14:05",
                    camps=["large_centaur", "medium_wolf"],
                    duration_seconds=1.1,
                    creeps_killed=4,
                    area="dire_jungle",
                )
            ],
        )
        assert response.hero == "antimage"


# =============================================================================
# Test: Rotation Analysis Models
# =============================================================================


class TestRotationAnalysisModels:
    """Tests for rotation analysis models."""

    def test_rotation_analysis_response_success(self):
        """RotationAnalysisResponse should accept valid rotation data."""
        response = RotationAnalysisResponse(
            success=True,
            match_id=12345,
            start_minute=0,
            end_minute=20,
            rotations=[
                Rotation(
                    rotation_id="rot_360",
                    hero="spirit_breaker",
                    role="support",
                    game_time=360.0,
                    game_time_str="6:00",
                    from_lane="top",
                    to_lane="mid",
                    rune_before=RuneCorrelation(
                        rune_type="haste",
                        pickup_time=355.0,
                        pickup_time_str="5:55",
                        seconds_before_rotation=5.0,
                    ),
                    outcome=RotationOutcome(
                        type="kill",
                        deaths_in_window=1,
                        rotation_hero_died=False,
                        kills_by_rotation_hero=["zeus"],
                    ),
                    travel_time_seconds=8.0,
                    returned_to_lane=True,
                    return_time=420.0,
                    return_time_str="7:00",
                )
            ],
            rune_events=RuneRotations(
                power_runes=[
                    PowerRuneEvent(
                        spawn_time=360.0,
                        spawn_time_str="6:00",
                        location="top",
                        taken_by="spirit_breaker",
                        pickup_time=365.0,
                        led_to_rotation=True,
                        rotation_id="rot_360",
                    )
                ],
                wisdom_runes=[
                    WisdomRuneEvent(
                        spawn_time=420.0,
                        spawn_time_str="7:00",
                        location="radiant_jungle",
                        taken_by="invoker",
                        contested=False,
                        deaths_nearby=0,
                    )
                ],
            ),
            summary=RotationSummary(
                total_rotations=5,
                by_hero={
                    "spirit_breaker": HeroRotationStats(
                        hero="spirit_breaker",
                        role="support",
                        total_rotations=3,
                        successful_ganks=2,
                        failed_ganks=1,
                        trades=0,
                        rune_rotations=2,
                    )
                },
                runes_leading_to_kills=2,
                wisdom_rune_fights=0,
                most_active_rotator="spirit_breaker",
            ),
        )
        assert response.summary.total_rotations == 5


# =============================================================================
# Test: Pro Scene Models
# =============================================================================


class TestProSceneModels:
    """Tests for pro scene models."""

    def test_player_search_response_success(self):
        """PlayerSearchResponse should accept valid search data."""
        response = PlayerSearchResponse(
            success=True,
            query="yatoro",
            total_results=1,
            results=[
                SearchResult(
                    id=311360822,
                    name="Yatoro",
                    matched_alias="yatoro",
                    similarity=1.0,
                )
            ],
        )
        assert response.total_results == 1

    def test_team_search_response_success(self):
        """TeamSearchResponse should accept valid search data."""
        response = TeamSearchResponse(
            success=True,
            query="spirit",
            total_results=1,
            results=[
                SearchResult(
                    id=8599101,
                    name="Team Spirit",
                    matched_alias="spirit",
                    similarity=0.9,
                )
            ],
        )
        assert response.total_results == 1

    def test_pro_player_response_success(self):
        """ProPlayerResponse should accept valid player data."""
        response = ProPlayerResponse(
            success=True,
            player=ProPlayerInfo(
                account_id=311360822,
                name="Yatoro",
                personaname="Yatoro",
                team_id=8599101,
                team_name="Team Spirit",
                team_tag="Sprt",
                country_code="UA",
                fantasy_role=1,
                role=1,
                signature_heroes=["npc_dota_hero_terrorblade", "npc_dota_hero_morphling"],
                is_active=True,
                aliases=["Yatoro", "yatoro"],
            ),
        )
        assert response.player.name == "Yatoro"

    def test_team_response_success(self):
        """TeamResponse should accept valid team data."""
        response = TeamResponse(
            success=True,
            team=TeamInfo(
                team_id=8599101,
                name="Team Spirit",
                tag="Sprt",
                logo_url="https://example.com/logo.png",
                rating=1500.0,
                wins=100,
                losses=50,
                aliases=["Spirit", "TS"],
            ),
            roster=[
                RosterEntry(
                    account_id=311360822,
                    player_name="Yatoro",
                    team_id=8599101,
                    role=1,
                    signature_heroes=["npc_dota_hero_terrorblade"],
                    games_played=200,
                    wins=120,
                    is_current=True,
                )
            ],
        )
        assert response.team.name == "Team Spirit"

    def test_pro_matches_response_success(self):
        """ProMatchesResponse should accept valid match data."""
        response = ProMatchesResponse(
            success=True,
            total_matches=1,
            total_series=1,
            matches=[
                ProMatchSummary(
                    match_id=8188461851,
                    radiant_team_id=8261500,
                    radiant_team_name="Xtreme Gaming",
                    dire_team_id=8599101,
                    dire_team_name="Team Spirit",
                    radiant_win=True,
                    radiant_score=35,
                    dire_score=28,
                    duration=2400,
                    start_time=1733580000,
                    league_id=16935,
                    league_name="ESL One Birmingham 2024",
                    series_id=123456,
                    series_type=1,
                    game_number=1,
                )
            ],
            series=[
                SeriesSummary(
                    series_id=123456,
                    series_type=1,
                    series_type_name="Bo3",
                    team1_id=8261500,
                    team1_name="Xtreme Gaming",
                    team1_wins=2,
                    team2_id=8599101,
                    team2_name="Team Spirit",
                    team2_wins=1,
                    winner_id=8261500,
                    winner_name="Xtreme Gaming",
                    is_complete=True,
                    league_id=16935,
                    league_name="ESL One Birmingham 2024",
                    start_time=1733580000,
                    games=[],
                )
            ],
        )
        assert response.total_matches == 1

    def test_leagues_response_success(self):
        """LeaguesResponse should accept valid league data."""
        response = LeaguesResponse(
            success=True,
            total_leagues=1,
            leagues=[
                LeagueInfo(
                    league_id=16935,
                    name="ESL One Birmingham 2024",
                    tier="premium",
                )
            ],
        )
        assert response.total_leagues == 1


# =============================================================================
# Test: HeroStats and MatchHeroesResponse
# =============================================================================


class TestHeroStatsValidation:
    """Tests for HeroStats model validation."""

    def test_hero_stats_with_string_items(self):
        """HeroStats should accept string item names."""
        hero = HeroStats(
            hero_id=1,
            hero_name="npc_dota_hero_antimage",
            localized_name="Anti-Mage",
            team="radiant",
            kills=5,
            deaths=2,
            assists=10,
            last_hits=300,
            denies=20,
            gpm=650,
            xpm=700,
            net_worth=25000,
            hero_damage=15000,
            tower_damage=3000,
            hero_healing=0,
            items=["Power Treads", "Battle Fury", "Manta Style", "Abyssal Blade", "Butterfly", ""],
            item_neutral="Paladin Sword",
        )

        assert hero.hero_id == 1
        assert hero.items[0] == "Power Treads"
        assert hero.items[5] == ""
        assert hero.item_neutral == "Paladin Sword"

    def test_hero_stats_rejects_integer_items(self):
        """HeroStats should reject integer item IDs - they must be converted to names."""
        with pytest.raises(ValidationError):
            HeroStats(
                hero_id=1,
                hero_name="npc_dota_hero_antimage",
                localized_name="Anti-Mage",
                team="radiant",
                kills=5,
                deaths=2,
                assists=10,
                last_hits=300,
                denies=20,
                gpm=650,
                xpm=700,
                net_worth=25000,
                hero_damage=15000,
                tower_damage=3000,
                hero_healing=0,
                items=[208, 65, 147, 0, 0, 0],
            )

    def test_hero_stats_team_literal(self):
        """HeroStats team must be 'radiant' or 'dire'."""
        with pytest.raises(ValidationError):
            HeroStats(
                hero_id=1,
                hero_name="npc_dota_hero_antimage",
                localized_name="Anti-Mage",
                team="invalid_team",
                kills=0,
                deaths=0,
                assists=0,
                last_hits=0,
                denies=0,
                gpm=0,
                xpm=0,
                net_worth=0,
                hero_damage=0,
                tower_damage=0,
                hero_healing=0,
                items=[],
            )

    def test_hero_stats_converts_float_gpm(self):
        """HeroStats.gpm/xpm should auto-convert floats to ints."""
        hero = HeroStats(
            hero_id=1,
            hero_name="npc_dota_hero_antimage",
            localized_name="Anti-Mage",
            team="radiant",
            kills=5.9,
            deaths=2.1,
            assists=10.7,
            last_hits=300.5,
            denies=20.3,
            gpm=650.5,
            xpm=700.9,
            net_worth=25000.75,
            hero_damage=15000.3,
            tower_damage=3000.8,
            hero_healing=500.2,
            items=[],
        )
        assert hero.gpm == 650
        assert hero.xpm == 700
        assert hero.kills == 5
        assert hero.deaths == 2
        assert hero.assists == 10
        assert hero.last_hits == 300
        assert hero.denies == 20
        assert hero.net_worth == 25000
        assert hero.hero_damage == 15000
        assert hero.tower_damage == 3000
        assert hero.hero_healing == 500


class TestMatchHeroesResponseValidation:
    """Tests for MatchHeroesResponse model validation."""

    def test_match_heroes_response_success(self):
        """MatchHeroesResponse should accept valid hero lists."""
        radiant_hero = HeroStats(
            hero_id=1,
            hero_name="npc_dota_hero_antimage",
            localized_name="Anti-Mage",
            team="radiant",
            kills=5,
            deaths=2,
            assists=10,
            last_hits=300,
            denies=20,
            gpm=650,
            xpm=700,
            net_worth=25000,
            hero_damage=15000,
            tower_damage=3000,
            hero_healing=0,
            items=["Power Treads", "Battle Fury", "", "", "", ""],
        )

        response = MatchHeroesResponse(
            success=True,
            match_id=8188461851,
            radiant_heroes=[radiant_hero],
            dire_heroes=[],
        )

        assert response.success is True
        assert response.match_id == 8188461851
        assert len(response.radiant_heroes) == 1


# =============================================================================
# Test: Item Conversion
# =============================================================================


class TestItemConversion:
    """Tests for item ID to name conversion."""

    def test_get_item_name_blink_dagger(self):
        """Item ID 1 should resolve to Blink Dagger."""
        name = constants_fetcher.get_item_name(1)
        assert name == "Blink Dagger"

    def test_get_item_name_power_treads(self):
        """Item ID 63 should resolve to Power Treads."""
        name = constants_fetcher.get_item_name(63)
        assert name == "Power Treads"

    def test_get_item_name_zero_returns_none(self):
        """Item ID 0 (empty slot) should return None."""
        name = constants_fetcher.get_item_name(0)
        assert name is None

    def test_get_item_name_none_returns_none(self):
        """Item ID None should return None."""
        name = constants_fetcher.get_item_name(None)
        assert name is None

    def test_convert_item_ids_to_names(self):
        """convert_item_ids_to_names should convert a list of IDs to names."""
        item_ids = [1, 63, 0, None, 208, 0]
        names = constants_fetcher.convert_item_ids_to_names(item_ids)

        assert len(names) == 6
        assert names[0] == "Blink Dagger"
        assert names[1] == "Power Treads"
        assert names[2] == ""
        assert names[3] == ""
        assert isinstance(names[4], str)
        assert names[5] == ""

    def test_item_conversion_produces_valid_hero_stats(self):
        """Item conversion should produce strings that pass HeroStats validation."""
        item_ids = [1, 63, 208, 0, 0, 0]
        item_names = constants_fetcher.convert_item_ids_to_names(item_ids)

        hero = HeroStats(
            hero_id=1,
            hero_name="npc_dota_hero_antimage",
            localized_name="Anti-Mage",
            team="radiant",
            kills=5,
            deaths=2,
            assists=10,
            last_hits=300,
            denies=20,
            gpm=650,
            xpm=700,
            net_worth=25000,
            hero_damage=15000,
            tower_damage=3000,
            hero_healing=0,
            items=item_names,
            item_neutral=constants_fetcher.get_item_name(676),
        )

        assert all(isinstance(item, str) for item in hero.items)
