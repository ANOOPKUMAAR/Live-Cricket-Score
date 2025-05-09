import requests
from bs4 import BeautifulSoup
import pyodbc
import datetime
import time  # ⬅️ Import time for sleeping
# Connect to SQL Server
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=ANOOP-KUMAR\\SQLEXPRESS;'
    'DATABASE=IPLLiveScores;'
    'Trusted_Connection=yes;'
)
cursor = conn.cursor()
# Create table if not exists
cursor.execute('''
IF NOT EXISTS (
    SELECT * FROM sysobjects WHERE name='MatchScores' AND xtype='U'
)
BEGIN
    CREATE TABLE MatchScores (
        ID INT IDENTITY(1,1) PRIMARY KEY,
        MatchName NVARCHAR(255),
        Score NVARCHAR(255),
        Status NVARCHAR(255),
        [Timestamp] DATETIME  -- ✅ Column added properly
    )
END
''')
conn.commit()
# 🔁 Run scraping every 5 minutes
while True:
    try:
        print("🔄 Fetching latest scores...")
        url = "https://www.cricbuzz.com/cricket-match/live-scores"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        matches = soup.find_all("div", class_="cb-mtch-lst")
        for match in matches:
            match_link_tag = match.find("a")
            if not match_link_tag:
                continue
            match_name = match_link_tag.text.strip()
            match_link = "https://www.cricbuzz.com" + match_link_tag["href"]
            match_page = requests.get(match_link, headers=headers)
            match_soup = BeautifulSoup(match_page.content, "html.parser")
            score_tag = match_soup.find("div", class_="cb-min-bat-rw")
            status_tag = match_soup.find("div", class_="cb-text-live")
            score = score_tag.text.strip() if score_tag else "Not Available"
            status = status_tag.text.strip() if status_tag else "Not Available"
            print(f"🏏 {match_name}")
            print(f"   Score: {score}")
            print(f"   Status: {status}")
            print("-------------")
            # Insert into database
            cursor.execute('''
                INSERT INTO MatchScores (MatchName, Score, Status, Timestamp)
                VALUES (?, ?, ?, ?)
            ''', (match_name, score, status, datetime.datetime.now()))
            conn.commit()
        print("✅ Scores inserted. Waiting 5 minutes...\n")
        time.sleep(300)  # Wait 5 minutes
    except Exception as e:
        print("⚠️ Error occurred:", e)
        time.sleep(300)

