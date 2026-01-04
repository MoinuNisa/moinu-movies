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

        # Artwork
        li.setArt({
            "thumb": movie.get("poster", ""),
            "poster": movie.get("poster", ""),
            "fanart": movie.get("fanart", "")
        })

        # Info labels
        li.setInfo("video", {
            "title": movie["title"],
            "year": movie.get("year", ""),
            "plot": movie.get("plot", "")
        })

        # Context menu
        context_items = []

        if movie.get("trailer"):
            context_items.append((
                "🎬 Trailer",
                "RunPlugin({})".format(movie["trailer"])
            ))

        context_items.append((
            "ℹ Movie Info",
            "Action(Info)"
        ))

        li.addContextMenuItems(context_items)

        xbmcplugin.addDirectoryItem(
            handle=handle,
            url=movie["play_url"],
            listitem=li,
            isFolder=False
        )

    xbmcplugin.endOfDirectory(handle)

except Exception as e:
    xbmcgui.Dialog().ok("Moinu Movies ERROR", str(e))
