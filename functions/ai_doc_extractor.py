import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ai_resume_extractor(text):
    """
    Uses an LLM to extract structured résumé info when rule-based extraction fails.
    """
    prompt = f"""
    You are an expert résumé parser. Extract the following fields from the given text:
    - Full name
    - Email
    - Phone number
    - Education (degrees, institutions, and dates)
    - Work Experience (roles, companies, and years)
    - Skills (comma-separated list)
    - Awards or notable achievements (if available)

    Return a valid JSON with this structure:
    {{
        "name": "",
        "email": "",
        "phone": "",
        "education": [],
        "experience": [],
        "skills": [],
        "awards": []
    }}

    Resume text:
    {text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are a résumé extraction assistant."},
                  {"role": "user", "content": prompt}],
        temperature=0.1
    )

    try:
        import json
        content = response.choices[0].message.content.strip()
        return json.loads(content)
    except Exception as e:
        print("AI extraction failed:", e)
        return None
