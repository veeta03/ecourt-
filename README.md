# eCourts Cause List Scraper with Selenium and UI

This project is a **real-time eCourts cause list scraper** that allows users to:

- Select **State, District, Court Complex, and optional Court Name**
- Pick a **date** for the cause list
- Download **all judges’ cause list PDFs** automatically
- Monitor download progress via a **live progress bar** in the UI

---

## 🔗 Project Demo

- UI screenshot / video: *(Add link or embed screenshot here)*  
- Example of downloaded PDFs: *(Optional screenshot)*  

---

## 🛠 Features

1. **Dynamic Selenium Scraper**
   - Handles dropdowns (State, District, Court Complex, Court Name)
   - Works with headless Chrome
   - Downloads PDFs in real-time

2. **User-friendly Tkinter UI**
   - Input fields for State, District, Court Complex, Court Name
   - Date picker
   - Browse folder for downloads
   - Live **progress bar** for download status

3. **Automatic PDF downloads**
   - Downloads all cause list PDFs for all judges if Court Name is left blank
   - Saves files in the specified folder with meaningful filenames

---

## ⚡ Prerequisites

- Python 3.8+
- Google Chrome (version 114 recommended to match ChromeDriver)
- Install required packages:

```bash
pip install -r requirements.txt
# or if requirements.txt is inside a folder named 'requirements'
pip install -r requirements/requirements.txt

Clone the repository:

git clone https://github.com/<YOUR_USERNAME>/ecourts_scraper.git
cd ecourts_scraper


Run the scraper UI:

python ecourts_ui_scraper_progress.py


Fill in:

State

District

Court Complex

(Optional) Court Name

Date (YYYY-MM-DD)

Output Folder

Click Download Cause List → PDFs will download with live progress updates.

📂 Folder Structure
ecourts_scraper/
├── ecourts_ui_scraper_progress.py   # Main UI + scraper script
├── README.md                        # This file
├── requirements/                    # Optional folder for requirements
│   └── requirements.txt
└── downloads/                       # Default folder where PDFs will be saved
📝 Notes

Ensure your Chrome version matches the ChromeDriver version. Recommended: Chrome 114

Automating CAPTCHA is not included (manual intervention may be required)

Tested on Windows 10/11 with Python 3.11

If Court Name is left empty, the scraper will attempt to download all judges’ PDFs for the selected court complex.
