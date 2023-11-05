#!/usr/bin/python3
import re
import os
import sys
import pydub
import eyed3
import shutil
import requests
import subprocess
from colorama import Fore, Style
from youtubesearchpython import VideosSearch


def connection() -> bool:
    print(color("[+] : Checking for Internet Connection...", Fore.BLUE))
    try:
        response = requests.get("https://google.com")
        response.raise_for_status()
        print(color(" |----Connection Present", Fore.GREEN))
        return True
    except requests.exceptions.RequestException as e:
        print(color(f' *----Connection Error\n *----{e}', Fore.LIGHTRED_EX))
        return False


def color(text: str, fore) -> str:
    colored_text = f"{fore}{text}{Style.RESET_ALL}"
    return colored_text


def authorizationHeader() -> dict:
    try:
        access_token_header = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        access_token_data = {
            "grant_type": "client_credentials",
            "client_id": "Enter your client id",
            "client_secret": "Enter your client secret"
        }

        access_token = (requests.post("https://accounts.spotify.com/api/token",
                                      headers=access_token_header,
                                      data=access_token_data)
                        ).json()['access_token']

        authorization_header = {"Authorization": f"Bearer {access_token}"}

        return authorization_header
    except Exception as e:
        print(color(f' *----Error Retrieving Authorization Header\n *----{e}', Fore.LIGHTRED_EX))
        sys.exit()


def playlistSongsURLs() -> list:
    try:
        global url
        global authorization_header
        playlist_ID = (re.findall(r'.*playlist/(.*)\?.*', url))[0]
        playlist_json = requests.get(f'https://api.spotify.com/v1/playlists/{playlist_ID}', headers=authorization_header)
        playlist_json.raise_for_status()

        number_of_tracks = playlist_json.json()['tracks']['total']
        tracks_list = []

        for x in range(0, number_of_tracks):
            track_uri = playlist_json.json()['tracks']['items'][x]['track']['uri']
            track_ID = (re.findall(r'spotify:track:(.*)', track_uri))[0]
            track_URL = f'https://open.spotify.com/track/{track_ID}?si'
            tracks_list.append(track_URL)
        return tracks_list
    except requests.exceptions.RequestException as e:
        print(color(f' *----Error Extracting Playlist Tracks URL List\n *----{e}', Fore.LIGHTRED_EX))
        sys.exit()


def albumSongsURLs() -> list:
    try:
        global url
        global authorization_header
        album_ID = (re.findall(r'.*album/(.*)\?.*', url))[0]
        album_json = requests.get(f'https://api.spotify.com/v1/albums/{album_ID}', headers=authorization_header)
        album_json.raise_for_status()

        number_of_tracks = album_json.json()['tracks']['total']
        tracks_list = []
        for x in range(0, number_of_tracks):
            track_uri = album_json.json()['tracks']['items'][x]['uri']
            track_ID = (re.findall(r'spotify:track:(.*)', track_uri))[0]
            track_URL = f'https://open.spotify.com/track/{track_ID}?si'
            tracks_list.append(track_URL)
        return tracks_list
    except requests.exceptions.RequestException as e:
        print(color(f' *----Error Extracting Album Tracks URL List\n *----{e}', Fore.LIGHTRED_EX))
        sys.exit()


