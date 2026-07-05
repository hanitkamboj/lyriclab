#!/usr/bin/env python3
"""
LyricLab Standalone Agent
Can run independently without the web dashboard.
Usage: python standalone_agent.py [command]
Commands:
  research           - Find trending songs
  create             - Create a lyric video (interactive)
  auto               - Run auto mode continuously
  bulk <file.json>   - Process bulk from JSON file
  help               - Show help
"""

import sys
import json
import asyncio
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.agents.research_agent import ResearchAgent
from backend.app.agents.lyrics_agent import LyricsAgent
from backend.app.agents.orchestrator import OrchestratorAgent
from backend.app.services.audio_service import AudioService
from backend.app.services.youtube_service import YouTubeService
from backend.app.database import init_db, query, execute
from backend.app.config import OUTPUT_DIR, DOWNLOADS_DIR

async def cmd_research():
    print("\n[LyricLab] Researching trending songs...")
    results = await ResearchAgent.research_trending_songs()
    print(f"\nFound {len(results)} trending songs:")
    for i, song in enumerate(results[:20], 1):
        print(f"  {i}. {song['title']} - {song['artist']} ({song['source']})")
    return results

async def cmd_create():
    print("\n[LyricLab] Create Lyric Video")
    title = input("  Song title: ").strip()
    artist = input("  Artist name: ").strip()
    song_url = input("  YouTube URL (optional): ").strip()
    style = input("  Style [7clouds/minimal/kpop]: ").strip() or "7clouds"

    print("\n  Processing...")
    result = await LyricsAgent.process_song(title, artist, song_url, style=style)

    if result["status"] == "failed":
        print(f"\n  Failed: {result.get('steps', {}).get('audio', {}).get('error', 'Unknown error')}")
        return

    print(f"\n  Audio: {result.get('audio_path', 'N/A')}")
    print(f"  Lyrics: {result.get('lyrics_path', 'N/A')}")
    print(f"  Background: {result.get('background_path', 'N/A')}")

    preview = input("\n  Generate preview? (y/n): ").strip().lower() == 'y'
    if preview:
        result = await LyricsAgent.render_preview(result)
        print(f"  Preview: {result.get('preview_path', 'N/A')}")

    render = input("  Render full quality? (y/n): ").strip().lower() == 'y'
    if render:
        result = await LyricsAgent.render_full(result)
        print(f"  Output: {result.get('output_path', 'N/A')}")
        print(f"  Thumbnail: {result.get('thumbnail_path', 'N/A')}")

    return result

async def cmd_auto():
    print("\n[LyricLab] Auto Mode Activated")
    print("  Continuously discovering, creating, and rendering...")
    print("  Press Ctrl+C to stop.\n")

    while True:
        try:
            trending = await ResearchAgent.research_trending_songs()
            for song in trending[:3]:
                print(f"  Processing: {song['title']} - {song['artist']}")
                result = await LyricsAgent.process_song(
                    song["title"], song.get("artist", ""), song.get("source_url", "")
                )
                if result["status"] != "failed":
                    result = await LyricsAgent.render_preview(result)
                    result = await LyricsAgent.render_full(result)
                    print(f"    Done: {result.get('output_path', 'N/A')}")
                await asyncio.sleep(5)
            print(f"  Cycle complete. Waiting 1 hour...")
            await asyncio.sleep(3600)
        except KeyboardInterrupt:
            print("\n  Auto mode stopped.")
            break
        except Exception as e:
            print(f"  Error: {e}")
            await asyncio.sleep(60)

async def cmd_bulk(filepath: str):
    print(f"\n[LyricLab] Bulk Processing from {filepath}")
    try:
        with open(filepath) as f:
            items = json.load(f)
    except:
        print(f"  Failed to load {filepath}")
        return

    print(f"  Loaded {len(items)} items")

    for i, item in enumerate(items, 1):
        print(f"\n  [{i}/{len(items)}] {item.get('title', 'Unknown')}")
        result = await LyricsAgent.process_song(
            item.get("title", ""), item.get("artist", ""), item.get("song_url", "")
        )
        if result["status"] != "failed":
            result = await LyricsAgent.render_preview(result)
            result = await LyricsAgent.render_full(result)
            print(f"    Done: {result.get('output_path', 'N/A')}")

async def main():
    init_db()

    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1].lower()

    if command == "research":
        await cmd_research()
    elif command == "create":
        await cmd_create()
    elif command == "auto":
        await cmd_auto()
    elif command == "bulk" and len(sys.argv) > 2:
        await cmd_bulk(sys.argv[2])
    else:
        print(__doc__)

if __name__ == "__main__":
    asyncio.run(main())
