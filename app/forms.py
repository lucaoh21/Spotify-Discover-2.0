from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, TextField
from wtforms.validators import DataRequired

class PlaylistForm(FlaskForm):
	short_term = BooleanField('Last Month')
	medium_term = BooleanField('6 Months')
	long_term = BooleanField('All-Time')
	sync = BooleanField('Automatic Updates')
	playlist_name = StringField('Playlist name', validators=[DataRequired()])
	submit = SubmitField('Create Playlist')


# class SearchForm(FlaskForm):
# 	autocomp = TextField('autocomp', id='autocomplete')