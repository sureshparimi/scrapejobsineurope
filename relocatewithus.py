import requests
import json
from datetime import datetime

url = 'https://relocate-with-us.github.io/db.json'
headers = {
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'Referer': 'https://relocate-with-us.github.io/',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'sec-ch-ua-platform': '"macOS"',
    'Accept-Encoding': 'gzip, deflate'
}

response = requests.get(url, headers=headers)
data = response.json()

# Extract required information and create new list with filtered data
filtered_data = []
for record in data:
    # Extract only the city and country from the job_location field
    location_parts = record["location"].split(',')
    city_country = location_parts[0].strip()
    
    # Set Visa_sponsorship_available based on the value of "visa"
    visa_sponsorship = record.get("visa", "")
    visa_available = "Yes" if "Visa Sponsorship" in visa_sponsorship else "No"
    
    filtered_record = {
        "Job_location": city_country,
        "Visa_sponsorship_available": visa_available,
        "company_name": record["company"],
        "job_link": record["description"],
        "Job_posted_on": record["post_date"]
    }
    filtered_data.append(filtered_record)

# Convert the post_date value to a sortable datetime format
sorted_data = sorted(filtered_data, key=lambda x: datetime.strptime(x['Job_posted_on'], "%B %d, %Y"), reverse=True)

# Remove duplicate records based on job_link
unique_data = []
job_links = set()
for record in sorted_data:
    if record["job_link"] not in job_links:
        job_links.add(record["job_link"])
        unique_data.append(record)

# Save updated data to relocatewithusjobs.json file
with open('relocatewithusjobs.json', 'w') as f:
    json.dump(unique_data, f, indent=4)

print("Data sorted, extra information removed, and duplicate records removed in relocatewithusjobs.json file.")
