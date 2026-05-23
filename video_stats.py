import requests
import os
from dotenv import load_dotenv
from datetime import date
import json

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



def get_video_statistics(video_ids):

    def batch_list(video_ids, batch_size):
        for video_id in range (0, len(video_ids), batch_size):
            yield video_ids[video_id : video_id + batch_size]
            #Yield enables batch processing as it will run the code for each batch without losing its place

    try:
        extraction = []

        for batch in batch_list(video_ids, MAX_ITEMS):
            video_id_str = ",".join(batch)

            url = f'https://youtube.googleapis.com/youtube/v3/videos?part=statistics&part=contentDetails&part=snippet&id={video_id_str}&key={API_KEY}'    

            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            for item in data.get("items", []):
                #Get nodes that contain data we want - then parse each node dict
                video_id = item["id"]
                snippet = item["snippet"]
                contentDetails = item["contentDetails"]
                statistics = item["statistics"]
           
                #Create dict of individual video data to add to list
                video_data = {
                    'video_id' : video_id,
                    'title' : snippet['title'],
                    'publishedAt' : snippet['publishedAt'],
                    'duration' : contentDetails['duration'],
                    'viewCount' : statistics.get('viewCount', None),
                    'likeCount' : statistics.get('likeCount', None),
                    'commentCount' : statistics.get('commentCount', None),
                }

                extraction.append(video_data)
            
        return extraction
    except requests.exceptions.RequestException as e:
        raise e

def save_to_json(extraction):
    file_path = f"data/YT_data_{date.today()}.json"

    with open(file_path, 'w', encoding='utf-8') as json_outfile:
        json.dump(extraction, json_outfile, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    playlist_id = get_playlist_id()
    video_ids = get_video_ids(playlist_id)
    video_extraction = get_video_statistics(video_ids)
    save_to_json(video_extraction)