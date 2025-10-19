# ecourts_ui_scraper_selenium_progress.py
import os
import re
from datetime import datetime
from tkinter import Tk, Label, Entry, Button, filedialog, StringVar, messagebox
from tkinter import ttk

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests

BASE = "https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/"

def safe_filename(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_\-\. ]+", "_", s).strip()

def selenium_fetch_and_download(state_label, district_label, complex_label, court_label, date_str, out_dir="downloads", progress_callback=None):
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(BASE)
    wait = WebDriverWait(driver, 15)

    def select_by_visible_text(select_id_or_name, visible_text):
        try:
            sel = driver.find_element(By.ID, select_id_or_name)
        except:
            try:
                sel = driver.find_element(By.NAME, select_id_or_name)
            except:
                return False
        options = sel.find_elements(By.TAG_NAME, "option")
        for opt in options:
            if visible_text.strip().lower() in opt.text.strip().lower():
                opt.click()
                return True
        return False

    select_by_visible_text("state", state_label)
    select_by_visible_text("district", district_label)
    select_by_visible_text("courtComplex", complex_label)
    if court_label.strip():
        select_by_visible_text("court", court_label)

    # Enter date
    try:
        date_inputs = driver.find_elements(By.XPATH, "//input[contains(@id,'date') or contains(@name,'date')]")
        for di in date_inputs:
            di.clear()
            di.send_keys(date_str)
    except:
        pass

    # Click search button
    try:
        btns = driver.find_elements(By.XPATH, "//button|//input[@type='submit']")
        for b in btns:
            text = b.text.lower() or b.get_attribute("value") or ""
            if "search" in text or "fetch" in text or "get" in text or "submit" in text:
                b.click()
                break
    except:
        pass

    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "a")))
    except:
        pass

    anchors = driver.find_elements(By.TAG_NAME, "a")
    pdf_links = []
    for a in anchors:
        try:
            href = a.get_attribute("href")
            if href and (href.lower().endswith(".pdf") or "cause-list" in href.lower() or "causelist" in href.lower()):
                pdf_links.append(href)
        except:
            continue

    driver.quit()

    os.makedirs(out_dir, exist_ok=True)
    downloaded_files = []
    total = len(pdf_links)
    for idx, url in enumerate(pdf_links, start=1):
        fname = safe_filename(f"{state_label}_{district_label}_{complex_label}_{court_label or 'All'}_{date_str}_{os.path.basename(url)}")
        out_path = os.path.join(out_dir, fname)
        try:
            r = requests.get(url, stream=True, timeout=30)
            r.raise_for_status()
            with open(out_path, "wb") as f:
                for chunk in r.iter_content(1024*32):
                    if chunk:
                        f.write(chunk)
            downloaded_files.append(out_path)
            if progress_callback:
                progress_callback(idx, total)
        except Exception as e:
            print(f"Failed to download {url}: {e}")

    return downloaded_files

# ---------------- UI -----------------
def run_ui():
    root = Tk()
    root.title("eCourts Cause List Downloader with Progress")
    root.geometry("550x450")

    Label(root, text="State:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    state_entry = Entry(root, width=40)
    state_entry.grid(row=0, column=1)

    Label(root, text="District:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    district_entry = Entry(root, width=40)
    district_entry.grid(row=1, column=1)

    Label(root, text="Court Complex:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    complex_entry = Entry(root, width=40)
    complex_entry.grid(row=2, column=1)

    Label(root, text="Court Name (optional):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
    court_entry = Entry(root, width=40)
    court_entry.grid(row=3, column=1)

    Label(root, text="Date (YYYY-MM-DD):").grid(row=4, column=0, padx=10, pady=5, sticky="w")
    date_entry = Entry(root, width=40)
    date_entry.grid(row=4, column=1)
    date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))

    Label(root, text="Output Folder:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
    folder_var = StringVar()
    folder_entry = Entry(root, textvariable=folder_var, width=30)
    folder_entry.grid(row=5, column=1, sticky="w")
    def browse_folder():
        folder = filedialog.askdirectory()
        folder_var.set(folder)
    Button(root, text="Browse", command=browse_folder).grid(row=5, column=2, padx=5)

    # Progress bar
    progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
    progress.grid(row=6, column=0, columnspan=3, pady=20)

    status_label = Label(root, text="Idle")
    status_label.grid(row=7, column=0, columnspan=3)

    def update_progress(current, total):
        progress['maximum'] = total
        progress['value'] = current
        status_label.config(text=f"Downloading {current}/{total} PDFs")
        root.update_idletasks()

    def download_action():
        state_val = state_entry.get()
        district_val = district_entry.get()
        complex_val = complex_entry.get()
        court_val = court_entry.get()
        date_val = date_entry.get()
        out_dir = folder_var.get() or "downloads"

        if not state_val or not district_val or not complex_val or not date_val:
            messagebox.showerror("Error", "Please fill at least State, District, Court Complex, and Date.")
            return

        try:
            files = selenium_fetch_and_download(state_val, district_val, complex_val, court_val, date_val, out_dir, progress_callback=update_progress)
            if files:
                messagebox.showinfo("Success", f"Downloaded {len(files)} PDFs to {out_dir}")
            else:
                messagebox.showwarning("Not Found", "No PDFs found for the given inputs.")
            progress['value'] = 0
            status_label.config(text="Idle")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")
            progress['value'] = 0
            status_label.config(text="Idle")

    Button(root, text="Download Cause List", command=download_action, bg="green", fg="white").grid(row=8, column=0, columnspan=3, pady=20)

    root.mainloop()

if __name__ == "__main__":
    run_ui()
