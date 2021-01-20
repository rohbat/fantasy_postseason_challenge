from wtforms import Form
from wtforms.fields import SelectField
from bson.objectid import ObjectId

from .fantasy_team import Player

class SelectTeamForm(Form):
    QB = SelectField("QB")
    RB1 = SelectField("RB1")
    RB2 = SelectField("RB2")
    WR1 = SelectField("WR1")
    WR2 = SelectField("WR2")
    TE = SelectField("TE")
    FLEX = SelectField("FLEX")
    K = SelectField("K")
    D_ST = SelectField("D/ST")

    # TODO: (very low prio) write a better custom validator a la
    # https://wtforms.readthedocs.io/en/2.3.x/validators/#custom-validators
    def validate_week_1(self):
        players = Player.objects(id__in=[ObjectId(player) for player in self.data.values()])
        # one player per team--innately ensures all unique players
        return len({player.team for player in players}) == 9

    def validate_week_2(self):
        players = Player.objects(id__in=[ObjectId(player) for player in self.data.values()])
        # 8 teams total--one player per team for 7 teams, two players from last team
        # also much have 9 unique players
        return len(players) == 9 and len({player.team for player in players}) == 8

    def validate_week_3(self):
        players = Player.objects(id__in=[ObjectId(player) for player in self.data.values()])
        teams = [player.team for player in players]
        
        teams_dict = {}
        for team in teams:
            teams_dict[team] = teams_dict.get(team, 0) + 1
        
        return len(players) == 9 and len(teams_dict) == 4 and all(count >= 2 for count in teams_dict.values())
    