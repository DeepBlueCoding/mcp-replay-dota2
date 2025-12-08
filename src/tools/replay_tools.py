"""Replay download and management MCP tools."""

from fastmcp import Context

from ..models.combat_log import DownloadReplayResponse


def register_replay_tools(mcp, services):
    """Register replay-related tools with the MCP server."""
    replay_service = services["replay_service"]

    @mcp.tool
    async def download_replay(match_id: int, ctx: Context) -> DownloadReplayResponse:
        """
        Download and cache the replay file for a Dota 2 match.

        Use this tool FIRST before asking analysis questions about a match.
        Replay files are large (50-400MB) and can take 1-5 minutes to download.

        Once downloaded, the replay is cached locally and subsequent queries
        for the same match will be instant.

        Progress is reported during download:
        - 0-10%: Checking cache and getting replay URL
        - 10-40%: Downloading compressed file
        - 40-50%: Extracting replay
        - 50-95%: Parsing replay
        - 95-100%: Caching results

        Args:
            match_id: The Dota 2 match ID (from OpenDota, Dotabuff, or in-game)

        Returns:
            DownloadReplayResponse with success status and file info
        """
        async def progress_callback(current: int, total: int, message: str) -> None:
            await ctx.report_progress(current, total)

        if replay_service.is_downloaded(match_id):
            file_size_mb = replay_service.get_replay_file_size(match_id)
            await ctx.report_progress(100, 100)
            return DownloadReplayResponse(
                success=True,
                match_id=match_id,
                replay_path=str(replay_service._replay_dir / f"{match_id}.dem"),
                file_size_mb=round(file_size_mb or 0, 1),
                already_cached=True,
            )

        try:
            replay_path = await replay_service.download_only(match_id, progress=progress_callback)
            file_size_mb = replay_path.stat().st_size / (1024 * 1024)
            return DownloadReplayResponse(
                success=True,
                match_id=match_id,
                replay_path=str(replay_path),
                file_size_mb=round(file_size_mb, 1),
                already_cached=False,
            )
        except ValueError as e:
            return DownloadReplayResponse(success=False, match_id=match_id, error=str(e))
        except Exception as e:
            return DownloadReplayResponse(
                success=False,
                match_id=match_id,
                error=f"Could not download replay: {e}",
            )
