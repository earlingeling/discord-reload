import logging

# Configure the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Print logs to file
fh = logging.FileHandler('log.log')
fh.setLevel(logging.INFO)

# Print logs to console
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Add timestamps to logfile and console output
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)