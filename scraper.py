import os
import json
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def scrape_ipl_score():
    try:
        # 1. SETUP GOOGLE SHEETS
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # Pulling the secret from GitHub Actions Environment
        creds_json = os.environ.get('GOOGLE_CREDENTIALS')
        if not creds_json:
            print("❌ Error: GOOGLE_CREDENTIALS secret not found.")
            return

        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # TARGET SHEET: Using your specific Sheet ID
        sheet_id = "1c1WtoomLI5CIkitzwjeoKZGOLQog6wL8FwDUcYnxa_s"
        sheet = client.open_by_key(sheet_id).sheet1

        # 2. DYNAMIC SCRAPING (Live from NDTV Sports)
        url = "https://sports.ndtv.com/cricket/live-scores"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Logic to find the MI vs KKR match section dynamically
        score = "Final"
        overs = "Result"
        status = "Match Ended"

        # Search for all match cards on the page
        match_cards = soup.find_all('div', class_='sp-scr_wrp')
        
        for card in match_cards:
            if "Mumbai Indians" in card.text and "Kolkata Knight Riders" in card.text:
                try:
                    # Extract the live numbers
                    score = card.find('span', class_='scr_tm-run').text.strip()
                    overs = card.find('span', class_='scr_tm-ovr').text.strip()
                    status = "MI vs KKR: Live Tracking"
                    break
                except:
                    continue

        print(f"DEBUG: Scraped {score} at {overs}")

        # 3. UPDATE THE SHEET
        # Format: [Score, Overs, Target, Status]
        data_to_save = [[score, overs, "221", status]]
        
        sheet.update(
            values=data_to_save, 
            range_name='A2:D2', 
            value_input_option='USER_ENTERED'
        )
        
        print(f"✅ Success! Sheet updated with {score}")

    except Exception as e:
        print(f"❌ Actual Error: {e}")

if __name__ == "__main__":
    scrape_ipl_score()
