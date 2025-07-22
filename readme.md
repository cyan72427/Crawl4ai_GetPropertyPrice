# Crawl4AI (Promenade Peak Price Extractor)

This project automates the extraction of property pricing data for the **Promenade Peak** condo from [PropertyGuru Singapore](https://www.propertyguru.com.sg/), using `crawl4ai` and a GPT-based LLM.

It:
- Navigates from main page to the listing page
- Simulates user search for the condo
- Waits for the price overview section
- Extracts the sale and rental price ranges
- Saves the output in both JSON and markdown format
- Captures a screenshot of the page

---

## Requirements

Python 3.9+
Install dependencies (recommended in a virtual environment):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

## Run 
python main.py
