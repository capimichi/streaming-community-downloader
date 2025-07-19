import shlex
from typing import List
from injector import inject
import os
import asyncio
import subprocess

from streamingcommunitydownloader.client.StreamingCommunityClient import StreamingCommunityClient
from streamingcommunitydownloader.model.M3uData.M3uData import M3uData
from streamingcommunitydownloader.model.StreamUrl import StreamUrl


class DownloadService:

    @inject
    def __init__(self, 
                 streaming_community_client: StreamingCommunityClient):
        self.streaming_community_client = streaming_community_client

    async def download(
        self, 
        url: str, 
        output_dir: str, 
        season: int = None, 
        episode: int = None, 
        concurrent_downloads: int = 1,
        best_video: bool = False
    ):
        # Verifica che la directory di output esista, altrimenti la crea
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Prima di tutto uso il client per ottenere il titolo
        # title = await self.streaming_community_client.get_title(url)

        is_movie = await self.streaming_community_client.is_movie(url)

        download_urls: List[StreamUrl] = []

        if not is_movie:
            # This is a series, handle season and episode
            episode_urls = await self.streaming_community_client.get_episode_urls(
                url,
                selected_season_number=season,
                selected_episode_number=episode
            )
            download_urls.extend(episode_urls)
        else:
            pass # Handle movie case if needed

        print(f"Found {len(download_urls)} streams to download.")

        # Ora scarico i file
        semaphore = asyncio.Semaphore(concurrent_downloads)

        async def download_with_semaphore(stream_url: StreamUrl):
            async with semaphore:
                await self.download_stream(stream_url, output_dir, best_video)

        await asyncio.gather(*[download_with_semaphore(url) for url in download_urls])

    async def download_stream(self, stream_url: StreamUrl, output_dir: str, best_video: bool):
        output_path = os.path.join(output_dir, stream_url.title)
        if stream_url.season_number is not None and stream_url.episode_number is not None:
            output_path = os.path.join(output_path, f"Season {stream_url.season_number}")
            output_path = os.path.join(output_path, f"{stream_url.title} - S{stream_url.season_number:02}E{stream_url.episode_number:02}.%(ext)s")
        else:
            output_path = os.path.join(output_path, f"{stream_url.title}.%(ext)s")

        # create the directory if it does not exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Verifca con varie test di estensioni se il file esiste già
        extensions_test = ['.mp4', '.mkv', '.avi']
        for ext in extensions_test:
            test_path = output_path.replace('%(ext)s', ext)
            if os.path.exists(test_path):
                print(f"File already exists: {test_path}")
                return

        print(f"Downloading {stream_url.url} to {output_path}")

        # first get j
        command = ["yt-dlp", "-j", stream_url.url]
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            m3u_data = M3uData.model_validate_json(result.stdout)
            print(f"Metadata for {stream_url.url}: {result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"Error getting metadata for {stream_url.url}: {e}")
            return
        
        format_video = None
        format_audio = []
        for format_item in m3u_data.formats or []:
            if format_item.height:
                if not format_video or (
                    (best_video and format_item.height > format_video.height) or 
                    (not best_video and format_item.height < format_video.height)
                ):
                    format_video = format_item
        
            if not format_item.height:
                format_audio.append(format_item)

        # Sort format_audio: "it" language first, others after
        format_audio.sort(key=lambda x: 0 if getattr(x, 'language', None) in ["it", "ita"] else 1)
        
        format_str = format_video.format_id if format_video else ""

        for format_item in format_audio:
            format_str += f"+{format_item.format_id}" if format_item else ""
    

        # Use yt-dlp to download the stream
        command = [
            "yt-dlp", 
            "-f", format_str, 
            "--audio-multistreams",
            "--merge-output-format", "mkv",
            "-o", output_path, 
            stream_url.url
        ]
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error downloading {stream_url.url}: {e}")






