# Spotify Discover 2.0 
**Luca Ostertag-Hill**

Check out the final product [here](https://discoverdaily.wl.r.appspot.com/).

This Flask based web application uses the Spotify API to provide users with more content and accessibility to the music they like. The application is deployed on the Google Cloud Platform.

Features of the application include:
1. TopTracks: Users can create a playlist with their most listened to music over the last month, 6 months, or all-time, and can choose to have the playlist updated daily to keep it current. Cloud SQL for MySQL is used as the database to store user information necessary for updating playlists.
2. Create: Users can create a playlist by entering up to five artist or track names and setting various tune-able attributes.
3. Interval Timer: Users can enter their desired interval time and length and the application will play songs from the specified playlist for the specified period of time before skipping to the next track.

Commands for setting up this application in a virtual environment:
1. Clone the repository. Setup a virtual environment and activate it.
    1. To create a virtual env: `virtualenv venv`
    2. To activate virtual env: `. venv/bin/activate`
    3. Download the required packages: `pip install --user --requirement requirements.txt`
2. To start the web application: `flask run`

Commands for deploying to Google Cloud Platform:
1. To deploy a new instance of the application
    1. Deploy with `gcloud app deploy`
    2. Delete the old instance using the Google Cloud console viewer
2. To check out the new version of the application
    1. Browse with `gcloud app browse`
