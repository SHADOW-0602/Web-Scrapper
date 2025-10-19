import requests
from bs4 import BeautifulSoup
import time

def test_website_access():
    """Test if we can access the government website"""
    url = "https://www.gov.mn/mn/organization"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive'
    }
    
    try:
        print(f"Testing connection to: {url}")
        response = requests.get(url, headers=headers, timeout=60)
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.content)}")
        
        if response.status_code == 200:
            # Handle encoding properly
            response.encoding = response.apparent_encoding or 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.title.string if soup.title else 'No title found'
            print(f"Title: {title.encode('ascii', 'ignore').decode('ascii')}")
            
            # Look for organization links
            links = soup.find_all('a', href=True)
            org_links = []
            for link in links:
                href = link.get('href')
                text = link.get_text(strip=True)
                if href and ('organization' in href.lower() or 'байгууллага' in href.lower()):
                    org_links.append((text, href))
            
            print(f"Found {len(org_links)} potential organization links")
            for i, (text, href) in enumerate(org_links[:10]):  # Show first 10
                safe_text = text.encode('ascii', 'ignore').decode('ascii')
                print(f"  {i+1}. {safe_text[:50]}... -> {href}")
            
            return True
        else:
            print(f"Failed with status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_website_access()