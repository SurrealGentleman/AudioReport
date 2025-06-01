import os
import subprocess
from dotenv import load_dotenv
import requests

# Загрузка .env файла
load_dotenv('.env')


# class Llama:
#     def __init__(self, model_name: str = "llama3"):
#         self.model_name = model_name
#
#     def generate(self, prompt: str) -> str:
#         result = subprocess.run(
#             ["ollama", "run", self.model_name],
#             input=prompt.encode(),
#             stdout=subprocess.PIPE,
#         )
#         return result.stdout.decode()

class Llama:
    def __init__(
            self,
            model_name: str = os.environ.get("LLAMA_MODEL"),
            host: str = os.environ.get("LLAMA_URL")
    ):
        self.model_name = model_name
        self.url = f"{host}/api/generate"

    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "temperature": 0.4,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.2,
            "num_predict": 1200,
            "stream": False
        }
        response = requests.post(self.url, json=payload)
        response.raise_for_status()
        return response.json()["response"]