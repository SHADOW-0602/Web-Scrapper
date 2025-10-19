import requests
from bs4 import BeautifulSoup
import csv
import re
import time
from urllib.parse import urljoin, urlparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GovMnScraper:
    def __init__(self):
        self.base_url = "https://www.gov.mn"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.emails_data = []
        
    def get_page(self, url, retries=3):
        """Get page content with retry mechanism"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=30, allow_redirects=True)
                response.raise_for_status()
                # Handle encoding properly
                response.encoding = response.apparent_encoding or 'utf-8'
                return response
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(5)
                else:
                    logger.error(f"Failed to fetch {url} after {retries} attempts")
                    return None
    
    def extract_emails(self, text):
        """Extract email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, text)
    
    def get_organization_links(self):
        """Get all organization links from the main page"""
        logger.info("Fetching organization links from main page...")
        response = self.get_page("https://www.gov.mn/mn/organization")
        
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        org_links = []
        
        # Find organization links - adjust selectors based on actual page structure
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href and ('/organization/' in href and href != '/mn/organization'):
                full_url = urljoin(self.base_url, href)
                org_name = link.get_text(strip=True)
                if org_name and len(org_name) > 2 and full_url not in [item[1] for item in org_links]:
                    org_links.append((org_name, full_url))
        
        logger.info(f"Found {len(org_links)} organization links")
        return org_links
    
    def scrape_organization_pages(self, org_name, org_url):
        """Scrape all pages within an organization for emails"""
        logger.info(f"Scraping organization: {org_name}")
        
        # Get main organization page
        response = self.get_page(org_url)
        if not response:
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract emails from main page
        page_text = soup.get_text()
        emails = self.extract_emails(page_text)
        
        for email in emails:
            self.emails_data.append({
                'organization': org_name,
                'page_url': org_url,
                'email': email,
                'page_type': 'main'
            })
        
        # Find internal links within the organization
        internal_links = set()
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href:
                full_url = urljoin(org_url, href)
                # Check if it's an internal link to the same organization
                if self.base_url in full_url and org_url in full_url:
                    internal_links.add((link.get_text(strip=True), full_url))
        
        # Scrape internal pages
        for page_name, page_url in internal_links:
            if page_url == org_url:  # Skip if it's the same as main page
                continue
                
            logger.info(f"  Scraping sub-page: {page_name}")
            time.sleep(1)  # Be respectful to the server
            
            response = self.get_page(page_url)
            if response:
                soup = BeautifulSoup(response.content, 'html.parser')
                page_text = soup.get_text()
                emails = self.extract_emails(page_text)
                
                for email in emails:
                    self.emails_data.append({
                        'organization': org_name,
                        'page_url': page_url,
                        'email': email,
                        'page_type': page_name or 'sub-page'
                    })
    
    def save_to_csv(self, filename='gov_mn_emails.csv'):
        """Save extracted emails to CSV file"""
        if not self.emails_data:
            logger.warning("No emails found to save")
            return
        
        # Remove duplicates
        unique_emails = []
        seen = set()
        for item in self.emails_data:
            key = (item['organization'], item['email'])
            if key not in seen:
                seen.add(key)
                unique_emails.append(item)
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['organization', 'email', 'page_url', 'page_type']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for item in unique_emails:
                writer.writerow(item)
        
        logger.info(f"Saved {len(unique_emails)} unique emails to {filename}")
    
    def run(self):
        """Main scraping process"""
        logger.info("Starting government organization email scraper...")
        
        # Get organization links
        org_links = self.get_organization_links()
        
        if not org_links:
            logger.error("No organization links found")
            return
        
        # Scrape each organization
        for i, (org_name, org_url) in enumerate(org_links, 1):
            logger.info(f"Processing {i}/{len(org_links)}: {org_name}")
            try:
                self.scrape_organization_pages(org_name, org_url)
                time.sleep(3)  # Be respectful to the server
            except Exception as e:
                logger.error(f"Error processing {org_name}: {e}")
                continue
        
        # Save results
        self.save_to_csv()
        logger.info("Scraping completed!")

if __name__ == "__main__":
    scraper = GovMnScraper()
    scraper.run()