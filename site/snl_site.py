import contextlib
import os
import queue
import random
import subprocess
import threading
from time import sleep
import re

video_queue = queue.Queue()
urls_file = 'urls.txt'

playlist_index = 0

def download_video(url):
    video_title = subprocess.check_output(['yt-dlp', '-f', 'bestvideo+bestaudio', '--merge-output-format', 'mp4', '--get-title', url]).decode().strip()
    sanitized_video_title = re.sub(r'\W+', '', video_title)
    video_file = f'{sanitized_video_title}.mp4'
    subprocess.run(['yt-dlp', '-f', 'bestvideo+bestaudio', '--merge-output-format', 'mp4', '-o', video_file, url])
    return f"C:\\Users\\totob\\Downloads\\snl\\{video_file}"

def enqueue_video(video_path):
    video_queue.put(video_path)
    print(f"Video '{video_path}' added to the queue.")

def broadcast_video(video_path):
    ffmpeg_cmd = ['ffmpeg', '-re', '-i', video_path, '-c:v', 'libx264', '-preset', 'medium', '-maxrate', '5000k', '-bufsize', '10000k', '-pix_fmt', 'yuv420p', '-g', '50', '-c:a', 'aac', '-b:a', '160k', '-ac', '2', '-ar', '44100', '-f', 'hls', '-hls_time', '4', '-hls_playlist_type', 'event', 'playlist.m3u8']

    try:
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"Finished broadcasting video file: {video_path}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while broadcasting the video: {e}")
    except KeyboardInterrupt:
        print("Broadcast interrupted by user.")

    # Wait for the video player to finish playing the current video
    sleep(os.path.getsize(video_path) / (5000 * 1024))  # video file size / bitrate

    # Delete the video file and its segments
    os.remove(video_path)
    for file in os.listdir('.'):
        if file.endswith('.ts'):
            os.remove(file)
    print(f"Deleted video file and its segments: {video_path}")

def download_and_enqueue(url):
    try:
        video_file = download_video(url)
        try:
            enqueue_video(video_file)
        except Exception:
            os.remove(video_file)
    except Exception as e:
        print(f'Error downloading from {url}: {str(e)}')

def start_broadcast():
    global playlist_index
    playlist_index = 0

    with open(urls_file, 'r') as file:
        urls = file.readlines()
    random.shuffle(urls)

    if urls:
        url = urls.pop()
        download_and_enqueue(url)

    while True:
        if video_queue.qsize() < 3 and urls:
            for _ in range(3-video_queue.qsize()):
                with contextlib.suppress(Exception):
                    url = urls.pop()
                    threading.Thread(target=download_and_enqueue, args=(url,)).start()

        if not video_queue.empty():
            video_path = video_queue.get()
            print(f"Now broadcasting: {video_path}")
            broadcast_video(video_path)
        elif not urls:
            break
        else:
            loop_video_path = 'C:\\Users\\totob\\Downloads\\snl\\wait.mp4'
            print(f"Now looping: {loop_video_path}")
            broadcast_video(loop_video_path)

while True:
    start_broadcast()
    print('Finished broadcasting all videos. Starting over...')