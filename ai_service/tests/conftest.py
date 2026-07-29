import os


if os.getenv("RUN_INTEGRATION_TESTS") != "1":
    os.environ.setdefault("API_KEY", "test-api-key")
    os.environ.setdefault("LLAMA_URL", "http://ollama.test")
