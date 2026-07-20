from pathlib import Path

from rest_framework import serializers

ALLOWED_AUDIO_EXTENSIONS = {".m4a", ".mp3", ".mp4", ".ogg", ".wav", ".webm"}
MAX_AUDIO_SIZE = 100 * 1024 * 1024


def validate_audio_file(audio):
    extension = Path(audio.name).suffix.lower()
    if extension not in ALLOWED_AUDIO_EXTENSIONS:
        raise serializers.ValidationError(
            "Допустимы файлы M4A, MP3, MP4, OGG, WAV и WEBM."
        )
    if audio.size > MAX_AUDIO_SIZE:
        raise serializers.ValidationError(
            "Размер аудиофайла не должен превышать 100 МБ."
        )
    return audio
