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
def download_command(url, output_dir, season, episode, concurrent_downloads):
    default_container: DefaultContainer = DefaultContainer.getInstance()
    download_service: DownloadService = default_container.get(DownloadService)

    asyncio.run(
        download_service.download(
            url, 
            output_dir,
            season=int(season) if season else None,
            episode=int(episode) if episode else None,
            concurrent_downloads=concurrent_downloads
        )
    )
    click.echo('Download process completed successfully!')