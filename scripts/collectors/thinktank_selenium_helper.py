#!/usr/bin/env python3
"""
Think Tank Selenium Helper

Provides Selenium-based web scraping as a fallback for sites that block normal HTTP requests.
Uses headless Chrome for minimal resource usage.
"""

import logging
import time
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager


class SeleniumHelper:
    """Helper class for Selenium-based web scraping."""

    def __init__(self, headless: bool = True, timeout: int = 30):
        """
        Initialize Selenium helper.

        Args:
            headless: Run browser in headless mode
            timeout: Default page load timeout in seconds
        """
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        self._init_driver()

    def _init_driver(self):
        """Initialize Chrome WebDriver with appropriate options."""
        try:
            chrome_options = Options()

            if self.headless:
                chrome_options.add_argument('--headless')

            # Common options for stability and anti-detection
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            # Set a realistic user agent
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            # Page load strategy
            chrome_options.page_load_strategy = 'normal'

            # Initialize driver with webdriver-manager
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(self.timeout)

            logging.info("Selenium WebDriver initialized successfully")

        except Exception as e:
            logging.error(f"Failed to initialize Selenium WebDriver: {e}")
            self.driver = None

    def fetch(self, url: str, wait_for_element: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch a URL using Selenium.

        Args:
            url: URL to fetch
            wait_for_element: Optional CSS selector to wait for before returning

        Returns:
            Dict with 'content' (HTML) and 'url' (final URL after redirects), or None if failed
        """
        if not self.driver:
            logging.error("WebDriver not initialized, cannot fetch")
            return None

        try:
            logging.info(f"Selenium fetching: {url}")
            self.driver.get(url)

            # Wait for specific element if requested
            if wait_for_element:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_element))
                    )
                except TimeoutException:
                    logging.warning(f"Timeout waiting for element: {wait_for_element}")
            else:
                # Default wait for body to load
                time.sleep(2)

            # Get page source and final URL
            page_source = self.driver.page_source
            final_url = self.driver.current_url

            logging.info(f"Successfully fetched {url} (final: {final_url})")

            return {
                'content': page_source.encode('utf-8'),
                'text': page_source,
                'url': final_url,
                'status_code': 200  # Selenium doesn't provide actual status code
            }

        except TimeoutException:
            logging.error(f"Timeout loading {url}")
            return None
        except WebDriverException as e:
            logging.error(f"WebDriver error fetching {url}: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error fetching {url}: {e}")
            return None

    def close(self):
        """Close the WebDriver."""
        if self.driver:
            try:
                self.driver.quit()
                logging.info("Selenium WebDriver closed")
            except Exception as e:
                logging.error(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def test_selenium():
    """Test Selenium setup."""
    print("Testing Selenium setup...")

    try:
        with SeleniumHelper(headless=True) as helper:
            # Test fetch
            result = helper.fetch("https://www.google.com")
            if result:
                print(f"✓ Successfully fetched page")
                print(f"  Content length: {len(result['content'])} bytes")
                print(f"  Final URL: {result['url']}")
            else:
                print("✗ Failed to fetch page")
    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nSelenium may not be properly installed.")
        print("To install:")
        print("  1. pip install selenium")
        print("  2. Download ChromeDriver: https://chromedriver.chromium.org/")
        print("  3. Add ChromeDriver to PATH")


if __name__ == "__main__":
    test_selenium()
