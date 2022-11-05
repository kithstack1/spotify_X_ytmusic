idea = """
I want to create a library that links spotify with youtube music. would like to be able 
 1.transfer my songs from youtube music to spotify and from spotify to youtube music.
   * SAMPLE COMMAND: ytmusic -u url -cf credential.json -a transfer --origin youtube --destination spotify --targetplaylist_name new_play
 2.upload my local playlists to spotify and youtube music as well
   * SAMPLE COMMAND: ytmusic --action upload --origin directory_name --destination spotify youtube --targetplaylist_name
 3.download albums, tracks and playlists from both spotifydl and ytmusic,
   # from youtube 
   * SAMPLE DOWNLOAD COMMAND: ytmusic --action download --url resource_url --source youtube  --outputdir . 
 4.download not only mp3 files but also videos of the songs 
   # from spotify
   * SAMPLE DOWNLOAD COMMAND: ytmusic --action download --pref_fileformat video --url url --source spotify --outputdir . 
 5.add metadata to all files i download to my local storage.
 6.download any other youtube media by passing on it's url to the program ,yes ik ytdl offers this but
   SAMPLE DOWNLOAD COMMAND: ytmusic --action download --source youtube --content_type other
 7.search for a song and download it.
   SMAPLE COMMAND: ytmusic --query  search_term --action download --outputdir . --pref_fileformat video 
 want to have all this functionality in one place. 
"""
# from the above idea i will generate the program
import mutagen
import argparse
import spotify_dl as spdl
from ytmusicapi import YTMusic as ytmusic
import yt_dlp
import pathlib
import spotipy
import os

session_df = "headers.json"

# client id and client secret from env variables
client_id = os.environ["SPOTIPY_CLIENT_ID"]
client_secret = os.environ["SPOTIPY_CLIENT_SECRET"]
username = "0nbhdgrs3yftuu38ndzlibibb"


def clean_input(query: str) -> str:
    """Remove illegal characters from search query"""
    illegal_chars = [
        "!",
        "@",
        "#",
        "$",
        "%",
        "^",
        "&",
        "*",
        "(",
        ")",
        "_",
        "+",
        "=",
        "{",
        "}",
        "[",
        "]",
        "|",
        "\\",
        ":",
        ";",
        '"',
        "<",
        ">",
        "?",
        "/",
    ]
    for char in illegal_chars:
        query = query.replace(char, "")
    return query


def parse_args():
    """parse arguments from CLI"""
    parser = argparse.ArgumentParser(
        description="Download songs from youtube music and spotify"
    )
    parser.add_argument("--action", type=str, help="action to perform")
    parser.add_argument("--url", type=str, help="url of resource to download")
    parser.add_argument("--query", type=str, help="search query")
    parser.add_argument("--source", type=str, help="source of resource to download")
    parser.add_argument("--outputdir", type=str, help="output directory")
    parser.add_argument("--pref_fileformat", type=str, help="preferred file format")
    parser.add_argument("--content_type", type=str, help="content type to download")
    parser.add_argument("--origin", type=str, help="origin of playlist to transfer")
    parser.add_argument(
        "--destination", type=str, help="destination of playlist to transfer"
    )
    parser.add_argument(
        "--targetplaylist_name", type=str, help="name of playlist to transfer to"
    )
    parser.add_argument("--cf", type=str, help="credential file")
    parser.add_argument("--u", type=str, help="url of resource to transfer")
    parser.add_argument("--a", type=str, help="action to perform")
    # add args for spotify_dl
    parser.add_argument("--multi", default=1, help="download multiple songs")
    args = parser.parse_args()
    return args


def make_ytplaylist(playlist_name: str, songs_to_add=None):
    """create youtube playlist under name specified"""
    yt_object = ytmusic(session_df)
    yt_object.create_playlist(playlist_name)
    if songs_to_add:
        addto_ytplaylist(yt_object, songs_to_add, playlist_name)


def make_spotifyplaylist(playlist_name, songs_to_add):
    """Create a new playlist on spotify under name specified"""
    global client_id, client_secret, username
    # insufficent scope error
    scope = "playlist-modify-public"
    auth = spotipy.SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="http://localhost:8888/callback",
        username=username,
        scope=scope,
    )
    sp = spotipy.Spotify(auth_manager=auth)
    sp.user_playlist_create(username, playlist_name)
    add_tospotifyplaylist(sp, songs_to_add, playlist_name)
    sp = spotipy.Spotify(auth_manager=auth)
    playlists = sp.current_user_playlists()
    for playlist in playlists["items"]:
        if playlist["name"].lower() == playlist_name.lower():
            print("playlist already exists")
            add_tospotifyplaylist(sp, songs_to_add, playlist_name)
            return
    sp.user_playlist_create(sp, playlist_name)
    return add_tospotifyplaylist(sp, songs_to_add, playlist_name)


