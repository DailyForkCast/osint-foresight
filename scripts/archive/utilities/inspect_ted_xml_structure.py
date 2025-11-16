import xml.etree.ElementTree as ET
from pathlib import Path
import tarfile

# Find a monthly archive
ted_dir = Path("F:/TED_Data/monthly")
archives = sorted(ted_dir.rglob("TED_monthly_*.tar.gz"))

# Try the first valid archive (skip corrupted ones)
test_archive = None
for archive in archives[2:5]:
    if '2014_02' in str(archive):
        test_archive = archive
        break

if not test_archive:
    print("Could not find test archive")
    exit(1)

print(f"Inspecting XML structure from: {test_archive.name}\n")

# Extract to temp
temp_dir = Path("C:/Projects/OSINT - Foresight/data/temp/test_extraction")
temp_dir.mkdir(parents=True, exist_ok=True)

try:
    # Open outer archive
    with tarfile.open(test_archive, 'r:gz') as outer_tar:
        # Extract just one inner archive
        members = [m for m in outer_tar.getmembers() if m.name.endswith('.tar.gz')]
        if members:
            outer_tar.extract(members[0], temp_dir)

            # Open inner archive
            inner_path = temp_dir / members[0].name
            with tarfile.open(inner_path, 'r:gz') as inner_tar:
                # Extract just one XML file
                xml_members = [m for m in inner_tar.getmembers() if m.name.endswith('.xml')][:1]

                for xml_member in xml_members:
                    inner_tar.extract(xml_member, temp_dir)
                    xml_path = temp_dir / xml_member.name

                    print(f"XML File: {xml_member.name}")
                    print("=" * 80)

                    # Parse XML
                    tree = ET.parse(xml_path)
                    root = tree.getroot()

                    # Print root element
                    print(f"Root element: {root.tag}")
                    print(f"Root attributes: {root.attrib}")
                    print()

                    # Print first level of structure (top-level elements)
                    print("Top-level elements:")
                    for child in root:
                        print(f"  - {child.tag}")
                        if child.text and child.text.strip():
                            print(f"      Text: {child.text.strip()[:100]}")
                        if child.attrib:
                            print(f"      Attributes: {child.attrib}")

                    print()
                    print("=" * 80)
                    print("\nSample of XML content (first 2000 characters):")
                    print("=" * 80)

                    # Read and print raw XML
                    with open(xml_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        print(content[:2000])

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    # Cleanup
    import shutil
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)
