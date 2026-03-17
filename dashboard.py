import streamlit as st
import os
import json
import time
from streamlit_sortables import sort_items
import pandas as pd
import editor_ui

from extract_text import universal_extractor
try:
    import srt as llm_processor
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    import srt as llm_processor


import generate_master_template as master_tpl
import generate_Professional as professional_tpl
# unbranded mid-page template
import generate_unbranded_template as unbranded_mid_tpl
# unbranded variants were removed per request
from main import normalize_cv_data
import style_utils
import clean_up

                                       
st.set_page_config(page_title="CV Generator", layout="wide")

def save_uploaded_file(uploaded_file):
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    file_path = os.path.join(upload_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

                                                                   
def get_section_counts(data):
    def safe_len(val):
        if val is None:
            return 0
        if isinstance(val, list):
            return len(val)
        if isinstance(val, dict):
            return len(val)
        if isinstance(val, str):
            return 1 if val.strip() else 0
        return 0

    counts = {}

    counts["Personal Details"] = safe_len(data.get("personal_details", {}))
    counts["Qualification"] = safe_len(data.get("qualifications", []))
    counts["Professional Membership"] = safe_len(data.get("professional_membership", []))
    counts["Projects"] = safe_len(data.get("projects", []))
    counts["Career Summary"] = safe_len(data.get("career_summary", []))

                                                                    
    curr = safe_len(data.get("current_employment", []))
    prev = safe_len(data.get("previous_employment", []))
    counts["Career History"] = curr + prev

    counts["Career Highlights"] = safe_len(data.get("career_highlights", []))
    counts["Course Work"] = safe_len(data.get("course_work", []))
    counts["Training"] = safe_len(data.get("training", []))
    counts["Courses"] = safe_len(data.get("courses", []))

    # Dynamic custom sections
    customs = data.get("custom_sections", [])
    if isinstance(customs, list):
        for cs in customs:
            name = cs.get("section_name", "Untitled")
            content = cs.get("content", [])
            counts[name] = safe_len(content)

    return counts

def save_layout_preset(preset_name, enabled_sections, section_order):
    os.makedirs("layouts", exist_ok=True)
    file_path = os.path.join("layouts", f"{preset_name}.json")

    preset_data = {
        "enabled_sections": enabled_sections,
        "section_order": section_order
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(preset_data, f, indent=4)

    return file_path

def load_layout_preset(preset_file):
    with open(preset_file, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    st.title("📄 CV Data Extractor & Generator")
    
    st.sidebar.header("🎨 Choose Template Style")
    template_choice = st.sidebar.selectbox(
        "Select Style", 
        [
            "SISOL Master (Consolidated)",

            "SISOL Professional",            
            "Unbranded (mid-page start)",
        ]
    )
    
                                       
    if "Master" in template_choice:
        active_tpl = master_tpl
        style_name = "Master"

    elif "Professional" in template_choice:
        active_tpl = professional_tpl
        style_name = "Professional"
    elif "Unbranded (mid-page" in template_choice:
        active_tpl = unbranded_mid_tpl
        style_name = "Unbranded_mid"
    else:
        active_tpl = master_tpl
        style_name = "Master"

    # For Professional layout, allow layout selection (auto or explicit preset)
    layout_files = [
        os.path.splitext(f)[0]
        for f in os.listdir("layouts")
        if f.endswith(".json") and f != "layout_keywords.json"
    ]
    layout_files = sorted(set(layout_files))
    selected_layout = st.sidebar.selectbox(
        "Layout Selection",
        ["Manual Section Order", "Auto (from Position)"] + layout_files,
        index=1, # Default to Auto
    )

    with st.sidebar.expander("🧠 Layout Keyword Rules"):
        keyword_map = style_utils.load_layout_keywords() if hasattr(style_utils, 'load_layout_keywords') else professional_tpl.load_layout_keywords()
        st.write("Edit keywords that drive auto-layout inference. Use commas to separate terms.")

        updated = {}
        for layout_name, keywords in sorted(keyword_map.items()):
            keywords_str = ", ".join(keywords or [])
            edited = st.text_area(
                f"{layout_name}",
                keywords_str,
                height=80,
                key=f"kw_{layout_name}",
            )
            updated[layout_name] = [k.strip() for k in edited.split(",") if k.strip()]

        if st.button("Save Keyword Rules"):
            style_utils.save_layout_keywords(updated)
            st.success("Saved layout keyword rules.")


    st.sidebar.header("🛠️ Template Management")
    if st.sidebar.button("Generate Empty Template"):
        with st.sidebar:
            with st.spinner(f"Generating {style_name} template..."):
                try:
                    if style_name == "Master":
                        active_tpl.create_template()
                        template_filename = "Master_CV_Template.docx"
                    elif style_name == "Professional":
                        active_tpl.create_template()
                        template_filename = "Professional_CV_Template.docx"
                    elif style_name == "Unbranded_mid":
                        active_tpl.create_template()
                        template_filename = "Unbranded_CV_Template.docx"
                    else:
                        active_tpl.create_template()
                        template_filename = "Master_CV_Template.docx"

                    st.success(f"{style_name} template generated!")
                    
                    template_path = os.path.join("uploads", template_filename)
                    if os.path.exists(template_path):
                        with open(template_path, "rb") as f:
                            st.download_button(
                                label=f"📥 Download {style_name} Template",
                                data=f,
                                file_name=template_filename,
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                except Exception as e:
                    st.error(f"Failed to generate template: {e}")

    st.header("1. Upload Resume")
    uploaded_file = st.file_uploader("Upload a CV (PDF or DOCX)", type=["pdf", "docx"])
    
    if uploaded_file is not None:
        file_path = save_uploaded_file(uploaded_file)
        st.success(f"File saved to: {file_path}")

        st.header("2. Extract & Structure Data")
        if "extracted_json" not in st.session_state:
            st.session_state.extracted_json = None
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Extract & Structure Information"):
                with st.spinner("Extracting text..."):
                    raw_text = universal_extractor(file_path)
                
                if not raw_text or "Error" in raw_text:
                    st.error(f"Extraction Failed: {raw_text}")
                else:
                    st.expander("View Raw Extracted Text").text_area("Raw Text", raw_text, height=200)
                    with st.spinner("Analyzing with AI..."):
                        try:
                            structured_data = llm_processor.structure_cv_data(raw_text)
                            st.session_state.extracted_json = structured_data
                            st.success("Analysis Complete!")
                        except Exception as e:
                            st.error(f"AI Analysis Failed: {e}")

        if st.session_state.extracted_json:
            with st.container():
                st.header("3. Review & Reorder Sections")
                st.info("You can edit the data or change the section order below.")
                
                final_data = editor_ui.section_based_editor(st.session_state.extracted_json)
                st.markdown("---")
                if st.button("Apply changes to structured data"):
                    st.session_state.extracted_json = final_data
                    st.success("Changes saved to structured JSON")
                default_order = [
                    "Personal Details",
                    "Qualification",
                    "Professional Membership",
                    "Projects",
                    "Career Summary",
                    "Career History",
                    "Career Highlights",
                    "Course Work",
                    "Training",
                    "Courses"
                ]

                                          
                if "master_section_order" not in st.session_state:
                    st.session_state.master_section_order = default_order.copy()

                if "master_enabled_sections" not in st.session_state:
                    st.session_state.master_enabled_sections = {s: True for s in default_order}

                # Always compute section counts and show layout UI (was incorrectly indented inside the initialization branch)
                section_counts = get_section_counts(final_data)

                os.makedirs("layouts", exist_ok=True)
                preset_files = [f for f in os.listdir("layouts") if f.endswith(".json")]

                colA, colB = st.columns([0.6, 0.4])

                with colA:
                    if preset_files:
                        preset_choice = st.selectbox("📂 Load Saved Layout Preset", ["None"] + preset_files)

                        if preset_choice != "None":
                            preset_path = os.path.join("layouts", preset_choice)
                            preset_data = load_layout_preset(preset_path)

                            st.session_state.master_section_order = preset_data.get("section_order", default_order)
                            st.session_state.master_enabled_sections = preset_data.get("enabled_sections", {s: True for s in default_order})

                            st.success(f"Loaded preset: {preset_choice}")
                            st.rerun()
                    else:
                        st.write("No presets saved yet.")

                with colB:
                    if st.button("🔄 Reset Layout to Default"):
                        st.session_state.master_section_order = default_order.copy()
                        st.session_state.master_enabled_sections = {s: True for s in default_order}
                        st.rerun()

                st.divider()

                st.markdown("### ✅ Enable / Disable Sections")

                for sec in st.session_state.master_section_order:
                    count = section_counts.get(sec, 0)

                    col1, col2 = st.columns([0.7, 0.3])

                    with col1:
                        st.session_state.master_enabled_sections[sec] = st.checkbox(
                            f"{sec}  ({count} items)",
                            value=st.session_state.master_enabled_sections.get(sec, True),
                            key=f"toggle_{sec}"
                        )

                    with col2:
                        if count == 0:
                            st.caption("⚠️ Empty")

                st.divider()

                st.markdown("### 🔥 Drag & Drop Section Order")

                new_order = sort_items(
                    st.session_state.master_section_order,
                    direction="vertical"
                )

                if new_order != st.session_state.master_section_order:
                    st.session_state.master_section_order = new_order
                    st.rerun()

                st.divider()

                st.markdown("### 💾 Save Layout Preset")

                preset_name = st.text_input("Preset Name (Example: Engineering_Layout)")

                if st.button("💾 Save Preset"):
                    if not preset_name.strip():
                        st.error("Please enter a preset name.")
                    else:
                        save_layout_preset(
                            preset_name.strip(),
                            st.session_state.master_enabled_sections,
                            st.session_state.master_section_order
                        )
                        st.success(f"Preset saved: {preset_name.strip()}")

                custom_order = [
                    sec for sec in st.session_state.master_section_order
                    if st.session_state.master_enabled_sections.get(sec, True)
                ]

                if final_data:
                    inferred_layout, inferred_keyword = style_utils.infer_layout_from_data(final_data)
                    effective_layout = (
                        None
                        if selected_layout in ("Auto (from Position)", "Manual Section Order")
                        else selected_layout
                    )
                    
                    # Only infer if we are in Auto mode
                    inferred_layout = None
                    inferred_keyword = None
                    if selected_layout == "Auto (from Position)":
                        inferred_layout, inferred_keyword = style_utils.infer_layout_from_data(final_data)
                        if inferred_layout:
                            effective_layout = inferred_layout

                    st.markdown("### 🧠 Layout Detection")
                    if selected_layout == "Manual Section Order":
                        st.info("Using manual section order from the dashboard UI above.")
                    elif inferred_layout:
                        st.info(
                            f"Auto-detected layout: **{inferred_layout}** (matched keyword: **{inferred_keyword}**)."
                        )
                    elif selected_layout == "Auto (from Position)":
                        st.warning(
                            "Could not auto-detect a layout from Position. Using default section order."
                        )
                    else:
                        st.info(f"Using explicitly selected layout: **{selected_layout}**")

                    if effective_layout:
                        # Use professional_tpl for preview if it exists, otherwise style_utils if it has get_layout_preview
                        preview = None
                        if hasattr(professional_tpl, 'get_layout_preview'):
                            preview = professional_tpl.get_layout_preview(effective_layout)
                        
                        if preview:
                            st.markdown(f"**Preview of layout:** `{effective_layout}`")
                            for item in preview:
                                typ = item.get("type")
                                name = item.get("name")
                                enabled = item.get("enabled")
                                flag = "✅" if enabled is None or enabled else "⚪"
                                st.write(f"{flag} **{name}** — `{typ}`")
                        else:
                            st.write("No preview details available for the selected layout.")

                    st.header("4. Download Result")
                    if st.button("Generate CV Document"):
                        try:
                            template_data = normalize_cv_data(final_data)
                            output_filename = f"Generated_{uploaded_file.name.rsplit('.', 1)[0]}.docx"
                            output_path = os.path.join("uploads", output_filename)

                            with st.spinner("Generating document..."):
                                if style_name == "Master":
                                    # If Auto is selected, pass layout=None and section_order=None to trigger internal inference
                                    # If Manual is selected, pass section_order=custom_order and layout=None
                                    # If a specific layout is selected, pass it as layout
                                    layout_arg = None if selected_layout in ("Auto (from Position)", "Manual Section Order") else selected_layout
                                    order_arg = custom_order if selected_layout == "Manual Section Order" else None
                                    
                                    master_tpl.generate_cv(template_data, output_path, section_order=order_arg, layout=layout_arg)
                                elif style_name == "Unbranded_mid":
                                    layout_arg = None if selected_layout in ("Auto (from Position)", "Manual Section Order") else selected_layout
                                    active_tpl.generate_cv(template_data, output_path, layout=layout_arg)
                                elif style_name == "Professional":
                                    layout_arg = None if selected_layout in ("Auto (from Position)", "Manual Section Order") else selected_layout
                                    active_tpl.generate_cv(template_data, output_path, layout=layout_arg)
                                else:
                                    active_tpl.generate_cv(template_data, output_path)

                                clean_up.clean_up_document(output_path)

                            st.success("Document Generated Successfully!")
                            with open(output_path, "rb") as f:
                                st.download_button(
                                    label="📥 Download Final CV",
                                    data=f,
                                    file_name=output_filename,
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                )
                        except Exception as e:
                            st.error(f"Generation Failed: {e}")
                            st.exception(e)

if __name__ == "__main__":
    main()
