import os
import json
import requests
from bs4 import BeautifulSoup
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials

# Load service account credentials from environment variable
service_account_info = json.loads(os.environ["GOOGLE_SHEETS_KEY"])
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)

# Setup Google Sheets client
SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]
SHEET_NAME = "Sheet1"
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

today = datetime.now().strftime("%Y-%m-%d")

def scrape_geneco():
    try:
        res = requests.get("https://www.geneco.sg/residential/electricity-plans/")
        soup = BeautifulSoup(res.text, "html.parser")
        plan = soup.find(text="Get It Fixed 24")
        rate = plan.find_next("div").text.strip() if plan else "Not Found"
        return rate
    except Exception as e:
        return f"Error: {e}"

def scrape_tuas():
    try:
        res = requests.get("https://www.savewithtuas.com/our-electricity-plans/")
        soup = BeautifulSoup(res.text, "html.parser")
        plan = soup.find(text="PowerFIX 24")
        rate = plan.find_next("div").text.strip() if plan else "Not Found"
        return rate
    except Exception as e:
        return f"Error: {e}"

# Scrape and log to sheet
geneco_rate = scrape_geneco()
tuas_rate = scrape_tuas()

sheet.append_row([today, "Geneco", "Get It Fixed 24", geneco_rate, 24])
sheet.append_row([today, "Tuas Power", "PowerFIX 24", tuas_rate, 24])
