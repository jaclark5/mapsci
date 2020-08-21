
import logging
import logging.handlers

# Logging
logger = logging.getLogger()
logger.setLevel(20)

# Set up logging to console
console_handler = logging.StreamHandler() # sys.stderr
console_handler.setFormatter( logging.Formatter('[%(levelname)s](%(name)s): %(message)s') )
console_handler.setLevel(args.verbose)
logger.addHandler(console_handler)


