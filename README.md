# 🎧 Whisperbox

> Local video transcription powered by Whisper AI — no API costs, your data stays private.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🚀 **Local Processing** — Runs on your machine, no API costs
- 📁 **Batch Processing** — Transcribe entire folders at once
- 🎯 **Multiple Formats** — Output as Markdown, JSON, SRT, or TXT
- 🌍 **Multi-language** — Supports 99+ languages (auto-detect or specify)
- 📊 **Progress Tracking** — Beautiful CLI progress bars
- 🧠 **AI-Ready Output** — Structured for RAG/embeddings pipelines
- ⚡ **GPU Accelerated** — Uses CUDA for fast transcription

## 🖥️ Demo

```bash
# Single file
whisperbox transcribe video.mp4

# Batch folder
whisperbox transcribe ./videos --output ./transcripts

# With options
whisperbox transcribe video.mp4 --language pt --format markdown --model large-v3
```

## 📦 Installation

### Prerequisites
- Python 3.10+
- NVIDIA GPU (optional but recommended)
- FFmpeg

### Install

```bash
# Clone the repo
git clone https://github.com/PeterTechDev/whisperbox.git
cd whisperbox

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .
```

### GPU Support (Recommended)

For NVIDIA GPU acceleration:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 🚀 Usage

### CLI

```bash
# Basic transcription
whisperbox transcribe video.mp4

# Specify language (faster than auto-detect)
whisperbox transcribe video.mp4 --language pt

# Choose model (tiny, base, small, medium, large-v3)
whisperbox transcribe video.mp4 --model medium

# Batch process folder
whisperbox transcribe ./my-videos --output ./transcripts

# Output formats
whisperbox transcribe video.mp4 --format markdown  # .md with frontmatter
whisperbox transcribe video.mp4 --format json      # structured JSON
whisperbox transcribe video.mp4 --format srt       # subtitles
whisperbox transcribe video.mp4 --format txt       # plain text
```

### Python API

```python
from whisperbox import WhisperBox

wb = WhisperBox(model="medium")

# Single file
result = wb.transcribe("video.mp4")
print(result.text)

# Batch
results = wb.transcribe_batch("./videos")
for r in results:
    print(f"{r.filename}: {len(r.text)} chars")
```

## 📄 Output Formats

### Markdown (default)
```markdown
---
title: My Video
duration: 1234
language: pt
model: medium
transcribed_at: 2026-02-06T15:00:00
---

# My Video

[00:00:00] First segment of transcription...

[00:01:30] Second segment continues here...
```

### JSON
```json
{
  "metadata": {
    "filename": "video.mp4",
    "duration": 1234,
    "language": "pt"
  },
  "segments": [
    {"start": 0.0, "end": 5.2, "text": "First segment..."},
    {"start": 5.2, "end": 12.1, "text": "Second segment..."}
  ],
  "text": "Full transcription text..."
}
```

## 🧠 AI Integration

Whisperbox outputs are designed for AI workflows:

```bash
# Generate embeddings-ready chunks
whisperbox transcribe video.mp4 --format json --chunk-size 500

# Export for RAG pipeline
whisperbox export ./transcripts --format langchain
```

## ⚙️ Configuration

Create `~/.whisperbox/config.yaml`:

```yaml
default_model: medium
default_language: auto
default_format: markdown
output_dir: ./transcripts
gpu: true
```

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [faster-whisper](https://github.com/guillaumekln/faster-whisper) - Fast Whisper implementation
- [OpenAI Whisper](https://github.com/openai/whisper) - Original model
