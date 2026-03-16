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

        # Check if has frontmatter and abstract
        if content.startswith('---') and '> [!abstract]' not in content:
            # Find frontmatter end
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                body = parts[2]

                # Find first heading (either # heading or just text that looks like a title)
                first_heading = re.search(r'^(#{1,6}\s+.+)$', body, re.MULTILINE)
                if first_heading:
                    # Add abstract before first heading
                    abstract_text = '\n> [!abstract] 摘要\n>\n> \n\n'
                    pos = first_heading.start()
                    new_body = body[:pos] + abstract_text + body[pos:]
                    new_content = parts[0] + '---' + frontmatter + '---\n' + new_body
                else:
                    # No heading found, add after frontmatter
                    abstract_text = '\n> [!abstract] 摘要\n>\n> \n\n---\n\n'
                    new_content = parts[0] + '---' + frontmatter + '---\n' + abstract_text + body

                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Added abstract: {filename}")
                except Exception as e:
                    print(f"Error {filename}: {e}")

print("Done!")
