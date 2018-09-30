import logging

__all__ = ['logger']

#
# Create logger
#
logger = logging.getLogger('tohu')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('{asctime} {levelname}  {message}', datefmt='%Y-%m-%d %H:%M:%S', style='{')
ch.setFormatter(formatter)
logger.addHandler(ch)
