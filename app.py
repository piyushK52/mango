import os
import streamlit as st
import tempfile
from subtitle_processor import parse_subtitle_file
from video_generator import generate_video

st.set_page_config(page_title="Subtitle Video Generator", layout="wide")

st.title("Subtitle Video Generator")
st.write("Upload a subtitle file to generate a video with transparent background")

# File uploader
uploaded_file = st.file_uploader("Choose a subtitle file", type=["srt", "vtt"])

if uploaded_file is not None:
    # Save the uploaded file to a temporary location
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, uploaded_file.name)
    
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
        
        # Video settings
        st.subheader("Video Settings")
        
        col1, col2, col3 = st.columns(3)
        
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
            
        # Video generation
        if st.button("Generate Video"):
            with st.spinner("Generating video..."):
                try:
                    output_path = os.path.join(temp_dir, "output.mp4")
                    result = generate_video(
                        subtitles=subtitles,
                        output_path=output_path,
                        settings={
                            "font_name": font_name,
                            "font_size": font_size,
                            "font_color": font_color
                        }
                    )
                    
                    if result["success"]:
                        # Provide download link
                        with open(output_path, "rb") as file:
                            st.download_button(
                                label="Download Video",
                                data=file,
                                file_name="output_video.mp4",
                                mime="video/mp4"
                            )
                        st.success("Video generated successfully!")
                    else:
                        st.error(f"Error generating video: {result['message']}")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
    else:
        st.error("Failed to parse subtitle file. Please check the format.")