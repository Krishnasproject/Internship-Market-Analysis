import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os

# Categories including both Data Science and Web Development
categories = [
    "data-science", "machine-learning", "data-analytics", 
    "artificial-intelligence-ai", "web-development", 
    "front-end-development", "backend-development", 
    "full-stack-development", "node-js-development", 
    "reactjs-development", "php-development"
]

all_new_internships = []
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

for cat in categories:
    print(f"\n--- Scraping Category: {cat} ---")
    base_url = f"https://internshala.com/internships/{cat}-internship"
    
    for page in range(1, 16):
        url = f"{base_url}/page-{page}"
        print(f"Scraping Page {page}...")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            cards = soup.find_all("div", class_="individual_internship")
            
            if not cards:
                break
                
            for card in cards:
                try:
                    title_tag = card.find("a", class_="job-title-href")
                    company_tag = card.find("p", class_="company-name")
                    location_tag = card.find("div", class_="locations")
                    raw_text = card.get_text(separator='|', strip=True)
                    
                    all_new_internships.append({
                        "job_title": title_tag.get_text(strip=True) if title_tag else "Unknown",
                        "company": company_tag.get_text(strip=True) if company_tag else "Unknown",
                        "location": location_tag.get_text(strip=True) if location_tag else "Remote",
                        "raw_content": raw_text,
                        "job_url": "https://internshala.com" + title_tag["href"] if title_tag else None,
                        "category": cat
                    })
                except Exception:
                    continue

            # Sleep timer to prevent detection/blocking
            time.sleep(random.uniform(1, 4))
        except Exception as e:
            print(f"Error on {url}: {e}")
            break

# Merging with existing data and removing duplicates
file_path = "cleaned_internship_data.csv"
df_new = pd.DataFrame(all_new_internships)

if os.path.exists(file_path):
    df_old = pd.read_csv(file_path)
    df_combined = pd.concat([df_old, df_new], ignore_index=True)
    
    # Remove duplicates to ensure clean data for analysis
    df_combined.drop_duplicates(subset=['job_url'], keep='first', inplace=True)
    
    df_combined.to_csv(file_path, index=False)
    print(f"\n✅ Dataset updated! Total unique rows: {len(df_combined)}")
else:
    df_new.to_csv(file_path, index=False)
    print(f"✅ Created new file with {len(df_new)} rows.")