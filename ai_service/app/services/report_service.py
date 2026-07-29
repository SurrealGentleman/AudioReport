import asyncio

from pathlib import Path

from app.services.report_generator import Llama
from app.services.transcriber import Whisper
from app.services.report_prompt import build_report_prompt


class ReportGenerationError(Exception):
    pass


class TranscriptionError(ReportGenerationError):
    pass


class GeneratorUnavailableError(ReportGenerationError):
    pass


class ReportService:
    def __init__(
        self,
        transcriber: Whisper,
        generator: Llama,
    ) -> None:
        self.transcriber = transcriber
        self.generator = generator

    async def generate(
        self,
        audio_path: Path,
        meeting_date: str,
        participants: str,
    ) -> str:
        try:
            transcript = await asyncio.to_thread(
                self.transcriber.transcribe,
                str(audio_path),
            )

            prompt = build_report_prompt(
                transcript=transcript,
                participants=participants,
                meeting_date=meeting_date,
            )

            return await asyncio.to_thread(
                self.generator.generate,
                prompt,
            )
        except Exception as exc:
            raise ReportGenerationError(
                "Could not generate report"
            ) from exc