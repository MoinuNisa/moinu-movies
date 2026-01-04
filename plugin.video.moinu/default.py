import xbmcplugin
import xbmcgui
import sys
import json
from urllib.request import urlopen

# ===============================
# CONFIG
# ===============================
TMDB_API_KEY = "051ccf72e026820cb53b8b8531b6a2ba"
JSON_URL = "https://raw.githubusercontent.com/MoinuNisa/moinu-movies/main/1080p_x264_pack.json"

handle = int(sys.argv[1])

# ===============================
# TMDB HELPER
# ===============================
def get_tmdb_info(title, year):
    try:
        # Clean title (remove year from name if present)
        clean_title = title.split("(")[0].strip()
        query = clean_title.replace(" ", "%20")

        # Search movie
        search_url = (
            f"https://api.themoviedb.org/3/search/movie"
            f"?api_key={TMDB_API_KEY}&query={query}&year={year}"
        )
        search_data = json.loads(urlopen(search_url).read().decode("utf-8"))

        if not search_data.get("results"):
            return {}

        movie = search_data["results"][0]
        movie_id = movie.get("id")

        # Basic info
        plot = movie.get("overview", "")
        poster_path = movie.get("poster_path")
        fanart_path = movie.get("backdrop_path")
        rating = movie.get("vote_average", 0)

        poster = f"https://image.tmdb.org/t/p/original{poster_path}" if poster_path else ""
        fanart = f"https://image.tmdb.org/t/p/original{fanart_path}" if fanart_path else ""

        # Credits (CAST)
        cast_list = []
        if movie_id:
            credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={TMDB_API_KEY}"
            credits_data = json.loads(urlopen(credits_url).read().decode("utf-8"))

            for c in credits_data.get("cast", [])[:8]:  # top 8 cast
                cast_list.append({
                    "name": c.get("name"),
                    "role": c.get("character")
                })

        return {
            "plot": plot,
            "poster": poster,
            "fanart": fanart,
            "rating": rating,
            "cast": cast_list
        }

    except Exception:
        return {}

# ===============================
# MAIN
# ===============================
try:
    response = urlopen(JSON_URL)
    data = json.loads(response.read().decode("utf-8"))

    for movie in data.get("movies", []):
        tmdb = get_tmdb_info(movie.get("title", ""), movie.get("year", ""))

        li = xbmcgui.ListItem(label=movie.get("title", "Movie"))

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

        # Cast
        if tmdb.get("cast"):
            li.setCast(tmdb["cast"])

        # Context menu
        context_items = []
        if movie.get("trailer"):
            context_items.append((
                "🎬 Trailer",
                f"PlayMedia({movie['trailer']})"
            ))
        context_items.append(("ℹ Movie Info", "Action(Info)"))
        li.addContextMenuItems(context_items)

        # Add to Kodi
        xbmcplugin.addDirectoryItem(
            handle=handle,
            url=movie.get("play_url", ""),
            listitem=li,
            isFolder=False
        )

    xbmcplugin.endOfDirectory(handle)

except Exception:
    xbmcgui.Dialog().notification(
        "Moinu Movies",
        "JSON / TMDB Network Error",
        xbmcgui.NOTIFICATION_ERROR
    )
