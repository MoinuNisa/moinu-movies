import sys
import json
import urllib.request
import xbmcplugin
import xbmcgui

HANDLE = int(sys.argv[1])

JSON_URL = "https://raw.githubusercontent.com/MoinuNisa/moinu-movies/main/1080p_x264_pack.json"

response = urllib.request.urlopen(JSON_URL)
data = json.loads(response.read())

for movie in data["movies"]:
    li = xbmcgui.ListItem(label=movie["title"])
    li.setArt({
        "thumb": movie["poster"],
        "poster": movie["poster"],
        "fanart": movie["fanart"]
    })
    li.setInfo("video", {
        "title": movie["title"],
        "year": movie["year"],
        "genre": movie["quality"]
    })

    xbmcplugin.addDirectoryItem(
        handle=HANDLE,
        url=movie["play_url"],
        listitem=li,
        isFolder=False
    )

xbmcplugin.endOfDirectory(HANDLE)