def get_vid_ids(yt_object: ytmusic, songs_to_add: list):
    """get video ids of songs in songs_to_add"""
    """yt_object.get_video_ids args: songs_to_add"""
    video_ids = []
    for song in songs_to_add:
        results = yt_object.search(song, filter="songs")
        if results:
            video_ids.append(results[0]["videoId"])
    return video_ids


def addto_ytplaylist(yt_object: ytmusic, songs_to_add: list, targetplaylist_name: str):
    """add songs to playlist on youtube music"""
    """ Create a playlist with songs in songs_to_add on youtube music account under the name targetplaylist_name"""
    """yt_object.create_playlist args: title, description, privacy_status, video_ids"""
    title = targetplaylist_name
    description = "playlist created by ytmusic"
    privacy_status = "PRIVATE"
    video_ids = get_vid_ids(yt_object, songs_to_add)
    yt_object.create_playlist(title, description, privacy_status, video_ids)


def add_tospotifyplaylist(
    sp: spotipy.Spotify, songs_to_add: list, targetplaylist_name: str
):
    """add song[s] to specified playlist on spotify"""
    """Create a playlist with the songs in songs_to_add under playlist  targetplaylist_name
     using the sp spotify.Spotify object"""
    """sp.user_playlist_create args: user, name, public, description"""

    playlists = sp.current_user_playlists()
    for playlist in playlists["items"]:
        if playlist["name"].lower() == targetplaylist_name.lower():
            playlist_id = playlist["id"]
            print("playlist already exists")
            break
    for song in songs_to_add:
        results = sp.search(q=song, limit=1)
        if results:
            try:
                track_uri = results["tracks"]["items"][0]["uri"]
                sp.playlist_add_items(playlist_id, [track_uri])
            except:
                print("error adding song to playlist")
                continue
    # return the playlist url
    return sp.playlist(playlist_id)["external_urls"]["spotify"]


def download_from_spotify(media_url, outputdir, pref_fileformat, multi):
    """get info from spotify playlists and download songs using the spotify_dl module"""
    """playlists: list of spotify playlist urls"""
    """outputdir: directory to download songs to"""
    """pref_fileformat: preferred file format to download songs in"""
    """multi: download multiple songs"""
    # create a spaced string of playlist urls
    playlist_url = media_url
    print(playlist_url)
    os.system(
        f"spotify_dl -l {playlist_url} -o {outputdir} -f {pref_fileformat} -mc {multi}"
    )


def download_from_ytmusic(yt_object, media_url, outputdir, pref_fileformat, sp_object):
    """download playlist from specified ytmusic account"""
    """we are going to twist things a bit here and download with inffo from spotify"""
    """we will determine if the url is a playlist or a song"""
    """if it is a playlist, we will get the playlist name and information about the songs in the playlist"""
    """ we will then create a spotufy playlist with the same name and add the songs to the playlist"""
    """we will then download the songs from spotify using the spotify_dl module"""
    """ finally, we will delete the playlist from spotify"""
    """if it is a song, we will get the song name and artist from youtube music and then search for the song on spotify"""
    """we will then download the song from spotify using the spotify_dl module"""

    if "playlist" in media_url:
        # get playlist_id from url
        media_url = (
            "".join(media_url.split("?")[-1])
            .split("&")[0]
            .split("=")[1]
            .replace("\\", "")
        )
        print(media_url)
        playlist_info = yt_object.get_playlist(media_url)
        playlist_name = playlist_info["title"]
        songs_to_add = []
        for song in playlist_info["tracks"]:
            songs_to_add.append(song["title"] + " " + song["artists"][0]["name"])
        playlist_url = make_spotifyplaylist(playlist_name, songs_to_add)
        # get the playlist id for the playlist we just created
        # create a spoify object with permissions to modify playlists
        scope = "playlist-modify-public"
        auth = spotipy.SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri="http://localhost:8888/callback",
            username=username,
            scope=scope,
        )
        sp = spotipy.Spotify(auth_manager=auth)
        playlists = sp.current_user_playlists()
        for playlist in playlists["items"]:
            if playlist["name"].lower() == playlist_name.lower():
                playlist_id = playlist["id"]
                break
        # get uri for playlist
        playlist_uri = sp_object.playlist(playlist_id)["uri"]
        # create share url from uri
        playlist_url = (
            "https://open.spotify.com/playlist/" + playlist_uri.split(":")[-1]
        )
        download_from_spotify(playlist_url, outputdir, pref_fileformat, multi=1)
    else:
        song_info = yt_object.get_song(media_url)
        song_name = song_info["title"]
        artist_name = song_info["artists"][0]["name"]
        results = sp_object.search(q=song_name + " " + artist_name, limit=1)
        if results:
            track_uri = results["tracks"]["items"][0]["uri"]
            sp_object.start_playback(uris=[track_uri])
            spdl.main(
                [
                    "--url",
                    track_uri,
                    "--output",
                    outputdir,
                    "--format",
                    pref_fileformat,
                ]
            )


