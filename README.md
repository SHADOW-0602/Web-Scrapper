# Government Email Scraper

Web scraper to extract email addresses from Mongolian government organizations at gov.mn.

## Features

- Scrapes 129+ government organizations
- Extracts emails from organization pages and sub-pages
- Handles Mongolian text encoding
- Exports results to CSV format
- Includes retry mechanism and rate limiting

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Quick Start
```bash
python run_scraper.py
```

### Manual Run
```bash
python gov_mn_scraper.py
```

### Test Connection
```bash
python test_connection.py
```

## Output

Results are saved to `gov_mn_emails.csv` with columns:
- organization: Organization name
- email: Email address
- page_url: Source page URL
- page_type: Type of page (main/sub-page)

## Files

- `gov_mn_scraper.py` - Main scraper script
- `run_scraper.py` - Easy runner with dependency installation
- `test_connection.py` - Connection test utility
- `requirements.txt` - Python dependencies
- `gov_mn_emails.csv` - Output file (generated after run)

## Requirements

- Python 3.6+
- requests
- beautifulsoup4

## Notes

- Respects server limits with 3-second delays
- Handles timeouts and retries automatically
- Filters duplicate emails
- Processes both Mongolian and English text