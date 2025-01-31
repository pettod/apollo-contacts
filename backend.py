from bottle import route, run, template, request, response
import requests
import json

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
    url = "https://api.apollo.io/v1/contacts/search"
    params = {
        "api_key": api_key,
        "q_organization_name": company_name,
        "per_page": max_results
    }
    
    if titles:
        params["q_titles"] = titles
        
    try:
        apollo_response = requests.get(url, params=params)
        apollo_data = apollo_response.json()
        
        # Format response data
        contacts = []
        for contact in apollo_data['contacts']:
            primary_phone = contact.get("primary_phone", {}).get("number", "-")
            phone_number = contact.get("phone_numbers", [{}])[0].get("raw_number", "-") if contact.get("phone_numbers") else "-"
            
            contacts.append({
                "first_name": contact.get("first_name", "-"),
                "last_name": contact.get("last_name", "-"),
                "primary_phone": primary_phone,
                "phone_number": phone_number,
                "organization": contact.get("organization_name", "-"),
                "title": contact.get("title", "-"),
                "email": contact.get("email", "-"),
                "linkedin_url": contact.get("linkedin_url", "-")
            })
            
        response.content_type = 'application/json'
        return json.dumps(contacts)
        
    except Exception as e:
        response.status = 500
        return json.dumps({"error": str(e)})

if __name__ == '__main__':
    run(host='localhost', port=8080, debug=True)
