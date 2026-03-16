import os
import re

base_path = r"D:\BaiduSyncdisk\work_log\02-Resources\10-中医"

for root, dirs, files in os.walk(base_path):
    for filename in files:
        if not filename.endswith('.md'):
            continue

        filepath = os.path.join(root, filename)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            continue

        # Fix: if content starts with ---\n\n then remove extra \n
        if content.startswith('---\n\n'):
            content = '---\n' + content[5:]
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Fixed: {filename}")
            except:
                pass

print("Done!")
