Check out the Streamlit frontend here: https://energy-forecaster.streamlit.app

---

# **Energy Consumption Forecaster**

## **Overview**
Welcome to the **Energy Consumption Forecaster**, a tool designed to analyze and forecast energy consumption for residential estates using Photrek's Risk-Aware Assessment Service. This application was built for the **SingularityNET Platform Hackathon**, leveraging the SingularityNET SDK to integrate Photrek’s robust metrics: **Accuracy**, **Decisiveness**, and **Robustness**.

By providing probabilistic forecasts for energy consumption, this tool empowers users with actionable insights into energy usage patterns, helping them make informed decisions about energy efficiency and management.

---

## **Core Features**
1. **Streamlit Frontend**:
   - Upload a CSV file containing probabilistic energy forecasts.
   - View visualizations of the input data and results.
   - Receive detailed metrics, including Accuracy, Decisiveness, and Robustness.
   - Access a dynamically generated chart based on Photreks assessment.

2. **Django Backend**:
   - Processes uploaded CSV files and prepares them for Photrek's service.
   - Validates API keys for secure access.
   - Interacts with Photrek’s Risk-Aware Assessment Service via the SingularityNET SDK.
   - Returns metrics and a base64-encoded image for visualization.

---

## **How It Works**
### **Frontend (Streamlit)**

The Streamlit app serves as the primary interface:
- Users upload a CSV file formatted to Photrek's requirements (no headers, N probability columns, and one outcome column).
- The app validates the input, communicates with the Django backend, and visualizes the results.

### **Backend (Django)**
The Django backend powers the analysis workflow:
1. **Authentication**: API keys are validated before any processing occurs.
2. **File Ingestion**: Uploaded CSV files are read and transformed into a base64-encoded string required by Photrek's service.
3. **Integration with Photrek**: Using the SingularityNET SDK, the backend sends the processed data to Photrek's `adr` method and retrieves the results.
4. **Protobuf Serialization**: The response from Photrek (in Protobuf format) is deserialized into JSON for consumption by the Streamlit app.
5. **Result Metrics**:
   - **Accuracy**: Evaluates how well the forecast matches actual outcomes.
   - **Decisiveness**: Assesses decision-making confidence.
   - **Robustness**: Measures performance in low-probability scenarios.

---

## **Key Components**

### **1. `streamlit/energy_forecaster.py`**
- Handles the Streamlit frontend.
- Allows users to:
  - Input an API key.
  - Upload a CSV file for analysis.
  - View the results, including:
    - Key metrics (Accuracy, Decisiveness, Robustness).
    - The number of rows and columns processed.
    - A dynamically generated chart visualizing probabilities.

### **2. `backend/views.py`**
- Contains the `EnergyForecastAPI` Django class-based view.
- Key functionalities:
  - Validates API keys using custom middleware.
  - Ingests and processes CSV files with the `ingest_csv` function.
  - Interacts with the SingularityNET SDK to call Photrek’s service.
  - Returns a JSON response with metrics and visualization data.

---

## **Folder Structure**
```
project/
├── backend/
│   ├── views.py                # Django backend logic
│   ├── urls.py                 # API routing
│   └── settings.py             # Django settings, including API key configurations
├── streamlit/
│   ├── energy_forecaster.py    # Streamlit app frontend
│   └── assets/                 # Contains any images or static files
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
└── manage.py                   # Django project entry point
```

---

## **Technologies Used**
1. **Frontend**:
   - [Streamlit](https://streamlit.io/): Interactive Python-based web app framework.
2. **Backend**:
   - [Django](https://www.djangoproject.com/): Web framework for backend logic and API development.
   - [SingularityNET SDK](https://github.com/singnet): For integrating Photrek’s service.
3. **Data Visualization**:
   - [Altair](https://altair-viz.github.io/): For generating probability distribution charts.
   - [Matplotlib](https://matplotlib.org/): For additional visualizations.

---

## **How to Set Up**
### **Prerequisites**
- Python 3.12 or higher
- pip (Python package manager)

### **1. Clone the Repository**
```bash
git clone https://github.com/aitrenches/showluv-ai
cd showluv-ai
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Set Up Environment Variables**
- Create a `.env` file in the project root:
  ```bash
  DJANGO_SECRET_KEY=<your_secret_key>
  API_URL=<your_photrek_service_endpoint>
  API_KEY=<your_photrek_api_key>
  PRIVATE_KEY=13c6f1eb3d45cd8b...
  INFURA_KEY=ea8b3576878979756f533f...
  ```

- Add the following to `secrets.toml` for Streamlit:
  ```toml
  API_URL = "<the_django_backend_url>"
  API_KEY = "<the_backend_api_key>"
  ```

### **4. Run the Backend**
Start the Django backend:
```bash
python manage.py runserver
```

### **5. Run the Frontend**
Launch the Streamlit app:
```bash
streamlit run streamlit/energy_forecaster.py
```
### **6. Try out the API**
You can try out the API using the `test_energy_forecast_api.py`
```bash
python test_energy_forecast_api.py
```

---

## **Contributing**
Contributions are welcome! 😊 Feel free to fork the repository, submit pull requests, or raise issues.

---