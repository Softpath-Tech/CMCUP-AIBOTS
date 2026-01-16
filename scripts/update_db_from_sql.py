import re
import csv
import os
import io

# SQL Dump Path
SQL_FILE = r"data/tgsports_db_12_01_2026.sql"
OUTPUT_DIR = r"data/csvs"

# Table Mapping: SQL Name -> CSV Name
TABLE_MAPPING = {
    "clustermaster": "clustermaster",
    "districtmaster": "districtmaster",
    "mandalmaster": "mandalmaster",
    "villagemaster": "villagemaster",
    "player_details": "player_details",
    "tb_discpline": "tb_discipline", # Fix typo in SQL
    "tb_category": "tb_category",
    "tb_events": "tb_events",
    "tb_fixtures": "tb_fixtures",
    "tb_selected_players": "tb_selected_players"
}

def parse_sql_value(value):
    """
    Clean SQL value string to CSV compatible string.
    Handles 'NULL', numbers, and quoted strings.
    """
    value = value.strip()
    if value.upper() == "NULL":
        return ""
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("\\'", "'").replace('\\"', '"')
    return value

def extract_values(sql_stmt):
    """
    Extract tuple values from INSERT statement.
    Regex logic to handle parenthesis groupings.
    """
    # Remove INSERT INTO ... VALUES
    # This is a bit complex because values can contain comma and parenthesis.
    # Simple regex for (val1, val2, ...) lists
    # We will use a parser that iterates chars to handle nesting/quotes if needed.
    # But for mysqldump, usually standard (..., ...), (..., ...) format.
    
    # Simple split by marked parenthesis?
    # Let's try a regex that matches `( ... )` but be careful of content.
    # Pattern: \((?:[^)(]+|(?R))*+\) - distinct recursive pattern not supported in Python re.
    
    # Alternative: Manual parsing
    values_list = []
    
    # Strip prefix
    header_match = re.search(r"INSERT INTO `.+?` \((.+?)\) VALUES", sql_stmt, re.IGNORECASE)
    columns = []
    start_idx = 0
    
    if header_match:
        # Explicit column definition
        # we might need this if CSV order matters, but here we assume CSV headers = SQL columns
        pass
        start_idx = header_match.end()
    else:
        # Try without columns: INSERT INTO `table` VALUES
        match = re.search(r"INSERT INTO `.+?` VALUES", sql_stmt, re.IGNORECASE)
        if match:
             start_idx = match.end()
    
    if start_idx == 0:
        return []

    # Parse what follows: (1, 'a'), (2, 'b');
    content = sql_stmt[start_idx:].strip()
    if content.endswith(';'): content = content[:-1]
    
    # State machine parser
    current_val = []
    current_token = ""
    in_quote = False
    quote_char = None
    in_paren = False
    rows = []
    
    i = 0
    n = len(content)
    
    while i < n:
        c = content[i]
        
        if not in_paren:
            if c == '(':
                in_paren = True
                current_val = []
                current_token = ""
            # else skip (spaces, commas between sets)
        else:
            # Inside (...)
            if in_quote:
                if c == quote_char:
                    # Check for escaped quote
                    if i+1 < n and content[i+1] == quote_char:
                        # Double quote escape '' or ""
                        current_token += c
                        i += 1 
                    elif content[i-1] == '\\':
                         # Backslash escape
                         current_token += c
                    else:
                        # End quote
                        in_quote = False
                else:
                    current_token += c
            else:
                if c == "'" or c == '"':
                    in_quote = True
                    quote_char = c
                elif c == ',':
                    # End of value
                    current_val.append(parse_sql_value(current_token))
                    current_token = ""
                elif c == ')':
                    # End of row
                    current_val.append(parse_sql_value(current_token))
                    rows.append(current_val)
                    in_paren = False
                else:
                    current_token += c
        i += 1
        
    return rows

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    print(f"Reading SQL dump: {SQL_FILE}")
    
    # Store schema/headers
    headers = {}
    data = {}
    
    current_table = None
    buffer = ""
    in_insert_stmt = False
    target_insert_table = None

    with open(SQL_FILE, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            stripped = line.strip()
            
            # 1. Detect Table Schema (Single line CREATE mostly or just name extraction)
            if stripped.startswith("CREATE TABLE"):
                # Handle optional backticks
                match = re.search(r"CREATE TABLE [`]?(\w+)[`]?\s*\(", stripped, re.IGNORECASE)
                if match:
                    current_table = match.group(1)
                    headers[current_table] = []
                    data[current_table] = []
                continue # Skip processing this line further

            # 2. Parse Columns (Inside CREATE TABLE)
            # Only if we just saw CREATE TABLE and haven't seen ); yet. 
            # Simplified: just look for `col` type ...
            if current_table and (stripped.startswith("`") or stripped.startswith('"') or (stripped and stripped[0].isalnum())):
                # Filter out Keys/Constraints
                if stripped.upper().startswith(("PRIMARY KEY", "KEY", "CONSTRAINT", "UNIQUE KEY", ")")):
                    continue

                # `id` int(11) ...
                # or id int(11)...
                col_match = re.match(r"[`\"]?(\w+)[`\"]?\s+\w+", stripped)
                if col_match:
                    headers[current_table].append(col_match.group(1))
            
            if stripped.endswith(";") and current_table and "CREATE TABLE" not in stripped:
                # End of create table usually
                # But could be end of column def? No, usually );
                if ");" in stripped:
                     current_table = None

            # 3. Detect INSERT
            if stripped.startswith("INSERT INTO"):
                # Handle `INSERT INTO table ...` or `INSERT INTO table VALUES ...`
                match = re.match(r"INSERT INTO [`\"]?(\w+)[`\"]?", stripped, re.IGNORECASE)
                if match:
                    tbl = match.group(1)
                    if tbl in TABLE_MAPPING:
                        in_insert_stmt = True
                        target_insert_table = tbl
                        buffer = line # Keep original formatting for easy parsing
                    else:
                        in_insert_stmt = False
            
            elif in_insert_stmt:
                buffer += line
            
            # Process Buffer if Complete
            if in_insert_stmt and stripped.endswith(";"):
                # End of INSERT
                rows = extract_values(buffer)
                if target_insert_table not in data: data[target_insert_table] = []
                data[target_insert_table].extend(rows)
                
                # Reset
                in_insert_stmt = False
                buffer = ""
                target_insert_table = None

    # Write CSVs
    print("\nWriting CSV files...")
    for sql_table, csv_name in TABLE_MAPPING.items():
        if sql_table in data and len(data[sql_table]) > 0:
            out_path = os.path.join(OUTPUT_DIR, f"{csv_name}.csv")
            
            # Get headers
            cols = headers.get(sql_table, [])
            
            # If we missed headers (e.g. CREATE TABLE was complex), verify
            if not cols:
                print(f"⚠️ Warning: No headers found for {sql_table}, skimming first row length")
                if data[sql_table]:
                    cols = [f"col_{i}" for i in range(len(data[sql_table][0]))]
            
            print(f" -> {csv_name}.csv: {len(data[sql_table])} rows")
            
            with open(out_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(cols)
                writer.writerows(data[sql_table])
        else:
            print(f"⚠️ Warning: No data found for {sql_table}")

if __name__ == "__main__":
    main()
