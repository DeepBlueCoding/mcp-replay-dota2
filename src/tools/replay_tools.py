"""Replay download and management MCP tools."""

from fastmcp import Context

from ..models.combat_log import DeleteReplayResponse, DownloadReplayResponse


def register_replay_tools(mcp, services):
    """Register replay-related tools with the MCP server."""
    replay_service = services["replay_service"]

    @mcp.tool
    async def delete_replay(match_id: int) -> DeleteReplayResponse:
        """
        Delete cached replay file and parsed data for a match.

        Use this tool when:
        - A replay appears to be corrupted and needs to be re-downloaded
        - You want to force a fresh download of a replay
        - Cached parsed data seems incorrect or outdated

        After deletion, the next analysis request for this match will
        trigger a fresh download and parse.

        Args:
            match_id: The Dota 2 match ID to delete cached data for

        Returns:
            DeleteReplayResponse with deletion status
        """
        file_deleted = False
        cache_deleted = False

        # Delete replay file
        replay_path = replay_service._replay_dir / f"{match_id}.dem"
        if replay_path.exists():
            replay_path.unlink()
            file_deleted = True

        # Delete parsed cache
        cache_deleted = replay_service._cache.delete(match_id)

        if file_deleted or cache_deleted:
            parts = []
            if file_deleted:
                parts.append("replay file")
            if cache_deleted:
                parts.append("parsed cache")
            message = f"Deleted {' and '.join(parts)} for match {match_id}"
        else:
            message = f"No cached data found for match {match_id}"

        return DeleteReplayResponse(
            success=True,
            match_id=match_id,
            file_deleted=file_deleted,
            cache_deleted=cache_deleted,
            message=message,
        )

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
