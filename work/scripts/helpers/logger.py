import logging
from pathlib import Path
from datetime import datetime

def setup_logging():

    log_dir = Path("/work/logs")
    log_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    log_file = log_dir / f"calm_update_{timestamp}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    logging.info("Logging initialized.")
    logging.info(f"Log file: {log_file}")