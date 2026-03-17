import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://aoai-public-labourlaw.openai.azure.com")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

if not API_KEY:
    raise ValueError("Missing AZURE_OPENAI_API_KEY. Please set it in your .env file or environment variables.")

client = AzureOpenAI(
    azure_endpoint=ENDPOINT,
    api_key=API_KEY,
    api_version="2024-02-15-preview"
)

KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge_base")

def get_examples(max_examples=2):
    examples = []
    if not os.path.exists(KNOWLEDGE_BASE_DIR):
        return examples
    
    files = [f for f in os.listdir(KNOWLEDGE_BASE_DIR) if f.endswith(".json")]
    
    for json_file in files[:max_examples]:
        base_name = json_file[:-5]
        text_file = base_name + ".txt"
        text_path = os.path.join(KNOWLEDGE_BASE_DIR, text_file)
        json_path = os.path.join(KNOWLEDGE_BASE_DIR, json_file)
        
        if os.path.exists(text_path):
            try:
                with open(text_path, "r", encoding="utf-8") as f:
                    text_content = f.read()
                with open(json_path, "r", encoding="utf-8") as f:
                    json_content = json.load(f)
                examples.append({"text": text_content, "json": json_content})
            except Exception as e:
                print(f"Error loading example {base_name}: {e}")
                
    return examples

def save_to_knowledge_base(raw_text, structured_json, filename):
    if not os.path.exists(KNOWLEDGE_BASE_DIR):
        os.makedirs(KNOWLEDGE_BASE_DIR)
        
    base_name = os.path.splitext(os.path.basename(filename))[0]
    base_name = "".join([c if c.isalnum() or c in (" ", "_", "-") else "_" for c in base_name]).strip()
    
    text_path = os.path.join(KNOWLEDGE_BASE_DIR, f"{base_name}.txt")
    json_path = os.path.join(KNOWLEDGE_BASE_DIR, f"{base_name}.json")
    
    try:
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(raw_text)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(structured_json, f, indent=4)
        print(f"Saved extraction to knowledge base: {base_name}")
    except Exception as e:
        print(f"Error saving to knowledge base: {e}")

def structure_cv_data(raw_text):
    examples = get_examples()
    example_str = ""
    for i, ex in enumerate(examples):
        example_str += f"\n--- EXAMPLE {i+1} ---\nRAW TEXT:\n{ex['text']}\n\nOUTPUT JSON:\n{json.dumps(ex['json'], indent=2)}\n"

    system_instruction = """
    You are an expert recruitment data analyst. Your task is to extract professional information from CV text into a strict JSON format. Accuracy and completeness are paramount across ALL professional departments (Engineering, Finance, IT, Medical, Legal, Artisans, etc.).

    CRITICAL CATEGORIZATION RULES:
    1. 'course_work': Subjects/modules specifically within a formal degree/diploma (list of strings).
    2. 'courses': Independent certifications, short courses, or workshops (list of objects).
    3. 'training': General training descriptions or specialized internal programs (list of strings).
    4. 'projects': Significant professional or academic projects (list of objects).
    5. 'professional_membership': Registration with regulatory boards (ECSA, HPCSA, SAICA, etc.).

    SUB-POSITION RULE:
    - If a candidate held multiple sequential roles at the SAME company, extract EACH role as a separate entry in 'career_history' with the same company name.
    - Preserve the chronology exactly.

    CAREER HISTORY EXTRACTION:
    - Preserved EVERY detail. Do not summarize responsibilities.
    - Capture 'reason_for_leaving' and 'achievements' for each job entry.
    - If a section header like "Clinical Rotations" or "Audit Client List" appears, treat it as 'career_history' if it describes job experience, or 'projects' if it's a specific list of assignments.

    UNIVERSAL SUPPORT (IMPORTANT):
    - Many CVs have unique sections (e.g., "Publications", "Exhibitions", "Volunteer Work", "Technical Proficiencies Matrix", "Clinical Rotations").
    - If you encounter a section that doesn't fit the standard schema keys perfectly, extract it into the 'custom_sections' array.
    - Choose the most appropriate 'content_type': 'list' (bullet points), 'paragraph' (text block), or 'table' (rows and columns).

    UNIVERSAL MAPPING HINTS:
    - 'Clinical Rotations' -> If detail-heavy, map to 'career_history'. If list-like, map to 'custom_sections'.
    - 'Publications/Research' -> Map to 'custom_sections' as a list.
    - 'Professional Affiliations' -> Map to 'professional_membership'.
    - 'Exhibitions/Showcases' -> Map to 'custom_sections' as a list or table.
    """

    prompt = f"""
    Extract the professional information from the provided RAW TEXT into a valid JSON object. 
    Maintain industry-standard terminology for use in high-end recruitment.

    { "See these examples for the expected extraction quality:" if example_str else "" }
    {example_str}

    JSON SCHEMA:
    {{
      "header": {{
        "cv_of": "string",
        "position_applied": "string",
        "presented_by": "string",
        "date": "YYYY-MM-DD",
        "current_salary": "string",
        "salary_expectation": "string",
        "email": "string"
      }},
      "personal_details": {{
        "full_name": "string",
        "known_as": "string",
        "gender": "string",
        "race": "string",
        "nationality": "string",
        "residential_address": "string",
        "marital_status": "string",
        "dob": "YYYY-MM-DD",
        "drivers_license": "string",
        "notice_period": "string",
        "criminal_record": "string",
        "languages": ["string"],
        "skills": ["string"],
        "computer_literacy": "string",
        "experience_summary": "string"
      }},
      "training": ["string"],
      "courses": [
        {{
          "course_name": "string",
          "institution": "string",
          "date": "string",
          "status": "string"
        }}
      ],
      "qualifications": [
        {{
          "qualification": "string",
          "institution": "string",
          "date": "string",
          "status": "string"
        }}
      ],
      "professional_membership": [
        {{
          "board_name": "string",
          "profession": "string",
          "year": "string",
          "prof_no": "string"
        }}
      ],
      "career_highlights": ["string"],
      "course_work": ["string"],
      "projects": [
        {{
          "project_name": "string",
          "project_value": "string",
          "description": ["string"]
        }}
      ],
      "career_summary": [
        {{
          "company": "string",
          "position": "string",
          "dates": "string"
        }}
      ],
      "career_history": [
        {{
          "company": "string",
          "date": "string",
          "final_position": "string",
          "reason_for_leaving": "string",
          "responsibilities": ["string"],
          "achievements": ["string"],
          "is_current": false
        }}
      ],
      "custom_sections": [
        {{
          "section_name": "string",
          "content_type": "list | paragraph | table",
          "content": "mixed (list of strings, string, or list of objects)"
        }}
      ],
      "llm_enhanced": true
    }}

    RAW TEXT:
    {raw_text}
    """
    
    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        clean_text = response.choices[0].message.content
        return json.loads(clean_text)
    except Exception as e:
        print(f"Error extracting data: {e}")
        return {"error": str(e)}
