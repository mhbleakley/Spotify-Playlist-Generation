# Spotify Playlist Generation

I can't be bothered to make my own playlists so I've made this to auto-rotate my liked songs from the last n units of time into n playlists and just use those. If you want it to run automatically you could use a cron job or just run it whenever you feel like it.

## Running the playlist generator/manager:

To make this work you will need a python 3.9 environment with the requirements installed, a spotify developer account, and a .env file in this directory with `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, and `SPOTIPY_REDIRECT_URI` which you can set to any valid link. when you run it the first time, it will open that page in your browser and you'll need to get the url one time for the token. After that, it should handle caching it properly and won't need another if it is running on a somewhat regular interval.


```
$ python rotating-playlist-manager.py 
Enter the URL you were redirected to: <url>

Processing Rotation: Year -1 (2024-12-04 → 2025-12-04)
Found 363 tracks.
Playlist is already up to date.

Processing Rotation: Year -2 (2023-12-05 → 2024-12-04)
Found 461 tracks.
Playlist is already up to date.

Processing Rotation: Year -3 (2022-12-05 → 2023-12-05)
Found 412 tracks.
Playlist is already up to date.
```