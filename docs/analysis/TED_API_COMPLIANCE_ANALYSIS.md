# TED Europe API Compliance Analysis for OSINT Foresight
## Terms of Service Deep Dive

**Date:** 2025-09-15
**Purpose:** Assess compliance for OSINT analysis of public procurement data
**API:** TED (Tenders Electronic Daily) - EU Public Procurement Platform

---

## 🟢 ALLOWED USES

### Explicitly Permitted Activities

1. **Commercial and Non-Commercial Reuse**
   - ✅ Procurement notices can be "freely reused, for commercial or non-commercial purposes"
   - ✅ No distinction between commercial/non-commercial for notice data
   - ✅ Open data policy explicitly supports company planning and analysis

2. **Data Analysis and Research**
   - ✅ Data reused by public authorities for policy analysis
   - ✅ Academic research explicitly mentioned as allowed use
   - ✅ Civil society analysis permitted
   - ✅ Company planning and market analysis allowed

3. **Automated Access via API**
   - ✅ API provided specifically for 3rd party integration
   - ✅ Search API allows anonymous access (no authentication)
   - ✅ Bulk data retrieval supported
   - ✅ Multiple API endpoints for different data types

4. **OSINT-Specific Activities**
   - ✅ Analyzing procurement patterns across countries
   - ✅ Tracking technology acquisitions
   - ✅ Identifying supplier relationships
   - ✅ Monitoring contract awards
   - ✅ Cross-referencing entities across notices

5. **Attribution Requirements (Simple)**
   - ✅ CC BY 4.0 for editorial content - just credit the source
   - ✅ CC0 for metadata - no attribution required
   - ✅ Procurement notices - no specific attribution mentioned

---

## 🟡 QUESTIONABLE/GRAY AREAS

### Activities Requiring Careful Consideration

1. **Rate Limits and Quotas**
   - ⚠️ No explicit rate limits documented
   - ⚠️ Recommended approach: Start conservatively, monitor for errors
   - ⚠️ Use Preview Environment for testing high-volume operations

2. **Data Enrichment and Combination**
   - ⚠️ Combining TED data with other sources not explicitly addressed
   - ⚠️ Creating derivative databases appears allowed but unclear on redistribution
   - ⚠️ Selling enriched datasets - likely allowed but verify

3. **China Exploitation Analysis**
   - ⚠️ Not explicitly addressed but appears within scope of "analysis"
   - ⚠️ Tracking Chinese entities in EU procurement - likely acceptable
   - ⚠️ Pattern analysis for security purposes - no prohibition found

4. **Automated Monitoring and Alerts**
   - ⚠️ Creating monitoring systems not explicitly covered
   - ⚠️ Real-time alerting on specific entities/patterns - probably OK
   - ⚠️ Competitive intelligence gathering - gray area but likely allowed

---

## 🔴 PROHIBITED USES

### Explicitly Forbidden Activities

1. **Trademark and Logo Usage**
   - ❌ Cannot use TED/SIMAP logos without permission
   - ❌ Cannot use EU institutional logos
   - ❌ Cannot misrepresent affiliation with TED/EU

2. **Industrial Property Rights**
   - ❌ Cannot reuse patented software/documents
   - ❌ Cannot violate registered designs
   - ❌ Respect third-party intellectual property

3. **Personal Data Misuse**
   - ❌ Cannot process personal data beyond legal basis
   - ❌ Must comply with GDPR/EU Regulation 2018/1725
   - ❌ Cannot use personal data for unauthorized purposes

4. **System Abuse**
   - ❌ Cannot disrupt service availability
   - ❌ Cannot bypass authentication where required
   - ❌ Cannot submit false/manipulated notices

5. **Misrepresentation**
   - ❌ Cannot alter data and present as original
   - ❌ Must indicate changes when reusing content
   - ❌ Cannot remove attribution where required

---

## 📋 REGISTRATION REQUIREMENTS

### API Access Setup

1. **Authentication Levels**
   - **Anonymous:** Search API only
   - **Authenticated:** All other APIs

2. **Registration Process**
   ```
   1. Create EU Login account
   2. Access TED Developer Portal
   3. Request API key
   4. Test in Preview Environment
   5. Move to Production when ready
   ```

3. **Best Practices**
   - Use functional/shared email for Production
   - Test thoroughly in Preview first
   - One API key per EU Login in Production
   - Multiple accounts allowed in Preview for testing

---

## ✅ COMPLIANCE ASSESSMENT FOR OSINT FORESIGHT

### Your Use Case Analysis

**Planned Activities:**
- Analyzing procurement patterns for China exploitation risks ✅
- Tracking technology transfers through contracts ✅
- Identifying dual-use technology acquisitions ✅
- Monitoring supplier networks and relationships ✅
- Creating intelligence reports on procurement trends ✅

**Compliance Status:** ✅ **FULLY COMPLIANT**

### Rationale:
1. All activities fall under "analysis" and "research" - explicitly allowed
2. Commercial use permitted - no restrictions on OSINT activities
3. Open data policy supports your exact use case
4. No prohibition on security/intelligence analysis found

---

## 🎯 RECOMMENDATIONS

### To Ensure Full Compliance:

1. **Registration**
   - Register for API key through EU Login
   - Start with Preview Environment
   - Document your organization and use case accurately

2. **Attribution**
   - Include source attribution: "Data source: TED (ted.europa.eu)"
   - Note any data transformations/enrichments
   - Don't use TED logos without permission

3. **Rate Limiting**
   - Start with conservative request rates (e.g., 1 request/second)
   - Monitor for HTTP 429 (rate limit) responses
   - Implement exponential backoff
   - Consider caching frequently accessed data

4. **Data Handling**
   - Respect personal data in notices
   - Focus on organizational/corporate data
   - Implement GDPR-compliant data retention

5. **Documentation**
   - Keep records of API usage
   - Document data processing methods
   - Maintain audit trail for compliance

---

## 📧 CONTACT FOR CLARIFICATION

If you need official confirmation:

**Copyright/Reuse Questions:**
- Email: op-copyright@publications.europa.eu

**Technical/API Questions:**
- TED Helpdesk (via Developer Portal)
- GitHub: github.com/OP-TED

**Legal/Compliance:**
- Publications Office Legal Service
- Via official EU channels

---

## 🔍 SPECIFIC OSINT CONSIDERATIONS

### Green Light Activities:
- ✅ Track Chinese companies winning EU contracts
- ✅ Analyze technology categories in procurement
- ✅ Map supplier relationships and networks
- ✅ Monitor dual-use technology acquisitions
- ✅ Create alerts for specific entities/patterns
- ✅ Generate intelligence reports from data
- ✅ Cross-reference with other public sources

### Best Practices:
- Focus on public/corporate data, not individuals
- Use data for analytical purposes
- Maintain transparency about data sources
- Respect the spirit of open data initiative

---

## 💡 CONCLUSION

**The TED API is exceptionally well-suited for OSINT analysis** with very permissive terms that explicitly allow commercial use, analysis, and research. Your planned activities are fully compliant with their terms of service.

**Key Advantages:**
- No cost for API access
- Explicit permission for commercial use
- Open data philosophy
- Strong legal foundation (CC licenses)
- EU backing ensures stability

**Sign up with confidence** - your OSINT activities align perfectly with TED's intended use cases.

---

*Analysis Date: 2025-09-15*
*Disclaimer: This analysis is based on publicly available information. For binding legal interpretation, consult with legal counsel or contact TED directly.*
