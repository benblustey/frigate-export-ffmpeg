import os
import time
import schedule
import logging
from datetime import datetime
from dotenv import load_dotenv
import download_frigate

# Configure logging
current_datetime = datetime.now().strftime('%Y-%m-%d--%H%M')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'frigate_export_{current_datetime}.log')
    ]
)

def setup_environment():
    """Setup environment variables and validate required settings."""
    load_dotenv()
    
    # Validate required environment variables
    required_vars = ['FRIGATE_SERVER', 'DOWNLOADS_DIR', 'LOGS_DIR', 'MONGODB_NAME', 'MONGODB_COLLECTION', 'CRON_SCHEDULE']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Create downloads directory if it doesn't exist
    downloads_dir = os.getenv('DOWNLOADS_DIR', './downloads')
    os.makedirs(downloads_dir, exist_ok=True)
    
    # Create logs directory if it doesn't exist
    logs_dir = os.getenv('LOGS_DIR', './logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    logging.info("Environment setup completed successfully")

def run_download_task():
    """Execute the download task with logging."""
    try:
        logging.info("Starting download task")
        # Get process video flag from environment
        process_video = os.getenv('PROCESS_VIDEO', 'false').lower() == 'true'
        if process_video:
            logging.info("Video processing is enabled")
        
        # Create argument list for download_frigate
        args = []
        if process_video:
            args.extend(['-p'])
        
        # Call main with arguments
        download_frigate.main()
        logging.info("Download task completed successfully")
    except Exception as e:
        logging.error(f"Error during download task: {str(e)}")

def main():
    """Main entry point for the application."""
    try:
        setup_environment()
        
        # Get cron schedule from environment or use default (hourly)
        cron_schedule = os.getenv('CRON_SCHEDULE', '0 * * * *')
        
        # Parse cron schedule and set up the job
        if cron_schedule == '0 * * * *':  # Default hourly
            schedule.every().hour.at(':00').do(run_download_task)
        else:
            # Add more schedule parsing logic here if needed
            schedule.every().hour.at(':00').do(run_download_task)
        
        # Run immediately on startup
        run_download_task()
        
        logging.info(f"Service started with schedule: {cron_schedule}")
        
        # Keep the script running
        while True:
            schedule.run_pending()
            time.sleep(60)
            
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        raise

if __name__ == "__main__":
    main()