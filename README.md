# 💼 Professional CV Generator Dashboard

An AI-powered web application that extracts, structures, and transforms raw resumes (PDF/DOCX) into standardized, high-quality CVs tailored to specific roles.

Built with Streamlit, this system provides an end-to-end pipeline for intelligent resume parsing, dynamic layout selection, and automated document generation.

---

## 🌐 Live Demo
👉 https://cv-generate-dcgznqq4behhupzrtnkzow.streamlit.app

---

## 🧠 Key Features

### 🔍 AI Resume Parsing
- Extracts unstructured resume data into structured JSON format  
- Handles PDF and DOCX inputs  
- Uses AI to intelligently interpret content  

### 🧩 Smart Layout Engine
- Automatically selects CV layout based on job role  
- Supports Software Engineering, Finance, DevOps, and more  
- Manual drag-and-drop section customization  

### 📄 Professional CV Templates
- Multiple premium templates:
  - Master (comprehensive)
  - Professional (clean & modern)
  - Unbranded (minimal)

### ⚙️ End-to-End Pipeline
- Extraction → Structuring → Editing → Generation → Cleanup  
- Real-time JSON editing before final output  
- Automatic removal of empty or redundant content  

---

## 🛠️ Tech Stack

- **Frontend/UI:** Streamlit  
- **Backend:** Python  
- **AI Processing:** OpenAI API  
- **Data Handling:** Pandas  
- **Document Generation:** python-docx  

---

## 📦 Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/cv-generator.git
cd cv-generator

Install dependencies
pip install -r requirements.txt

Setup environment variables
Create a .env file in the root directory:
   AZURE_OPENAI_API_KEY=your_api_key_here
   AZURE_OPENAI_ENDPOINT=your_endpoint_here
   AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
▶️ Running the Application
streamlit run dashboard.py

📁 Project Structure
```bash
dashboard.py          # Main Streamlit app
style_utils.py        # Layout logic and styling
srt.py                # AI text-to-JSON structuring
main.py               # Data normalization pipeline
generate_*.py         # CV template generators
layouts/              # Role-based layout configs
extract_text.py       # PDF/DOCX extraction
clean_up.py           # Post-processing & formatting

## 🎯 Use Cases
- Generate professional CVs instantly  
- Standardize candidate resumes for recruitment  
- Customize CVs based on job roles  
- Automate resume formatting workflows  

---

## 👨‍💻 Author
**Shumani Marvellous Raludzingana**

- GitHub: https://github.com/Raludzingana98  
- LinkedIn: https://linkedin.com/in/shumani-raludzingana  

---

## ⭐ Why This Project Stands Out
This project demonstrates:

- Real-world AI application development  
- End-to-end system design and architecture  
- Data processing and automation skills  
- User-focused interface design  

---

## 📌 Future Improvements
- Add support for more CV templates  
- Integrate advanced NLP models  
- Export to multiple formats (PDF, DOCX, HTML)  
- Enhance UI/UX with advanced interactivity  

---

## 📝 License
This project is for educational and professional demonstration purposes.


