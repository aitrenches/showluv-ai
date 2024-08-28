import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"
KEY = "EQq22/s2o9EaXKTJ8EFbKxfoTTuW" 

def main():
    st.title("YouTube Transcript Summarizer & X Thread Generator")
    
    youtube_url = st.text_input("Enter YouTube Video URL")
    
    if st.button("Get Summary"):
        if youtube_url:
            with st.spinner("Processing..."):
                headers = {
                    "X-API-KEY": KEY
                }
                response = requests.post(
                    f"{BACKEND_URL}/api/generate-summary/",
                    json={"youtube_url": youtube_url},
                    headers=headers
                )
                if response.status_code == 200:
                    data = response.json()
                    summary = data.get('message', 'No summary available')
                    thread = data.get('thread', 'No thread available')

                    st.success("Summary generated!")
                    st.write("### Summary")
                    st.write(summary)

                    st.write("### Twitter Thread")
                    if thread:
                        # Display the thread
                        st.write(thread)
                    else:
                        st.write("No thread available.")
                else:
                    st.error(f"Error: {response.json().get('error', 'Unknown error occurred')}")
        else:
            st.warning("Please enter a YouTube URL")

if __name__ == "__main__":
    main()

# TO RUN THE STREAMLIT APP
# streamlit run app.py