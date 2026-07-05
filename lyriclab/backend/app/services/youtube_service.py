import json
import asyncio
from typing import Optional, Dict, List, Any
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from app.config import YouTubeConfig, DATA_DIR

SCOPES = ["https://www.googleapis.com/auth/youtube", "https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube.force-ssl"]

class YouTubeService:
    @staticmethod
    def get_oauth_flow() -> InstalledAppFlow:
        client_config = {"web": {
            "client_id": YouTubeConfig.client_id,
            "project_id": YouTubeConfig.project_id,
            "auth_uri": YouTubeConfig.auth_uri,
            "token_uri": YouTubeConfig.token_uri,
            "client_secret": YouTubeConfig.client_secret,
        }}
        return InstalledAppFlow.from_client_config(client_config, SCOPES)

    @staticmethod
    def get_credentials(token_json: Optional[str] = None) -> Optional[Credentials]:
        if token_json:
            try:
                data = json.loads(token_json)
                return Credentials.from_authorized_user_info(data, SCOPES)
            except:
                pass
        return None

    @staticmethod
    def build_service(token_json: str):
        creds = YouTubeService.get_credentials(token_json)
        if not creds:
            raise Exception("Invalid YouTube credentials")
        return build("youtube", "v3", credentials=creds, developerKey=YouTubeConfig.api_key)

    @staticmethod
    async def upload_video(token_json: str, video_path: str, title: str, description: str = "",
                           tags: List[str] = None, category_id: str = "10",
                           privacy_status: str = "public", thumbnail_path: Optional[str] = None,
                           playlist_ids: List[str] = None) -> Dict[str, Any]:
        def _upload():
            youtube = YouTubeService.build_service(token_json)
            body = {"snippet": {"title": title, "description": description, "tags": tags or [],
                    "categoryId": category_id}, "status": {"privacyStatus": privacy_status, "selfDeclaredMadeForKids": False}}
            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
            request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
            response = None
            while response is None:
                status, response = request.next_chunk()
            video_id = response.get("id")
            if thumbnail_path and video_id:
                try:
                    youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(thumbnail_path)).execute()
                except:
                    pass
            if playlist_ids and video_id:
                for pid in playlist_ids:
                    try:
                        youtube.playlistItems().insert(part="snippet", body={"snippet": {
                            "playlistId": pid, "resourceId": {"kind": "youtube#video", "videoId": video_id}}}).execute()
                    except:
                        pass
            return {"video_id": video_id, "url": f"https://youtube.com/watch?v={video_id}"}
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _upload)

    @staticmethod
    async def get_channel_info(token_json: str) -> Dict[str, Any]:
        def _get():
            youtube = YouTubeService.build_service(token_json)
            request = youtube.channels().list(part="snippet,statistics", mine=True)
            response = request.execute()
            if response.get("items"):
                item = response["items"][0]
                return {"channel_id": item["id"], "title": item["snippet"]["title"],
                        "description": item["snippet"]["description"],
                        "subscriber_count": item["statistics"].get("subscriberCount", 0),
                        "video_count": item["statistics"].get("videoCount", 0)}
            return {}
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _get)

    @staticmethod
    async def check_video_exists(token_json: str, video_id: str) -> bool:
        def _check():
            youtube = YouTubeService.build_service(token_json)
            try:
                youtube.videos().list(part="id", id=video_id).execute()
                return True
            except HttpError:
                return False
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _check)

    @staticmethod
    async def update_video_metadata(token_json: str, video_id: str, title: Optional[str] = None,
                                     description: Optional[str] = None, tags: Optional[List[str]] = None,
                                     category_id: Optional[str] = None, privacy_status: Optional[str] = None) -> bool:
        def _update():
            youtube = YouTubeService.build_service(token_json)
            body = {"id": video_id, "snippet": {}, "status": {}}
            if title: body["snippet"]["title"] = title
            if description: body["snippet"]["description"] = description
            if tags is not None: body["snippet"]["tags"] = tags
            if category_id: body["snippet"]["categoryId"] = category_id
            if privacy_status: body["status"]["privacyStatus"] = privacy_status
            youtube.videos().update(part="snippet,status", body=body).execute()
            return True
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _update)

    @staticmethod
    def generate_seo_metadata(title: str, artist: str, tags: List[str] = None) -> Dict[str, Any]:
        base_tags = [title, artist, f"{title} lyrics", f"{artist} lyrics", "lyric video", "lyrics", "music", "song", "LyricLab"]
        if tags: base_tags.extend(tags)
        description = (f"{title} - {artist} (Lyric Video)\n\n🎵 {title} by {artist}\n\n"
                       f"📌 Don't forget to LIKE, COMMENT, and SUBSCRIBE!\n\n"
                       f"🔔 Turn on notifications to never miss an update!\n\n"
                       f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n🔊 Follow {artist}:\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                       f"#Lyrics #LyricVideo #Music #Song #Trending")
        return {"title": f"{title} - {artist} (Lyric Video)", "description": description,
                "tags": list(set(base_tags)), "category_id": "10"}
