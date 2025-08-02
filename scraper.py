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
SHEET_NAME = "vendor-pricing"
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

today = datetime.now().strftime("%Y-%m-%d")

def scrape_geneco():
    try:
        res = requests.get("https://www.geneco.sg/residential/electricity-plans/")
        soup = BeautifulSoup(res.text, "html.parser")
        plan_blocks = soup.find_all("div", class_="tab-pane")

        for block in plan_blocks:
            if "Get It Fixed 24" in block.text:
                rate_div = block.find("div", class_="plan-rate")
                if rate_div:
                    return rate_div.text.strip()
        return "Rate not found"
    except Exception as e:
        return f"Error: {e}"

def scrape_tuas():
    try:
        res = requests.get("https://www.savewithtuas.com/our-electricity-plans/")
        soup = BeautifulSoup(res.text, "html.parser")
        cards = soup.find_all("div", class_="plan-info-box")

        for card in cards:
            if "PowerFIX 24" in card.text:
                rate = card.find("h4")
                if rate:
                    return rate.text.strip()
        return "Rate not found"
    except Exception as e:
        return f"Error: {e}"

def scrape_keppel():
    try:
        res = requests.get("https://www.keppelelectric.com/residential-price-plan")
        soup = BeautifulSoup(res.text, "html.parser")
        plans = soup.find_all("div", class_="plan-details")

        for plan in plans:
            title = plan.find("h3")
            if title and "24 Months" in title.text:
                rate_div = plan.find("div", class_="rate")
                if rate_div:
                    return rate_div.text.strip()
        return "Rate not found"
    except Exception as e:
        return f"Error: {e}"

# Scrape and log to sheet
geneco_rate = scrape_geneco()
tuas_rate = scrape_tuas()
keppel_rate = scrape_keppel()

sheet.append_row([today, "Geneco", "Get It Fixed 24", geneco_rate, 24])
sheet.append_row([today, "Tuas Power", "PowerFIX 24", tuas_rate, 24])
sheet.append_row([today, "Keppel Electric", "Fixed 24", keppel_rate, 24])
