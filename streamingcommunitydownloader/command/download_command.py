import click
import asyncio
from streamingcommunitydownloader.container.DefaultContainer import DefaultContainer
from streamingcommunitydownloader.service.DownloadService import DownloadService

@click.command(
    name='download'
)
@click.argument('url')
@click.argument('output_dir')
@click.option('--season', default=None, help='Season number (optional).')
@click.option('--episode', default=None, help='Episode number (optional).')
@click.option('--concurrent-downloads', default=1, type=int, help='Number of concurrent downloads.')
@click.option('--best-video', is_flag=True, default=False, help='Download the best video quality available.')
@click.option('--include-title-dir', is_flag=True, default=True, help='Include the title directory in the output path.')
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