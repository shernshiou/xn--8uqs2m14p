import os
from collections import Counter

from jinja2 import Environment, FileSystemLoader
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth


def main():
    manager = SpotifyOAuth(
        client_id=os.environ["CLIENT_ID"],
        client_secret=os.environ["CLIENT_SECRET"],
        redirect_uri="http://localhost:9090",
        scope="user-library-read",
        open_browser=False,
    )

    at = manager.refresh_access_token(os.environ["REFRESH_TOKEN"])
    sp = Spotify(auth=at["access_token"])
    PLAYLIST_ID = "37pobuX6d2NXODEPOPiKZB"
    playlist = sp.playlist(playlist_id=PLAYLIST_ID)
    result = sp.user_playlist_tracks(playlist_id=PLAYLIST_ID)
    tracks = result["items"]

    while result["next"]:
        result = sp.next(result)
        tracks.extend(result["items"])

    added_by = [track["added_by"]["id"] for track in tracks]
    c = Counter(added_by)

    num_by_user = []
    for user_id in c:
        user = sp.user(user=user_id)
        num_by_user.append({"username": user["display_name"], "count": c[user_id]})

    environment = Environment(loader=FileSystemLoader("templates/"))
    template = environment.get_template("index.jinja")
    content = template.render(playlist_title=playlist["name"], num_by_user=num_by_user)

    # to save the results
    with open("./static/index.html", "w") as f:
        f.write(content)


if __name__ == "__main__":
    main()
