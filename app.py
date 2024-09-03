import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"
KEY = "EQq22/s2o9EaXKTJ8EFbKxfoTTuW"

def main():
    st.title("YouTube Video Repurposer")
    
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

                    st.success("Congratulations, the Summary and Thread were generated!")

                    # Layout with two columns
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("Summary")
                        st.write(summary)

                    with col2:
                        st.markdown(
                            """
                            <div style="background-color: #f0f8ff; padding: 10px;">
                                <h3>Twitter Thread</h3>
                                <p>{}</p>
                            </div>
                            """.format(thread),
                            unsafe_allow_html=True
                        )

                else:
                    st.error(f"Error: {response.json().get('error', 'Unknown error occurred')}")
        else:
            st.warning("Please enter a YouTube URL")

if __name__ == "__main__":
    main()

# TO RUN THE STREAMLIT APP
# streamlit run app.py
