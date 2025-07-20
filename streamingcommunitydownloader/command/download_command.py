import click
import asyncio
from streamingcommunitydownloader.container.DefaultContainer import DefaultContainer
from streamingcommunitydownloader.service.DownloadService import DownloadService

@click.command(
    name='download'
)
@click.argument('url')
@click.argument('output_dir')
@click.option('--season', default=None, help='Season number (optional). Default is None. Specify the season number to download a specific season. Example: --season 2')
@click.option('--episode', default=None, help='Episode number (optional). Default is None. Specify the episode number to download a specific episode. Example: --episode 5')
@click.option('--concurrent-downloads', default=1, type=int, help='Number of concurrent downloads. Default is 1. Increase this value to download multiple files simultaneously. Example: --concurrent-downloads 3')
@click.option('--best-video', is_flag=True, default=False, help='Download the best video quality available. Default is False. Use this flag to prioritize video quality. Example: --best-video')
@click.option('--exclude-title-dir', is_flag=True, default=False, help='Exclude the title directory from the output path. Default is False. Use this flag to skip creating a title directory. Example: --exclude-title-dir')
@click.option('--proxy', default=None, help='Proxy server to use. Format: protocol://user:pass@host:port. Example: --proxy http://127.0.0.1:8080')
def download_command(url, output_dir, season, episode, concurrent_downloads, best_video, exclude_title_dir, proxy):
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
            exclude_title_dir=exclude_title_dir,
            proxy=proxy
        )
    )
    click.echo('Download process completed successfully!')