import os
import requests
import trafilatura
import json

def get_fcx_token(session):
    """Get FCX user token after successful login"""
    
    # Check if we have all required auth cookies
    required_cookies = [
        'fcx_access_token',
        'fcx_refresh_token',
        'fcx_access_state',
        'fcx_contact_id',
        'economist_piano_id',
        'economist_auth_complete',
        'login_callback',
        'wall_session'
    ]
    
    current_cookies = session.cookies.get_dict()
    print("\nCurrent cookies before refresh:")
    for name, value in current_cookies.items():
        print(f"{name}: {value}")
    
    missing_cookies = [cookie for cookie in required_cookies if not current_cookies.get(cookie)]
    if missing_cookies:
        raise Exception(f"Missing required cookies: {missing_cookies}")
    
    # Set additional required cookies if not present
    additional_cookies = {
        'fcx_auth_type': 'fcx',
        'state-is-subscriber': 'true',
        '_consentT': 'true'
    }
    
    for name, value in additional_cookies.items():
        if not session.cookies.get(name):
            session.cookies.set(name, value, domain='.economist.com')
    
    refresh_headers = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Referer": "https://www.economist.com/business/2025/01/17/tiktoks-time-is-up-can-donald-trump-save-it",
        "DNT": "1",
        "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin"
    }
    
    # Prepare request with cookies explicitly shown
    request = requests.Request('GET', 
                             "https://www.economist.com/api/auth/refresh",
                             headers=refresh_headers,
                             cookies=session.cookies.get_dict())
    prepared = request.prepare()
    
    print("\nRequest details:")
    print("Headers:", prepared.headers)
    print("\nCookie header:", prepared.headers.get('Cookie'))
    
    # Send the request
    refresh_response = session.send(prepared)
    
    if refresh_response.status_code != 200:
        print(f"\nRefresh request failed with status {refresh_response.status_code}")
        print("Response:", refresh_response.text)
        raise Exception("Failed to refresh FCX token")
    
    fcx_user = refresh_response.cookies.get('fcx_user') or session.cookies.get('fcx_user')
    
    if not fcx_user:
        raise Exception("Failed to get fcx_user token")
    
    print("Successfully obtained fcx_user token")
    return fcx_user

