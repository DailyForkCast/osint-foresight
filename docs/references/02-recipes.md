# Ready-to-run Recipes (curl / SQL)

> Replace placeholders: `COUNTRY` (ISO2), `YEARS` (e.g., 2015–2025), and keyword sets.

## OpenAIRE — Research Products (co-publications)
```bash
curl -s "https://api.openaire.eu/v1/graph/search/researchProducts?size=200&from=0&sortBy=bestmatch&title=(\"deep%20learning\"%20OR%20\"machine%20learning\"%20OR%20HPC%20OR%20supercomput*)&relOrganizationCountryCode=COUNTRY,CN&fromDate=2015-01-01&toDate=2025-12-31"
```
Fields to extract: `id,title,publicationYear,doi,authors[],relOrganizations[],subjects,projects[].code,links[].url`

## OpenAIRE — Projects (co-participation)
```bash
curl -s "https://api.openaire.eu/v1/graph/search/projects?size=200&from=0&relOrganizationCountryCode=COUNTRY,CN&title=(AI%20OR%20HPC%20OR%20%22Earth%20observation%22)&startDate>=2015-01-01"
```

## Crossref — Works (affiliation filter, cursor paging)
```bash
curl -s "https://api.crossref.org/works?filter=from-pub-date:2015-01-01,until-pub-date:2025-12-31&query.affiliation=COUNTRY&rows=1000&cursor=*&select=DOI,title,author,issued,container-title,affiliation,funder"
```
Post-filter Chinese affiliations: `China|PRC|Beijing|Shanghai|Shenzhen|中国|中國`.

## Crossref — Event Data (by DOI)
```bash
curl -s "https://api.eventdata.crossref.org/v1/events?obj-id=DOI:10.1234/abcd&rows=1000&from-collected-date=2024-01-01"
```

## IETF Datatracker — WG drafts and authors
```bash
curl -s "https://datatracker.ietf.org/api/v1/group/group/?type=wg&state=active&acronym__icontains=mls"
curl -s "https://datatracker.ietf.org/api/v1/doc/document/?group=/api/v1/group/group/12345/&states__type__slug__in=draft-stream-ietf"
```

## GLEIF — LEI by country + keywords
```bash
curl -s "https://api.gleif.org/api/v1/lei-records?filter[entity.legalAddress.country]=COUNTRY&filter[q]=semiconductor&pages[size]=200"
```
Relationships (Level-2):
```bash
curl -s "https://api.gleif.org/api/v1/relationships?filter[relationship.startNode.lei][:in]=LEI1,LEI2"
```

## OpenCorporates — officers/companies (requires token)
```bash
curl -s "https://api.opencorporates.com/v0.4/companies/search?q=semiconductor&country_code=COUNTRY&per_page=100&api_token=$OPENCORP_TOKEN"
```

## EPO OPS — CQL search (patent biblio)
**Auth:** use `EPO_OPS_KEY`/`EPO_OPS_SECRET`.
- Endpoint style: `/rest-services/published-data/search/biblio?CQL=...`
- Example CQL:
```
cpc=G06N or G06F and pd within "2015 2025" and pa any "COUNTRY" and pa any (CN OR China)
```

## Google Patents (BigQuery) — co-assignee/co-inventor (COUNTRY & CN)
```sql
SELECT
  publication_number,
  filing_date,
  grant_date,
  ANY_VALUE(title_localized) AS title,
  ARRAY(SELECT code FROM UNNEST(cpc) WHERE code LIKE 'G06N%' OR code LIKE 'G06F%' OR code LIKE 'G01S%' OR code LIKE 'H04N%') AS cpc_hits,
  ARRAY(SELECT assignee_harmonized.name FROM UNNEST(assignee_harmonized)) AS assignees,
  ARRAY(SELECT inventor_harmonized.country_code FROM UNNEST(inventor_harmonized)) AS inventor_countries,
  ARRAY(SELECT assignee_harmonized.country_code FROM UNNEST(assignee_harmonized)) AS assignee_countries
FROM `patents-public-data.patents.publications`
WHERE (EXISTS (SELECT 1 FROM UNNEST(assignee_harmonized) a WHERE a.country_code='COUNTRY')
       OR EXISTS (SELECT 1 FROM UNNEST(inventor_harmonized) i WHERE i.country_code='COUNTRY'))
  AND (EXISTS (SELECT 1 FROM UNNEST(assignee_harmonized) a WHERE a.country_code='CN')
       OR EXISTS (SELECT 1 FROM UNNEST(inventor_harmonized) i WHERE i.country_code='CN'))
  AND filing_date BETWEEN '2015-01-01' AND '2025-12-31'
  AND EXISTS (SELECT 1 FROM UNNEST(cpc) c
              WHERE c.code LIKE 'G06N%' OR c.code LIKE 'G06F%' OR c.code LIKE 'G01S%' OR c.code LIKE 'H04N%');
```

## WIPO PATENTSCOPE — Advanced Query (UI)
```
(IC:(G06N OR G06F OR G06T) OR TI:("earth observation" OR "remote sensing" OR SAR) OR AB:("machine learning" OR "deep learning"))
AND (IA:COUNTRY OR PA:COUNTRY)
AND (IA:(CN OR "China" OR 中国) OR PA:(CN OR "China" OR 中国))
AND PD:[2015 TO 2025]
```