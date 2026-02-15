# 📄✨ Resume Screening Parser  

An intelligent **Python-based Resume Screening System** that automates resume parsing, skill extraction, and candidate ranking based on a given Job Description (JD).  

This project helps recruiters and hiring managers shortlist the most relevant candidates efficiently and objectively.

---

## 🚀 Features  

🔍 **Job Description Parsing**  
- Extracts required skills  
- Extracts preferred skills  
- Identifies minimum experience  

📂 **Resume Parsing**  
- Supports parsing resumes from a folder  
- Extracts text from resumes  
- Handles multiple resumes at once  

🧠 **Skill & Experience Extraction**  
- Uses structured skill taxonomy  
- Identifies matched & missing skills  
- Calculates total years of experience  

📊 **Smart Scoring System**  
- Required skill match percentage  
- Preferred skill match percentage  
- Keyword match percentage  
- Experience match percentage  
- Final weighted total score  

🏆 **Candidate Ranking & Filtering**  
- Rank resumes by total score  
- Filter by minimum score  
- Select top N candidates  

📁 **Flexible Output Formats**  
- CSV output  
- JSON output  
- Timestamped result files  

---

## 🗂️ Project Structure  

```
Resume-Screening-Parser/
│
├── app.py                  # Entry point (if applicable)
├── main.py                 # Main CLI-based screening system
├── screen.py               # Simple folder-based screening
│
├── extractors/             # Skill & experience extraction logic
├── parsers/                # Resume and JD parsing modules
├── matcher/                # Resume scoring & ranking logic
│
├── data/                   # Skills taxonomy & config
├── tests/                  # Unit tests
├── output/                 # Generated screening results
│
├── requirements.txt        # Dependencies
└── venv/                   # Virtual environment (ignored)
````

---

## 🛠️ Installation  

### 1️⃣ Clone the Repository  

```bash
git clone https://github.com/Saurabh6266/Resume-Screening-Parser.git
cd Resume-Screening-Parser
````

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate     # Mac/Linux
venv\Scripts\activate        # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 📌 Usage

### 🖥️ Standard CLI Mode

```bash
python main.py \
  --jd path/to/job_description.txt \
  --resumes path/to/resumes_folder \
  --top 10 \
  --min-score 60 \
  --format csv
```

### 🔹 Arguments

| Flag          | Description                     |
| ------------- | ------------------------------- |
| `--jd`        | Path to job description file    |
| `--resumes`   | Path to resumes directory       |
| `--top`       | Number of top resumes to return |
| `--min-score` | Minimum score threshold         |
| `--format`    | Output format (`csv` or `json`) |

---

### 📁 Simple Folder Mode

If JD and resumes are inside the same folder:

```bash
python screen.py \
  --folder path/to/folder \
  --top 5 \
  --min-score 70 \
  --format json
```

---

## 📊 Output

Results are saved inside the `output/` folder.

Example output file:

```
results_software_engineer_20260215_143200.csv
```

Each output includes:

* 🏅 Rank
* 📄 Resume Name
* 📧 Email
* 📞 Phone
* 📊 Total Score (%)
* 🎯 Required Skills Match (%)
* ⭐ Preferred Skills Match (%)
* 🧮 Experience Match (%)
* 🔑 Keyword Match (%)
* 📌 Matched Skills
* ❌ Missing Skills

---

## 🧠 How It Works

1️⃣ Parse Job Description
2️⃣ Extract required & preferred skills
3️⃣ Parse all resumes
4️⃣ Extract candidate skills & experience
5️⃣ Compute match scores
6️⃣ Rank candidates
7️⃣ Generate CSV/JSON output

---

## 🧪 Running Tests

```bash
pytest
```

---

## 💡 Future Improvements

* 🌐 Web Interface (Flask / FastAPI)
* 🤖 ML-based semantic matching
* 🧾 PDF report generation
* 🗄️ Database integration
* 📊 Visualization dashboard

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a new branch
3. Commit changes
4. Submit a Pull Request

---

⭐ If you found this project helpful, consider giving it a star!
