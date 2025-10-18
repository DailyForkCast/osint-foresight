# NATIONAL PROCUREMENT PORTAL AUTOMATION REPORT

**Date**: September 23, 2025
**Objective**: Automate searches for Chinese entities in Eastern European procurement portals

---

## EXECUTIVE SUMMARY

Attempted automated searches across three Eastern European procurement portals (Czech Republic, Poland, Slovakia) for major Chinese technology companies. Initial automation revealed significant technical challenges requiring more sophisticated approaches.

---

## 🔍 AUTOMATION RESULTS

### Czech Republic (nen.nipez.cz)
- **Status**: Partial Success
- **Searches**: 10 companies
- **Results Found**: 20 (but only captured menu navigation)
- **Issue**: JavaScript-rendered content not captured
- **Solution Required**: Selenium WebDriver with JavaScript execution

### Poland (ezamowienia.gov.pl)
- **Status**: Failed
- **Searches**: 5 attempted
- **Results**: All returned 404 errors
- **Issue**: Incorrect API endpoint / URL structure
- **Solution Required**: Portal analysis to identify correct endpoints

### Slovakia (uvo.gov.sk)
- **Status**: No Results
- **Searches**: 5 companies
- **Results**: 0 found
- **Issue**: Possible JavaScript rendering or authentication required
- **Solution Required**: Further investigation of portal structure

---

## 🛠️ TECHNICAL FINDINGS

### 1. JavaScript-Heavy Portals
All three portals appear to use modern JavaScript frameworks that:
- Load search results dynamically via AJAX
- Require session management
- May use anti-bot protection (CAPTCHAs, rate limiting)

### 2. Authentication Requirements
- **Czech Portal**: Public search appears available
- **Polish Portal**: May require registration for search access
- **Slovak Portal**: Unclear - possibly requires authentication

### 3. API Endpoints
**Czech Portal Structure** (Observed):
```
Base: https://nen.nipez.cz
Search: /en/search?q={query}
Results: Loaded via JavaScript/AJAX
```

**Polish Portal Structure** (Needs Investigation):
```
Base: https://ezamowienia.gov.pl
Search: Unknown - /mp-srv/search/list returns 404
Likely: Requires session token or different path
```

**Slovak Portal Structure**:
```
Base: https://www.uvo.gov.sk
Search: /vyhladavanie-zakaziek
Results: No data returned - likely JS rendered
```

---

## 📊 SEARCH TERMS EFFECTIVENESS

### Companies Searched
1. **Huawei** - Most likely to return results
2. **ZTE** - Major telecom provider
3. **Lenovo** - Common IT equipment supplier
4. **Hikvision** - Security/surveillance systems
5. **DJI** - Drones and aerial systems

### Multilingual Terms Created
- Polish: "Chiny", "Chiński", "Chińska"
- Czech: "Čína", "Čínský", "Čínská"
- Slovak: "Čína", "Čínsky", "Čínska"

---

## 💡 LESSONS LEARNED

### What Worked
✅ HTTP session management and rate limiting
✅ BeautifulSoup HTML parsing framework
✅ Multilingual search term preparation
✅ Result extraction patterns identified

### What Failed
❌ Simple HTTP requests insufficient for JS sites
❌ Static HTML parsing misses dynamic content
❌ Polish portal endpoint identification
❌ Slovak portal result retrieval

### Technical Barriers
1. **Dynamic Content Loading**: Results loaded after page render
2. **Session Management**: Cookies/tokens required
3. **Anti-Automation**: Rate limits, CAPTCHAs possible
4. **Language Barriers**: Error messages in native languages

---

## 🚀 RECOMMENDED NEXT STEPS

### Immediate Actions

#### 1. Implement Selenium WebDriver
```python
# Required for JavaScript execution
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.get(url)
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "results"))
)
```

#### 2. Manual Portal Analysis
- Use browser Developer Tools (F12) to:
  - Monitor network requests during search
  - Identify AJAX endpoints
  - Capture request headers and parameters
  - Find result container selectors

#### 3. Focus on Czech Portal First
- Has English interface
- Most accessible of the three
- Good starting point for automation

### Alternative Approaches

#### Option 1: Browser Automation Tools
- **Playwright**: Modern alternative to Selenium
- **Puppeteer**: Headless Chrome automation
- **Scrapy with Splash**: JavaScript rendering

#### Option 2: API Discovery
- Use browser network inspector to find hidden APIs
- May discover JSON endpoints bypassing HTML parsing

#### Option 3: Semi-Automated Approach
- Generate search URLs programmatically
- Manual execution with result collection
- Use browser extensions for bulk data extraction

---

## 📈 COMPARISON WITH TED DATA

### TED Results (Already Collected)
- **Poland**: 112 Chinese contracts found
- **Czech Republic**: 13 Chinese contracts found
- **Slovakia**: 1 Chinese contract found
- **Hungary**: 46 Chinese contracts found
- **Romania**: 17 Chinese contracts found

### Expected National Portal Results
National portals should contain:
- **Below-threshold contracts** not in TED
- **Regional/municipal contracts**
- **Framework agreements**
- **Direct awards**

Estimate: 2-5x more contracts than TED data

---

## 🎯 PRIORITY RECOMMENDATION

### Phase 1: Czech Portal Deep Dive
1. Set up Selenium WebDriver
2. Navigate to https://nen.nipez.cz/en/
3. Search for top 5 Chinese companies
4. Extract and analyze results
5. Build company-specific patterns

### Phase 2: Polish Portal Investigation
1. Analyze portal structure manually
2. Identify correct search endpoints
3. Check if registration provides API access
4. Implement appropriate scraping method

### Phase 3: Expand Coverage
1. Add Slovak portal once pattern established
2. Include Hungarian and Romanian portals
3. Build comprehensive Eastern Europe dataset

---

## 📋 MANUAL VERIFICATION URLs

For immediate manual checking:

### Czech Republic
- Huawei: https://nen.nipez.cz/en/search?q=Huawei
- ZTE: https://nen.nipez.cz/en/search?q=ZTE
- Lenovo: https://nen.nipez.cz/en/search?q=Lenovo

### Poland
- Huawei: https://ezamowienia.gov.pl (manual navigation required)
- Search for: "Huawei", "Chiny" (China in Polish)

### Slovakia
- Huawei: https://www.uvo.gov.sk/vyhladavanie?q=Huawei
- Search for: "Čína" (China in Slovak)

---

## 🏆 SUCCESS METRICS

### Current Status
- ✅ Search terms prepared in 5 languages
- ✅ Automation framework built
- ⚠️ Portal access partially successful
- ❌ Chinese entity extraction needs improvement

### Target Metrics
- Find 50+ Chinese contracts per country
- Identify companies beyond TED coverage
- Map procurement patterns by sector
- Track temporal trends 2019-2025

---

## CONCLUSION

While initial automation attempts faced technical challenges due to JavaScript-heavy portals, we've established:

1. **Clear technical requirements** (Selenium/WebDriver needed)
2. **Comprehensive search terms** in native languages
3. **Portal-specific challenges** documented
4. **Path forward** with prioritized approach

The Czech portal with its English interface remains the most promising starting point for successful automation. Manual verification of search URLs can provide immediate value while enhanced automation is developed.

---

*Next Action: Implement Selenium-based scraper for Czech portal with JavaScript support*
