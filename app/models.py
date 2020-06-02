from app import db
from app.functions import refreshToken, dbAddTracksPlaylist, dbClearPlaylist, dbGetTopTracksURI

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	# password_hash = db.Column(db.String(128))
	username = db.Column(db.String(64), index=True, unique=True)
	refresh_token = db.Column(db.String(150), index=True, unique=True)
	playlist_id_short = db.Column(db.String(30), index=True, unique=True)
	playlist_id_medium = db.Column(db.String(30), index=True, unique=True)
	playlist_id_long = db.Column(db.String(30), index=True, unique=True)

	def __repr__(self):
		return '<User {}>'.format(self.username)


def addUser(username, refresh_token, playlist_id_short=None, playlist_id_medium=None, playlist_id_long=None):
	user = User.query.filter_by(username=username).first()

	if user == None:
		user = User(username=username, refresh_token=refresh_token, playlist_id_short=playlist_id_short, playlist_id_medium=playlist_id_medium, playlist_id_long=playlist_id_long)
		db.session.add(user)
	else:
		if playlist_id_short != None:
			user.playlist_id_short = playlist_id_short
		if playlist_id_medium != None:
			user.playlist_id_medium = playlist_id_medium
		if playlist_id_long != None:
			user.playlist_id_long = playlist_id_long

	db.session.commit()


def updatePlaylists():
	print("start update")
	all_users = User.query.all()

	for user in all_users:
		is_active = False
		payload = refreshToken(user.refresh_token)

		if payload == None:
			db.session.delete(user)
			db.session.commit()
			break
		
		access_token = payload[0]

		playlist = user.playlist_id_short
		if playlist != None:
			if (dbClearPlaylist(access_token, playlist) != None):
				uri_list = dbGetTopTracksURI(access_token, 'short_term')
				dbAddTracksPlaylist(access_token, playlist, uri_list)
				is_active = True
			else:
				user.playlist_id_short = None

		playlist = user.playlist_id_medium
		if playlist != None:
			if (dbClearPlaylist(access_token, playlist) != None):
				uri_list = dbGetTopTracksURI(access_token, 'medium_term')
				dbAddTracksPlaylist(access_token, playlist, uri_list)
				is_active = True
			else:
				user.playlist_id_medium = None

		playlist = user.playlist_id_long
		if playlist != None:
			if (dbClearPlaylist(access_token, playlist) != None):
				uri_list = dbGetTopTracksURI(access_token, 'long_term')
				dbAddTracksPlaylist(access_token, playlist, uri_list)
				is_active = True
			else:
				user.playlist_id_long = None

	if not is_active:
		db.session.delete(user)

	db.session.commit()



