import xbmcplugin
import xbmcgui
import sys
import json
from urllib.request import urlopen

JSON_URL = "https://raw.githubusercontent.com/MoinuNisa/moinu-movies/main/1080p_x264_pack.json"

handle = int(sys.argv[1])

try:
    response = urlopen(JSON_URL)
    data = json.loads(response.read().decode("utf-8"))

    for movie in data["movies"]:
        li = xbmcgui.ListItem(label=movie["title"])

        # Poster + fanart support
        li.setArt({
            "thumb": movie.get("poster", ""),
            "poster": movie.get("poster", ""),
            "fanart": movie.get("fanart", "")
        })

        # Optional info (future ready)
        li.setInfo("video", {
            "title": movie["title"],
            "year": movie.get("year", "")
        })

        xbmcplugin.addDirectoryItem(
            handle=handle,
            url=movie["play_url"],   # 🔥 CORRECT KEY
            listitem=li,
            isFolder=False
        )

    xbmcplugin.endOfDirectory(handle)

except Exception as e:
    xbmcgui.Dialog().notification(
        "Moinu Movies",
        "Failed to load movie list",
        xbmcgui.NOTIFICATION_ERROR
    )
