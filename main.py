import json
import os
import sys
import copy

                                         
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extract_text import universal_extractor
from srt import structure_cv_data


def get_nested_value(d, path, default=""):
    curr = d
    try:
        for key in path.split("."):
            if isinstance(curr, dict):
                curr = curr.get(key, {})
            else:
                return default
                                                                                   
        return curr if curr else default
    except Exception:
        return default

def group_career_history_by_company(history):
    if not history:
        return []
    
    grouped = []
    company_map = {}                                   
    
    def sanitize_company(name):
        import re
        if not name:
            return ""
        name = str(name).strip().upper()
                                                                                                   
        name = re.sub(r"\(.*?\)", "", name)
        name = re.split(r"[-–—,;\|\\/]", name)[0].strip()

                                                          
        for suffix in [" PTY LTD", " PTY", " LTD", " INC", " CO", " CORP", " LIMITED"]:
            if name.endswith(suffix):
                name = name[:-len(suffix)].strip()

                                                      
        name = re.sub(r"[\.,:]", "", name)
        name = re.sub(r"\s+", " ", name).strip()
        return name

                                                                            
                                                                              
                                                                                      
    import re as _re
    for _e in history:
        _resps = _e.get('responsibilities', [])
        if not isinstance(_resps, list):
            continue
        _new_resps = []
        for _r in _resps:
            if isinstance(_r, str):
                                                      
                _m = _re.match(r"^\s*(?P<title>[^():\\n]{1,80}?)\s*\((?P<dates>[^)]+)\)\s*[:\-–—]\s*(?P<text>.+)$", _r)
                if _m:
                    _title = _m.group('title').strip()
                    _dates = _m.group('dates').strip()
                    _text = _m.group('text').strip()
                    _bullets = [t.strip() for t in _re.split(r";|\.|\\n", _text) if t.strip()]
                    _new_resps.append({'title': _title, 'dates': _dates, 'bullets': _bullets})
                    continue

                                                                           
                _m2 = _re.match(r"^\s*(?P<header>[^:]{1,60}?)\s*:\s*(?P<body>.+)$", _r)
                if _m2 and _re.search(r"\d{4}", _m2.group('body')):
                    _header = _m2.group('header').strip()
                    _body = _m2.group('body').strip()
                    _date_match = _re.search(r"(\b\d{4}[^,;\\n]*)", _body)
                    _dates = _date_match.group(1).strip() if _date_match else ""
                    _remainder = _re.sub(_re.escape(_dates), '', _body).strip() if _dates else _body
                    _bullets = [t.strip() for t in _re.split(r";|\.|\\n", _remainder) if t.strip()]
                    _new_resps.append({'title': _header, 'dates': _dates, 'bullets': _bullets})
                    continue

            _new_resps.append(_r)
        _e['responsibilities'] = _new_resps

    for entry in history:
        company_raw = entry.get("company", "")
        company = sanitize_company(company_raw)
        if not company:
            grouped.append(entry)
            continue

        if company in company_map:
            idx = company_map[company]
            existing = grouped[idx]

                                                                                                       
            if "responsibilities" not in existing or not isinstance(existing["responsibilities"], list):
                existing["responsibilities"] = []

                                                                                              
            if existing.get("_has_sub_pos") is not True:
                first_sub = {
                    "title": existing.get("final_position", ""),
                    "dates": existing.get("date", ""),
                    "bullets": existing.get("responsibilities", []) if isinstance(existing.get("responsibilities", []), list) else [],
                    "achievements": existing.get("achievements", []) if isinstance(existing.get("achievements", []), list) else []
                }
                existing["responsibilities"] = [first_sub]
                                                                                                   
                existing["achievements"] = existing.get("achievements", []) if isinstance(existing.get("achievements", []), list) else []
                existing["_has_sub_pos"] = True

                                                                                                               
            new_sub = {
                "title": entry.get("final_position", ""),
                "dates": entry.get("date", ""),
                "bullets": entry.get("responsibilities", []) if isinstance(entry.get("responsibilities", []), list) else [],
                "achievements": entry.get("achievements", []) if isinstance(entry.get("achievements", []), list) else []
            }
            existing["responsibilities"].append(new_sub)

                                                                                            
            if not existing.get("reason_for_leaving") and entry.get("reason_for_leaving"):
                existing["reason_for_leaving"] = entry.get("reason_for_leaving")

                                                                                                   
        else:
                                            
            company_map[company] = len(grouped)
                                                             
            new_entry = dict(entry)
            grouped.append(new_entry)

                             
    for g in grouped:
        if "_has_sub_pos" in g:
            del g["_has_sub_pos"]
            
    return grouped

