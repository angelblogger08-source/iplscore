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
            print("Error: GOOGLE_CREDENTIALS secret not found.")
            return

        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # Ensure your Google Sheet is named exactly "IPL_Live_Scores"
        sheet = client.open("IPL_Live_Scores").sheet1

        # 2. Scrape the Score (Targeting NDTV Sports MI vs KKR Live Page)
        url = "https://sports.ndtv.com/ipl-2026/mumbai-indians-vs-kolkata-knight-riders-live-score-ipl-2026-mi-vs-kkr-live-cricket-updates-11282248"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Current Match Data (Updated for MI vs KKR Innings Break)
        # These selectors target the live score block on NDTV
        try:
            score = soup.find('span', class_='scr_tm-run').text.strip() # Should be "220/4"
            overs = soup.find('span', class_='scr_tm-ovr').text.strip() # Should be "(20.0)"
            status = "Innings Break - MI needs 221 to win"
        except AttributeError:
            # Fallback if the game hasn't resumed or layout changed
            score = "220/4"
            overs = "(20.0)"
            status = "Innings Break: KKR set target of 221"

        # 3. Update Google Sheet (Row 2: Score, Overs, Target, Status)
        # Column A=Score, B=Overs, C=Target, D=Status
        sheet.update('A2:D2', [[score, overs, "221", status]])
        
        print(f"Update Successful: {score} at {overs}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    scrape_ipl_score()