def login(session, email, password):
    """Login to economist.com and get authentication tokens"""
    
    # Common headers for all requests
    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://myaccount.economist.com",
        "Referer": "https://myaccount.economist.com/s/login/",
        "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "DNT": "1"
    }
    
    # Step 1: Initial auth check
    data1 = {
        "message": '{"actions":[{"id":"6;a","descriptor":"apex://CommunitySsoAuthController_LT/ACTION$getSsoAuth","callingDescriptor":"markup://c:loginForm","params":{"ssoProvider":"WT","startUrl":"/setup/secur/RemoteAccessAuthorizationPage.apexp?source=CAAAAZR_v4DPMDAwMDAwMDAwMDAwMDAwAAAA_POrU9PQ2VokKCHPXpeh3MrQ2MxMOIHXzf0nbqUaDcYKrLy5Np1PL36FxuHIB_6TB5rSYonE_uYdF1gzTNp-DuCNc8CObEbd2QfiCvsc0pmox4kn74fq5RVG7SnMMq3yJq0OCWDoTVdnfOKFbKV-faSqdu9DFmB2aCSCo0ukFOzTcMDysdLKM5wQYtzyoOBbyHAI3BNjeKhAKLKuOrtOJgrRU0XkwQ3Mfpsg3f03T72QeYOYcdvgZyBdR1NOlbZgz4MzpcUykbY2pM8XlwaaY8IM5KNVbh2J2ysOAbP-NUajTn6ufJjjimDz8y_lOLwVRxzD9-9QQG76jkfvUPZ4e0N5YVOHZustwVM4llMxgpttJKj5_nzcl1mN2NTPC6Kx8io8OGEhn9cduy4yWWElilcrGYt4tUW2fZj0NrLTYgRBlgRtnb2VFyATxfYiWKvJw8K7VgRcujReIt9oJ9oCD7tOMJ2Bpd4a1gOlXHxW71KfNNLuUonZoc1YC-BKB3wjN4_f82jyFoGfSPRJIDk7lWsbzFbN2fChwMfJ0iUs3uVIjhG8tczSbWJZD2VMeo-BTn2qOHfq3yHdkxLCyH9nCIVAuLH8VrYkNHQMFwlDhiTgdS9qExRDQqMwxO4ot2tIFFkHRAa823YSy5UAep_LQt2vIL2MYAh5x1LF7CtJPkIKx1uj_xZJnArQs0LRaqQzlP0vjS8-dEWkGkFAS1ANVWgokclA6p03aq0f7T1eHOk9EJ_v-2dtwPyEi9V7tLCs9A%3D%3D"}}]}',
        "aura.context": '{"mode":"PROD","fwuid":"","app":"siteforce:communityApp","loaded":{"APPLICATION@markup://siteforce:communityApp":""},"dn":[],"globals":{},"uad":false}',
        "aura.pageURI": "/s/login/",
        "aura.token": "null"
    }
    
    # Step 2: SSO auth
    data2 = {
        "message": '{"actions":[{"id":"7;a","descriptor":"apex://PartnerSsoProvider/ACTION$getSsoAuth","callingDescriptor":"markup://c:loginForm","params":{"ssoProvider":"WT","startUrl":"/setup/secur/RemoteAccessAuthorizationPage.apexp?source=CAAAAZR_v4DPMDAwMDAwMDAwMDAwMDAwAAAA_POrU9PQ2VokKCHPXpeh3MrQ2MxMOIHXzf0nbqUaDcYKrLy5Np1PL36FxuHIB_6TB5rSYonE_uYdF1gzTNp-DuCNc8CObEbd2QfiCvsc0pmox4kn74fq5RVG7SnMMq3yJq0OCWDoTVdnfOKFbKV-faSqdu9DFmB2aCSCo0ukFOzTcMDysdLKM5wQYtzyoOBbyHAI3BNjeKhAKLKuOrtOJgrRU0XkwQ3Mfpsg3f03T72QeYOYcdvgZyBdR1NOlbZgz4MzpcUykbY2pM8XlwaaY8IM5KNVbh2J2ysOAbP-NUajTn6ufJjjimDz8y_lOLwVRxzD9-9QQG76jkfvUPZ4e0N5YVOHZustwVM4llMxgpttJKj5_nzcl1mN2NTPC6Kx8io8OGEhn9cduy4yWWElilcrGYt4tUW2fZj0NrLTYgRBlgRtnb2VFyATxfYiWKvJw8K7VgRcujReIt9oJ9oCD7tOMJ2Bpd4a1gOlXHxW71KfNNLuUonZoc1YC-BKB3wjN4_f82jyFoGfSPRJIDk7lWsbzFbN2fChwMfJ0iUs3uVIjhG8tczSbWJZD2VMeo-BTn2qOHfq3yHdkxLCyH9nCIVAuLH8VrYkNHQMFwlDhiTgdS9qExRDQqMwxO4ot2tIFFkHRAa823YSy5UAep_LQt2vIL2MYAh5x1LF7CtJPkIKx1uj_xZJnArQs0LRaqQzlP0vjS8-dEWkGkFAS1ANVWgokclA6p03aq0f7T1eHOk9EJ_v-2dtwPyEi9V7tLCs9A%3D%3D"}}]}',
        "aura.context": '{"mode":"PROD","fwuid":"","app":"siteforce:communityApp","loaded":{"APPLICATION@markup://siteforce:communityApp":""},"dn":[],"globals":{},"uad":false}',
        "aura.pageURI": "/s/login/",
        "aura.token": "null"
    }
    
    # Step 3: Get prospect
    data3 = {
        "message": '{"actions":[{"id":"8;a","descriptor":"apex://LoginFormController_LT/ACTION$getProspect","callingDescriptor":"markup://c:loginForm","params":{"email":"' + email + '"}}]}',
        "aura.context": '{"mode":"PROD","fwuid":"","app":"siteforce:communityApp","loaded":{"APPLICATION@markup://siteforce:communityApp":""},"dn":[],"globals":{},"uad":false}',
        "aura.pageURI": "/s/login/",
        "aura.token": "null"
    }
    
    # Step 4: Login
    data4 = {
        "message": '{"actions":[{"id":"9;a","descriptor":"apex://LoginFormController_LT/ACTION$login","callingDescriptor":"markup://c:loginForm","params":{"username":"' + email + '","password":"' + password + '","startUrl":"/setup/secur/RemoteAccessAuthorizationPage.apexp?source=CAAAAZR_v4DPMDAwMDAwMDAwMDAwMDAwAAAA_POrU9PQ2VokKCHPXpeh3MrQ2MxMOIHXzf0nbqUaDcYKrLy5Np1PL36FxuHIB_6TB5rSYonE_uYdF1gzTNp-DuCNc8CObEbd2QfiCvsc0pmox4kn74fq5RVG7SnMMq3yJq0OCWDoTVdnfOKFbKV-faSqdu9DFmB2aCSCo0ukFOzTcMDysdLKM5wQYtzyoOBbyHAI3BNjeKhAKLKuOrtOJgrRU0XkwQ3Mfpsg3f03T72QeYOYcdvgZyBdR1NOlbZgz4MzpcUykbY2pM8XlwaaY8IM5KNVbh2J2ysOAbP-NUajTn6ufJjjimDz8y_lOLwVRxzD9-9QQG76jkfvUPZ4e0N5YVOHZustwVM4llMxgpttJKj5_nzcl1mN2NTPC6Kx8io8OGEhn9cduy4yWWElilcrGYt4tUW2fZj0NrLTYgRBlgRtnb2VFyATxfYiWKvJw8K7VgRcujReIt9oJ9oCD7tOMJ2Bpd4a1gOlXHxW71KfNNLuUonZoc1YC-BKB3wjN4_f82jyFoGfSPRJIDk7lWsbzFbN2fChwMfJ0iUs3uVIjhG8tczSbWJZD2VMeo-BTn2qOHfq3yHdkxLCyH9nCIVAuLH8VrYkNHQMFwlDhiTgdS9qExRDQqMwxO4ot2tIFFkHRAa823YSy5UAep_LQt2vIL2MYAh5x1LF7CtJPkIKx1uj_xZJnArQs0LRaqQzlP0vjS8-dEWkGkFAS1ANVWgokclA6p03aq0f7T1eHOk9EJ_v-2dtwPyEi9V7tLCs9A%3D%3D"}}]}',
        "aura.context": '{"mode":"PROD","fwuid":"","app":"siteforce:communityApp","loaded":{"APPLICATION@markup://siteforce:communityApp":""},"dn":[],"globals":{},"uad":false}',
        "aura.pageURI": "/s/login/",
        "aura.token": "null"
    }
    
    base_url = "https://myaccount.economist.com/s/sfsites/aura"
    data_sequence = [data1, data2, data3, data4]
    endpoints = [
        "?r=6&aura.ApexAction.execute=1&aura.Component.reportFailedAction=1",
        "?r=7&aura.ApexAction.execute=1",
        "?r=8&aura.ApexAction.execute=1",
        "?r=9&aura.ApexAction.execute=1"
    ]
    
    # Execute login sequence
    for endpoint, data in zip(endpoints, data_sequence):
        response = session.post(
            base_url + endpoint,
            headers=headers,
            data=data
        )
        print("\nCookies after request:")
        for cookie in session.cookies:
            print(f"  {cookie.name}: {cookie.value}")
        if response.status_code != 200:
            raise Exception(f"Login step failed with status {response.status_code}: {response.text}")
        print(f"Login step completed successfully")
    
    # After successful login, we need to:
    # 1. Visit an article page first
    article_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Referer": "https://www.economist.com/",
        "DNT": "1"
    }
    
    article_response = session.get(
        "https://www.economist.com/business/2025/01/17/tiktoks-time-is-up-can-donald-trump-save-it",
        headers=article_headers
    )
    print("Article page cookies:", session.cookies.get_dict())
    
    # 2. Then make the refresh request
    refresh_headers = {
        "Accept": "*/*",
        'authority': 'www.economist.com',
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Referer": "https://www.economist.com/business/2025/01/17/tiktoks-time-is-up-can-donald-trump-save-it",
        "DNT": "1",
        "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"'
    }
    
    refresh_response = session.get(
        "https://www.economist.com/api/auth/refresh",
        headers=refresh_headers
    )
    print("Refresh response cookies:", refresh_response.cookies.get_dict())
    
    # Try to get fcx_user from either the refresh response or session cookies
    fcx_user = refresh_response.cookies.get('fcx_user') or session.cookies.get('fcx_user')
    
    if not fcx_user:
        raise Exception("Failed to get fcx_user token")
    
    print("Successfully obtained fcx_user token")
    return fcx_user

def scrape_article(url, session):
    """Scrape an article with proper authentication"""
    # Refresh token before each article request
    fcx_token = get_fcx_token(session)
    if fcx_token:
        session.cookies.set('fcx_user', fcx_token, domain='.economist.com')
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.economist.com/'
    }
    
    response = session.get(url, headers=headers)
    return response.text

# Main execution
try:
    username = os.getenv('ECONOMIST_EMAIL')
    password = os.getenv('ECONOMIST_PASSWORD')
    
    if not username or not password:
        raise ValueError("Missing ECONOMIST_EMAIL or ECONOMIST_PASSWORD environment variables")

    session = requests.Session()
    fcx_user = login(session, username, password)
    session.cookies.set('fcx_user', fcx_user, domain='.economist.com')

    print("Successfully logged in to The Economist")

    protected_url = "https://www.economist.com/business/2025/01/17/tiktoks-time-is-up-can-donald-trump-save-it"
    article_html = scrape_article(protected_url, session)
    text = trafilatura.extract(article_html)
    
    if not text:
        raise Exception("Failed to extract article content")
        
    print("\nArticle content:")
    print("-" * 80)
    print(text)
    print("-" * 80)

except Exception as e:
    print(f"Error: {str(e)}")
    raise
