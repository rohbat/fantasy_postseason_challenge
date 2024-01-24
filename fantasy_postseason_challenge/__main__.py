import argparse

from .api import upload_all_rosters, grab_scores_for_games
from .app import create_app
from .config import GAMES, CURRENT_ROUND

if __name__ == "__main__":
    # Define and parse command line arguments
    parser = argparse.ArgumentParser(description="Run the Fantasy Postseason Challenge script")
    parser.add_argument('--mode', type=str, default='app', help="Mode to run the script in ('upload' or 'scores')")
    args = parser.parse_args()

    # Check the mode and execute accordingly
    if args.mode == 'upload':
        print("Running script: upload players to DB")

        upload_all_rosters()
        
        print("Rosters uploaded to MongoDB")
    elif args.mode == 'scores':
        game_ids = GAMES[CURRENT_ROUND]['game_ids']

        print("Running script: upload scores for current playoff round to DB")

        grab_scores_for_games(game_ids)
        
        print("Scores uploaded")
    else:
        app = create_app()
        app.run()
        pass
