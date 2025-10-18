#!/usr/bin/env python3
"""
Export MCF Database to CSV/JSON for viewing
"""

import sqlite3
import csv
import json
from datetime import datetime
from pathlib import Path

def export_mcf_data():
    """Export MCF database to readable formats"""

    db_path = "F:/OSINT_WAREHOUSE/osint_research.db"
    export_dir = Path("C:/Projects/OSINT - Foresight/mcf_data_export")
    export_dir.mkdir(exist_ok=True)

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        print("Exporting MCF database...")

        # 1. Export documents to CSV
        cursor.execute("SELECT * FROM mcf_documents")
        documents = cursor.fetchall()

        csv_file = export_dir / f"mcf_documents_{datetime.now().strftime('%Y%m%d')}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if documents:
                writer = csv.DictWriter(f, fieldnames=documents[0].keys(), escapechar='\\')
                writer.writeheader()
                for doc in documents:
                    writer.writerow(dict(doc))

        print(f"[OK] Exported {len(documents)} documents to: {csv_file}")

        # 2. Export summary to JSON (more readable)
        summary_data = {
            "export_date": datetime.now().isoformat(),
            "total_documents": len(documents),
            "documents": []
        }

        for doc in documents[:50]:  # First 50 for readability
            doc_dict = dict(doc)
            # Truncate content for summary
            if 'content' in doc_dict and doc_dict['content']:
                doc_dict['content'] = doc_dict['content'][:500] + "..."
            summary_data["documents"].append(doc_dict)

        json_file = export_dir / f"mcf_summary_{datetime.now().strftime('%Y%m%d')}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)

        print(f"[OK] Exported summary to: {json_file}")

        # 3. Export entities
        cursor.execute("SELECT * FROM mcf_entities")
        entities = cursor.fetchall()

        if entities:
            entities_file = export_dir / f"mcf_entities_{datetime.now().strftime('%Y%m%d')}.csv"
            with open(entities_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=entities[0].keys(), escapechar='\\')
                writer.writeheader()
                for entity in entities:
                    writer.writerow(dict(entity))
            print(f"[OK] Exported {len(entities)} entities to: {entities_file}")

        # 4. Create readable report
        report_file = export_dir / f"mcf_report_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("MCF COLLECTION REPORT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Documents: {len(documents)}\n\n")

            f.write("DOCUMENTS COLLECTED:\n")
            f.write("-" * 80 + "\n")

            for i, doc in enumerate(documents, 1):
                f.write(f"\n{i}. {doc['title']}\n")
                f.write(f"   Source: {doc.get('collector', 'Unknown')}\n")
                f.write(f"   Score: {doc.get('relevance_score', 0):.3f}\n")
                f.write(f"   URL: {doc.get('url', 'N/A')}\n")
                f.write(f"   Collected: {doc.get('collection_timestamp', 'Unknown')}\n")

                # First 200 chars of content
                content = doc.get('content', '')
                if content:
                    preview = content[:200].replace('\n', ' ')
                    f.write(f"   Preview: {preview}...\n")

        print(f"[OK] Created readable report: {report_file}")

        conn.close()

        print("\n" + "=" * 80)
        print("EXPORT COMPLETE!")
        print(f"Files saved to: {export_dir}")
        print("\nYou can now open these files in VS Code:")
        print(f"  - {csv_file.name} (spreadsheet view)")
        print(f"  - {json_file.name} (structured data)")
        print(f"  - {report_file.name} (readable text)")

        return export_dir

    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    export_mcf_data()
