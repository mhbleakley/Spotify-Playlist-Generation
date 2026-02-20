import time
import os
from datetime import datetime, timedelta, timezone

# Define a UTC timezone object manually for Python < 3.11
UTC = timezone.utc

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

SCOPE = "user-library-read playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative"

def init_spotify_client():
    return Spotify(auth_manager=SpotifyOAuth(
        scope=SCOPE,
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        redirect_uri=os.getenv("REDIRECT_URI"),
        cache_path=".cache_rotation"
    ))

def fetch_liked_tracks_range(sp, start_dt, end_dt):
    results = []
    offset = 0

    while True:
        items = sp.current_user_saved_tracks(limit=50, offset=offset)["items"]
        if not items:
            break

        for item in items:
            added_at = datetime.strptime(item["added_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)

            if added_at < start_dt:
                return results

            if start_dt <= added_at < end_dt:
                results.append(item["track"]["id"])

        offset += len(items)

    return results


def get_all_user_playlists(sp) -> list[dict]:
    playlists = []
    offset = 0

    while True:
        response = sp.current_user_playlists(limit=50, offset=offset)
        items = response.get('items', [])
        if not items:
            break
        playlists.extend(items)
        offset += len(items)

    return playlists


def find_or_create_playlist(sp, user_id, name):
    offset = 0
    while True:
        resp = sp.current_user_playlists(limit=50, offset=offset)
        for pl in resp.get("items", []):
            if pl["name"] == name and pl["owner"]["id"] == user_id:
                return pl["id"]
        if resp["next"] is None:
            break
        offset += 50

    new_pl = sp.user_playlist_create(user=user_id, name=name, public=False)
    return new_pl["id"]

def get_playlist_track_ids(sp, playlist_id):
    ids = []
    offset = 0
    while True:
        resp = sp.playlist_items(playlist_id, fields="items.track.id,next", limit=100, offset=offset)
        items = resp.get("items", [])
        if not items:
            break
        ids.extend(track["track"]["id"] for track in items if track["track"])
        offset += len(items)
    return ids

def update_playlist_if_needed(sp, playlist_id, new_track_ids):
    existing_ids = get_playlist_track_ids(sp, playlist_id)

    if set(existing_ids) == set(new_track_ids):
        print("Playlist is already up to date.")
        return

    # Clear and re-add (Spotify API does not support replace in one call)
    sp.playlist_replace_items(playlist_id, new_track_ids[:100])
    for i in range(100, len(new_track_ids), 100):
        sp.playlist_add_items(playlist_id, new_track_ids[i:i+100])

    print(f"Updated playlist with {len(new_track_ids)} tracks.")

def main():
    sp = init_spotify_client()
    user_id = sp.current_user()["id"]

    now = datetime.now(UTC)
    year_windows = []
    for i in range(3):
        end = now - timedelta(days=365 * i)
        start = now - timedelta(days=365 * (i + 1))
        year_windows.append((start, end))


    for idx, (start, end) in enumerate(year_windows, 1):
        name = f"Rotation: Year -{idx}"

        print(f"\nProcessing {name} ({start.date()} → {end.date()})")

        track_ids = fetch_liked_tracks_range(sp, start, end)
        print(f"Found {len(track_ids)} tracks.")

        playlists = get_all_user_playlists(sp)

        target = None
        for p in playlists:
            if p["name"] == name:
                target = p["id"]
                break

        if target is None:
            target = find_or_create_playlist(sp, user_id, name)

        update_playlist_if_needed(sp, target, track_ids)



if __name__ == "__main__":
    main()
