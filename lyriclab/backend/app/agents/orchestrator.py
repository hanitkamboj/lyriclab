import asyncio
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from app.agents.research_agent import ResearchAgent
from app.agents.lyrics_agent import LyricsAgent
from app.services.youtube_service import YouTubeService
from app.database import query, execute

class OrchestratorAgent:
    @staticmethod
    async def handle_chat_command(command: str, params: Dict[str, Any], user_id: str) -> Dict:
        cmd = command.lower().strip()

        if cmd in ["research", "discover", "trending"]:
            return await OrchestratorAgent._cmd_research(params)

        elif cmd in ["create", "make", "process"]:
            return await OrchestratorAgent._cmd_create(params, user_id)

        elif cmd in ["preview", "preview_video"]:
            return await OrchestratorAgent._cmd_preview(params, user_id)

        elif cmd in ["render", "render_full"]:
            return await OrchestratorAgent._cmd_render(params, user_id)

        elif cmd in ["upload", "publish"]:
            return await OrchestratorAgent._cmd_upload(params, user_id)

        elif cmd in ["bulk", "batch"]:
            return await OrchestratorAgent._cmd_bulk(params, user_id)

        elif cmd in ["auto", "auto_mode"]:
            return await OrchestratorAgent._cmd_auto(params, user_id)

        elif cmd in ["status", "progress"]:
            return await OrchestratorAgent._cmd_status(params, user_id)

        elif cmd in ["analyze", "analyze_style"]:
            return await OrchestratorAgent._cmd_analyze(params)

        elif cmd in ["help", "commands"]:
            return {
                "type": "help",
                "commands": {
                    "research": "Discover trending songs from YouTube/Billboard",
                    "create": "Create a new lyric video project (params: title, artist, song_url)",
                    "preview": "Generate a quick preview (params: project_id)",
                    "render": "Render full quality video (params: project_id)",
                    "upload": "Upload to YouTube (params: project_id, token_json)",
                    "bulk": "Process multiple songs at once",
                    "auto": "Enable auto mode - full pipeline automated",
                    "status": "Check project or job status",
                    "analyze": "Analyze a reference video's style",
                }
            }

        else:
            return {
                "type": "error",
                "message": f"Unknown command: {command}. Type 'help' for available commands.",
            }

    @staticmethod
    async def _cmd_research(params: Dict) -> Dict:
        platforms = params.get("platforms", ["youtube", "billboard"])
        limit = params.get("limit", 20)

        results = await ResearchAgent.research_trending_songs(platforms)

        for song in results[:limit]:
            existing = query("SELECT id FROM trending_songs WHERE title=? AND artist=?",
                           (song["title"], song.get("artist", "")))
            if not existing:
                execute("""
                    INSERT INTO trending_songs (id, title, artist, source, source_url, rank, platform, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(uuid.uuid4()), song["title"], song.get("artist", ""),
                    song.get("source", "youtube"), song.get("source_url", ""),
                    song.get("rank", 0), song.get("source", "youtube"),
                    json.dumps(song),
                ))

        return {
            "type": "research",
            "songs": results[:limit],
            "count": len(results[:limit]),
            "message": f"Found {len(results[:limit])} trending songs",
        }

    @staticmethod
    async def _cmd_create(params: Dict, user_id: str) -> Dict:
        title = params.get("title", "")
        artist = params.get("artist", "")
        song_url = params.get("song_url", "")
        audio_path = params.get("audio_path", "")
        style = params.get("style", "7clouds")

        if not title:
            return {"type": "error", "message": "Title is required"}

        project_id = str(uuid.uuid4())
        execute("""
            INSERT INTO projects (id, user_id, title, artist, song_url, audio_path, style, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'processing')
        """, (project_id, user_id, title, artist, song_url, audio_path, style))

        result = await LyricsAgent.process_song(
            title=title, artist=artist, song_url=song_url,
            audio_path=audio_path, style=style,
        )

        execute("""
            UPDATE projects SET audio_path=?, lyrics_path=?, background_path=?, status=?, metadata=?
            WHERE id=?
        """, (
            result.get("audio_path", ""), result.get("lyrics_path", ""),
            result.get("background_path", ""), result["status"],
            json.dumps(result), project_id,
        ))

        return {
            "type": "project_created",
            "project_id": project_id,
            "status": result["status"],
            "steps": result.get("steps", {}),
            "message": f"Project '{title}' created successfully",
        }

    @staticmethod
    async def _cmd_preview(params: Dict, user_id: str) -> Dict:
        project_id = params.get("project_id", "")

        projects = query("SELECT * FROM projects WHERE id=? AND user_id=?", (project_id, user_id))
        if not projects:
            return {"type": "error", "message": "Project not found"}

        project = projects[0]

        result = {
            "title": project["title"],
            "artist": project["artist"],
            "audio_path": project["audio_path"],
            "lyrics_path": project["lyrics_path"],
            "background_path": project["background_path"],
            "style": project.get("style", "7clouds"),
        }

        result = await LyricsAgent.render_preview(result)

        execute("UPDATE projects SET preview_path=?, status=? WHERE id=?",
               (result.get("preview_path", ""), result["status"], project_id))

        return {
            "type": "preview",
            "project_id": project_id,
            "preview_path": result.get("preview_path", ""),
            "status": result["status"],
            "message": "Preview generated. Type 'render' to render full quality.",
        }

    @staticmethod
    async def _cmd_render(params: Dict, user_id: str) -> Dict:
        project_id = params.get("project_id", "")

        projects = query("SELECT * FROM projects WHERE id=? AND user_id=?", (project_id, user_id))
        if not projects:
            return {"type": "error", "message": "Project not found"}

        project = projects[0]

        result = {
            "title": project["title"],
            "artist": project["artist"],
            "audio_path": project["audio_path"],
            "lyrics_path": project["lyrics_path"],
            "background_path": project["background_path"],
            "style": project.get("style", "7clouds"),
            "resolution": project.get("resolution", "1920x1080"),
            "fps": project.get("fps", 60),
            "bitrate": project.get("bitrate", "10M"),
        }

        result = await LyricsAgent.render_full(result)

        execute("UPDATE projects SET output_path=?, thumbnail_path=?, status=? WHERE id=?",
               (result.get("output_path", ""), result.get("thumbnail_path", ""), result["status"], project_id))

        return {
            "type": "render_complete",
            "project_id": project_id,
            "output_path": result.get("output_path", ""),
            "thumbnail_path": result.get("thumbnail_path", ""),
            "status": result["status"],
            "message": "Full render complete! Type 'upload' to publish to YouTube.",
        }

    @staticmethod
    async def _cmd_upload(params: Dict, user_id: str) -> Dict:
        project_id = params.get("project_id", "")
        token_json = params.get("token_json", "")
        privacy = params.get("privacy", "public")

        projects = query("SELECT * FROM projects WHERE id=? AND user_id=?", (project_id, user_id))
        if not projects:
            return {"type": "error", "message": "Project not found"}

        project = projects[0]

        if not project["output_path"] or not Path(project["output_path"]).exists():
            return {"type": "error", "message": "Video not rendered yet. Run 'render' first."}

        if not token_json:
            channels = query("SELECT * FROM youtube_channels WHERE user_id=?", (user_id,))
            if channels:
                channel = channels[0]
                token_json = json.dumps({
                    "token": channel["access_token"],
                    "refresh_token": channel["refresh_token"],
                })

        if not token_json:
            return {"type": "error", "message": "No YouTube channel connected. Please connect first."}

        seo = YouTubeService.generate_seo_metadata(
            title=project["title"],
            artist=project.get("artist", ""),
            tags=json.loads(project.get("tags", "[]"))
        )

        try:
            result = await YouTubeService.upload_video(
                token_json=token_json,
                video_path=project["output_path"],
                title=seo["title"],
                description=seo["description"],
                tags=seo["tags"],
                category_id=seo["category_id"],
                privacy_status=privacy,
                thumbnail_path=project.get("thumbnail_path"),
            )

            execute("UPDATE projects SET youtube_video_id=?, youtube_status='uploaded', status='published' WHERE id=?",
                   (result["video_id"], project_id))

            # Mark as processed
            execute("INSERT OR IGNORE INTO processed_videos (id, youtube_video_id, title) VALUES (?, ?, ?)",
                   (str(uuid.uuid4()), result["video_id"], project["title"]))

            return {
                "type": "uploaded",
                "project_id": project_id,
                "video_id": result["video_id"],
                "url": result["url"],
                "message": f"Uploaded successfully! View at {result['url']}",
            }
        except Exception as e:
            return {"type": "error", "message": f"Upload failed: {e}"}

    @staticmethod
    async def _cmd_bulk(params: Dict, user_id: str) -> Dict:
        items = params.get("items", [])
        auto_mode = params.get("auto_mode", False)

        if not items:
            trending = await ResearchAgent.research_trending_songs()
            items = [{
                "title": s["title"],
                "artist": s.get("artist", ""),
                "song_url": s.get("source_url", ""),
            } for s in trending[:10]]

        project_ids = []
        for item in items:
            create_params = {
                "title": item.get("title", ""),
                "artist": item.get("artist", ""),
                "song_url": item.get("song_url", ""),
                "style": item.get("style", "7clouds"),
            }
            result = await OrchestratorAgent._cmd_create(create_params, user_id)
            if result.get("project_id"):
                project_ids.append(result["project_id"])

        if auto_mode and project_ids:
            asyncio.create_task(OrchestratorAgent._auto_process_bulk(project_ids, user_id))

        return {
            "type": "bulk_created",
            "project_ids": project_ids,
            "count": len(project_ids),
            "auto_mode": auto_mode,
            "message": f"Created {len(project_ids)} projects in bulk mode",
        }

    @staticmethod
    async def _auto_process_bulk(project_ids: List[str], user_id: str):
        for pid in project_ids:
            try:
                await OrchestratorAgent._cmd_preview({"project_id": pid}, user_id)
                await OrchestratorAgent._cmd_render({"project_id": pid}, user_id)

                channels = query("SELECT * FROM youtube_channels WHERE user_id=?", (user_id,))
                if channels:
                    channel = channels[0]
                    token_json = json.dumps({
                        "token": channel["access_token"],
                        "refresh_token": channel["refresh_token"],
                    })
                    await OrchestratorAgent._cmd_upload({
                        "project_id": pid,
                        "token_json": token_json,
                        "privacy": "public",
                    }, user_id)

                await asyncio.sleep(5)
            except Exception as e:
                print(f"Auto-process failed for {pid}: {e}")

    @staticmethod
    async def _cmd_auto(params: Dict, user_id: str) -> Dict:
        enabled = params.get("enabled", True)

        if enabled:
            asyncio.create_task(OrchestratorAgent._auto_discover_and_process(user_id))

        return {
            "type": "auto_mode",
            "enabled": enabled,
            "message": "Auto mode enabled. System will continuously discover, create, render, and upload."
        }

    @staticmethod
    async def _auto_discover_and_process(user_id: str):
        while True:
            try:
                research = await ResearchAgent.research_trending_songs()
                for song in research[:5]:
                    existing = query(
                        "SELECT id FROM trending_songs WHERE title=? AND artist=? AND processed=1",
                        (song["title"], song.get("artist", ""))
                    )
                    if existing:
                        continue

                    processed = query(
                        "SELECT id FROM processed_videos WHERE title LIKE ?",
                        (f"%{song['title']}%",)
                    )
                    if processed:
                        continue

                    create_result = await OrchestratorAgent._cmd_create(song, user_id)
                    if create_result.get("project_id"):
                        pid = create_result["project_id"]
                        await OrchestratorAgent._cmd_preview({"project_id": pid}, user_id)
                        await OrchestratorAgent._cmd_render({"project_id": pid}, user_id)

                        execute("UPDATE trending_songs SET processed=1 WHERE title=? AND artist=?",
                               (song["title"], song.get("artist", "")))

                await asyncio.sleep(3600)
            except Exception as e:
                print(f"Auto-discover error: {e}")
                await asyncio.sleep(300)

    @staticmethod
    async def _cmd_status(params: Dict, user_id: str) -> Dict:
        project_id = params.get("project_id", "")

        if project_id:
            projects = query("SELECT * FROM projects WHERE id=? AND user_id=?", (project_id, user_id))
            if projects:
                p = projects[0]
                return {
                    "type": "status",
                    "project": dict(p),
                }
            return {"type": "error", "message": "Project not found"}

        projects = query("SELECT id, title, status, created_at FROM projects WHERE user_id=? ORDER BY created_at DESC LIMIT 10", (user_id,))
        jobs = query("SELECT id, job_type, status, progress, message FROM job_queue WHERE user_id=? ORDER BY created_at DESC LIMIT 5", (user_id,))

        return {
            "type": "status",
            "projects": projects,
            "jobs": jobs,
            "total_projects": len(projects),
        }

    @staticmethod
    async def _cmd_analyze(params: Dict) -> Dict:
        video_id = params.get("video_id", "")
        url = params.get("url", "")

        if url and "v=" in url:
            video_id = url.split("v=")[-1].split("&")[0]

        if not video_id:
            return {"type": "error", "message": "Video ID or URL required"}

        style = await ResearchAgent.analyze_video_style(video_id)
        details = await ResearchAgent._get_video_details(video_id)

        return {
            "type": "analysis",
            "video_id": video_id,
            "style": style,
            "details": details,
            "message": "Style analysis complete",
        }
