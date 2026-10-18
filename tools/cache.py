import hashlib
import json
import redis
from config import REDIS_HOST, REDIS_PORT
_client = None
def get_client():
    global _client
    if _client is None:
        _client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT,
                              decode_responses=True)
    return _client
def _key(text):
    h = hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]
    return f'emb:{h}'
def get_embedding(text):
    raw = get_client().get(_key(text))
    if raw is None:
        return None
    return json.loads(raw)
def set_embedding(text,vector,ttl=7*24*3600):
    get_client().set(_key(text), json.dumps(vector), ex=ttl)
if __name__ == '__main__':
    set_embedding('hello', [0.1, 0.2, 0.3])
    print(get_embedding('hello'))
    print(get_embedding('world'))