def downloadSong(url: str, download_error: list) -> None:
    global authorization_header
    track_ID = (re.findall(r'.*track/(.*)\?.*', url))[0]
    try:
        track_json = requests.get(f"https://api.spotify.com/v1/tracks/{track_ID}", headers=authorization_header)
        metadata = (track_json.json())
        track_metadata = {
            "track_name": metadata['name'],
            "album_name": metadata['album']['name'],
            "album_art_url": metadata['album']['images'][0]['url'],
            "album_artist": metadata['album']['artists'][0]['name'],
            "artist_name": [x['name'] for x in metadata['artists']]
        }
    except Exception as e:
        print(color(f' *----Error Retrieving Track Metadata\n *----{e}', Fore.LIGHTRED_EX))
        return

    song_name = (f'{track_metadata["artist_name"][0]} - {track_metadata["track_name"]}.mp3').replace("/", "_")
    music_folder = '/home/frank/Music/'
    working_directory = '/home/frank/'

    if song_name in os.listdir(music_folder):
        print(color(f"   *----Song already present in {music_folder}", Fore.YELLOW))
        return
    else:
        album_artist = track_metadata["album_artist"].lower()
        track_name = track_metadata["track_name"].lower()
        if ('remix' in album_artist) or ('remix' in track_name):
            search_phrase = f'{track_name} by {",".join(track_metadata["artist_name"])} official audio remix'
        else:
            search_phrase = f'{track_name} by {album_artist} official audio'

        try:
            search_results = ((VideosSearch(search_phrase, limit=5)).result())
            search_results = search_results['result']
        except Exception as e:
            print(color(f' *----Error Searching for Song Results\n *----{e}', Fore.LIGHTRED_EX))
            download_error.append(f'{search_phrase} : Error Searching For Song')
            return

        video_link = None
        for x in range(len(search_results)):
            title = search_results[x]['title'].lower()
            if track_name and 'audio' in title:
                print(title)
                video_link = search_results[x]['link']
                break
            if (track_name and album_artist and ('audio' or 'visualizer') in title):
                print(title)
                video_link = search_results[x]['link']
                break
            elif (track_name and album_artist and 'lyrics' in title):
                print(title)
                video_link = search_results[x]['link']
                break
            elif (track_name and album_artist in title):
                if 'video' in title:
                    continue
                print(title)
                video_link = search_results[x]['link']
                break
            elif (track_name in title):
                if 'video' in title:
                    continue
                print(title)
                video_link = search_results[x]['link']

        if video_link is None:
            title = search_results[x]['title'].lower()
            for x in range(len(search_results)):
                if 'video' in title:
                    print(title)
                    video_link = search_results[x]['link']

        if video_link is None:
            download_error.append(f'{search_phrase} : Track not Found')
            return

        try:
            subprocess.run(['youtube-dl', '-x', '--audio-quality', '0', video_link])
            subprocess.run(['youtube-dl', '--rm-cache-dir'])
        except Exception as e:
            print(color(f' *----Error Downloading Song\n *----{e}', Fore.LIGHTRED_EX))
            download_error.append(f'{search_phrase} : Error Downloading Track')
            return

        file_types = ['aac', 'flac', 'm4a', 'opus', 'vorbis', 'wav']
        for file in os.listdir(working_directory):
            for x in file_types:
                try:
                    if file.endswith(x):
                        old_audio = pydub.AudioSegment.from_file(file)
                        old_audio.export(file.replace(x, ".mp3"), format="mp3")
                except Exception as e:
                    print(color(f' *----Error converting File\n *----{e}', Fore.LIGHTRED_EX,))
                    download_error.append(f'{search_phrase} : Error During Conversion to mp3')
                    os.remove(file)
                    return

        for file in os.listdir(working_directory):
            for x in file_types:
                if file.endswith(x):
                    os.remove(file)
            if file.endswith("mp3"):
                try:
                    os.rename(file, song_name)
                    full_path = os.path.join(working_directory, song_name)
                except Exception as e:
                    print(color(f' *----Error Changing File name\n *----{e}', Fore.LIGHTRED_EX))
                    download_error.append(f'{search_phrase} : Error Changing File name')
                    os.remove(file)
                    return

        try:
            audiofile = eyed3.load(full_path)
            print(audiofile)
        except Exception as e:
            print(color(f' *----Error Loading Audiofile\n *----{e}', Fore.LIGHTRED_EX))
            download_error.append(f'{search_phrase} : Error loading audio File')
            return

        if audiofile is not None:
            try:
                audiofile.tag.artist = ",".join(track_metadata["artist_name"])
                audiofile.tag.title = track_metadata['track_name']
                audiofile.tag.album = track_metadata['album_name']

                response = requests.get(track_metadata['album_art_url'])
                album_art_data = response.content
                audiofile.tag.images.set(3, album_art_data, 'image/jpeg')
                audiofile.tag.save()
            except Exception as e:
                print(color(f' *----Error Editing Metadata\n *----{e}', Fore.LIGHTRED_EX))
                download_error.append(f'{search_phrase} : Error Editing Metadata')
                os.remove(full_path)
                return

        shutil.move(full_path, '/home/frank/Music/')

        print(color(" |------Download Finished--------------------------------------------\n", Fore.GREEN))


def main():
    if connection():
        global url
        download_error = []
        if 'track' in url:
            print(color(f"[+] : Searching for song...", Fore.BLUE))
            downloadSong(url, download_error)
        if 'playlist' in url:
            print(color(f"[+] : Downloading Playlist...", Fore.BLUE))
            playlist_songs = playlistSongsURLs()
            song = 1
            for url in playlist_songs:
                print(color(f"|----Searching for song {song} of {len(playlist_songs)}...", Fore.CYAN))
                downloadSong(url, download_error)
                song = song + 1
            print(color(" |----Finished Downloading Playlist\n", Fore.GREEN))
        if 'album' in url:
            print(color(f"[+] : Downloading Album...", Fore.BLUE))
            album_songs = albumSongsURLs()
            song = 1
            for url in album_songs:
                print(color(f" |----Searching for song {song} of {len(album_songs)}...", Fore.CYAN))
                downloadSong(url, download_error)
                song = song + 1
            print(color(" |----Finished Downloading Album\n", Fore.GREEN))

        if len(download_error) > 0:
            print(color("[+] : The Following Tracks were not found...", Fore.YELLOW))
            song = 1
            for x in download_error:
                print(f'{song} : {x}')
                song = song + 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(color("[*] Error -- Usage : music <spotify url>", Fore.LIGHTRED_EX))
    else:
        url = sys.argv[1]
        authorization_header = authorizationHeader()
        main()

# -> >= ==> != === != <== <= <-
