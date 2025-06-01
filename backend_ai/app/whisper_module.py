from faster_whisper import WhisperModel


class Whisper:
    def __init__(self, model_name: str, device: str):
        self.model = WhisperModel(model_name, device=device)

    def transcribe(self, audio_path: str) -> str:
        segments, _ = self.model.transcribe(audio_path, language='ru', beam_size=5, vad_filter=True)
        # segments, _ = self.model.transcribe(audio_path)
        return " ".join([seg.text for seg in segments])
