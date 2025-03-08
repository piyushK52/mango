import os
import streamlit as st
import tempfile
from subtitle_processor import parse_subtitle_file
from video_generator import generate_frames, create_preview
import shutil
from PIL import Image

st.set_page_config(page_title="Subtitle Frame Generator", layout="wide")

st.title("Subtitle Frame Generator")
st.write("Upload a subtitle file to generate frames with transparent background")

# Create temp directory for preview images
temp_dir = tempfile.mkdtemp()
preview_path = os.path.join(temp_dir, "preview.png")

# File uploader
uploaded_file = st.file_uploader("Choose a subtitle file", type=["srt", "vtt"])

if uploaded_file is not None:
    # Save the uploaded file to a temporary location
    temp_file_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_file_dir, uploaded_file.name)
    
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Parse the subtitle file
    subtitles = parse_subtitle_file(temp_path)
    
    if subtitles:
        st.success(f"Successfully loaded {len(subtitles)} subtitles")
        
        # Display subtitle preview
        st.subheader("Subtitle Preview")
        preview_df = [(i+1, f"{sub['start_time']}", f"{sub['end_time']}", sub['text']) 
                     for i, sub in enumerate(subtitles[:10])]
        
        if len(subtitles) > 10:
            st.write(f"Showing first 10 of {len(subtitles)} subtitles")
        
        st.table({
            "#": [item[0] for item in preview_df],
            "Start": [item[1] for item in preview_df],
            "End": [item[2] for item in preview_df],
            "Text": [item[3] for item in preview_df]
        })
        
        # Frame settings
        st.subheader("Frame Settings")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            font_name = st.selectbox(
                "Font",
                ["Arial", "Helvetica", "Times New Roman", "Courier New", "Verdana", "Georgia"]
            )
        
        with col2:
            font_size = st.slider("Font Size", 12, 72, 24)
        
        with col3:
            font_color = st.color_picker("Font Color", "#FFFFFF")
            # Convert from hex to RGB
            font_color = font_color.lstrip('#')
            
        with col4:
            width = st.number_input("Width (px)", min_value=480, max_value=3840, value=1080, step=120)
        
        # Settings for preview
        settings = {
            "font_name": font_name,
            "font_size": font_size,
            "font_color": font_color,
            "width": width
        }
        
        # Create a preview with sample text
        sample_text = "Preview: " + (subtitles[0]['text'] if subtitles else "Sample Text")
        preview_result = create_preview(sample_text, preview_path, settings)
        
        # Update the preview display to use a fixed size
        if preview_result["success"]:
            st.subheader("Preview")
            
            # Create a column with fixed width for the preview
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                # Add CSS for border
                st.markdown("""
                <style>
                .img-container {
                    border: 3px solid #ff4b4b;
                    border-radius: 5px;
                    padding: 5px;
                    display: inline-block;
                    background-color: rgba(0, 0, 0, 0.1);
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Convert image to base64 for HTML display
                import base64
                with open(preview_path, "rb") as img_file:
                    img_str = base64.b64encode(img_file.read()).decode()
                
                # Display image with border using HTML
                st.markdown(f"""
                <div class="img-container">
                    <img src="data:image/png;base64,{img_str}" width="300">
                </div>
                <p style="text-align: center; font-size: 0.8em; color: gray;">Preview of subtitle appearance</p>
                """, unsafe_allow_html=True)
                
                # Original image display code is replaced by the HTML version above
                # st.image(
                #     preview_path, 
                #     caption="Preview of subtitle appearance", 
                #     width=300
                # )

            with col3:
                # In the frame generation section, ensure the zip file is properly created and downloaded:
                if st.button("Generate Frames"):
                    with st.spinner("Generating frames..."):
                        try:
                            # Create output directory
                            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output_frames")
                            
                            result = generate_frames(
                                subtitles=subtitles,
                                output_dir=output_dir,
                                settings=settings
                            )

                        except Exception as e:
                            st.error(f"An error occurred: {str(e)}")
    else:
        st.error("Failed to parse subtitle file. Please check the format.")

# Clean up temp directory when the app is closed
def cleanup():
    if 'temp_dir' in locals() and os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    if 'temp_file_dir' in locals() and os.path.exists(temp_file_dir):
        shutil.rmtree(temp_file_dir)

# Register the cleanup function
import atexit
atexit.register(cleanup)