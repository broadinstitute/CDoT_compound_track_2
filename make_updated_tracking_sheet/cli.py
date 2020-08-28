"""
Entry point to 'make_updated_tracking_sheet' command line script.
"""

from make_updated_tracking_sheet.make_updated_tracking_sheet import main
import click


# Using click to manage the command line interface
@click.command()
@click.option('--file', '-f', is_flag=True,
              help="Option to indicate reading tracking sheet from a file as opposed to reading directly from Google Sheets.")
@click.option('--save_file', prompt="Please type the name of the updated tracking file NO .xlsx extension NEEDED")
def run_main(file, save_file):
    main(file=file, save_file=save_file)