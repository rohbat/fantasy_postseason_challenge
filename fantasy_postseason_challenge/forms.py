from flask_wtf import FlaskForm
from wtforms import Form, StringField, PasswordField, SelectField
from bson.objectid import ObjectId
from wtforms.validators import DataRequired, Length, EqualTo

from .classes.player import Player

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        EqualTo('confirm', message='Passwords must match.')
    ])
    confirm = PasswordField('Repeat Password')
    display_name = StringField('Display Name', validators=[DataRequired(), Length(min=2, max=50)])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

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

    def validate_wildcard_team(self):
        players = Player.objects(id__in=[ObjectId(player) for player in self.data.values()])
        # one player per team--innately ensures all unique players
        return len({player.team for player in players}) == 9

    def validate_divisional_team(self):
        players = Player.objects(id__in=[ObjectId(player) for player in self.data.values()])
        print(players)
        # 8 teams total--one player per team for 7 teams, two players from last team
        # also much have 9 unique players
        return len(players) == 9 and len({player.team for player in players}) == 8

    def validate_championship_team(self):
        players = Player.objects(id__in=[ObjectId(player) for player in self.data.values()])
        teams = [player.team for player in players]
        
        teams_dict = {}
        for team in teams:
            teams_dict[team] = teams_dict.get(team, 0) + 1
        
        return len(players) == 9 and len(teams_dict) == 4 and all(count >= 2 for count in teams_dict.values())
    