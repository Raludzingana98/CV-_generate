import streamlit as st
import pandas as pd

def edit_personal_details(data):
    st.subheader("👤 Personal Details")

    col1, col2 = st.columns(2)

    with col1:
        data["CANDIDATE_NAME"] = st.text_input("Full Name", data.get("CANDIDATE_NAME", ""))
        data["KNOWN_AS"] = st.text_input("Known As", data.get("KNOWN_AS", ""))
        data["RACE_GENDER"] = st.text_input("Race and Gender", data.get("RACE_GENDER", ""))
        data["NATIONALITY"] = st.text_input("Nationality", data.get("NATIONALITY", ""))
        data["MARITAL_STATUS"] = st.text_input("Marital Status", data.get("MARITAL_STATUS", ""))

    with col2:
        data["DOB"] = st.text_input("Date of Birth", data.get("DOB", ""))
        data["DRIVERS"] = st.text_input("Driver's License / Own Car", data.get("DRIVERS", ""))
        data["NOTICE"] = st.text_input("Notice Period", data.get("NOTICE", ""))
        data["CRIMINAL"] = st.text_input("Clear Criminal Record?", data.get("CRIMINAL", ""))
        data["RESIDENCE"] = st.text_input("Area of Residence", data.get("RESIDENCE", ""))

    data["LANGUAGES"] = st.text_area("Languages", data.get("LANGUAGES", ""))
    data["SALARY_EXP"] = st.text_input("Salary Expectations", data.get("SALARY_EXP", ""))
    data["SKILLS"] = st.text_area("Skills", data.get("SKILLS", ""))
    data["COMPUTER"] = st.text_area("Computer Literacy", data.get("COMPUTER", ""))
    data["EXPERIENCE_SUMMARY"] = st.text_area("Experience Summary", data.get("EXPERIENCE_SUMMARY", ""))

    return data

def edit_list_section(title, key, data):
    st.subheader(title)

    items = data.get(key, [])
    if not isinstance(items, list):
        items = []

    text = "\n".join(items)
    edited_text = st.text_area(f"{title} (one per line)", text, height=150)

    data[key] = [line.strip() for line in edited_text.split("\n") if line.strip()]
    return data

def edit_table_section(title, key, columns, data):
    st.subheader(title)

    items = data.get(key, [])
    if not isinstance(items, list):
        items = []

    # if the section came through as a simple list of strings (often
    # happens when the LLM mis-parses a table), convert it into a list
    # of single-key dicts so pandas will render a proper table instead of
    # a single unnamed column.
    if items and all(isinstance(i, str) for i in items):
        items = [{columns[0]: i} for i in items]

    # convert to DataFrame after ensuring `items` is a list of dicts
    df = pd.DataFrame(items)
    # ensure every expected column exists so indexing below won't fail
    for col in columns:
        if col not in df.columns:
            df[col] = ""
    df = df[columns]

    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    data[key] = edited_df.to_dict(orient="records")
    return data

def edit_bullet_list(label, bullets):
    if not bullets or not isinstance(bullets, list):
        bullets = []

    text_val = "\n".join([str(x) for x in bullets if str(x).strip()])
    edited_text = st.text_area(label, text_val, height=140)

    return [line.strip() for line in edited_text.split("\n") if line.strip()]

def edit_sub_positions(sub_positions, prefix="sub"):
    if not sub_positions or not isinstance(sub_positions, list):
        sub_positions = []

    updated_sub_positions = []

    st.markdown("#### 🧩 Sub-Positions / Promotions")

    for idx, sub in enumerate(sub_positions):
        if not isinstance(sub, dict):
            continue

        with st.expander(f"Sub-Position {idx+1}: {sub.get('title','(No Title)')}"):
            title = st.text_input(
                "Sub-Position Title",
                sub.get("title", ""),
                key=f"{prefix}_title_{idx}"
            )

            dates = st.text_input(
                "Dates",
                sub.get("dates", ""),
                key=f"{prefix}_dates_{idx}"
            )

            bullets = edit_bullet_list(
                "Responsibilities / Duties (one per line)",
                sub.get("bullets", [])
            )

            achievements = edit_bullet_list(
                "Achievements (one per line)",
                sub.get("achievements", [])
            )

            updated_sub_positions.append({
                "title": title,
                "dates": dates,
                "bullets": bullets,
                "achievements": achievements
            })

    if st.button("➕ Add New Sub-Position", key=f"{prefix}_add"):
        updated_sub_positions.append({
            "title": "",
            "dates": "",
            "bullets": [],
            "achievements": []
        })

    return updated_sub_positions

