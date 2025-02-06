import streamlit as st
import pandas as pd
import requests
import time
import google.generativeai as genai
#from gemini_api import extract_symptoms_gemini

def extract_symptoms_gemini(symptom_description, API_KEY):
    """
    Extracts a list of symptoms from free-text description using the Gemini API.

    Args:
        symptom_description: The user's free-text description of symptoms.

    Returns:
        A list of extracted symptoms (strings), or None if there's an error.
        Returns an empty list if no symptoms are found.
    """
    try:
      genai.configure(api_key=API_KEY) # configure API key
      prompt = f"""
      Extract a list of individual symptoms from the following text.
      Return the symptoms as a comma-separated list, without new line at the end of the string. If no symptoms are found, return None.

      Text:
      {symptom_description}
      """
      model = genai.GenerativeModel("gemini-1.5-flash")# Or another suitable Gemini model
      response = model.generate_content(prompt)

      return response.text.strip()

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return None

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

API_KEY = st.secrets["API_KEY"]

symptoms_description = st.text_area("Describe your symptoms:")

if st.button("Check Diseases"):
    if not symptoms_description.strip():
        st.warning("Please enter a description of your symptoms.")
    else:
        extracted_symptoms = extract_symptoms_gemini(symptoms_description, API_KEY)
        if extracted_symptoms:
            #st.write(f"Extracted Symptoms: {extracted_symptoms}")
            url = 'https://medai-39170945173.europe-west1.run.app/diagnosis'
            params = {"inputs": extracted_symptoms}

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
