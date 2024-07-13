import os
import logging
from datetime import datetime
import subprocess

def setup_logger(title):
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # Generate log file name based on the current time and video title
    log_file = os.path.join("logs", f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{title}.log")
    
    # Set up logger
    logger = logging.getLogger("YouTubeDownloader")
    logger.setLevel(logging.DEBUG)
    
    # File handler
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    
    # Stream handler for terminal output
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    sh.setFormatter(formatter)
    
    if not logger.hasHandlers():
        logger.addHandler(fh)
        logger.addHandler(sh)
    
    return logger

def get_video_info(url, logger):
    try:
        # Fetch video formats available for the provided URL
        command = ['yt-dlp', '-F', url]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            logger.error(f"Error fetching video info: {result.stderr}")
            raise Exception(result.stderr)
        
        logger.info(f"Fetched video info:\n{result.stdout}")
        return result.stdout
    except Exception as e:
        logger.error(f"Error extracting video streams: {str(e)}")
        raise

def download_video(url, format_code, logger):
    download_dir = "videos"
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    try:
        # Download video with the specified format code
        command = ['yt-dlp', '-f', format_code, '-o', f'{download_dir}/%(title)s.%(ext)s', url]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            logger.error(f"Error downloading video: {result.stderr}")
            raise Exception(result.stderr)
        
        logger.info(f"Download completed:\n{result.stdout}")
    except Exception as e:
        logger.error(f"Error during download: {str(e)}")
        raise

def main():
    # Get the YouTube video URL from the user
    url = input("Enter the YouTube video URL: ")
    logger = setup_logger("main")

    try:
        video_info = get_video_info(url, logger)
        
        # Display video format information
        print(video_info)
        
        # Prompt the user to select a format code for downloading
        selected_option = input("Select the format code to download (e.g., '18' for 360p video+audio, 'bestvideo+bestaudio' for the best quality with merged audio): ")
        
        # Log the user's selection
        logger.info(f"User selected format code: {selected_option}")
        
        if selected_option.lower() == 'all':
            # Download the best quality video with audio
            download_video(url, 'bestvideo+bestaudio', logger)
        else:
            # Download video with the specified format code
            download_video(url, selected_option, logger)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
