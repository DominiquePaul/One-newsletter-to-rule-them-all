import trafilatura
import requests

def get_article(url, cookie):
    # Set up headers to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Cookie': f'fcx_user={cookie}'
    }
    
    # Make the request
    response = requests.get(url, headers=headers)
    
    # Check if request was successful
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to get article. Status code: {response.status_code}")
        return None

if __name__ == "__main__":
    # Article URL and cookie
    url = "https://www.economist.com/business/2025/01/17/tiktoks-time-is-up-can-donald-trump-save-it"
    cookie = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDMzejAwMDAycE1VSjRBQU8iLCJlbnRpdGxlbWVudHMiOlsiVEUuUE9EQ0FTVCIsIlRFLkFQUCIsIlRFLldFQiIsIlRFLk5FV1NMRVRURVIiXSwidXNlclR5cGUiOiJzdWJzY3JpYmVyIiwiZXhwIjoxNzQ1MDAyMjE4LCJpYXQiOjE3MzcyMjI2MTh9.cM2j59GvpDbqS7vIMnLm4PoVrSutpht-lU-HOEPTV6U"
    
    # Get the article content
    content = get_article(url, cookie)
    if content:
        # Extract article content using trafilatura
        text = trafilatura.extract(content)
        if text:
            print("Article content:")
            print(text)
        else:
            print("Could not extract article content")