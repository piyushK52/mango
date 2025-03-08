import os
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont
import shutil

# Replace the textsize method with textbbox
# Update the generate_frames function to handle empty subtitles
def generate_frames(subtitles, output_dir, settings):
    """Generate frames with subtitles on transparent background"""
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Clear existing files in the output directory
        for file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        
        # Get frame width and height
        width = settings.get('width', 1920)
        height = width  # Square aspect ratio
        
        # Create a transparent image
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        
        # Try to load the font
        try:
            font_size = settings.get('font_size', 24)
            # Scale font size based on width
            scaled_font_size = int(font_size * width / 1920)
            font = ImageFont.truetype(settings.get('font_name', 'Arial'), scaled_font_size)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Convert hex color to RGB
        font_color_hex = settings.get('font_color', 'FFFFFF')
        r = int(font_color_hex[0:2], 16)
        g = int(font_color_hex[2:4], 16)
        b = int(font_color_hex[4:6], 16)
        font_color = (r, g, b, 255)  # Full opacity
        
        # Generate a sample frame for preview
        preview_image = image.copy()
        draw = ImageDraw.Draw(preview_image)
        sample_text = "Sample Subtitle Text"
        
        # Use textbbox instead of textsize
        left, top, right, bottom = draw.textbbox((0, 0), sample_text, font=font)
        text_width = right - left
        text_height = bottom - top
        
        position = ((width - text_width) // 2, height - text_height - 50)
        draw.text(position, sample_text, font=font, fill=font_color)
        preview_path = os.path.join(output_dir, "preview.png")
        preview_image.save(preview_path)
        
        # Generate frames for each subtitle
        frame_count = 0
        for sub in subtitles:
            # Calculate how many frames this subtitle needs
            start_time = sub['start_seconds']
            end_time = sub['end_seconds']
            duration = end_time - start_time
            
            # Generate 1 frame per 0.1 seconds (10 fps)
            num_frames = int(duration * 10)
            
            for i in range(num_frames):
                frame = image.copy()
                
                # Only draw text if the subtitle text is not empty
                if sub['text'].strip():
                    draw = ImageDraw.Draw(frame)
                    
                    # Calculate text position (centered horizontally, near bottom vertically)
                    left, top, right, bottom = draw.textbbox((0, 0), sub['text'], font=font)
                    text_width = right - left
                    text_height = bottom - top
                    
                    position = ((width - text_width) // 2, height - text_height - 50)
                    
                    # Draw text
                    draw.text(position, sub['text'], font=font, fill=font_color)
                
                # Save frame (even if it's blank)
                frame_path = os.path.join(output_dir, f"frame_{frame_count:06d}.png")
                frame.save(frame_path)
                frame_count += 1
        
        return {
            "success": True,
            "message": f"Generated {frame_count} frames successfully",
            "preview_path": preview_path,
            "frame_count": frame_count,
            "output_dir": output_dir
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

def create_preview(text, output_path, settings):
    """Create a preview image with the given text and settings"""
    try:
        # Get frame width and height
        width = settings.get('width', 1920)
        height = width  # Square aspect ratio
        
        # Create a transparent image
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Try to load the font
        try:
            font_size = settings.get('font_size', 24)
            # Scale font size based on width
            scaled_font_size = int(font_size * width / 1920)
            font = ImageFont.truetype(settings.get('font_name', 'Arial'), scaled_font_size)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Convert hex color to RGB
        font_color_hex = settings.get('font_color', 'FFFFFF')
        r = int(font_color_hex[0:2], 16)
        g = int(font_color_hex[2:4], 16)
        b = int(font_color_hex[4:6], 16)
        font_color = (r, g, b, 255)  # Full opacity
        
        # Calculate text position (centered horizontally, near bottom vertically)
        # Use textbbox instead of textsize
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        text_width = right - left
        text_height = bottom - top
        
        position = ((width - text_width) // 2, height - text_height - 50)
        
        # Draw text
        draw.text(position, text, font=font, fill=font_color)
        
        # Save image
        image.save(output_path)
        
        return {
            "success": True,
            "path": output_path
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

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