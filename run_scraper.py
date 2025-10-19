#!/usr/bin/env python3
"""
Simple runner script for the government email scraper
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        return False
    return True

def run_scraper():
    """Run the main scraper"""
    print("Starting the government email scraper...")
    try:
        from gov_mn_scraper import GovMnScraper
        scraper = GovMnScraper()
        scraper.run()
        print("\nScraping completed! Check 'gov_mn_emails.csv' for results.")
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure all requirements are installed.")
    except Exception as e:
        print(f"Error running scraper: {e}")

if __name__ == "__main__":
    print("Government Organization Email Scraper")
    print("=" * 40)
    
    # Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        print("requirements.txt not found!")
        sys.exit(1)
    
    # Install requirements
    if install_requirements():
        print("\n" + "=" * 40)
        run_scraper()
    else:
        print("Failed to install requirements. Please install manually:")
        print("pip install requests beautifulsoup4 lxml")