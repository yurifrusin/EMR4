import os
import xml.etree.ElementTree as ET
import csv
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, MetaData

# DB Config
DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:5434/gp_pms_dev"

xml_path = r"c:\Users\YuriFrusin\Documents\EMR4\MBS\MBS-XML-20260701.XML"
csv_path = r"c:\Users\YuriFrusin\Documents\EMR4\MBS\MBS-CSV-20260701.csv"
jsonl_path = r"c:\Users\YuriFrusin\Documents\EMR4\MBS\MBS-JSONL-20260701.jsonl"

def main():
    print(f"Parsing XML file: {xml_path}")
    if not os.path.exists(xml_path):
        print(f"XML file not found at {xml_path}")
        return

    tree = ET.parse(xml_path)
    root = tree.getroot()

    items = []
    seen_keys = set()

    for data_elem in root.findall("Data"):
        item_num_elem = data_elem.find("ItemNum")
        desc_elem = data_elem.find("Description")
        fee_elem = data_elem.find("ScheduleFee")

        item_num = item_num_elem.text.strip() if item_num_elem is not None and item_num_elem.text else ""
        desc = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else ""
        fee = fee_elem.text.strip() if fee_elem is not None and fee_elem.text else ""

        if not item_num or not desc:
            continue

        # Deduplicate on item_number
        key = (item_num, desc)
        if key in seen_keys:
            continue
        seen_keys.add(key)

        items.append({
            "item_number": item_num,
            "description": desc,
            "fee": fee
        })

    print(f"Parsed {len(items)} unique items.")

    # 1. Save as CSV
    print(f"Saving CSV to: {csv_path}")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["item_number", "description", "fee"])
        writer.writeheader()
        writer.writerows(items)

    # 2. Save as JSON Lines (structured format for Discovery Engine)
    print(f"Saving JSONL to: {jsonl_path}")
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for idx, item in enumerate(items):
            # Format expected by Discovery Engine for structured data
            record = {
                "id": f"mbs_{item['item_number']}_{idx}",
                "structData": {
                    "item_number": item["item_number"],
                    "description": item["description"],
                    "fee": item["fee"]
                }
            }
            f.write(json.dumps(record) + "\n")

    # 3. Load into PostgreSQL
    try:
        print(f"Connecting to database: {DATABASE_URL}")
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()

        metadata = MetaData()
        mbs_table = Table("mbs_directory", metadata, autoload_with=engine)

        print("Inserting records into PostgreSQL...")

        # Clear existing seed items to prevent constraint errors or overwrite
        # Let's perform upsert or insert-ignore.
        # We can clean the table first or do batch insertion.
        # Let's clean the table to ensure we have a fresh import.
        session.execute(mbs_table.delete())
        session.commit()

        # Batch insert in chunks of 500
        chunk_size = 500
        for i in range(0, len(items), chunk_size):
            chunk = items[i:i + chunk_size]
            session.execute(mbs_table.insert(), chunk)
            session.commit()

        print("PostgreSQL import complete!")
        session.close()

    except Exception as e:
        print(f"Failed to load into PostgreSQL: {e}")

if __name__ == "__main__":
    main()
