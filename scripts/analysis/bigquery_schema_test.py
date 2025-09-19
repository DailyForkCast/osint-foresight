#!/usr/bin/env python3
"""
Test BigQuery Patents Schema to understand current field structure
"""

from google.cloud import bigquery

def test_schema():
    """Test the current BigQuery patents schema"""

    try:
        client = bigquery.Client(project='osint-foresight-2025')
        print("Connected to BigQuery")

        # Simple query to see available fields - minimal scan
        query = """
        SELECT
            publication_number,
            publication_date,
            title_localized,
            inventor,
            assignee,
            cpc
        FROM `patents-public-data.patents.publications`
        WHERE country_code = 'DE'
        LIMIT 1
        """

        print("Testing basic query...")
        query_job = client.query(query)
        results = list(query_job.result())

        print(f"Found {len(results)} results")

        if results:
            result = results[0]
            print("\nSample record structure:")
            for field_name in result.keys():
                value = getattr(result, field_name)
                print(f"  {field_name}: {type(value)} = {str(value)[:100]}...")

    except Exception as e:
        print(f"Error: {e}")

        # Try alternative query
        try:
            client = bigquery.Client(project='osint-foresight-2025')
            alt_query = """
            SELECT *
            FROM `patents-public-data.patents.publications`
            WHERE publication_number = 'US-10000000-B2'
            LIMIT 1
            """

            print("\nTrying alternative query...")
            query_job = client.query(alt_query)
            results = list(query_job.result())

            if results:
                result = results[0]
                print("\nAvailable fields:")
                for field_name in result.keys():
                    print(f"  - {field_name}")

        except Exception as e2:
            print(f"Alternative query also failed: {e2}")

if __name__ == "__main__":
    test_schema()
