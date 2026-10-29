from langchain_community.cache import InMemoryCache, SQLiteCache
from langchain_core.globals import set_llm_cache

_current_cache = None

def configure_cache(choice):
    """Register a global LangChain cache (in-memory or SQLite)."""
    global _current_cache
    if choice == "SQLite":
        _current_cache = SQLiteCache(database_path=".langchain_cache.db")
    else:
        _current_cache = InMemoryCache()
    set_llm_cache(_current_cache)
    return _current_cache
