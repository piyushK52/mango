import os
import subprocess
import tempfile

def generate_video(subtitles, output_path, settings):
    """Generate video with subtitles on transparent background using FFmpeg"""
    try:
        # Create a temporary SRT file
        temp_srt = tempfile.NamedTemporaryFile(suffix='.srt', delete=False)
        temp_srt_path = temp_srt.name
        
        with open(temp_srt_path, 'w', encoding='utf-8') as f:
            for i, sub in enumerate(subtitles):
                f.write(f"{i+1}\n")
                f.write(f"{sub['start_time']} --> {sub['end_time']}\n")
                f.write(f"{sub['text']}\n\n")
        
        # Calculate video duration based on the last subtitle end time
        if subtitles:
            duration = max(sub['end_seconds'] for sub in subtitles) + 1  # Add 1 second buffer
        else:
            duration = 5  # Default duration if no subtitles
        
        # Prepare FFmpeg command
        font_color_hex = settings['font_color']
        # Convert hex to FFmpeg compatible format
        r = int(font_color_hex[0:2], 16)
        g = int(font_color_hex[2:4], 16)
        b = int(font_color_hex[4:6], 16)
        
        # Escape special characters in font name
        font_name = settings['font_name'].replace(' ', '\\ ')
        
        # Build FFmpeg command
        cmd = [
            'ffmpeg',
            '-y',  # Overwrite output file if it exists
            '-f', 'lavfi',
            '-i', f'color=color=black@0.0:size=1920x1080:rate=30',
            '-t', str(duration),
            '-vf', f"subtitles={temp_srt_path}:force_style='FontName={font_name},FontSize={settings['font_size']},PrimaryColour=&H{font_color_hex},BorderStyle=4'",
            '-c:v', 'libx264',
            '-pix_fmt', 'yuva420p',
            '-preset', 'ultrafast',
            output_path
        ]
        
        # Run FFmpeg
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        # Clean up temporary file
        os.unlink(temp_srt_path)
        
        if process.returncode != 0:
            return {
                "success": False,
                "message": f"FFmpeg error: {process.stderr}"
            }
        
        return {
            "success": True,
            "message": "Video generated successfully",
            "path": output_path
        }
    
    except Exception as e:
        # Clean up temporary file if it exists
        if 'temp_srt_path' in locals() and os.path.exists(temp_srt_path):
            os.unlink(temp_srt_path)
        
        return {
            "success": False,
            "message": str(e)
        }