from pathlib import Path
import environ
import os
import requests
from audio_report.settings import env


class NeuroServerClient:
    def __init__(self):
        self.api_url = env("AI_API_URL")
        self.x_api_key = env("AI_API_KEY")

    def send_to_neuro_server(self, audio_file, participants, meeting_date):
        files = {"audio": (audio_file.name, audio_file.file, audio_file.content_type)}
        data = {
            "meeting_date": meeting_date,
            "participants": ", ".join(participants),
            "x_api_key": str(self.x_api_key)
        }
        response = requests.post(self.api_url, files=files, data=data)
        return response.json()
