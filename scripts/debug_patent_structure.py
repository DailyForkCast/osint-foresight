#!/usr/bin/env python3
import json

# Check the actual structure of one expanded file
filepath = "F:/OSINT_DATA/epo_expanded/tencent_20250926_185246.json"
with open(filepath, 'r') as f:
    data = json.load(f)

print("Keys in main data:", data.keys())
print("\nPatent batches:", len(data.get('patent_batches', [])))

if 'patent_batches' in data and len(data['patent_batches']) > 0:
    batch = data['patent_batches'][0]
    print("\nFirst batch keys:", batch.keys())

    if 'raw_data' in batch:
        raw = batch['raw_data']
        print("Raw data keys:", raw.keys())

        if 'exchange-documents' in raw:
            docs = raw['exchange-documents']
            print(f"Exchange docs: {len(docs)} items")

            if len(docs) > 0:
                first_doc = docs[0]
                print("\nFirst doc keys:", first_doc.keys())

                if 'exchange-document' in first_doc:
                    ex_doc = first_doc['exchange-document']
                    print("\nExchange doc keys:", ex_doc.keys())

                    if 'bibliographic-data' in ex_doc:
                        biblio = ex_doc['bibliographic-data']
                        print("\nBiblio keys:", biblio.keys())

                        if 'publication-reference' in biblio:
                            pub_ref = biblio['publication-reference']
                            print("\nPub ref keys:", pub_ref.keys())

                            if 'document-id' in pub_ref:
                                doc_ids = pub_ref['document-id']
                                print(f"\nDocument IDs: {len(doc_ids)} items")

                                for i, doc_id in enumerate(doc_ids[:2]):
                                    print(f"\n  Doc ID {i}:")
                                    print(f"    Type: {doc_id.get('@document-id-type')}")

                                    # Check the doc-number structure
                                    if 'doc-number' in doc_id:
                                        doc_num = doc_id['doc-number']
                                        print(f"    Doc number type: {type(doc_num)}")
                                        if isinstance(doc_num, dict):
                                            print(f"    Doc number keys: {doc_num.keys()}")
                                            if '$' in doc_num:
                                                print(f"    Doc number value: {doc_num['$']}")

                                    # Check date
                                    if 'date' in doc_id:
                                        date = doc_id['date']
                                        print(f"    Date type: {type(date)}")
                                        if isinstance(date, dict) and '$' in date:
                                            print(f"    Date value: {date['$']}")