def edit_job(job, job_key_prefix="job"):
    if not job or not isinstance(job, dict):
        job = {}

    company = st.text_input("Company", job.get("company", ""), key=f"{job_key_prefix}_company")
    date = st.text_input("Dates", job.get("date", ""), key=f"{job_key_prefix}_date")
    final_position = st.text_input("Final Position", job.get("final_position", ""), key=f"{job_key_prefix}_pos")
    reason_for_leaving = st.text_input("Reason for Leaving", job.get("reason_for_leaving", ""), key=f"{job_key_prefix}_reason")

    st.markdown("#### 📌 Responsibilities")
    responsibilities = job.get("responsibilities", [])

    plain_bullets = []
    sub_positions = []

    if isinstance(responsibilities, list):
        for r in responsibilities:
            if isinstance(r, str):
                plain_bullets.append(r)
            elif isinstance(r, dict):
                sub_positions.append(r)

    updated_plain_bullets = edit_bullet_list("Main Responsibilities (one per line)", plain_bullets)

    updated_sub_positions = edit_sub_positions(sub_positions, prefix=f"{job_key_prefix}_sub")

    st.markdown("#### 🏆 Key Achievements")
    achievements = edit_bullet_list("Achievements (one per line)", job.get("achievements", []))

    rebuilt_responsibilities = updated_plain_bullets + updated_sub_positions

    return {
        "company": company,
        "date": date,
        "final_position": final_position,
        "reason_for_leaving": reason_for_leaving,
        "responsibilities": rebuilt_responsibilities,
        "achievements": achievements
    }

def edit_job_section(title, data_key, data):
    st.markdown(f"## {title}")

    jobs = data.get(data_key, [])
    if not isinstance(jobs, list):
        jobs = []

    updated_jobs = []

    if not jobs:
        st.warning("No jobs found. Add one below.")

    for idx, job in enumerate(jobs):
        company_name = ""
        if isinstance(job, dict):
            company_name = job.get("company", "")

        label = f"{idx+1}. {company_name}" if company_name else f"{idx+1}. Job Entry"

        with st.expander(label, expanded=(idx == 0)):
            updated_job = edit_job(job, job_key_prefix=f"{data_key}_{idx}")
            updated_jobs.append(updated_job)

            if st.button(f"🗑️ Delete Job {idx+1}", key=f"delete_{data_key}_{idx}"):
                updated_jobs.pop()
                st.warning("Job deleted. Click Generate / rerun to refresh.")
                st.stop()

    if st.button(f"➕ Add New Job to {title}", key=f"add_{data_key}"):
        updated_jobs.append({
            "company": "",
            "date": "",
            "final_position": "",
            "reason_for_leaving": "",
            "responsibilities": [],
            "achievements": []
        })
        st.success("New job added. Scroll down to edit it.")

    data[data_key] = updated_jobs
    return data

def edit_career_history_full(data):
    st.header("🏢 Career History Editor (Full)")

    data = edit_job_section("Current Employment", "current_employment", data)
    st.divider()
    data = edit_job_section("Previous Employment", "previous_employment", data)

    return data

def section_based_editor(final_data):
    edited_data = final_data.copy()

    edited_data = edit_personal_details(edited_data)

    edited_data = edit_table_section(
        "🎓 Qualifications",
        "qualifications",
        ["qualification", "institution", "date", "status"],
        edited_data
    )

    edited_data = edit_table_section(
        "📚 Courses",
        "courses",
        ["course_name", "institution", "date", "status"],
        edited_data
    )

    edited_data = edit_table_section(
        "📌 Professional Membership",
        "professional_membership",
        ["board_name", "profession", "year", "prof_no"],
        edited_data
    )

    edited_data = edit_table_section(
        "📍 Projects",
        "projects",
        ["title", "value"],
        edited_data
    )

    edited_data = edit_table_section(
        "🧾 Career Summary",
        "career_summary",
        ["company", "position", "dates"],
        edited_data
    )

    edited_data = edit_list_section(
        "⭐ Career Highlights",
        "career_highlights",
        edited_data
    )

    edited_data = edit_list_section(
        "📖 Course Work",
        "course_work",
        edited_data
    )

    edited_data = edit_list_section(
        "🛠️ Training",
        "training",
        edited_data
    )

    edited_data = edit_career_history_full(edited_data)

    edited_data = edit_custom_sections(edited_data)

    return edited_data

def edit_custom_sections(data):
    custom_sections = data.get("custom_sections", [])
    if not isinstance(custom_sections, list) or not custom_sections:
        return data
    
    st.divider()
    st.header("✨ Industry-Specific Sections (Custom)")
    st.info("These sections were dynamically detected based on the industry/department.")

    updated_custom = []
    for idx, section in enumerate(custom_sections):
        name = section.get("section_name", "Untitled Section")
        content_type = section.get("content_type", "paragraph")
        content = section.get("content")

        with st.expander(f"Section: {name} ({content_type})", expanded=True):
            new_name = st.text_input("Section Name", name, key=f"custom_name_{idx}")
            
            if content_type == "list" and isinstance(content, list):
                new_content = edit_bullet_list("Items (one per line)", content)
            elif content_type == "table" and isinstance(content, list):
                if content and isinstance(content[0], dict):
                    cols = list(content[0].keys())
                    df = pd.DataFrame(content)
                    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key=f"custom_table_{idx}")
                    new_content = edited_df.to_dict(orient="records")
                else:
                    new_content = st.text_area("Content", str(content), key=f"custom_content_{idx}")
            else:
                if isinstance(content, list): content = "\n".join(map(str, content))
                new_content = st.text_area("Content", str(content), key=f"custom_content_{idx}")

            updated_custom.append({
                "section_name": new_name,
                "content_type": content_type,
                "content": new_content
            })
            
            if st.button(f"🗑️ Remove {name}", key=f"del_custom_{idx}"):
                updated_custom.pop()
                st.rerun()

    data["custom_sections"] = updated_custom
    return data
