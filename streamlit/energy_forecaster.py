import streamlit as st
import pandas as pd
import numpy as np
import requests
import altair as alt
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import environ

env = environ.Env()
environ.Env.read_env()

# API_URL = st.secrets["API_URL"]
# API_KEY = st.secrets["API_KEY"]

API_URL = "https://djangoapp.vveeq17939eno.us-east-2.cs.amazonlightsail.com/snet/energy-forecast/"
API_KEY = "EQq22/s2o9EaXKTJ8EFbKxfoTTuW"

headers = {
    "X-API-KEY": API_KEY
}

# Streamlit App Configuration
st.set_page_config(
    page_title="kWh Energy Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Header and Banner
st.markdown("""
<style>
    .main-header {
        background-color: #4CAF50;
        color: white;
        padding: 20px;
        text-align: center;
        border-radius: 5px;
    }
    .sub-header {
        color: #4CAF50;
        text-align: center;
        margin-bottom: 30px;
    }
</style>
<div class="main-header">
    <h1>⚡ Energy Forecaster</h1>
    <p>Analyze and Forecast Your Energy Consumption</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<h3 class="sub-header">Upload Your Data and Explore Insights</h3>', unsafe_allow_html=True)

st.sidebar.title("Navigation")
menu = st.sidebar.radio("Select Page", ["🔍 Analyze Data", "📊 Insights & Trends"])

# Sidebar Animation
st.sidebar.title("Quick Stats")
scrolling_text = """
Energy Insights:
- Average consumption: 32 kWh/day
- Peak usage: 65 kWh (at 6 PM)
- Forecast Accuracy: 94%
"""
st.sidebar.info(scrolling_text)

# Main Layout
# tab1, tab2 = st.tabs(["🔍 Analyze Data", "📊 Insights & Trends"])

# File Upload Page
if menu == "🔍 Analyze Data":
    st.header("Upload and Analyze")
    uploaded_file = st.file_uploader(
        "Upload a CSV file (no header, probabilities, and true class)",
        type=["csv"],
    )
    
    if uploaded_file:
        try:
            # Read and display the CSV file
            data = pd.read_csv(uploaded_file, header=None)

            # Assign meaningful column names
            feature_columns = [f"Feature {i+1}" for i in range(data.shape[1] - 1)]
            label_column = "Label"
            data.columns = feature_columns + [label_column]

            # Create two columns to display data side by side
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Uploaded Data Preview")
                st.dataframe(data.head())  # Show the first 5 rows

            with col2:
                st.subheader("Summary Statistics")
                st.write(data.describe())  # Display summary statistics

            # Extract the number of features and rows
            num_rows, num_columns = data.shape
            st.write(f"The dataset contains **{num_rows} rows** and **{num_columns} columns**.")
            
            # Assign meaningful column names
            feature_columns = [f"Feature {i+1}" for i in range(num_columns - 1)]
            label_column = "Label"
            data.columns = feature_columns + [label_column]

            # Visualize the distribution of the features
            st.subheader("Feature Distributions")
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.histplot(data.iloc[:, :-1].values.flatten(), kde=True, ax=ax, bins=30, color="blue")
            ax.set_title("Distribution of Feature Values")
            ax.set_xlabel("Feature Value")
            ax.set_ylabel("Frequency")
            st.pyplot(fig)

            # Class distribution visualization
            st.subheader("Class Distribution")
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.countplot(x=data[label_column], ax=ax, legend=False)
            ax.set_title("Class Distribution in the Dataset")
            ax.set_xlabel("Class")
            ax.set_ylabel("Count")
            st.pyplot(fig)

            # Correlation heatmap
            st.subheader("Correlation Heatmap")
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(data.iloc[:, :-1].corr(), annot=True, cmap="coolwarm", ax=ax)
            ax.set_title("Correlation Matrix of Features")
            st.pyplot(fig)

            # Text analysis and insights
            st.subheader("Insights")
            st.markdown(f"""
            - The dataset contains **{num_rows} rows** and **{num_columns} columns**, where the last column represents class labels.
            - The feature values are numeric and typically range between 0 and 1.
            - The dataset is balanced with approximately equal representation of the different classes, as observed in the class distribution plot.
            - The correlation heatmap helps identify relationships between features, which could influence the prediction of the class labels.
            """)

            # Banner and Button Styles
            st.markdown("""
            <style>
                .banner {
                    background-color: #4CAF50;  /* Green color matching the header */
                    color: white;
                    padding: 10px;
                    text-align: center;
                    border-radius: 5px;
                    margin-bottom: 20px;  /* Space below the banner */
                }
                .center-button {
                    display: flex;
                    justify-content: center;
                    margin-top: 20px;
                }
                button[data-baseweb="button"] {
                    width: 300px;  /* Button width */
                    font-size: 16px;
                    font-weight: bold;
                    background-color: #4CAF50 !important;  /* Match the banner green */
                    color: white !important;
                    border: none;
                    border-radius: 10px;
                    height: 50px;
                }
                button[data-baseweb="button"]:hover {
                    background-color: #45a049 !important;  /* Slightly darker green for hover */
                }
            </style>
            <div class="banner">
                <h2>We can further analyze the forecasts using Photrek's Risk Assessment Tool.</h2>
            </div>
            """, unsafe_allow_html=True)
            
            # Centralized Button
            st.markdown('<div class="center-button">', unsafe_allow_html=True)
            if st.button("Analyze Forecast"):
                with st.spinner("Processing..."):
                    # Send the POST request to the API with the uploaded file
                    uploaded_file.seek(0)
                    response = requests.post(
                        API_URL,
                        files={"file": uploaded_file},  # Ensure this is the file object
                        headers=headers,
                    )

                    if response.status_code == 200:
                        st.success("Analysis Complete!")

                        # Parse the JSON response
                        result = response.json()

                        # Extract response fields
                        a = result.get("a", 0)  # Accuracy
                        d = result.get("d", 0)  # Decisiveness
                        r = result.get("r", 0)  # Robustness
                        img = result.get("img", None)  # Base64-encoded image
                        numr = result.get("numr", 0)  # Number of rows processed
                        numc = result.get("numc", 0)  # Number of columns processed

                        # Display results summary
                        st.header("Risk Aware Assessment Results")
                        st.markdown(f"""
                        Results computed from processing `{numr} records`, each having probabilities for `{numc - 1} categories`.
                        """)

                        # Metric descriptions
                        st.markdown(f"""
                        ---------------------------------
                        **Accuracy:** **{a:.4f}**
                        `Accuracy` metric is consistent with the log score of information theory and is computed by the geometric mean (which is the zeroth power of the generalized mean) of the probabilities.

                        
                        **Decisiveness:** **{d:.4f}**
                        `Decisiveness` is measured by the arithmetic mean, closely related to the classification performance of an algorithm.

                        
                        **Robustness:** **{r:.4f}**
                        The `Robustness` metric evaluates the performance of poor forecasts with low probabilities using a -2/3rds generalized-mean.
                        """)

                        # Display image if present
                        if img:
                            st.subheader("Generated Chart")
                            decoded_img = base64.b64decode(img)  # Decode the Base64 string
                            st.image(decoded_img, caption="Generated Image", use_container_width=True)

                        # Additional Information
                        st.subheader("Additional Information")
                        st.write(f"Number of Rows Processed: {numr}")
                        st.write(f"Number of Columns Processed: {numc}")

                    else:
                        st.error(f"Response Code: {response.status_code} Error: {response.content}")

            st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error reading file: {e}")

    st.subheader("Energy Tips")
    st.markdown("""
    - **Optimize appliances**: Use energy-efficient appliances.
    - **Peak hour usage**: Avoid peak hours to save on costs.
    - **Smart thermostats**: Manage energy better with smart tools.
    """)

# Metrics Overview Page
if menu == "📊 Insights & Trends":
    st.header("Forecast Trends")
    # Example Data
    trend_data = pd.DataFrame({
        "Day": pd.date_range("2024-01-01", periods=30),
        "Consumption (kWh)": np.random.randint(20, 60, size=30)
    })

    st.line_chart(trend_data.set_index("Day"))
    st.subheader("Energy Tips")
    st.markdown("""
    - **Optimize appliances**: Use energy-efficient appliances.
    - **Peak hour usage**: Avoid peak hours to save on costs.
    - **Smart thermostats**: Manage energy better with smart tools.
    """)

# Footer
st.markdown("""
<div style="text-align: center; padding: 10px; font-size: 12px;">
    Built with ❤️ for the SingularityNET Hackathon - Empowering Energy Solutions
</div>
""", unsafe_allow_html=True)