def make_upload_list(origin):

    origin_dir = pathlib.Path(origin)
    if origin_dir.is_dir():
        files = origin_dir.glob("*")
        audio_files = [
            file for file in files if file.suffix in [".mp3", ".wav", ".flac", ".ogg"]
        ]
        metadata = [mutagen.File(file) for file in audio_files]
        titles = [meta["TIT2"] for meta in metadata]
        artists = [meta["TPE1"] for meta in metadata]
        upload_list = [
            f"{str(title)}-{str(artist)}" for title, artist in zip(titles, artists)
        ]
        return upload_list


def transfer(origin, destination, targetplaylist_name, orgin_playlist_name):
    """transfer playlist from origin to destination"""
    """origin and destination are either spotify or ytmusic"""
    """targetplaylist_name is the name of the playlist to transfer to"""
    """origin_playlist_name is the name of the playlist to transfer from"""
    auth = spotipy.SpotifyOAuth(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(auth_manager=auth)
    if origin == "spotify":
        # destination is obviously ytmusic
        # get playlist from spotify
        # make playlist on ytmusic

        playlists = sp.current_user_playlists()
        for playlist in playlists["items"]:
            if playlist["name"].lower() == origin_playlist_name.lower():
                playlist_id = playlist["id"]
                break
        playlist = sp.playlist(playlist_id)
        songs_to_add = [song["track"]["name"] for song in playlist["tracks"]["items"]]
        make_ytplaylist(targetplaylist_name, songs_to_add)
    elif origin == "ytmusic":
        # destination is obviously spotify
        # get playlist from ytmusic
        # make playlist on spotify
        yt_object = ytmusic(session_df)
        playlist = yt_object.get_playlist(origin_playlist_name)
        songs_to_add = [song["title"] for song in playlist["tracks"]]
        make_spotifyplaylist(targetplaylist_name, songs_to_add)


def main():

    args = parse_args()
    # getting client id and secret from environment variables
    client_id = os.environ["SPOTIPY_CLIENT_ID"]
    client_secret = os.environ["SPOTIPY_CLIENT_SECRET"]
    sp = spotipy.Spotify(
        auth_manager=spotipy.SpotifyClientCredentials(
            client_id=client_id, client_secret=client_secret
        )
    )

    if args.action == "download":
        if args.source == "youtube":
            url = args.url
            yt_object = ytmusic(session_df)
            if url:
                print("downloading from youtube")
                download_from_ytmusic(
                    yt_object, url, args.outputdir, "audio/bestaudio", sp
                )
            elif args.query:

                args.query = clean_input(args.query)
                results = yt_object.search(args.query, filter="songs")
                if results:
                    url = f"https://music.youtube.com/watch?v={results[0]['videoId']}"
                    download_from_ytmusic(
                        yt_object, url, args.output, "audio/bestaudio", sp
                    )
                else:
                    print("no results found")
        elif args.source == "spotify":
            playlist_url = args.url
            outputdir = args.outputdir
            pref_fileformat = "audio/bestaudio"
            multi = 1
            if args.url:
                download_from_spotify(playlist_url, outputdir, pref_fileformat, multi)
            elif args.query:
                args.query = clean_input(args.query)
                results = sp.search(args.query, limit=1)
                if results:
                    track_uri = results["tracks"]["items"][0]["uri"]
                    # create share url from uri
                    playlist_url = (
                        "https://open.spotify.com/playlist/" + track_uri.split(":")[-1]
                    )
                    download_from_spotify(playlist_url, outputdir, pref_fileformat, multi)

    elif args.action == "upload":
        args.upload_list = make_upload_list(args.origin)
        if args.destination == "spotify":
            targetplaylist_name = args.targetplaylist_name
            sp = spotipy.Spotify(
                auth_manager=spotipy.SpotifyOAuth(
                    client_id=client_id, client_secret=client_secret
                )
            )
            songs_to_add = args.upload_list
            add_tospotifyplaylist(sp, songs_to_add, targetplaylist_name)
        elif args.destination == "youtube":
            targetplaylist_name = args.targetplaylist_name
            yt_object = ytmusic(session_df)
            songs_to_add = args.upload_list
            addto_ytplaylist(yt_object, songs_to_add, targetplaylist_name)

    elif args.action == "transfer":
        origin = args.origin
        destination = args.destination
        targetplaylist_name = args.targetplaylist_name
        origin_playlist_name = args.origin_playlist_name
        transfer(origin, destination, targetplaylist_name, origin_playlist_name)



if __name__ == "__main__":
    main()

# final program flow
# 1. download from youtube
# 2. download from spotify
# 3. upload to spotify
# 4. upload to youtube
# 5. transfer from spotify to youtube
# 6. transfer from youtube to spotify
# 7. download from youtube and not ytmusic
