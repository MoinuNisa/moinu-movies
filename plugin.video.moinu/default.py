import xbmcplugin
import xbmcgui
import xbmc
import sys
import json
import re
import ssl
from urllib.request import urlopen, Request

# ===============================
# SSL FIX (VERY IMPORTANT FOR ANDROID)
# ===============================
ssl._create_default_https_context = ssl._create_unverified_context

# ===============================
# CONFIG
# ===============================
TMDB_API_KEY = "051ccf72e026820cb53b8b8531b6a2ba"
JSON_URL = "https://dl.dropboxusercontent.com/scl/fi/5cn3ryzl6kuxbgceyfin7/1080p_x264_pack.json?rlkey=qlmd22d76h8cd6a4r9f8b4z3q&dl=1"
handle = int(sys.argv[1])

# ===============================
# pCloud RESOLVER
# ===============================
def resolve_pcloud(page_url):
    try:
        req = Request(page_url, headers={"User-Agent": "Mozilla/5.0"})
        html = urlopen(req, timeout=20).read().decode("utf-8")

        match = re.search(r'(https://e\.pcloud\.link[^"]+)', html)
        if match:
            return match.group(1)

    except Exception as e:
        xbmc.log("[MoinuMovies] pCloud resolve error: " + str(e), xbmc.LOGERROR)

    return None

# ===============================
# TMDB HELPER (SAFE)
# ===============================
def get_tmdb_info(title, year):
    try:
        clean_title = title.split("(")[0].strip()
        query = clean_title.replace(" ", "%20")

        search_url = (
            "https://api.themoviedb.org/3/search/movie"
            f"?api_key={TMDB_API_KEY}&query={query}&year={year}"
        )

        req = Request(search_url, headers={"User-Agent": "Mozilla/5.0"})
        search_data = json.loads(urlopen(req, timeout=15).read().decode("utf-8"))

        if not search_data.get("results"):
            return {}

        movie = search_data["results"][0]
        movie_id = movie.get("id")

        poster = ""
        fanart = ""

        if movie.get("poster_path"):
            poster = "https://image.tmdb.org/t/p/original" + movie["poster_path"]
        if movie.get("backdrop_path"):
            fanart = "https://image.tmdb.org/t/p/original" + movie["backdrop_path"]

        return {
            "plot": movie.get("overview", ""),
            "poster": poster,
            "fanart": fanart,
            "rating": movie.get("vote_average", 0),
            "cast_text": ""
        }

    except Exception as e:
        xbmc.log("[MoinuMovies] TMDB error: " + str(e), xbmc.LOGERROR)
        return {}

# ===============================
# MAIN
# ===============================
try:
    # ---- SAFE JSON LOAD ----
    req = Request(JSON_URL, headers={"User-Agent": "Mozilla/5.0"})
    response = urlopen(req, timeout=20)
    data = json.loads(response.read().decode("utf-8"))

    for movie in data.get("movies", []):
        tmdb = get_tmdb_info(movie.get("title", ""), movie.get("year", "")) or {}

        li = xbmcgui.ListItem(label=movie.get("title", "Movie"))
        li.setProperty("IsPlayable", "true")

        # Artwork
        li.setArt({
            "thumb": tmdb.get("poster") or movie.get("poster", ""),
            "poster": tmdb.get("poster") or movie.get("poster", ""),
            "fanart": tmdb.get("fanart") or movie.get("fanart", "")
        })

        # Info
        li.setInfo("video", {
            "title": movie.get("title", ""),
            "year": movie.get("year", ""),
            "plot": tmdb.get("plot", ""),
            "rating": tmdb.get("rating", 0)
        })

        # Context menu
        context_items = []
        if movie.get("trailer"):
            context_items.append(("🎬 Trailer", f"PlayMedia({movie['trailer']})"))
        context_items.append(("ℹ Movie Info", "Action(Info)"))
        li.addContextMenuItems(context_items)

        # ---- PLAY ----
        page_url = movie.get("play_url", "")
        stream_url = resolve_pcloud(page_url)

        if not stream_url:
            xbmc.log("[MoinuMovies] Stream not resolved", xbmc.LOGERROR)
            continue

        xbmcplugin.addDirectoryItem(
            handle=handle,
            url=stream_url,
            listitem=li,
            isFolder=False
        )

    xbmcplugin.endOfDirectory(handle)

except Exception as e:
    xbmc.log("[MoinuMovies] MAIN error: " + str(e), xbmc.LOGERROR)
    xbmcgui.Dialog().notification(
        "Moinu Movies",
        "Network / JSON Error",
        xbmcgui.NOTIFICATION_ERROR
        )
