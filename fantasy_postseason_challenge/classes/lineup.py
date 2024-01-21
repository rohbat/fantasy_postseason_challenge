from ..db import db
from ..config import get_db_alias
from .player import Player

class Lineup(db.Document):
    QB = db.ReferenceField(Player)
    RB1 = db.ReferenceField(Player)
    RB2 = db.ReferenceField(Player)
    WR1 = db.ReferenceField(Player)
    WR2 = db.ReferenceField(Player)
    TE = db.ReferenceField(Player)
    FLEX = db.ReferenceField(Player)
    K = db.ReferenceField(Player)
    D_ST = db.ReferenceField(Player)

    meta = {
        'db_alias': get_db_alias(),  # Database alias
        'collection': 'Lineups'  # Collection name
    }

    def get_score_by_round(self, round_name, league_ruleset):
        # Initialize total score to 0
        total_score = 0.0

        # List of all player positions in the lineup
        player_positions = ['QB', 'RB1', 'RB2', 'WR1', 'WR2', 'TE', 'FLEX', 'K', 'D_ST']

        # Iterate through each player position in the lineup
        for position in player_positions:
            player = getattr(self, position)

            # Check if player exists and has scores for the given round
            if player and round_name in player.playoff_scores:
                # Get the player's score based on the league ruleset
                player_score = getattr(player.playoff_scores[round_name], league_ruleset)

                # Add player's score to the total score
                if player_score:
                    total_score += float(player_score)

        return total_score
