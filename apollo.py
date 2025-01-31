import requests
import csv

with open('apollo_api.txt', 'r') as f:
    api_key = f.read().strip()

url = "https://api.apollo.io/v1/contacts/search"

params = {
    "api_key": api_key,
    "q_organization_name": "Esperi",  # Search by company domain
    #"q_titles": ["COO"],
    "per_page": 10
}

response = requests.get(url, params=params)
data = response.json()

# Define CSV headers
headers = ['First Name', 'Last Name', 'Primary Phone', 'Phone Number', 'Organization', 'Title', 'Email', 'LinkedIn URL']

# Write to CSV file
with open('apollo_contacts.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(headers)
    
    for contact in data['contacts']:
        primary_phone = contact["primary_phone"]["number"] if "primary_phone" in contact else "-"
        phone_number = contact["phone_numbers"][0]["raw_number"] if len(contact["phone_numbers"]) > 0 else "-"
        
        row = [
            contact["first_name"],
            contact["last_name"], 
            primary_phone,
            phone_number,
            contact["organization_name"],
            contact["title"],
            contact["email"],
            contact["linkedin_url"]
        ]
        writer.writerow(row)

print(f"Contact details have been saved to apollo_contacts.csv")
