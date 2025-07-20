import click
import asyncio
from streamingcommunitydownloader.container.DefaultContainer import DefaultContainer
from streamingcommunitydownloader.service.DownloadService import DownloadService

@click.command(
    name='download'
)
@click.argument('url')
@click.argument('output_dir')
@click.option('--season', default=None, help='Season number (optional). Default is None. Specify the season number to download a specific season.')
@click.option('--episode', default=None, help='Episode number (optional). Default is None. Specify the episode number to download a specific episode.')
@click.option('--concurrent-downloads', default=1, type=int, help='Number of concurrent downloads. Default is 1. Increase this value to download multiple files simultaneously.')
@click.option('--best-video', is_flag=True, default=False, help='Download the best video quality available. Default is False. Use this flag to prioritize video quality.')
@click.option('--include-title-dir', is_flag=True, default=True, help='Include the title directory in the output path. Default is True. Disable this flag to skip creating a title directory.')
def download_command(url, output_dir, season, episode, concurrent_downloads, best_video, include_title_dir):
    default_container: DefaultContainer = DefaultContainer.getInstance()
    download_service: DownloadService = default_container.get(DownloadService)

    asyncio.run(
        download_service.download(
            url, 
            output_dir,
            season=int(season) if season else None,
            episode=int(episode) if episode else None,
            concurrent_downloads=concurrent_downloads,
            best_video=best_video,
            include_title_dir=include_title_dir
        )
    )
    click.echo('Download process completed successfully!')