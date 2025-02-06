import streamlit as st
import pandas as pd
import requests
import time

PRIMARY_BLUE = "#3498db"

def display_used_symptoms(used_symptoms):
    """Display used symptoms as tiles."""
    if used_symptoms:
        st.markdown("### Used Symptoms")
        symptom_tiles = "".join(
            [f"<span class='symptom-tile'>{symptom}</span>" for symptom in used_symptoms]
        )
        st.markdown(
            f"""
            <style>
                .symptom-tile {{
                    display: inline-block;
                    background-color: {PRIMARY_BLUE};
                    color: white;
                    padding: 8px 15px;
                    margin: 5px;
                    border-radius: 10px;
                    font-size: 14px;
                }}
            </style>
            {symptom_tiles}
            """,
            unsafe_allow_html=True,
        )

st.set_page_config(
    page_title="MedAI",
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
        url = 'https://medai-39170945173.europe-west1.run.app/diagnosis'
        params = {"inputs": symptoms_input}

        with st.spinner("Fetching diagnosis, please wait..."):
            time.sleep(1)
            try:
                res = requests.get(url, params=params)
                res.raise_for_status()
                json_data = res.json()

                used_symptoms = json_data.get("Used_Symptoms", [])
                display_used_symptoms(used_symptoms)

                predictions = json_data.get('Predictions', [])
                if not predictions:
                    st.warning("No diseases found. Try modifying your input symptoms.")

                for pred in predictions:
                    disease = pred.get("Disease", "Unknown Disease")
                    probability = pred.get("Probability", 0) * 100  # Convert to percentage
                    symptoms_dict = pred.get("Symptoms", {})

                    with st.expander(f"🦠 **{disease}** - {probability:.2f}% probability"):
                        if symptoms_dict:
                            st.markdown("### Symptoms & Probabilities")
                            symptoms_df = pd.DataFrame(
                                symptoms_dict.items(), columns=["Symptom", "Probability"]
                            ).sort_values(by="Probability", ascending=False)
                            symptoms_df["Probability"] = (symptoms_df["Probability"] * 100).round(2).astype(str) + "%"
                            st.dataframe(symptoms_df, hide_index=True)
                        else:
                            st.write("No symptom data available.")

            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred while fetching data: {e}")
