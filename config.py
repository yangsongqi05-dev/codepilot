import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.join(BASE_DIR, 'workspace')

API_KEY_FILE = r'E:\python\api_key.txt.txt'

CHAT_MODEL = 'deepseek-ai/DeepSeek-v3'
CHAT_URL='https://api.siliconflow.cn/v1/chat/completions'

MAX_STEPS = 15
def get_headers():
    with open(API_KEY_FILE, encoding='utf_8') as f:
        key = f.read().strip()
    return {
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }
DOCKER_IMAGE = 'codepilot-python'

CHROMA_DIR = os.path.join(BASE_DIR, 'chroma_db')
EMBED_MODEL = 'BAAI/bge-m3'
EMBED_URL = 'https://api.siliconflow.cn/v1/embeddings'



