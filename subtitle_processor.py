import re
from datetime import datetime

def parse_srt_time(time_str):
    """Convert SRT time format to seconds"""
    hours, minutes, seconds = time_str.replace(',', '.').split(':')
    return float(hours) * 3600 + float(minutes) * 60 + float(seconds)

def format_time(seconds):
    """Format seconds to HH:MM:SS.mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}".replace('.', ',')

def parse_subtitle_file(file_path):
    """Parse SRT or VTT subtitle file"""
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        content = file.read()
    
    # Determine file type based on content
    if 'WEBVTT' in content:
        return parse_vtt(content)
    else:
        return parse_srt(content)

def parse_srt(content):
    """Parse SRT format subtitles"""
    subtitles = []
    
    # Split by double newline to get subtitle blocks
    blocks = re.split(r'\n\n+', content.strip())
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 2:  # Changed from 3 to 2 to include empty subtitles
            # Skip the index line
            time_line = lines[1] if '-->' in lines[1] else lines[0]
            
            # Get text (might be empty)
            text = ''
            if len(lines) > 2 and not '-->' in lines[2]:
                text = ' '.join(lines[2:])
            
            # Parse time line
            time_match = re.match(r'(\d+:\d+:\d+,\d+)\s*-->\s*(\d+:\d+:\d+,\d+)', time_line)
            if time_match:
                start_time = parse_srt_time(time_match.group(1))
                end_time = parse_srt_time(time_match.group(2))
                
                subtitles.append({
                    'start_time': format_time(start_time),
                    'end_time': format_time(end_time),
                    'start_seconds': start_time,
                    'end_seconds': end_time,
                    'text': text
                })
    
    return subtitles

def parse_vtt(content):
    """Parse WebVTT format subtitles"""
    subtitles = []
    
    # Remove WEBVTT header
    content = re.sub(r'^WEBVTT.*\n', '', content)
    
    # Split by double newline to get subtitle blocks
    blocks = re.split(r'\n\n+', content.strip())
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 2:  # Valid subtitle block has at least 2 lines
            # Find the time line
            time_line_index = -1
            for i, line in enumerate(lines):
                if '-->' in line:
                    time_line_index = i
                    break
            
            if time_line_index != -1:
                time_line = lines[time_line_index]
                text = ' '.join(lines[time_line_index + 1:])
                
                # Parse time line
                time_match = re.match(r'(\d+:\d+:\d+\.\d+)\s*-->\s*(\d+:\d+:\d+\.\d+)', time_line)
                if time_match:
                    start_time = parse_srt_time(time_match.group(1))
                    end_time = parse_srt_time(time_match.group(2))
                    
                    subtitles.append({
                        'start_time': format_time(start_time),
                        'end_time': format_time(end_time),
                        'start_seconds': start_time,
                        'end_seconds': end_time,
                        'text': text
                    })
    
    return subtitles