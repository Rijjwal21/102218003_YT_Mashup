import os
import yt_dlp
from pydub import AudioSegment
import argparse

def download_audio(keyword, num_videos, trim_duration, output_file, download_dir):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        search_results = ydl.extract_info(f"ytsearch{num_videos}:{keyword}", download=False)['entries']
        for result in search_results:
            try:
                print(f"Downloading: {result['title']} from {result['webpage_url']}")
                ydl.download([result['webpage_url']])
            except Exception as e:
                print(f"Error downloading {result['title']}: {e}")

    print(f"Contents of download directory '{download_dir}':")
    all_files = os.listdir(download_dir)
    for file in all_files:
        print(file)

    audio_paths = [os.path.join(download_dir, file) for file in all_files if file.endswith('.mp3')]
    print(f"Detected mp3 files: {audio_paths}")

    if not audio_paths:
        print("No audio files were detected after download.")
        return

    combined = AudioSegment.empty()
    for path in audio_paths:
        try:
            print(f"Processing file: {path}")
            audio = AudioSegment.from_file(path)
            if len(audio) > trim_duration * 1000:
                trimmed_audio = audio[:trim_duration * 1000]
                combined += trimmed_audio
                print(f"Trimmed and added: {path}")
            else:
                print(f"Audio file {path} is shorter than {trim_duration} seconds, skipped trimming.")
        except Exception as e:
            print(f"Error processing {path}: {e}")

    if combined:
        combined.export(output_file, format="mp3")
        print(f"Combined audio saved as {output_file}")
    else:
        print("No audio files were combined.")

def main():
    parser = argparse.ArgumentParser(description="Download & Combine YouTube MP3 clips.")
    parser.add_argument('keyword', type=str, help='Keywords for YouTube videos.')
    parser.add_argument('num_videos', type=int, help='No of videos to Download.')
    parser.add_argument('trim_duration', type=int, help='Duration in (seconds) to trim from each audio file.')
    parser.add_argument('output_file', type=str, help='Output file name for the combined audio.')
    parser.add_argument('download_dir', type=str, help='Directory to save downloaded audio files.')

    args = parser.parse_args()

    download_audio(args.keyword, args.num_videos, args.trim_duration, args.output_file, args.download_dir)

if __name__ == "__main__":
    main()
