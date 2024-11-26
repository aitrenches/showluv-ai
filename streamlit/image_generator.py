import os
import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import base64
import environ

env = environ.Env()
environ.Env.read_env()

# Django API URL
API_URL = env("API_URL")
API_KEY = env("API_KEY")

headers = {
    "X-API-KEY": API_KEY
}

st.title('Image Generator')

# Create two columns for input type and image size slider
col1, col2 = st.columns(2)

with col1:
    # Prompt input for text generation
    prompt = st.text_input("Enter a prompt to generate images:")

with col2:
    # Image size selection as a slider with labels
    size_options = ['256x256', '512x512', '1024x1024']
    size_idx = st.slider("Choose Image Size (256x256, 512x512, 1024x1024):", min_value=0, max_value=2, value=2)
    size = size_options[size_idx]  # Get the selected size from the index

# Button to generate images
if st.button("Generate Images"):
    if prompt:
        with st.spinner("Processing Images..."):
            # Sending request with prompt
            payload = {"prompt": prompt}
            response = requests.post(f"{API_URL}{size}/", headers=headers, json=payload)

            # Handle API response
            if response.status_code == 200:
                image_data = response.json().get('images', [])
                if image_data:
                    # Display the generated images and provide download links
                    for i, img_data in enumerate(image_data):
                        img_bytes = base64.b64decode(img_data)
                        image = Image.open(BytesIO(img_bytes))

                        # Display image
                        st.image(image, caption=f"Generated Image {i + 1}", use_column_width=True)

                        # Create a download button for the image
                        buffered = BytesIO()
                        image.save(buffered, format="PNG")
                        buffered.seek(0)
                        b64 = base64.b64encode(buffered.read()).decode()
                        download_link = f"data:file/png;base64,{b64}"
                        
                        # Center the button and style it with modern design
                        st.markdown(
                        f"""
                        <div style="display: flex; flex-direction: column; align-items: center; margin-bottom: 20px;">
                            <a href="{download_link}" download="generated_image_{i + 1}.png" style="text-decoration: none;">
                                <button style="
                                    padding: 12px 24px;
                                    font-size: 16px;
                                    cursor: pointer;
                                    border: none;
                                    border-radius: 8px;
                                    background-color: #ADD8E6;
                                    color: black;
                                    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
                                    transition: background-color 0.3s ease;
                                " onmouseover="this.style.backgroundColor='#45a049'" onmouseout="this.style.backgroundColor='#4CAF50'">
                                    Download Image {i + 1}
                                </button>
                            </a>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.error("No image data returned from API!")
            else:
                st.error(f"Error from API: {response.status_code} - {response.text}")
    else:
        st.error("Please enter a valid prompt!")
