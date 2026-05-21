import requests
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="./.env")

API_KEY = os.getenv('API_KEY')
CHANNEL_HANDLE = 'MrBeast'
MAX_ITEMS = 50


def get_playlist_id():
    try:
        url = f'https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        channel_items = data["items"][0]
        playlist_id = channel_items["contentDetails"]["relatedPlaylists"]["uploads"]
        return playlist_id
    except requests.exceptions.RequestException as e:
        raise e


def get_video_ids(playlist_id):
    try:
        video_list = []

        page_token = None

        base_url = f'https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={MAX_ITEMS}&playlistId={playlist_id}&key={API_KEY}'

        while True:
            url = base_url

            if page_token:
                url += f'&pageToken={page_token}'

            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            for i in data.get("items",[]):
                video_list.append(i["contentDetails"]['videoId'])


            page_token = data.get('nextPageToken')

            if not page_token:
                break

        return video_list
    except requests.exceptions.RequestException as e:
        raise e

if __name__ == "__main__":
    playlist_id = get_playlist_id()
    get_video_ids(playlist_id)
