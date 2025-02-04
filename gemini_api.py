import google.generativeai as genai


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

#### for testing
symptom_description=input("How do you feel today?\n")
API_KEY=input("Enter your Google Genai API key\n")
print(extract_symptoms_gemini(symptom_description, API_KEY))
