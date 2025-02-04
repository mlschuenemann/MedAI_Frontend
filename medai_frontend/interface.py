import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import time


PRIMARY_BLUE = "#3498db"

st.set_page_config(
    page_title="MedAI",
    layout="wide",
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


symptoms_input = st.text_area("Enter your symptoms separated by commas:")

if st.button("Check Probable Diseases"):
    if not symptoms_input.strip():
        st.warning("Please enter at least one symptom to get a diagnosis.")
    else:
        url = 'https://disease-predictor-vol2-39170945173.europe-west1.run.app/diagnosis'
        params = {"inputs": symptoms_input}

        with st.spinner("Fetching diagnosis, please wait..."):
            time.sleep(1)
            try:
                res = requests.get(url, params=params)
                res.raise_for_status()
                json_data = res.json()


                predictions = json_data.get('Predictions', [])

                df = pd.DataFrame([{ "Disease": p["Disease"], "Probability": p["Probability"] * 100} for p in predictions])


                df = df.sort_values(by="Probability", ascending=False).head(3)


                fig = px.bar(df, x="Probability", y="Disease", orientation='h',
                             title="Top 3 Probable Diseases", color="Probability")
                fig.update_layout(yaxis={'categoryorder':'total ascending'})


                st.plotly_chart(fig)


                st.dataframe(df)


                st.subheader("Symptoms contributing to top diseases")
                for index, row in df.iterrows():
                    disease_name = row["Disease"]
                    symptoms_data = next((p["Symptoms"] for p in predictions if p["Disease"] == disease_name), {})
                    symptoms_df = pd.DataFrame(symptoms_data.items(), columns=["Symptom", "Probability"])
                    symptoms_df["Probability"] *= 100
                    symptoms_df = symptoms_df.sort_values(by="Probability", ascending=False)
                    st.write(f"**{disease_name}**")
                    st.dataframe(symptoms_df)

            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred while fetching data: {e}")
