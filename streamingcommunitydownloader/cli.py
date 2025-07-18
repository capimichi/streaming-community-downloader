import click

from streamingcommunitydownloader.command.download_command import download_command

@click.group()
def cli():
    pass

cli.add_command(download_command)

if __name__ == '__main__':
    cli()