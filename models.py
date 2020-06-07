"""
DiscoverDaily Web Application: Database File
Author: Luca Ostertag-Hill

A database is required to store active users of the TopTracks program, which
automatically updates a user's TopTracks playlist to keep it current. The table
structure is specified here. This file contains a function to add new users to
the database and one to update the database and user playlists.
"""

from main import Base, Session
from functions import refreshToken, dbAddTracksPlaylist, dbClearPlaylist, dbGetTopTracksURI
import logging

from sqlalchemy import Column, Integer, String


"""
Structue of the User table in the database. Stores the username of the user, as well
as their refresh token which is needed for authorization. The playlist IDs of the TopTracks
playlists are also stored.
"""
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


"""
Function called when a user signs up for a new TopTracks playlist. If the user is new,
then a new row is created with the appropriate column information. If the user already exists
in the table, then only the playlist IDs are updated (happens when a user signs up for one 
type of TopTracks playlist and then later signs up for another).
"""
def addUser(username, refresh_token, playlist_id_short=None, playlist_id_medium=None, playlist_id_long=None):
	session = Session()
	id_exists = session.query(User.id).filter_by(username=username).scalar()

	# new user
	if id_exists == None:
		user = User(username=username, refresh_token=refresh_token, playlist_id_short=playlist_id_short, playlist_id_medium=playlist_id_medium, playlist_id_long=playlist_id_long)
		session.add(user)
		logging.info('New auto user: ' + username)

	#user already exists
	else:
		user = session.query(User).get(id_exists)
		logging.info('Auto user updated: ' + user.username)

		# only update playlist IDs that are new
		if playlist_id_short != None:
			user.playlist_id_short = playlist_id_short
		if playlist_id_medium != None:
			user.playlist_id_medium = playlist_id_medium
		if playlist_id_long != None:
			user.playlist_id_long = playlist_id_long

	session.commit()
	session.close()


"""
This function is called by the Scheduler from the main file once every 24 hours.
The function iterates through all rows of the table (each user) and attempts to update
the TopTracks playlists specified by the playlist IDs. The refresh token is used to 
authorize the application to make requests to the Spotify API. Then, for each playlist
the playlist is cleared, the TopTracks are gathered, and the playlist is refilled. If
the playlist no longer exists (because the user deleted it), then remove the ID from the
table. If a user has no TopTracks playlists remaining, then remove the user from the table.
"""
def updatePlaylists():
	session = Session()

	# attempt to update each user's playlists
	for user in session.query(User):
		is_active = False

		# authorize the application with Spotify API
		payload = refreshToken(user.refresh_token)

		# if user account has been removed or authorization revoked, user is deleted
		if payload == None:
			session.delete(user)
		else:		
			access_token = payload[0]

			playlist = user.playlist_id_short
			if playlist != None:

				# if the playlist has not been deleted
				if (dbClearPlaylist(access_token, playlist) != None):
					uri_list = dbGetTopTracksURI(access_token, 'short_term', 50)
					dbAddTracksPlaylist(access_token, playlist, uri_list)
					is_active = True
				else:
					user.playlist_id_short = None

			playlist = user.playlist_id_medium
			if playlist != None:
				if (dbClearPlaylist(access_token, playlist) != None):
					uri_list = dbGetTopTracksURI(access_token, 'medium_term', 50)
					dbAddTracksPlaylist(access_token, playlist, uri_list)
					is_active = True
				else:
					user.playlist_id_medium = None

			playlist = user.playlist_id_long
			if playlist != None:
				if (dbClearPlaylist(access_token, playlist) != None):
					uri_list = dbGetTopTracksURI(access_token, 'long_term', 50)
					dbAddTracksPlaylist(access_token, playlist, uri_list)
					is_active = True
				else:
					user.playlist_id_long = None

			# if no playlists could be updated, then remove user
			if not is_active:
				session.delete(user)

	session.commit()
	session.close()

	logging.info('Updated TopTracks Playlists')

