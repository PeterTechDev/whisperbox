"""Data models for Whisperbox."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class Segment:
    """A single transcription segment with timing."""

    start: float
    end: float
    text: str

    @property
    def duration(self) -> float:
        return self.end - self.start

    def to_dict(self) -> dict:
        return {
            "start": self.start,
            "end": self.end,
            "text": self.text,
        }


@dataclass
class TranscriptionResult:
    """Result of a transcription job."""

    filename: str
    text: str
    segments: list[Segment] = field(default_factory=list)
    language: str = "unknown"
    duration: float = 0.0
    model: str = "unknown"
    transcribed_at: datetime = field(default_factory=datetime.now)

    @property
    def word_count(self) -> int:
        return len(self.text.split())

    def to_dict(self) -> dict:
        return {
            "metadata": {
                "filename": self.filename,
                "duration": self.duration,
                "language": self.language,
                "model": self.model,
                "transcribed_at": self.transcribed_at.isoformat(),
                "word_count": self.word_count,
            },
            "segments": [s.to_dict() for s in self.segments],
            "text": self.text,
        }

    def to_markdown(self) -> str:
        """Export as markdown with frontmatter."""
        lines = [
            "---",
            f"title: {Path(self.filename).stem}",
            f"duration: {self.duration:.0f}",
            f"language: {self.language}",
            f"model: {self.model}",
            f"transcribed_at: {self.transcribed_at.isoformat()}",
            f"word_count: {self.word_count}",
            "---",
            "",
            f"# {Path(self.filename).stem}",
            "",
        ]

        for segment in self.segments:
            timestamp = self._format_timestamp(segment.start)
            lines.append(f"[{timestamp}] {segment.text}")
            lines.append("")

        return "\n".join(lines)

    def to_srt(self) -> str:
        """Export as SRT subtitle format."""
        lines = []
        for i, segment in enumerate(self.segments, 1):
            start = self._format_srt_timestamp(segment.start)
            end = self._format_srt_timestamp(segment.end)
            lines.append(str(i))
            lines.append(f"{start} --> {end}")
            lines.append(segment.text)
            lines.append("")
        return "\n".join(lines)

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """Format seconds as HH:MM:SS."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    @staticmethod
    def _format_srt_timestamp(seconds: float) -> str:
        """Format seconds as HH:MM:SS,mmm for SRT."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
