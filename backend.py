from bottle import route, run, template, request, response
import requests
import json
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--global', default=None, action='store_true', help='Use 0.0.0.0 instead of localhost')
parser.add_argument('--port', default=9999, type=int, help='Port to run the server on')
args = parser.parse_args()

# Set host based on args
HOST = '0.0.0.0' if getattr(args, 'global') else 'localhost'
PORT = args.port

# Load Apollo API key
with open('apollo_api.txt', 'r') as f:
    api_key = f.read().strip()

@route('/')
def home():
    return template('index.html')

@route('/search_contacts', method='POST')
def search_contacts():
    data = request.json
    
    # Get search parameters from request
    company_name = data.get('company_name', '')
    titles = data.get('titles', [])
    max_results = data.get('max_results', 10)
    
    # Call Apollo API
    url = "https://api.apollo.io/v1/mixed_people/search"
    params = {
        "api_key": api_key,
        "q_organization_name": company_name,
        "per_page": max_results,
    }
    
    if titles:
        params["q_titles"] = titles
        
    try:
        apollo_response = requests.get(url, params=params)
        apollo_data = apollo_response.json()
        
        # Format response data
        contacts = []
        for contact in apollo_data['people']:
            person_id = contact.get("id", "-")
            unlocked_details = unlock_contact_details(person_id)
            primary_phone = contact.get("primary_phone", {}).get("number", "-")
            phone_number = contact.get("phone_numbers", [{}])[0].get("raw_number", "-") if contact.get("phone_numbers") else "-"
            
            contacts.append({
                "name": (contact.get("first_name") or "-") + " " + (contact.get("last_name") or "-"),
                "primary_phone": primary_phone,
                "phone_number": phone_number,
                "organization": contact.get("organization", {}).get("name", "-"),
                "title": contact.get("title", "-"),
                "email": unlocked_details["email"],
                "linkedin_url": contact.get("linkedin_url", "-")
            })
            
        response.content_type = 'application/json'
        return json.dumps(contacts)
        
    except Exception as e:
        response.status = 500
        return json.dumps({"error": str(e)})


def unlock_contact_details(person_id):
    url = "https://api.apollo.io/v1/people/match"

    payload = {
        "api_key": api_key,
        "id": person_id,  # Contact's Apollo ID
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

        data = response.json()
        contact = data.get("person", {})
        print(contact)

        # Extract unlocked details
        email = contact.get("email", "-")
        phone = contact.get("phone_number", "-")

        return {"email": email, "phone": phone}

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

if __name__ == '__main__':
    run(host=HOST, port=PORT, debug=True)
