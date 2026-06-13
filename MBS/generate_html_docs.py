import os
import csv
import html

csv_path = r"c:\Users\YuriFrusin\Documents\EMR4\MBS\MBS-CSV-20260701.csv"
output_dir = r"c:\Users\YuriFrusin\Documents\EMR4\MBS\mbs_unstructured"

def main():
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Reading CSV from: {csv_path}")
    if not os.path.exists(csv_path):
        print("CSV file not found!")
        return

    count = 0
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            item_num = row.get("item_number", "").strip()
            desc = row.get("description", "").strip()
            fee = row.get("fee", "").strip()

            if not item_num or not desc:
                continue

            # Create a clean HTML page for the item
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>MBS Item {html.escape(item_num)}</title>
    <meta name="item_number" content="{html.escape(item_num)}">
    <meta name="fee" content="{html.escape(fee)}">
</head>
<body>
    <h1>Medicare Benefits Schedule - Item {html.escape(item_num)}</h1>
    <p><strong>Item Number:</strong> {html.escape(item_num)}</p>
    <p><strong>Schedule Fee:</strong> {html.escape(fee)}</p>
    <p><strong>Description:</strong></p>
    <p>{html.escape(desc)}</p>
</body>
</html>
"""
            # Save file
            file_name = f"mbs_item_{item_num}.html"
            file_path = os.path.join(output_dir, file_name)
            with open(file_path, "w", encoding="utf-8") as out_f:
                out_f.write(html_content)
            count += 1

    print(f"Generated {count} HTML files in {output_dir}")

if __name__ == "__main__":
    main()
