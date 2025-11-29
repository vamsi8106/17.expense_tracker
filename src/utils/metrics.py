#src/utils/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# LLM API calls
LLM_API_CALLS = Counter(
    "llm_api_calls_total",
    "Total number of LLM calls"
)

# LLM latency
LLM_LATENCY = Histogram(
    "llm_api_latency_seconds",
    "Latency of LLM calls"
)

# Active users (Redis sessions)
ACTIVE_USERS = Gauge(
    "active_users_total",
    "Number of active user sessions"
)

# Cache metrics
CACHE_HITS = Counter(
    "cache_hits_total",
    "Total number of cache hits"
)

CACHE_MISSES = Counter(
    "cache_misses_total",
    "Total number of cache misses"
)

# MCP tool calls
MCP_TOOL_CALLS = Counter(
    "mcp_tool_calls_total",
    "Total number of MCP tool calls"
)

# Expenses added
EXPENSES_ADDED = Counter(
    "expenses_added_total",
    "Total expenses added"
)