def normalize_cv_data(raw_data):
    data = dict(raw_data) # Start by copying all existing data to prevent loss from editor

                                              
    scalar_mapping = {
                              
        "CANDIDATE_NAME": "personal_details.full_name",
        "POSITION": "header.position_applied",
        "RECRUITER_NAME": "header.presented_by",
        "DATE": "header.date",
        "PREVIOUS_SALARY": "header.current_salary",
        "SALARY_EXPECTATION": "header.salary_expectation",
        "EMAIL": "header.email",
        
                          
        "FULL_NAME": "personal_details.full_name",
        "KNOWN_AS": "personal_details.known_as",
        "NATIONALITY": "personal_details.nationality",
        "RESIDENTIAL_ADDRESS": "personal_details.residential_address",
        "MARITAL_STATUS": "personal_details.marital_status",
        "DOB": "personal_details.dob",
        "DRIVERS_LICENSE": "personal_details.drivers_license",
        "DRIVERS": "personal_details.drivers_license",        
        "MEDICAL_AID": "personal_details.medical_aid",
        "DEPENDENTS": "personal_details.dependents",
        "AREA_OF_RESIDENCE": "personal_details.area_residence",
        "RESIDENCE": "personal_details.area_residence",        
        "CRIMINAL": "personal_details.criminal_record",
        "AVAILABILITY": "personal_details.availability",
        "NOTICE": "personal_details.notice_period", # Updated for SRT 2.0
        "NOTICE_PERIOD": "personal_details.notice_period",
        "SALARY_EXPECTATIONS": "personal_details.salary_expectations",
        "SALARY_EXP": "personal_details.salary_expectations",        
        "COMPUTER_LITERACY": "personal_details.computer_literacy",
        "COMPUTER": "personal_details.computer_literacy",        
        "EXPERIENCE": "personal_details.experience_summary",
        "EXPERIENCE_SUMMARY": "personal_details.experience_summary",        
        
                                             
        "RACE": "personal_details.race",
        "GENDER": "personal_details.gender"
    }

    for key, path in scalar_mapping.items():
        val = get_nested_value(raw_data, path)
        if val is not None and str(val).strip():
            data[key] = str(val)
                                                                                    

                                       
    race = data.get("RACE", "")
    gender = data.get("GENDER", "")
    data["RACE_GENDER"] = f"{race} / {gender}" if race and gender else (race or gender)
    data["YEARS_GENDER"] = data["RACE_GENDER"]                                    

                                    
    list_to_string_keys = {
        "LANGUAGES": "personal_details.languages",
        "SKILLS": "personal_details.skills",
    }

    for key, path in list_to_string_keys.items():
        val = get_nested_value(raw_data, path, [])
        if isinstance(val, list):
            data[key] = ", ".join(str(v) for v in val)
        else:
            data[key] = str(val)

                              
    raw_list_keys = [
        "personal_details",
        "training",
        "courses",
        "qualifications",
        "professional_membership",
        "projects",
        "career_summary",
        "career_history",
        "career_highlights",
        "course_work",
        "custom_sections" # Added for universal support
    ]
    
    for key in raw_list_keys:
        val = raw_data.get(key, [])
        
                                                                                
        if key == "career_history":
                                                                                                  
            raw_history = val or []
            data["career_history_full"] = copy.deepcopy(raw_history)

                                                                                                          
            current_full = [job for job in data["career_history_full"] if job.get("is_current")]
            previous_full = [job for job in data["career_history_full"] if not job.get("is_current")]

                                                                                                  
            if not current_full and data["career_history_full"]:
                first_raw = data["career_history_full"][0]
                date_str_raw = str(first_raw.get("date", "")).lower()
                if "present" in date_str_raw or "current" in date_str_raw or "to date" in date_str_raw or date_str_raw.endswith("-") or date_str_raw.endswith("–"):
                    current_full = [first_raw]
                    previous_full = data["career_history_full"][1:]

            data["current_employment_full"] = current_full
            data["previous_employment_full"] = previous_full

                                                                    
            grouped_history = group_career_history_by_company(copy.deepcopy(raw_history))
            data["career_history"] = grouped_history
            
                                                                          
            current = [job for job in grouped_history if job.get("is_current")]
            previous = [job for job in grouped_history if not job.get("is_current")]
            
            if not current and grouped_history:
                first = grouped_history[0]
                date_str = str(first.get("date", "")).lower()
                if "present" in date_str or "current" in date_str or "to date" in date_str or date_str.endswith("-") or date_str.endswith("–"):
                    current = [first]
                    previous = grouped_history[1:]
            
            # Only overwrite if we actually found something to group, or if the target keys are missing
            if grouped_history or ("current_employment" not in data and "previous_employment" not in data):
                data["current_employment"] = current
                data["previous_employment"] = previous
            
        else:
            data[key] = val

                                                                               
    train_list = data.get("training", [])
    data["TRAINING_BULLETS"] = "\n".join([f"- {t}" for t in train_list]) if isinstance(train_list, list) else str(train_list)

    return data

