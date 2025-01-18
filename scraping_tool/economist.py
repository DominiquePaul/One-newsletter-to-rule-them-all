import requests

def get_economist_article(url):
    # Set up session with your login credentials
session = requests.Session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    # Add any required headers
}

# Use your actual login credentials
login_data = {
    'email-address': 'dominique.paul.info@gmail.com',
    'password': 'Polybahn1855'
}

# Login first
login_url = 'https://myaccount.economist.com/api/auth/'
r = session.post(login_url, data=login_data, headers=headers)

r.text
# Now fetch the article using your authenticated session
response = session.get(url, headers=headers)
return response.text

# Example usage
article_url = 'https://www.economist.com/your-article-url'
content = get_economist_article(article_url)