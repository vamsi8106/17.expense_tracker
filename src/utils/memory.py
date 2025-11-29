#src/utils/memory.py
from src.utils.redis_client import redis_client

USER_KEY_PREFIX = "user:session:"
CACHE_KEY_PREFIX = "cache:"
SESSION_KEY_PREFIX = "session:"

def set_user(session_id: str, username: str):
    redis_client.set(f"{USER_KEY_PREFIX}{session_id}", username)

def get_user(session_id: str):
    return redis_client.get(f"{USER_KEY_PREFIX}{session_id}")

def clear_user(session_id: str):
    redis_client.delete(f"{USER_KEY_PREFIX}{session_id}")

def get_cached_response(user: str, query: str):
    return redis_client.get(f"{CACHE_KEY_PREFIX}{user}:{query}")

def set_cached_response(user: str, query: str, response: str):
    redis_client.set(f"{CACHE_KEY_PREFIX}{user}:{query}", response, ex=3600)

def count_sessions():
    return len(redis_client.keys(f"{SESSION_KEY_PREFIX}*"))
