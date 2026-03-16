import os
import re

base_path = r"D:\BaiduSyncdisk\work_log\02-Resources\10-中医"

for root, dirs, files in os.walk(base_path):
    for filename in files:
        if not filename.endswith('.md'):
            continue

        filepath = os.path.join(root, filename)
        filename_clean = os.path.splitext(filename)[0]

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            continue

        # Check if starts with --- but has no title: in frontmatter
        if content.startswith('---'):
            # Find frontmatter end
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                body = parts[2]

                # Check if title exists in frontmatter
                if not re.search(r'^title:', frontmatter, re.MULTILINE):
                    # Add title from filename
                    # Clean filename
                    title = re.sub(r'^\d+[_-]?\d*\s*', '', filename_clean)
                    title = title.replace('_', ' ').replace('-', ' ').strip()

                    frontmatter = 'title: ' + title + '\n' + frontmatter
                    new_content = '---' + frontmatter + '---' + body

                    try:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"Fixed title: {filename}")
                    except Exception as e:
                        print(f"Error {filename}: {e}")

print("Done!")
