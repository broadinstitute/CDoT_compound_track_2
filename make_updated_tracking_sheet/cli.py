"""
Entry point to 'make_updated_tracking_sheet' command line script.
"""

from make_updated_tracking_sheet.make_updated_tracking_sheet import main
import click

# Using click to manage the command line interface
@click.command()
@click.option('--tracking_file', prompt="Please paste the path of the original"
                                        " compound tracking sheet saved as a .csv file", type=click.Path(exists=True))
@click.option('--save_file', prompt="Please type the name of the updated tracking file NO .xlsx extension NEEDED")
def main(tracking_file, save_file):
    main(tracking_file=tracking_file, save_file=save_file)