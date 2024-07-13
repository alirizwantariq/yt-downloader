import os
import logging
from datetime import datetime
import subprocess
import re

def setup_logger(title):
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    log_file = os.path.join("logs", f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{title}.log")
    
    logger = logging.getLogger("YouTubeDownloader")
    logger.setLevel(logging.DEBUG)
    
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    sh.setFormatter(formatter)
    
    if not logger.hasHandlers():
        logger.addHandler(fh)
        logger.addHandler(sh)
    
    return logger

def run_command(command, logger):
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.cmd}")
        logger.error(f"Error output: {e.stderr}")
        raise

def get_video_info(url, logger):
    try:
        command = ['yt-dlp', '-F', url]
        output = run_command(command, logger)
        logger.info(f"Fetched video info:\n{output}")
        return output
    except Exception as e:
        logger.error(f"Error extracting video streams: {str(e)}")
        raise

def download_video(url, format_code, logger):
    download_dir = "videos"
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    try:
        output_template = os.path.join(download_dir, '%(title)s.%(ext)s')
        command = [
            'yt-dlp',
            '-f', format_code,
            '-o', output_template,
            '--merge-output-format', 'mp4',
            '--postprocessor-args', '-c:v libx264 -c:a aac',
            url
        ]
        output = run_command(command, logger)
        
        # Extract the filename from the output
        match = re.search(r'\[download\] (.+) has already been downloaded', output)
        if match:
            filename = match.group(1)
        else:
            filename = "Unknown"
        
        logger.info(f"Download completed: {filename}")
        print(f"Video downloaded successfully: {filename}")
    except Exception as e:
        logger.error(f"Error during download: {str(e)}")
        raise

def get_best_formats(video_info):
    video_formats = re.findall(r'(\d+)\s+mp4.*\s+(\d+x\d+)', video_info)
    audio_formats = re.findall(r'(\d+)\s+audio only.*?(\d+k)', video_info)
    
    if not video_formats:
        raise ValueError("No suitable video formats found.")
    if not audio_formats:
        raise ValueError("No suitable audio formats found.")
    
    best_video = max(video_formats, key=lambda x: int(x[1].split('x')[0]))
    best_audio = max(audio_formats, key=lambda x: int(x[1][:-1]))
    
    return f"{best_video[0]}+{best_audio[0]}"

def main():
    url = input("Enter the YouTube video URL: ")
    logger = setup_logger("main")

    try:
        video_info = get_video_info(url, logger)
        print(video_info)
        
        print("\nOptions:")
        print("1. Best quality (auto-selected)")
        print("2. Custom format code")
        choice = input("Enter your choice (1 or 2): ")
        
        if choice == '1':
            try:
                format_code = get_best_formats(video_info)
                logger.info(f"Auto-selected best format: {format_code}")
            except ValueError as e:
                logger.error(f"Error in auto-selection: {str(e)}")
                print(f"Error: {str(e)}")
                print("Falling back to default format 'bestvideo+bestaudio'")
                format_code = 'bestvideo+bestaudio'
        elif choice == '2':
            format_code = input("Enter the format code: ")
            logger.info(f"User selected format code: {format_code}")
        else:
            raise ValueError("Invalid choice. Please enter 1 or 2.")
        
        download_video(url, format_code, logger)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        print(f"An error occurred: {str(e)}")
        print("Please check the log file for details.")

if __name__ == "__main__":
    main()