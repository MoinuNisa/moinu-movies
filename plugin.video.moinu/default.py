import xbmcplugin, xbmcgui, sys, json
import urllib.request

URL = "https://raw.githubusercontent.com/MoinuNisa/moinu-movies/main/1080p_x264_pack.json"

handle = int(sys.argv[1])

try:
    response = urllib.request.urlopen(URL)
    data = json.loads(response.read().decode())

    for movie in data["movies"]:
        li = xbmcgui.ListItem(label=movie["title"])
        li.setArt({
            "poster": movie.get("poster", ""),
            "thumb": movie.get("poster", "")
        })
        xbmcplugin.addDirectoryItem(
            handle=handle,
            url=movie["url"],
            listitem=li,
            isFolder=False
        )

    xbmcplugin.endOfDirectory(handle)

except Exception as e:
    xbmcgui.Dialog().notification(
        "Moinu Movies",
        "Failed to load movie list",
        xbmcgui.NOTIFICATION_ERROR,
        5000
    )
