import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import time

# Define primary color
PRIMARY_BLUE = "#3498db"

# Set Streamlit page config
st.set_page_config(
    page_title="My Light Mode App",
    layout="wide",  # Enables wide mode
    initial_sidebar_state="expanded"
)

st.markdown(
    f"""
    <style>
        .stButton>button {{
            background-color: {PRIMARY_BLUE} !important;
            color: white !important;
            border-radius: 10px !important;
            border: none !important;
            font-size: 16px !important;
            padding: 10px 20px !important;
        }}
        .stSpinner {{
            color: {PRIMARY_BLUE} !important;
        }}
        textarea:focus {{
            border: 2px solid {PRIMARY_BLUE} !important;
            box-shadow: 0 0 5px {PRIMARY_BLUE} !important;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("MedAI")

st.markdown("""
MedAI allows you to specify your symptoms and can diagnose a disease for you.
*Note: This is only an indication for your disease and should not be used for actual medical diagnosis.*
""")

# User input for symptoms
symptoms_input = st.text_area("Enter your symptoms separated by commas:")

if st.button("Check Probable Diseases"):
    if not symptoms_input.strip():
        st.warning("Please enter at least one symptom to get a diagnosis.")
    else:
        url = 'https://disease-predictor-vol3-739437866088.europe-west1.run.app/diagnosis'
        params = {"inputs": symptoms_input}

        with st.spinner("Fetching diagnosis, please wait..."):
            time.sleep(1)  # Simulate loading effect
            try:
                res = requests.get(url, params=params)
                res.raise_for_status()
                json_data = res.json()

                # Extract diseases and probabilities from response
                predictions = json_data.get('predictions', [])
                df = pd.DataFrame(predictions)
                df.columns = ["Disease", "Probability"]

                # Convert probability to percentage
                df["Probability"] *= 100

                # Sort and select top 3 probable diseases
                df = df.sort_values(by="Probability", ascending=False).head(3)

                # Create a Plotly bar chart
                fig = px.bar(df, x="Probability", y="Disease", orientation='h',
                             title="Top 3 Probable Diseases", color="Probability")
                fig.update_layout(yaxis={'categoryorder':'total ascending'})

                # Show chart in Streamlit
                st.plotly_chart(fig)

                # Display results as a dataframe
                st.dataframe(df)

            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred while fetching data: {e}")
