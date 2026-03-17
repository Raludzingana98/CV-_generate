# 📄 Professional CV Generator Dashboard

A powerful Streamlit-based application for extracting structured data from resumes (PDF/DOCX) and generating standardized, premium-quality CV documents.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- [Streamlit](https://streamlit.io/)
- [python-docx](https://python-docx.readthedocs.io/)
- [Google GenAI Python SDK](https://github.com/google/generative-ai-python)

### Installation
1. Install dependencies:
   ```bash
   pip install streamlit python-docx openai python-dotenv streamlit-sortables pandas
   ```
2. Create a `.env` file in the root directory (one has been created for you) and add your credentials:
   ```env
   AZURE_OPENAI_API_KEY=your_api_key_here
   AZURE_OPENAI_ENDPOINT=your_endpoint_here
   AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
   ```

### Running the Application
```bash
streamlit run dashboard.py
```
or Visit this cv-generate-dcgznqq4behhupzrtnkzow.streamlit.app

## 🛠️ Key Features

### 🧠 Automatic Layout Detection
The system automatically determines the optimal section order based on the position applied for. It uses keyword matching against specialized technical layouts (e.g., Software Engineering, Finance, DevOps).
- **Auto Mode**: Inferred from the "Position Applied" field.
- **Manual Mode**: Drag-and-drop sections to customize the order.
- **Preset Selection**: Force a specific technical layout from the dropdown.

### 📄 Smart Template Engine
Standardized output using several premium styles:
- **Master**: Comprehensive template with layout support.
- **Professional**: Clean design with dynamic section rendering.
- **Unbranded**: Clean, neutral style for various needs.

### 🔍 End-to-End Pipeline
1. **Extraction**: Advanced AI parsing of raw resumes into structured JSON.
2. **Standardization**: Normalizes data fields (dates, company names, etc.).
3. **Editor**: Real-time JSON and section-order editing before generation.
4. **Cleanup**: Intelligent removal of empty bullet points and placeholder text.

## 📁 Project Structure

- `dashboard.py`: Main Streamlit UI and application logic.
- `style_utils.py`: Centralized styling, layout logic, and keyword matching.
- `srt.py`: AI-powered text-to-JSON structuring.
- `main.py`: Data normalization and pipeline utilities.
- `generate_*.py`: Specific template generation logic.
- `layouts/`: JSON configurations for different technical CV roles.
- `extract_text.py`: Robust text extraction for PDF and DOCX.
- `clean_up.py`: Post-generation document formatting and optimization.

---
*Developed for SISOL Recruitment* by SHUMANI MARVELLOUS RALUDZINGANA
