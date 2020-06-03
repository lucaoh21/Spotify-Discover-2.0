from main import Base, Session
from functions import refreshToken, dbAddTracksPlaylist, dbClearPlaylist, dbGetTopTracksURI
import logging

from sqlalchemy import Column, Integer, String

class User(Base):
	__tablename__ = 'users'
	id = Column(Integer, primary_key=True)
	username = Column(String(64), index=True, unique=True)
	refresh_token = Column(String(150), index=True, unique=True)
	playlist_id_short = Column(String(30), index=True, unique=True)
	playlist_id_medium = Column(String(30), index=True, unique=True)
	playlist_id_long = Column(String(30), index=True, unique=True)

	def __repr__(self):
		return '<User {}>'.format(self.username)


def addUser(username, refresh_token, playlist_id_short=None, playlist_id_medium=None, playlist_id_long=None):
	session = Session()
	user = session.query(User).filter_by(username=username).first()

	if user == None:
		user = User(username=username, refresh_token=refresh_token, playlist_id_short=playlist_id_short, playlist_id_medium=playlist_id_medium, playlist_id_long=playlist_id_long)
		session.add(user)
		logging.info('New auto user: ' + username)
	else:
		if playlist_id_short != None:
			user.playlist_id_short = playlist_id_short
		if playlist_id_medium != None:
			user.playlist_id_medium = playlist_id_medium
		if playlist_id_long != None:
			user.playlist_id_long = playlist_id_long

	session.commit()
	session.close()


def updatePlaylists():
	session = Session()
	all_users = session.query(User).all()
	logging.info('Updating TopTracks Playlists:' + str(len(all_users)))

	for user in all_users:
		is_active = False
		payload = refreshToken(user.refresh_token)

		if payload == None:
			session.delete(user)

		else:		
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
				session.delete(user)

	session.commit()
	session.close()



