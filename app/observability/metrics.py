from prometheus_client import Counter, Histogram

REQUESTS = Counter("nexora_requests_total", "Total inference requests", ["model", "status"])
LATENCY = Histogram("nexora_request_latency_seconds", "Inference request latency", ["model"])
TOKENS = Counter("nexora_tokens_total", "Total tokens", ["model", "type"])
