import os
import queue
import random
import subprocess
import threading
from time import sleep

video_queue = queue.Queue()
urls_file = 'urls.txt'

def download_video(url):
    video_title = subprocess.check_output(['yt-dlp', '-f', 'best[ext=mp4]+bestaudio[ext=m4a]/mp4', '--get-title', url]).decode().strip()
    sanitized_video_title = video_title.replace(':', '_')  # Replace colons with underscores
    video_file = f'{sanitized_video_title}.mp4'
    subprocess.run(['yt-dlp', '-f', 'best[ext=mp4]+bestaudio[ext=m4a]/mp4', '-o', video_file, url])
    return f"C:\\Users\\totob\\Downloads\\snl\\{video_file}"

def enqueue_video(video_path):
    video_queue.put(video_path)
    print(f"Video '{video_path}' added to the queue.")

def broadcast_video(video_path, stream_url, stream_key):
    ffmpeg_cmd = [
        'ffmpeg',
        '-re',
        '-i',
        video_path,
        '-c:v',
        'libx264',
        '-preset',
        'veryfast',
        '-maxrate',
        '3000k',
        '-bufsize',
        '6000k',
        '-pix_fmt',
        'yuv420p',
        '-g',
        '50',
        '-c:a',
        'aac',
        '-b:a',
        '160k',
        '-ac',
        '2',
        '-ar',
        '44100',
        '-f',
        'flv',
        f'{stream_url}/{stream_key}'
    ]
    # ffmpeg_cmd = [
    #     'ffmpeg',
    #     '-re',
    #     '-i',
    #     video_path,
    #     '-c:v',
    #     'libx264',
    #     '-preset',
    #     'veryfast',
    #     '-tune',
    #     'zerolatency',
    #     '-c:a',
    #     'aac',
    #     '-ar',
    #     '44100',
    #     '-f',
    #     'flv',
    #     'rtmp://node-rtsp-rtmp-server.totob12.repl.co/live/STREAM_NAME'
    # ]

    try:
        subprocess.run(ffmpeg_cmd, check=True)
        os.remove(video_path)  # delete the video file after broadcasting
        print(f"Finished broadcasting and deleted video file: {video_path}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while broadcasting the video: {e}")
    except KeyboardInterrupt:
        os.remove(video_path)  # Attempt to delete video file in case of interruption
        print("Broadcast interrupted by user.")

def start_broadcast(stream_url, stream_key):
    while True:
        while video_queue.qsize() < 3 and urls:  # Download videos until there are at least 3 in the queue
            url = urls.pop()
            try:
                video_file = download_video(url)
                enqueue_video(video_file)
            except Exception as e:
                print(f'Error downloading from {url}: {str(e)}')

        if not video_queue.empty():
            video_path = video_queue.get()
            print(f"Now broadcasting: {video_path}")
            broadcast_video(video_path, stream_url, stream_key)
        elif not urls:
            break  # Break the loop if all videos have been broadcasted and there are no more URLs to download
        else:
            loop_video_path = 'C:\\Users\\totob\\Downloads\\snl\\wait.mp4'  # Specify the loop video path
            print(f"Now looping: {loop_video_path}")
            broadcast_video(loop_video_path, stream_url, stream_key)

# Main script execution
# stream_url = 'rtmp://a.rtmp.youtube.com/live2'  # youtube
# stream_key = 'sx5j-wds6-77k5-pwsx-8khy'  # youtube
stream_url = 'rtmp://localhost:1935'  # api.video
stream_key = '05ff367e-d348-4b52-99a7-e54150ce8263'  # api.video

with open(urls_file, 'r') as file:
    urls = file.readlines()
random.shuffle(urls)  # Shuffle URLs before starting

# Start the broadcasting loop
start_broadcast(stream_url, stream_key)

# Shuffle URLs and start broadcasting loop again
while True:
    print('Finished broadcasting all videos. Starting over...')
    random.shuffle(urls)
    start_broadcast(stream_url, stream_key)
