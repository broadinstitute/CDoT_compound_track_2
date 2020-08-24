from make_updated_tracking_sheet.cli import run_main


if __name__ == '__main__':

    # Load environmental variables
    from dotenv import load_dotenv
    load_dotenv()
    run_main()