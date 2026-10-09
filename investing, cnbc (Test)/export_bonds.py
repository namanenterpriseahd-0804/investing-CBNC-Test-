import urllib.request
import json
import subprocess
import os
from datetime import datetime
import pandas as pd

SYMBOLS = ["US1M", "US3M", "US6M", "US1Y", "US2Y", "US3Y", "US5Y", "US7Y", "US10Y", "US20Y", "US30Y"]

def fetch_bond_data():
    symbols_param = "|".join(SYMBOLS)
    url = f"https://quote.cnbc.com/quote-html-webservice/restQuote/symbolType/symbol?symbols={symbols_param}&requestMethod=itv&noform=1&partnerId=2&fund=1&exthrs=1&output=json"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        quotes = data.get("FormattedQuoteResult", {}).get("FormattedQuote", [])
        return quotes

def export_to_excel_and_csv():
    quotes = fetch_bond_data()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    rows = []
    for q in quotes:
        yield_val = q.get("last", "").replace("%", "").strip()
        try:
            yield_num = float(yield_val) if yield_val else None
        except ValueError:
            yield_num = None

        change_val = q.get("change", "").strip()
        try:
            change_num = float(change_val) if change_val and change_val != "UNCH" else 0.0
        except ValueError:
            change_num = 0.0

        price_val = q.get("bond_last_price", "").strip()
        try:
            price_num = float(price_val) if price_val else None
        except ValueError:
            price_num = None

        rows.append({
            "Symbol": q.get("symbol", ""),
            "Benchmark Name": q.get("name", ""),
            "Yield (%)": yield_num,
            "Yield String": q.get("last", ""),
            "Change": change_num,
            "Change (%)": q.get("change_pct", "0%"),
            "Day Low": q.get("low", ""),
            "Day High": q.get("high", ""),
            "Bond Price": price_num,
            "Coupon (%)": q.get("coupon", ""),
            "Maturity Date": q.get("maturity_date", ""),
            "Exchange": q.get("exchange", ""),
            "Last Updated (EDT)": q.get("last_timedate", ""),
            "Data Fetched At": now_str
        })
    
    df = pd.DataFrame(rows)
    
    # 1. Save to CSV (.csv)
    csv_filename = "bond_rates.csv"
    df.to_csv(csv_filename, index=False, encoding="utf-8-sig")
    print(f"Exported to CSV: {csv_filename}")
    
    # 2. Save to Excel (.xlsx)
    excel_filename = "bond_rates.xlsx"
    with pd.ExcelWriter(excel_filename, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="US Treasury Rates", index=False)
        worksheet = writer.sheets["US Treasury Rates"]
        for col in worksheet.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = col[0].column_letter
            worksheet.column_dimensions[col_letter].width = max(max_len + 3, 12)
    print(f"Exported to Excel: {excel_filename}")

    # 3. Save to Excel (.xls) BIFF8 format
    xls_filename = "bond_rates.xls"
    try:
        node_script = """
        const fs = require('fs');
        const XLSX = require('./xlsx.full.min.js');
        const csvContent = fs.readFileSync('bond_rates.csv', 'utf8');
        const wb = XLSX.read(csvContent, { type: 'string' });
        const biff8Buf = XLSX.write(wb, { type: 'buffer', bookType: 'biff8' });
        fs.writeFileSync('bond_rates.xls', biff8Buf);
        """
        subprocess.run(["node", "-e", node_script], check=True, capture_output=True)
        print(f"Exported to Excel (.xls): {xls_filename}")
    except Exception as e:
        print(f"Warning: could not generate .xls via node: {e}")

    # 4. Save to styled HTML table
    html_filename = "bond_rates_table.html"
    html_table = df.to_html(classes="excel-table", index=False, border=0)
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>U.S. Treasury Bond Rates - .xls / .csv Spreadsheet View</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{
            background: #090d16;
            color: #f8fafc;
            font-family: 'Outfit', sans-serif;
            padding: 30px 20px;
            margin: 0;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            flex-wrap: wrap;
            gap: 16px;
        }}
        h1 {{
            margin: 0;
            font-size: 1.6rem;
            color: #38bdf8;
        }}
        .btn-group {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 16px;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            text-decoration: none;
            cursor: pointer;
            border: none;
            transition: all 0.2s;
        }}
        .btn-xls {{
            background: #107c41;
            color: white;
        }}
        .btn-xls:hover {{
            background: #15803d;
        }}
        .btn-csv {{
            background: #0284c7;
            color: white;
        }}
        .btn-csv:hover {{
            background: #0369a1;
        }}
        .btn-xlsx {{
            background: #2563eb;
            color: white;
        }}
        .btn-xlsx:hover {{
            background: #1d4ed8;
        }}
        .table-wrap {{
            overflow-x: auto;
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 12px;
        }}
        table.excel-table {{
            width: 100%;
            border-collapse: collapse;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            text-align: left;
        }}
        table.excel-table th {{
            background: rgba(30, 41, 59, 0.9);
            color: #38bdf8;
            padding: 12px 14px;
            border-bottom: 2px solid rgba(255, 255, 255, 0.1);
            text-transform: uppercase;
            font-size: 0.75rem;
        }}
        table.excel-table td {{
            padding: 10px 14px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            white-space: nowrap;
        }}
        table.excel-table tr:hover td {{
            background: rgba(255, 255, 255, 0.03);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>📊 U.S. Treasury Bond Rates — .xls & .csv Data</h1>
                <p style="color: #94a3b8; font-size: 0.85rem; margin-top: 4px;">Updated live at {now_str}</p>
            </div>
            <div class="btn-group">
                <a href="bond_rates.xls" class="btn btn-xls" download>📥 Download .XLS</a>
                <a href="bond_rates.csv" class="btn btn-csv" download>📥 Download .CSV</a>
                <a href="bond_rates.xlsx" class="btn btn-xlsx" download>📥 Download .XLSX</a>
                <a href="index.html" class="btn" style="background: rgba(255,255,255,0.1); color: #fff;">📈 Open Live Dashboard</a>
            </div>
        </div>
        <div class="table-wrap">
            {html_table}
        </div>
    </div>
</body>
</html>
"""
    with open(html_filename, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"Exported to HTML: {html_filename}")

    return csv_filename, xls_filename, excel_filename, html_filename

if __name__ == "__main__":
    export_to_excel_and_csv()
