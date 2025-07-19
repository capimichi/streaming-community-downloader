import click

from streamingcommunitydownloader.command.download_command import download_command

@click.group()
def cli():
    pass

cli.add_command(download_command)

def main():
    cli()

if __name__ == '__main__':
    main()