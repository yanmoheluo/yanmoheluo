import os
import re
from pathlib import Path

base_path = r"D:\BaiduSyncdisk\work_log\02-Resources\10-中医"

def clean_filename(title):
    """Clean filename to get a proper title"""
    # Remove file extension
    title = re.sub(r'\.(md|MD)$', '', title)
    # Replace common patterns
    title = title.replace('_', ' ')
    title = title.replace('-', ' ')
    # Remove date prefix patterns like 202410_
    title = re.sub(r'^\d{4}\d{2,4}[_-]?\d*\s*', '', title)
    return title.strip()

for root, dirs, files in os.walk(base_path):
    for filename in files:
        if not filename.endswith('.md'):
            continue

        filepath = os.path.join(root, filename)
        filename_clean = Path(filename).stem

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            print(f"Error reading: {filename}")
            continue

        new_content = content
        modified = False
        lines = content.split('\n')

        # Check if has frontmatter
        has_frontmatter = content.startswith('---')

        if has_frontmatter:
            # Find the second ---
            frontmatter_end = -1
            for i in range(1, len(lines)):
                if lines[i].strip() == '---':
                    frontmatter_end = i
                    break

            if frontmatter_end > 0:
                frontmatter_lines = lines[:frontmatter_end+1]
                body_lines = lines[frontmatter_end+1:]
                frontmatter = '\n'.join(frontmatter_lines)

                # 1. Fix title in frontmatter
                title_match = re.search(r'^title:\s*(.+)$', frontmatter, re.MULTILINE)
                if title_match:
                    current_title = title_match.group(1).strip()
                    if '{' in current_title or len(current_title) < 3 or current_title.startswith(' '):
                        new_title = clean_filename(filename_clean)
                        frontmatter = re.sub(
                            r'^title:\s*.+$',
                            f'title: {new_title}',
                            frontmatter,
                            flags=re.MULTILINE
                        )
                        modified = True

                # 2. Fix tags
                # Replace 读书/笔记 tags with 中医
                if re.search(r'tags:\s*\n\s*-\s*读书', frontmatter):
                    frontmatter = re.sub(
                        r'(tags:\s*\n)(\s*-\s*)读书',
                        r'\1\2中医',
                        frontmatter
                    )
                    modified = True

                # Remove 笔记 tag if present
                if re.search(r'\n\s*-\s*笔记\s*\n', frontmatter):
                    frontmatter = re.sub(
                        r'\n\s*-\s*笔记\s*\n',
                        '\n',
                        frontmatter
                    )
                    modified = True

                # Remove category if present
                if re.search(r'\ncategory:', frontmatter):
                    frontmatter = re.sub(
                        r'\ncategory:.*\n',
                        '\n',
                        frontmatter
                    )
                    modified = True

                # Ensure 中医 tag exists
                if '中医' not in frontmatter:
                    if re.search(r'^tags:', frontmatter, re.MULTILINE):
                        # Add 中医 tag
                        frontmatter = re.sub(
                            r'^(tags:\s*)$',
                            r'\1\n  - 中医',
                            frontmatter,
                            flags=re.MULTILINE
                        )
                        modified = True

                new_content = frontmatter + '\n' + '\n'.join(body_lines)

        # 3. Add abstract callout if missing (only if has frontmatter)
        if has_frontmatter and '> [!abstract]' not in new_content:
            # Find first heading
            first_heading = re.search(r'^(#{1,6}\s+.+)$', new_content, re.MULTILINE)
            if first_heading:
                pos = first_heading.start()
                abstract = '\n> [!abstract] 摘要\n>\n> \n\n---\n\n'
                new_content = new_content[:pos] + abstract + new_content[pos:]
                modified = True

        if modified:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Fixed: {filename}")
            except Exception as e:
                print(f"Error writing {filename}: {e}")

print("\nDone!")
