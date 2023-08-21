import subprocess
import queue
import os
import time


video_queue = queue.Queue()

def enqueue_video(video_path):
    video_queue.put(video_path)
    print(f"Video '{video_path}' added to the queue.")

def get_queue_length():
    return video_queue.qsize()

def get_queue_duration():
    duration = 0
    for video_path in list(video_queue.queue):
        try:
            output = subprocess.check_output(['ffprobe', '-i', video_path, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=%s' % ("p=0")])
            duration += float(output)
        except subprocess.CalledProcessError:
            print(f"Failed to retrieve duration for video '{video_path}'.")
    
    return duration / 60

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

    try:
        subprocess.run(ffmpeg_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while broadcasting the video: {e}")
    except KeyboardInterrupt:
        print("Broadcast interrupted by user.")

def start_broadcast(stream_url, stream_key):
    while True:
        if not video_queue.empty():
            video_path = video_queue.get()
            print(f"Now broadcasting: {video_path}")
            broadcast_video(video_path, stream_url, stream_key)
            print(f"Finished broadcasting: {video_path}")

            # Delete the video file after broadcasting
            os.remove(video_path)
        else:
            loop_video_path = 'path/to/your/loop/video.mp4'  # Specify the loop video path
            print(f"Now looping: {loop_video_path}")
            broadcast_video(loop_video_path, stream_url, stream_key)
            print(f"Finished looping: {loop_video_path}")

# Example usage
video_file1 = 'C:\\Users\\totob\\Downloads\\live\\snt0.mp4'
video_file2 = 'C:\\Users\\totob\\Downloads\\live\\snt0.mp4'
stream_url = 'rtmp://a.rtmp.youtube.com/live2'
stream_key = 'sx5j-wds6-77k5-pwsx-8khy'

enqueue_video(video_file1)
enqueue_video(video_file2)

print(f"Queue length: {get_queue_length()} videos")
print(f"Queue duration: {get_queue_duration()} minutes")

start_broadcast(stream_url, stream_key)
