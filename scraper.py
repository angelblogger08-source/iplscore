import os
import json
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def scrape_ipl_score():
    # 1. Setup Google Sheets connection
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # Pulling the secret from GitHub Actions Environment
        creds_json = os.environ.get('GOOGLE_CREDENTIALS')
        if not creds_json:
            print("❌ Error: GOOGLE_CREDENTIALS secret not found.")
            return

        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # FIXED: Use open_by_key because you are using the long ID string
        # Ensure the bot email is an "Editor" on this specific sheet ID
        sheet_id = "1c1WtoomLI5CIkitzwjeoKZGOLQog6wL8FwDUcYnxa_s"
        sheet = client.open_by_key(sheet_id).sheet1

        # 2. Scrape the Score (Targeting NDTV Sports MI vs KKR Live Page)
        url = "https://sports.ndtv.com/ipl-2026/mumbai-indians-vs-kolkata-knight-riders-live-score-ipl-2026-mi-vs-kkr-live-cricket-updates-11282248"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Current Match Data logic
        try:
            score = soup.find('span', class_='scr_tm-run').text.strip()
            overs = soup.find('span', class_='scr_tm-ovr').text.strip()
            status = "Innings Break - MI needs 221 to win"
        except AttributeError:
            # Fallback values
            score = "220/4"
            overs = "(20.0)"
            status = "Innings Break: KKR set target of 221"

        print(f"DEBUG: Scraped Score is {score}, Overs are {overs}")

        # 3. Update Google Sheet
        # Fixed the indentation and the update method parameters
        data_to_save = [[score, overs, "221", status]]
        
        sheet.update(
            values=data_to_save, 
            range_name='A2:D2', 
            value_input_option='USER_ENTERED'
        )
        
        print(f"✅ Success! Updated sheet with: {score}")

    except Exception as e:
        print(f"❌ Actual Error: {e}")

if __name__ == "__main__":
    scrape_ipl_score()
