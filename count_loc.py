import os

def count_lines():
    target_dirs = ['api', 'rag', 'tests', 'ingestion', 'config', 'static']
    root = os.getcwd()
    total_lines = 0
    file_count = 0
    
    extensions = {'.py', '.js', '.html', '.css', '.md', '.txt'}
    
    print(f"{'File':<60} | Lines")
    print("-" * 70)
    
    # Also count root files
    for f in os.listdir(root):
        if os.path.isfile(f) and os.path.splitext(f)[1] in extensions:
             try:
                with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
                    lines = len(fp.readlines())
                    total_lines += lines
                    file_count += 1
                    # print(f"{f:<60} | {lines}")
             except: pass

    for d in target_dirs:
        path = os.path.join(root, d)
        if not os.path.exists(path): continue
        
        for r, _, files in os.walk(path):
            if 'node_modules' in r or 'venv' in r or '__pycache__' in r: continue
            
            for f in files:
                if os.path.splitext(f)[1] in extensions:
                    full_path = os.path.join(r, f)
                    try:
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as fp:
                            lines = len(fp.readlines())
                            total_lines += lines
                            file_count += 1
                            # print(f"{os.path.relpath(full_path, root):<60} | {lines}")
                    except: pass
                    
    print("-" * 70)
    print(f"Total Files: {file_count}")
    print(f"Total Lines of Code: {total_lines}")

if __name__ == "__main__":
    count_lines()
