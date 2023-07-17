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

# Extract city and country from location and remove extra characters
for record in data:
    location = record['location']
    city_country = ' '.join(location.split()[0:2])
    record['location'] = city_country

# Convert the post_date value to a sortable datetime format
sorted_data = sorted(data, key=lambda x: datetime.strptime(x['post_date'], "%B %d, %Y"), reverse=True)

# Load existing data from relocatewithusjobs.json file if it exists
existing_data = []
try:
    with open('relocatewithusjobs.json', 'r') as f:
        existing_data = json.load(f)
except FileNotFoundError:
    pass

# Remove duplicate records from existing data (if any)
filtered_data = [record for record in existing_data if record not in sorted_data]

# Append sorted_data to filtered_data
updated_data = sorted_data + filtered_data

# Save updated data to JSON file
with open('relocatewithusjobs.json', 'w') as f:
    json.dump(updated_data, f, indent=4)

print("Data sorted, extra characters removed, and appended to relocatewithusjobs.json file.")
