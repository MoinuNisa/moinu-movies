import xbmcplugin
import xbmcgui
import sys
import json
from urllib.request import urlopen

TMDB_API_KEY = "051ccf72e026820cb53b8b8531b6a2ba"
JSON_URL = "https://raw.githubusercontent.com/MoinuNisa/moinu-movies/main/1080p_x264_pack.json"

handle = int(sys.argv[1])

def get_tmdb_info(title, year):
    try:
        clean_title = title.split("(")[0].strip()
        query = clean_title.replace(" ", "%20")

        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}&year={year}"
        data = json.loads(urlopen(url).read().decode("utf-8"))

        if not data.get("results"):
            return {}

        m = data["results"][0]

        poster = m.get("poster_path")
        backdrop = m.get("backdrop_path")

        return {
            "plot": m.get("overview", ""),
            "poster": f"https://image.tmdb.org/t/p/original{poster}" if poster else "",
            "fanart": f"https://image.tmdb.org/t/p/original{backdrop}" if backdrop else ""
        }

    except:
        return {}

try:
    response = urlopen(JSON_URL)
    data = json.loads(response.read().decode("utf-8"))

    for movie in data["movies"]:
        tmdb = get_tmdb_info(movie["title"], movie.get("year", ""))

        li = xbmcgui.ListItem(label=movie["title"])

        li.setArt({
            "thumb": tmdb.get("poster") or movie.get("poster", ""),
            "poster": tmdb.get("poster") or movie.get("poster", ""),
            "fanart": tmdb.get("fanart") or movie.get("fanart", "")
        })

        li.setInfo("video", {
            "title": movie["title"],
            "year": movie.get("year", ""),
            "plot": tmdb.get("plot", "")
        })

        context = []

        if movie.get("trailer"):
            context.append((
                "🎬 Trailer",
                f"PlayMedia({movie['trailer']})"
            ))

        context.append(("ℹ Movie Info", "Action(Info)"))
        li.addContextMenuItems(context)

        xbmcplugin.addDirectoryItem(
            handle=handle,
            url=movie["play_url"],
            listitem=li,
            isFolder=False
        )

    xbmcplugin.endOfDirectory(handle)

except Exception as e:
    xbmcgui.Dialog().notification(
        "Moinu Movies",
        "JSON / TMDB Network Error",
        xbmcgui.NOTIFICATION_ERROR
    )
