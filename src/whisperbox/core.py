"""Core transcription functionality using faster-whisper."""

import os
from pathlib import Path
from typing import Iterator, Literal, Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn

from whisperbox.models import Segment, TranscriptionResult

console = Console()

# Supported video/audio extensions
SUPPORTED_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".mp3", ".wav", ".flac", ".m4a", ".ogg"}

ModelSize = Literal["tiny", "base", "small", "medium", "large-v3"]


class WhisperBox:
    """Main transcription class using faster-whisper."""

    def __init__(
        self,
        model: ModelSize = "medium",
        device: str = "auto",
        compute_type: str = "auto",
    ):
        """
        Initialize WhisperBox.

        Args:
            model: Model size (tiny, base, small, medium, large-v3)
            device: Device to use (auto, cuda, cpu)
            compute_type: Compute type (auto, float16, int8, int8_float16)
        """
        self.model_name = model
        self.device = device
        self.compute_type = compute_type
        self._model = None

    def _load_model(self):
        """Lazy load the model."""
        if self._model is None:
            from faster_whisper import WhisperModel

            console.print(f"[dim]Loading model '{self.model_name}'...[/dim]")

            # Auto-detect best settings
            device = self.device
            compute_type = self.compute_type

            if device == "auto":
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"

            if compute_type == "auto":
                compute_type = "float16" if device == "cuda" else "int8"

            self._model = WhisperModel(
                self.model_name,
                device=device,
                compute_type=compute_type,
            )
            console.print(f"[green]✓ Model loaded on {device} ({compute_type})[/green]")

        return self._model

    def transcribe(
        self,
        file_path: str | Path,
        language: Optional[str] = None,
        verbose: bool = True,
    ) -> TranscriptionResult:
        """
        Transcribe a single audio/video file.

        Args:
            file_path: Path to the file
            language: Language code (e.g., 'pt', 'en') or None for auto-detect
            verbose: Show progress output

        Returns:
            TranscriptionResult with text and segments
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported format: {file_path.suffix}")

        model = self._load_model()

        if verbose:
            console.print(f"\n[bold]Transcribing:[/bold] {file_path.name}")

        # Transcribe with faster-whisper
        segments_gen, info = model.transcribe(
            str(file_path),
            language=language,
            beam_size=5,
            word_timestamps=False,
            vad_filter=True,  # Filter out silence
        )

        # Collect segments
        segments = []
        full_text_parts = []

        if verbose:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                console=console,
            ) as progress:
                task = progress.add_task("Processing...", total=info.duration)

                for segment in segments_gen:
                    segments.append(Segment(
                        start=segment.start,
                        end=segment.end,
                        text=segment.text.strip(),
                    ))
                    full_text_parts.append(segment.text.strip())
                    progress.update(task, completed=segment.end)
        else:
            for segment in segments_gen:
                segments.append(Segment(
                    start=segment.start,
                    end=segment.end,
                    text=segment.text.strip(),
                ))
                full_text_parts.append(segment.text.strip())

        result = TranscriptionResult(
            filename=file_path.name,
            text=" ".join(full_text_parts),
            segments=segments,
            language=info.language,
            duration=info.duration,
            model=self.model_name,
        )

        if verbose:
            console.print(f"[green]✓ Done![/green] {result.word_count} words, {len(segments)} segments")

        return result

    def transcribe_batch(
        self,
        input_path: str | Path,
        output_path: Optional[str | Path] = None,
        language: Optional[str] = None,
        format: Literal["markdown", "json", "srt", "txt"] = "markdown",
        recursive: bool = False,
    ) -> list[TranscriptionResult]:
        """
        Transcribe all supported files in a directory.

        Args:
            input_path: Directory containing files
            output_path: Directory for output files (default: same as input)
            language: Language code or None for auto-detect
            format: Output format
            recursive: Search subdirectories

        Returns:
            List of TranscriptionResults
        """
        input_path = Path(input_path)
        output_path = Path(output_path) if output_path else input_path / "transcripts"

        if not input_path.exists():
            raise FileNotFoundError(f"Directory not found: {input_path}")

        # Find all supported files
        pattern = "**/*" if recursive else "*"
        files = [
            f for f in input_path.glob(pattern)
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
        ]

        if not files:
            console.print("[yellow]No supported files found.[/yellow]")
            return []

        console.print(f"\n[bold]Found {len(files)} files to transcribe[/bold]\n")

        # Create output directory
        output_path.mkdir(parents=True, exist_ok=True)

        results = []
        for i, file in enumerate(files, 1):
            console.print(f"[dim]({i}/{len(files)})[/dim]", end=" ")

            try:
                result = self.transcribe(file, language=language)
                results.append(result)

                # Save output
                self._save_result(result, output_path, format)

            except Exception as e:
                console.print(f"[red]✗ Error: {e}[/red]")

        console.print(f"\n[bold green]✓ Completed {len(results)}/{len(files)} files[/bold green]")
        console.print(f"[dim]Output: {output_path}[/dim]")

        return results

    def _save_result(
        self,
        result: TranscriptionResult,
        output_dir: Path,
        format: str,
    ):
        """Save transcription result to file."""
        import json

        stem = Path(result.filename).stem

        if format == "markdown":
            output_file = output_dir / f"{stem}.md"
            output_file.write_text(result.to_markdown(), encoding="utf-8")

        elif format == "json":
            output_file = output_dir / f"{stem}.json"
            output_file.write_text(
                json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        elif format == "srt":
            output_file = output_dir / f"{stem}.srt"
            output_file.write_text(result.to_srt(), encoding="utf-8")

        elif format == "txt":
            output_file = output_dir / f"{stem}.txt"
            output_file.write_text(result.text, encoding="utf-8")

        elif format == "html":
            from whisperbox.templates import generate_html
            output_file = output_dir / f"{stem}.html"
            output_file.write_text(generate_html(result), encoding="utf-8")

        else:
            raise ValueError(f"Unknown format: {format}")
