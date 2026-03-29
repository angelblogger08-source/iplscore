import os
import json
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def scrape_ipl_score():
    try:
        # 1. AUTHENTICATION & TARGETING
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_json = os.environ.get('GOOGLE_CREDENTIALS')
        if not creds_json:
            print("❌ Error: GOOGLE_CREDENTIALS secret not found in GitHub.")
            return

        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # TARGET SHEET: Using your specific ID
        sheet_id = "1c1WtoomLI5CIkitzwjeoKZGOLQog6wL8FwDUcYnxa_s"
        sheet = client.open_by_key(sheet_id).sheet1

        # 2. DYNAMIC LIVE SCRAPING
        url = "https://sports.ndtv.com/cricket/live-scores"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the specific match card for MI vs KKR
        score, overs, status = "Live", "Updating...", "Match in Progress"
        
        # Look through all match containers on the NDTV live page
        cards = soup.find_all('div', class_='sp-scr_wrp')
        for card in cards:
            card_text = card.get_text()
            if "Mumbai Indians" in card_text and "Kolkata Knight Riders" in card_text:
                try:
                    score = card.find('span', class_='scr_tm-run').text.strip()
                    overs = card.find('span', class_='scr_tm-ovr').text.strip()
                    status = "MI Chasing 221 - Wankhede on fire!"
                except:
                    pass
                break

        print(f"DEBUG: Scraped {score} at {overs}")

        # 3. PUSH TO SHEET
        # Column A=Score, B=Overs, C=Target, D=Status
        data_to_save = [[score, overs, "221", status]]
        sheet.update(range_name='A2:D2', values=data_to_save, value_input_option='USER_ENTERED')
        
        print(f"✅ Success! Updated sheet with {score}")

    except Exception as e:
        print(f"❌ Actual Error: {e}")

if __name__ == "__main__":
    scrape_ipl_score()
