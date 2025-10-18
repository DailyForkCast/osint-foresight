#!/usr/bin/env python3
"""
Focused scraper for Czech procurement portal with visible browser for debugging.
"""

import logging
import json
import time
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def scrape_czech_portal_visible():
    """Scrape Czech portal with visible browser for debugging"""

    logger.info("Setting up Chrome WebDriver (VISIBLE mode for debugging)...")

    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    results = []

    try:
        # Navigate to Czech portal
        url = "https://nen.nipez.cz/en/"
        logger.info(f"Opening {url}")
        driver.get(url)

        logger.info("Waiting for page to load...")
        time.sleep(5)

        # Accept cookies if present
        try:
            cookie_button = driver.find_element(By.XPATH, "//button[contains(@class, 'cookie') or contains(text(), 'Accept')]")
            cookie_button.click()
            logger.info("Cookies accepted")
            time.sleep(2)
        except:
            logger.info("No cookie banner found")

        # Search for Chinese companies
        search_terms = ['Huawei', 'Lenovo', 'ZTE']

        for term in search_terms:
            logger.info(f"\nSearching for: {term}")

            # Navigate directly to search URL
            search_url = f"https://nen.nipez.cz/en/search?q={term}"
            logger.info(f"Navigating to: {search_url}")
            driver.get(search_url)

            logger.info("Waiting for search results...")
            time.sleep(5)

            # Take screenshot for debugging
            screenshot_file = f"data/screenshots/czech_{term}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            Path("data/screenshots").mkdir(parents=True, exist_ok=True)
            driver.save_screenshot(screenshot_file)
            logger.info(f"Screenshot saved: {screenshot_file}")

            # Try multiple ways to find results
            logger.info("Looking for results...")

            # Method 1: Look for any divs with substantial text
            try:
                all_divs = driver.find_elements(By.TAG_NAME, "div")
                for div in all_divs:
                    text = div.text.strip()
                    if len(text) > 100 and term.lower() in text.lower():
                        logger.info(f"Found potential result: {text[:200]}...")
                        results.append({
                            'search_term': term,
                            'text': text[:1000],
                            'country': 'CZ',
                            'portal': 'nen.nipez.cz',
                            'timestamp': datetime.now().isoformat()
                        })
                        break
            except Exception as e:
                logger.error(f"Error extracting results: {e}")

            # Method 2: Look for tables
            try:
                tables = driver.find_elements(By.TAG_NAME, "table")
                if tables:
                    logger.info(f"Found {len(tables)} tables")
                    for table in tables:
                        text = table.text.strip()
                        if text and len(text) > 50:
                            logger.info(f"Table content: {text[:200]}...")
                            results.append({
                                'search_term': term,
                                'text': text[:1000],
                                'type': 'table',
                                'country': 'CZ',
                                'portal': 'nen.nipez.cz',
                                'timestamp': datetime.now().isoformat()
                            })
            except:
                pass

            # Method 3: Get full page text
            body_text = driver.find_element(By.TAG_NAME, "body").text
            if "No results" in body_text or "0 results" in body_text:
                logger.info(f"No results found for {term}")
            else:
                logger.info(f"Page contains text (length: {len(body_text)} chars)")

                # Look for procurement-related keywords
                keywords = ['contract', 'tender', 'procurement', 'supplier', 'vendor', 'award']
                for keyword in keywords:
                    if keyword in body_text.lower():
                        logger.info(f"  Found keyword: {keyword}")

        logger.info("\nPress Enter in the console to close the browser...")
        input()  # Keep browser open for manual inspection

    except Exception as e:
        logger.error(f"Fatal error: {e}")

    finally:
        driver.quit()
        logger.info("Browser closed")

        # Save results
        if results:
            output_file = f"data/processed/czech_debug/results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            Path("data/processed/czech_debug").mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

            logger.info(f"Saved {len(results)} results to {output_file}")

        return results

if __name__ == "__main__":
    logger.info("\n" + "="*70)
    logger.info("CZECH PORTAL VISIBLE BROWSER DEBUGGING")
    logger.info("Browser will remain open for inspection")
    logger.info("="*70)

    results = scrape_czech_portal_visible()

    print("\n" + "="*70)
    print("SUMMARY")
    print(f"Total results extracted: {len(results)}")
    print("="*70)
