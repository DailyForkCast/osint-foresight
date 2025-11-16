import json

data = json.load(open('C:/Projects/OSINT - Foresight/analysis/quantum_tech/cordis_quantum_projects.json', 'r', encoding='utf-8'))
projects = data['all_projects']

print(f"Total projects: {len(projects)}")

# Check for country data
with_country = [p for p in projects[:100] if p.get('coordinatorCountry')]
print(f"Projects with country in first 100: {len(with_country)}")

if with_country:
    print("\nSample project with country:")
    sample = with_country[0]
    print(f"  Title: {sample.get('title')}")
    print(f"  Coordinator: {sample.get('coordinator')}")
    print(f"  Country: {sample.get('coordinatorCountry')}")
    print(f"  Cost: {sample.get('totalCost')}")

# Check all projects
all_with_country = [p for p in projects if p.get('coordinatorCountry')]
print(f"\nTotal projects with country data: {len(all_with_country)}")

if all_with_country:
    # Count by country
    from collections import Counter
    countries = Counter([p['coordinatorCountry'] for p in all_with_country])
    print("\nTop 10 countries:")
    for country, count in countries.most_common(10):
        print(f"  {country}: {count} projects")
