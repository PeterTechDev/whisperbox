"""HTML templates for Whisperbox output."""

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.8;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #fafafa;
            color: #333;
        }}
        h1 {{
            color: #1a1a1a;
            border-bottom: 3px solid #6366f1;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }}
        .meta {{
            background: #f0f0f0;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            font-size: 14px;
            color: #666;
        }}
        .meta span {{
            margin-right: 20px;
        }}
        .content {{
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin-bottom: 30px;
        }}
        .content p {{
            margin-bottom: 1.5em;
            text-align: justify;
        }}
        .ai-section {{
            background: #1e1e2e;
            color: #cdd6f4;
            padding: 20px;
            border-radius: 12px;
            margin-top: 40px;
        }}
        .ai-section h2 {{
            color: #89b4fa;
            font-size: 16px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .ai-section pre {{
            background: #313244;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 13px;
            line-height: 1.6;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .copy-btn {{
            background: #6366f1;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            transition: background 0.2s;
        }}
        .copy-btn:hover {{
            background: #4f46e5;
        }}
        .copy-btn.copied {{
            background: #22c55e;
        }}
        footer {{
            text-align: center;
            margin-top: 40px;
            color: #999;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    
    <div class="meta">
        <span>⏱️ {duration}</span>
        <span>📝 {word_count} palavras</span>
        <span>🌐 {language}</span>
    </div>
    
    <div class="content">
        {content_html}
    </div>
    
    <div class="ai-section">
        <h2>
            🤖 Versão para IA
            <button class="copy-btn" onclick="copyToClipboard()">📋 Copiar</button>
        </h2>
        <pre id="ai-text">{plain_text}</pre>
    </div>
    
    <footer>
        Transcrito com 🎧 Whisperbox
    </footer>
    
    <script>
        function copyToClipboard() {{
            const text = document.getElementById('ai-text').textContent;
            navigator.clipboard.writeText(text).then(() => {{
                const btn = document.querySelector('.copy-btn');
                btn.textContent = '✓ Copiado!';
                btn.classList.add('copied');
                setTimeout(() => {{
                    btn.textContent = '📋 Copiar';
                    btn.classList.remove('copied');
                }}, 2000);
            }});
        }}
    </script>
</body>
</html>
'''


def format_duration(seconds: float) -> str:
    """Format seconds as human readable duration."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    if minutes > 0:
        return f"{minutes}min {secs}s"
    return f"{secs}s"


def segments_to_paragraphs(segments: list, min_pause: float = 1.5) -> list[str]:
    """
    Group segments into paragraphs based on pauses.
    
    Args:
        segments: List of Segment objects
        min_pause: Minimum pause (seconds) to start new paragraph
    
    Returns:
        List of paragraph strings
    """
    if not segments:
        return []
    
    paragraphs = []
    current_paragraph = [segments[0].text]
    
    for i in range(1, len(segments)):
        prev_end = segments[i-1].end
        curr_start = segments[i].start
        pause = curr_start - prev_end
        
        if pause >= min_pause:
            # New paragraph
            paragraphs.append(" ".join(current_paragraph))
            current_paragraph = [segments[i].text]
        else:
            current_paragraph.append(segments[i].text)
    
    # Don't forget last paragraph
    if current_paragraph:
        paragraphs.append(" ".join(current_paragraph))
    
    return paragraphs


def generate_html(result) -> str:
    """Generate HTML from TranscriptionResult."""
    from whisperbox.models import TranscriptionResult
    
    # Group into paragraphs
    paragraphs = segments_to_paragraphs(result.segments)
    
    # Build HTML content
    content_html = "\n".join(f"<p>{p}</p>" for p in paragraphs)
    
    # Plain text for AI section
    plain_text = "\n\n".join(paragraphs)
    
    # Fill template
    return HTML_TEMPLATE.format(
        title=result.filename.rsplit(".", 1)[0],
        duration=format_duration(result.duration),
        word_count=result.word_count,
        language=result.language.upper(),
        content_html=content_html,
        plain_text=plain_text,
    )
