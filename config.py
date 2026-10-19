import os
import logging
from dotenv import load_dotenv
load_dotenv()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.join(BASE_DIR, 'workspace')

API_KEY = os.getenv('API_KEY', '')

CHAT_MODEL = 'deepseek-ai/DeepSeek-v3'
CHAT_URL='https://api.siliconflow.cn/v1/chat/completions'

MAX_STEPS = 15
def get_headers():
    if not API_KEY:
        raise RuntimeError('API_KEY not set')
    return {
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }
DOCKER_IMAGE = 'codepilot-python'

CHROMA_DIR = os.path.join(BASE_DIR, 'chroma_db')
EMBED_MODEL = 'BAAI/bge-m3'
EMBED_URL = 'https://api.siliconflow.cn/v1/embeddings'

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

LOG_LEVEL = 'DEBUG'
def setup_logging():
    logging.basicConfig(
        level=LOG_LEVEL,
        format ='%(asctime)s[%(levelname)s]%(name)s: %(message)s',
        datefmt = '%H:%M:%S'
    )
    for noisy in ('urllib3','chromadb'):
        logging.getLogger(noisy).setLevel(logging.WARNING)














