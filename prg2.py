import os
import zipfile
from flask import Flask, request, render_template
import smtplib
from email.message import EmailMessage
from yt_dlp import YoutubeDL
from moviepy.editor import VideoFileClip
from pydub import AudioSegment

app = Flask(__name__)

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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        singer_name = request.form['singer_name']
        num_videos = int(request.form['num_videos'])
        audio_duration = int(request.form['audio_duration'])
        output_file = 'mashup.mp3'  

        download_videos(singer_name, num_videos)
        convert_videos_to_audio(num_videos)
        trim_audios(num_videos, audio_duration)
        merge_audios(num_videos, output_file)

        zip_file_path = 'mashup.zip'
        if os.path.exists(output_file):
            with zipfile.ZipFile(zip_file_path, 'w') as zf:
                zf.write(output_file)

            email = request.form['email']
            sender_email = "aagarwal_be22@thapar.edu"
            password = "phdw wnpi wgec xiht"

            msg = EmailMessage()
            msg['From'] = sender_email
            msg['To'] = email
            msg['Subject'] = "Song Mashup Request"

            body = f"""
            Number of Songs: {num_videos}
            Artist Name: {singer_name}
            Video Length (seconds): {audio_duration}
            """
            msg.set_content(body)

            with open(zip_file_path, 'rb') as f:
                file_data = f.read()
                msg.add_attachment(file_data, maintype='application', subtype='zip', filename='mashup.zip')

            try:
                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                    server.starttls()
                    server.login(sender_email, password)
                    server.send_message(msg)
                return "Request submitted successfully!", 200
            except Exception as e:
                return f"An error occurred: {e}", 500
        else:
            return "Error: The mashup file was not created.", 500

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
