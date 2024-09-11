from datetime import datetime,timezone
import requests
import configparser

config = configparser.ConfigParser()
config.read('data/config.ini')
API_KEY = config['Youtube_API'].get('API_KEY')
CHANNEL_ID = config['Youtube_API'].get('CHANNEL_ID')
VEDIO_PLAYLIST_ID = config['Youtube_API'].get('VEDIO_PLAYLIST_ID')

def subs_view_request():
    url = f"https://youtube.googleapis.com/youtube/v3/channels?part=statistics&id={CHANNEL_ID}&key={API_KEY}"
    response = requests.get(url)
    return response.json()["items"][0]["statistics"]["subscriberCount"], response.json()["items"][0]["statistics"]["viewCount"]

def lastlive_request(formatted:bool = True):
    playlist_response = requests.get(f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults=10&playlistId={VEDIO_PLAYLIST_ID}&key={API_KEY}")
    videos_id = [contentDetails["videoId"] for contentDetails in [item["contentDetails"] for item in playlist_response.json()["items"] ] ]
    url = f"https://youtube.googleapis.com/youtube/v3/videos?part=liveStreamingDetails&key={API_KEY}&id="
    url += "&id=".join(videos_id)
    
    videos_response = requests.get(url)
    for item in videos_response.json()['items']:
        if "liveStreamingDetails" in item:
            if "actualEndTime" not in item["liveStreamingDetails"]:
                return '🔴正在直播中'
            time_str =  item["liveStreamingDetails"]["actualEndTime"]
            break

    live_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
    now = datetime.now(timezone.utc)
    delta = now - live_time
    if formatted:
        days = delta.days
        hours = delta.seconds // 3600
        result = ''
        if days:
            result += f' {days}天'
        if hours:
            result += f' {hours}小時'
        if result == '':
            result += f' {delta.seconds // 60}分鐘'
        return result
    else:
        return str(delta)
    
    
if __name__ == "__main__":
    print(lastlive_request())
