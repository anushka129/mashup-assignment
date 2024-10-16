import os
import sys
from yt_dlp import YoutubeDL
from moviepy.editor import VideoFileClip
from pydub import AudioSegment

def download_videos(singer_name, num_videos):
    search_query = f"ytsearch{num_videos}:{singer_name} songs"
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',  
        'noplaylist': True, 
        'default_search': 'ytsearch',
        'outtmpl': 'video_%(autonumber)s.%(ext)s',
    }

    with YoutubeDL(ydl_opts) as ydl:
        video_entries = ydl.extract_info(search_query, download=False).get('entries', [])
        video_urls = [entry['webpage_url'] for entry in video_entries[:num_videos]]
        ydl.download(video_urls)

def convert_videos_to_audio(num_videos):
    for i in range(1, num_videos + 1):
        video_path = f"video_{i:05}.mp4"
        if os.path.exists(video_path):
            VideoFileClip(video_path).audio.write_audiofile(f"audio_{i:05}.mp3")
        else:
            print(f"Warning: {video_path} not found. Skipping...")

def trim_audios(num_videos, duration):
    for i in range(1, num_videos + 1):
        audio_path = f"audio_{i:05}.mp3"
        if os.path.exists(audio_path):
            trimmed_audio = AudioSegment.from_file(audio_path)[:duration * 1000]
            trimmed_audio.export(f"trimmed_audio_{i}.mp3", format="mp3")
        else:
            print(f"Warning: {audio_path} not found. Skipping...")

def merge_audios(num_videos, output_file):
    combined = AudioSegment.empty()
    for i in range(1, num_videos + 1):
        trimmed_audio_path = f"trimmed_audio_{i}.mp3"
        if os.path.exists(trimmed_audio_path):
            combined += AudioSegment.from_file(trimmed_audio_path)
        else:
            print(f"Warning: {trimmed_audio_path} not found. Skipping...")
    combined.export(output_file, format="mp3")

def main():
    if len(sys.argv) != 5:
        print("Usage: python <program.py> <SingerName> <NumberOfVideos> <AudioDuration> <OutputFileName>")
        sys.exit(1)

    singer_name, num_videos, audio_duration, output_file = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]

    download_videos(singer_name, num_videos)
    convert_videos_to_audio(num_videos)
    trim_audios(num_videos, audio_duration)
    merge_audios(num_videos, output_file)

    print(f"Mashup created successfully: {output_file}")

if __name__ == "__main__":
    main()