from generate_master_template import generate_cv as generate_master_cv

def run_pipeline(cv_file_path, template_type="master"):
    print(f"--- Step 1: Extracting text from {cv_file_path} ---")
    if not os.path.exists(cv_file_path):
        print(f"Error: File {cv_file_path} not found.")
        return

    raw_text = universal_extractor(cv_file_path)
    
    if not raw_text or "Error" in raw_text:
        print("Extraction failed.")
        
    print("--- Step 2: Sending text to Gemini for structuring ---")
    structured_json = {}
    if os.path.exists("structured_data.json"):
        try:
            with open("structured_data.json", "r", encoding="utf-8") as f:
                structured_json = json.load(f)
            print("Loaded cached structured_data.json")
        except Exception as read_err:
            print(f"Could not read cached structured_data.json: {read_err}")
            structured_json = {}
    else:
        try:
            structured_json = structure_cv_data(raw_text if raw_text else "DUMMY")
            if structured_json and "error" not in structured_json:
                with open("structured_data.json", "w", encoding="utf-8") as f:
                    json.dump(structured_json, f, indent=4)
                
                                                     
                from srt import save_to_knowledge_base
                save_to_knowledge_base(raw_text if raw_text else "DUMMY", structured_json, cv_file_path)
        except Exception as e:
            print(f"An error occurred during structuring: {e}")
            structured_json = {}

    print("--- Step 3: Generating Final CV with Template ---")
    try:
        output_file = "FINAL_SISOL_RESUME.docx"
        template_data = normalize_cv_data(structured_json)
        
        if template_type == "master":
            generate_master_cv(template_data, output_file)
        else:
            from generate_Professional import generate_cv
            generate_cv(template_data, output_file, layout="universal")
        
        import clean_up
        clean_up.clean_up_document(output_file)
        print(f"Successfully generated {output_file}")
    except Exception as e:
        print(f"Generation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    my_file = os.path.join("uploads", "test_data_science.docx")
    if not os.path.exists(my_file):
        my_file = "test_output.docx"
    t_type = "master"
    
    if len(sys.argv) > 1:
        my_file = sys.argv[1]
    if len(sys.argv) > 2:
        t_type = sys.argv[2]
        
    run_pipeline(my_file, t_type)
