"""Command-line interface for Whisperbox."""

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from whisperbox.core import WhisperBox, ModelSize, SUPPORTED_EXTENSIONS

app = typer.Typer(
    name="whisperbox",
    help="🎧 Local video transcription powered by Whisper AI",
    add_completion=False,
)
console = Console()


@app.command()
def transcribe(
    input_path: Path = typer.Argument(
        ...,
        help="Video/audio file or directory to transcribe",
        exists=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Output directory (default: ./transcripts or next to file)",
    ),
    language: Optional[str] = typer.Option(
        None,
        "--language", "-l",
        help="Language code (e.g., 'pt', 'en'). Auto-detect if not specified.",
    ),
    model: ModelSize = typer.Option(
        "medium",
        "--model", "-m",
        help="Model size: tiny, base, small, medium, large-v3",
    ),
    format: str = typer.Option(
        "markdown",
        "--format", "-f",
        help="Output format: markdown, json, srt, txt",
    ),
    recursive: bool = typer.Option(
        False,
        "--recursive", "-r",
        help="Search subdirectories when processing a folder",
    ),
):
    """
    Transcribe video/audio files using local Whisper AI.

    Examples:

        whisperbox transcribe video.mp4

        whisperbox transcribe ./videos --output ./transcripts

        whisperbox transcribe video.mp4 -l pt -m large-v3 -f json
    """
    console.print("\n[bold blue]🎧 Whisperbox[/bold blue]\n")

    wb = WhisperBox(model=model)

    if input_path.is_file():
        # Single file
        result = wb.transcribe(input_path, language=language)

        # Determine output path
        if output:
            output.mkdir(parents=True, exist_ok=True)
            output_dir = output
        else:
            output_dir = input_path.parent

        wb._save_result(result, output_dir, format)
        console.print(f"\n[dim]Saved to: {output_dir}[/dim]")

    else:
        # Directory
        wb.transcribe_batch(
            input_path,
            output_path=output,
            language=language,
            format=format,
            recursive=recursive,
        )


@app.command()
def info(
    file_path: Path = typer.Argument(
        ...,
        help="Video/audio file to get info about",
        exists=True,
    ),
):
    """Show information about a media file."""
    import subprocess

    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", str(file_path)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        console.print("[red]Error: Could not read file info. Is ffmpeg installed?[/red]")
        raise typer.Exit(1)

    data = json.loads(result.stdout)
    fmt = data.get("format", {})

    table = Table(title=f"📄 {file_path.name}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    duration = float(fmt.get("duration", 0))
    minutes = int(duration // 60)
    seconds = int(duration % 60)

    table.add_row("Duration", f"{minutes}m {seconds}s")
    table.add_row("Size", f"{int(fmt.get('size', 0)) / 1024 / 1024:.1f} MB")
    table.add_row("Format", fmt.get("format_long_name", "Unknown"))

    for stream in data.get("streams", []):
        if stream.get("codec_type") == "audio":
            table.add_row("Audio Codec", stream.get("codec_name", "Unknown"))
            table.add_row("Sample Rate", f"{stream.get('sample_rate', 'Unknown')} Hz")
        elif stream.get("codec_type") == "video":
            table.add_row("Video Codec", stream.get("codec_name", "Unknown"))
            table.add_row("Resolution", f"{stream.get('width')}x{stream.get('height')}")

    console.print(table)


@app.command()
def models():
    """List available Whisper models and their requirements."""
    table = Table(title="🧠 Available Models")
    table.add_column("Model", style="cyan")
    table.add_column("Size", style="yellow")
    table.add_column("VRAM", style="green")
    table.add_column("Speed", style="magenta")
    table.add_column("Quality", style="blue")

    table.add_row("tiny", "39M", "~1 GB", "⚡⚡⚡⚡⚡", "★☆☆☆☆")
    table.add_row("base", "74M", "~1 GB", "⚡⚡⚡⚡", "★★☆☆☆")
    table.add_row("small", "244M", "~2 GB", "⚡⚡⚡", "★★★☆☆")
    table.add_row("medium", "769M", "~4 GB", "⚡⚡", "★★★★☆")
    table.add_row("large-v3", "1.5G", "~6 GB", "⚡", "★★★★★")

    console.print(table)
    console.print("\n[dim]Tip: Use 'medium' for best speed/quality balance on 4GB VRAM[/dim]")


@app.command()
def formats():
    """Show supported input formats."""
    console.print("\n[bold]Supported formats:[/bold]\n")

    video = [ext for ext in SUPPORTED_EXTENSIONS if ext in {".mp4", ".mkv", ".avi", ".mov", ".webm"}]
    audio = [ext for ext in SUPPORTED_EXTENSIONS if ext in {".mp3", ".wav", ".flac", ".m4a", ".ogg"}]

    console.print("[cyan]Video:[/cyan]", ", ".join(video))
    console.print("[cyan]Audio:[/cyan]", ", ".join(audio))


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version", "-v",
        help="Show version and exit",
    ),
):
    """🎧 Whisperbox - Local video transcription powered by Whisper AI."""
    if version:
        from whisperbox import __version__
        console.print(f"whisperbox {__version__}")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


if __name__ == "__main__":
    app()
