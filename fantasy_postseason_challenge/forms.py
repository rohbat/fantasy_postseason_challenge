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

        # one player per team
        if len({player.team for player in players}) < len(self.data):
            return False

        # # unique players at all positions--first condition covers this as well
        # if len({player.display_name for player in players}) < len(self.data):
        #     return False

        return True
