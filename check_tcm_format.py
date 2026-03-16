import os
import re
from pathlib import Path

base_path = r"D:\BaiduSyncdisk\work_log\02-Resources\10-中医"

issues = []

for root, dirs, files in os.walk(base_path):
    for filename in files:
        if not filename.endswith('.md'):
            continue

        filepath = os.path.join(root, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if has frontmatter
        if not content.startswith('---'):
            issues.append({
                'file': filename,
                'issue': 'No frontmatter'
            })
            continue

        # Extract frontmatter
        parts = content.split('---')
        if len(parts) < 3:
            issues.append({
                'file': filename,
                'issue': 'Incomplete frontmatter'
            })
            continue

        frontmatter = parts[1]

        # Check title
        title_match = re.search(r'^title:\s*(.+)$', frontmatter, re.MULTILINE)
        if not title_match:
            issues.append({
                'file': filename,
                'issue': 'No title in frontmatter'
            })
            continue

        title = title_match.group(1).strip()

        # Check tags
        tags_match = re.search(r'^tags:\s*$', frontmatter, re.MULTILINE)
        if not tags_match:
            issues.append({
                'file': filename,
                'issue': 'No tags in frontmatter'
            })
            continue

        # Check if 中医 tag exists
        if '中医' not in frontmatter:
            issues.append({
                'file': filename,
                'issue': f'Missing 中医 tag. Current tags section: {frontmatter[frontmatter.find("tags"):frontmatter.find("tags")+100]}'
            })

        # Check abstract callout
        if '> [!abstract]' not in content:
            issues.append({
                'file': filename,
                'issue': 'Missing abstract callout'
            })

print(f"Found {len(issues)} issues:\n")
for issue in issues:
    print(f"- {issue['file']}: {issue['issue']}")
