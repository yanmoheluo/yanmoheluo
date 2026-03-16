#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Obsidian 文档自动化处理脚本 v2
修复版：确保正确添加 frontmatter、标签、摘要
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple


class ObsidianFormatter:
    """Obsidian 文档格式化工具"""

    PROJECT_ROOT = Path(r"D:\BaiduSyncdisk\work_log")

    # 关键词到标签的映射（忽略大小写）
    TAG_KEYWORDS = {
        'php': 'PHP',
        'mysql': 'MySQL',
        'sql': 'MySQL',
        'linux': 'Linux',
        '服务器': 'Linux',
        'api': 'API',
        'git': 'Git',
        'python': 'Python',
        'javascript': 'JavaScript',
        'curl': 'curl',
        '正则': '正则表达式',
        '加密': '加密',
        'deepseek': 'AI',
        'ollama': 'AI',
        'claude': 'AI',
        'windows': 'Windows',
        'ssh': 'SSH',
    }

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.processed_files = []
        self.skipped_files = []
        self.error_files = []
        self.relation_rules = self.load_relation_rules()

    def load_relation_rules(self) -> Dict[str, List[str]]:
        """加载关联规则"""
        rules_file = self.PROJECT_ROOT / "relation_rules.json"
        if rules_file.exists():
            try:
                with open(rules_file, 'r', encoding='utf-8') as f:
                    rules = json.load(f)
                cleaned = {}
                for key, values in rules.items():
                    cleaned[key] = [v for v in values if v and not v.startswith('*') and not v.startswith('.') and len(v) > 2]
                return cleaned
            except:
                pass
        return self.get_default_relations()

    def get_default_relations(self) -> Dict[str, List[str]]:
        return {
            'PHP': ['PHP常用函数大全', 'mysql 常用查询语句'],
            'MySQL': ['mysql 常用查询语句', 'mysql 优化索引'],
            'Linux': ['Linux CentOS 7常用命令', 'ngn ix'],
            'API': ['API索引', 'curl 并发处理'],
            'Obsidian': ['Obsidian系列教程目录'],
            'AI': ['AI提示词收藏目录'],
        }

    def extract_title_from_content(self, content: str) -> Optional[str]:
        """从内容中提取标题"""
        # 尝试从第一行 # 标题提取
        match = re.match(r'^#\s+(.+)$', content.strip(), re.MULTILINE)
        if match:
            return match.group(1).strip()
        return None

    def extract_tags_from_content(self, content: str) -> List[str]:
        """根据内容提取标签"""
        tags = []
        content_lower = content.lower()

        for keyword, tag in self.TAG_KEYWORDS.items():
            if keyword in content_lower:
                if tag not in tags:
                    tags.append(tag)

        return tags[:5]  # 最多5个标签

    def parse_frontmatter(self, content: str) -> Tuple[Dict, str]:
        """解析 frontmatter"""
        frontmatter = {}

        if not content.startswith('---'):
            return frontmatter, content

        parts = content.split('---', 2)
        if len(parts) < 3:
            return frontmatter, content

        fm_text = parts[1]
        body = parts[2]

        for line in fm_text.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            if line.startswith('#'):
                continue
            if line.startswith('- '):
                key = list(frontmatter.keys())[-1] if frontmatter else None
                if key and isinstance(frontmatter[key], list):
                    frontmatter[key].append(line[2:].strip())
            else:
                match = re.match(r'^([^:]+):\s*(.*)$', line)
                if match:
                    key = match.group(1).strip()
                    value = match.group(2).strip()
                    if value:
                        frontmatter[key] = value
                    else:
                        frontmatter[key] = []

        return frontmatter, body

    def format_frontmatter(self, frontmatter: Dict) -> str:
        """格式化 frontmatter"""
        lines = ['---']
        for key, value in frontmatter.items():
            if isinstance(value, list):
                lines.append(f'{key}:')
                for v in value:
                    lines.append(f'  - {v}')
            else:
                lines.append(f'{key}: {value}')
        lines.append('---')
        return '\n'.join(lines)

    def generate_aliases(self, title: str) -> List[str]:
        """生成别名"""
        aliases = []
        clean_title = re.sub(r'(系列教程|笔记|指南|目录|索引|大全|汇总|使用|怎么|如何|条)$', '', title)
        if clean_title != title and len(clean_title) > 2:
            aliases.append(clean_title)
        if '笔记' in title:
            aliases.append(title.replace('笔记', '记录'))
        if '指南' in title:
            aliases.append(title.replace('指南', '手册'))
        if '教程' in title:
            aliases.append(title.replace('教程', '入门'))
        return list(set(aliases))[:3]

    def generate_abstract(self, content: str, title: str) -> str:
        """生成摘要"""
        # 移除代码块
        content = re.sub(r'```[\s\S]*?```', '', content)
        # 移除图片
        content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
        # 移除 HTML
        content = re.sub(r'<[^>]+>', '', content)
        # 移除 frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) > 2:
                content = parts[2]

        # 获取有意义的第一段
        lines = [l.strip() for l in content.split('\n')
                 if l.strip()
                 and not l.strip().startswith('#')
                 and len(l.strip()) > 20]

        first_paragraph = ''
        for line in lines[:10]:
            if 'sk-' not in line and 'http' not in line[:20]:  # 跳过 API key 等
                first_paragraph = line
                break

        if first_paragraph:
            abstract = first_paragraph[:120]
            if len(first_paragraph) > 120:
                abstract += '...'
        else:
            abstract = f'{title}相关文档'

        return abstract

    def find_relations(self, content: str) -> List[str]:
        """查找关联笔记"""
        relations = []
        content_lower = content.lower()

        for keyword, related in self.relation_rules.items():
            if keyword.lower() in content_lower:
                for rel in related:
                    relations.append(rel)

        seen = set()
        unique = []
        for r in relations:
            if r not in seen:
                seen.add(r)
                unique.append(r)

        return unique[:4]

    def add_emoji_numbering(self, content: str) -> str:
        """添加 emoji 编号"""
        emoji_numbers = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

        def replace(match):
            level = len(match.group(1))
            title = match.group(2).strip()
            if title and not any(e in title[0] for e in emoji_numbers):
                num_match = re.match(r'^(\d+)[.、\s]+\s*(.+)', title)
                if num_match:
                    idx = int(num_match.group(1)) - 1
                    if 0 <= idx < len(emoji_numbers):
                        return f"{'#' * level} {emoji_numbers[idx]} {num_match.group(2)}"
            return match.group(0)

        return re.sub(r'^(#{1,6})\s+(.+)$', replace, content, flags=re.MULTILINE)

    def process_file(self, file_path: Path) -> bool:
        """处理单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 解析现有 frontmatter
            frontmatter, body = self.parse_frontmatter(content)

            # 获取标题
            title = frontmatter.get('title')
            if not title:
                title = self.extract_title_from_content(content)
            if not title:
                title = file_path.stem

            # 如果已有 date 和 tags，检查是否需要补充标签
            if frontmatter.get('date') and frontmatter.get('tags'):
                # 提取内容中的标签（包含标题和正文）
                full_text = f"{title} {body}"
                content_tags = self.extract_tags_from_content(full_text)
                existing_tags = frontmatter.get('tags', [])
                if isinstance(existing_tags, str):
                    existing_tags = [existing_tags]

                # 补充缺失的标签
                tags_added = False
                for tag in content_tags:
                    if tag not in existing_tags:
                        existing_tags.append(tag)
                        tags_added = True

                if tags_added:
                    frontmatter['tags'] = existing_tags
                    # 重新组装
                    parts = []
                    parts.append(self.format_frontmatter(frontmatter))
                    parts.append('\n')
                    parts.append(body.strip())
                    parts.append('\n')

                    new_content = ''.join(parts)
                    new_content = self.add_emoji_numbering(new_content)

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)

                    self.processed_files.append(str(file_path))
                    print(f"[OK] Added tags: {file_path.name}")
                    return True
                else:
                    self.skipped_files.append(str(file_path))
                    return False

            # 生成标签
            tags = frontmatter.get('tags', [])
            if isinstance(tags, str):
                tags = [tags]
            if not tags:
                tags = self.extract_tags_from_content(body)

            # 添加默认标签
            if '代码' not in tags and '编程' not in tags:
                tags.insert(0, '代码')

            # 生成别名
            aliases = self.generate_aliases(title)

            # 生成摘要
            abstract = self.generate_abstract(body, title)

            # 查找关联
            relations = self.find_relations(body)

            # 更新 frontmatter
            frontmatter['title'] = title
            frontmatter['date'] = datetime.now().strftime('%Y-%m-%d')
            frontmatter['tags'] = tags
            if aliases and 'aliases' not in frontmatter:
                frontmatter['aliases'] = aliases

            # 重新组装
            parts = []
            parts.append(self.format_frontmatter(frontmatter))
            parts.append('\n')

            # 添加摘要 callout
            if '> [!abstract]' not in body:
                parts.append(f'> [!abstract] 摘要\n> {abstract}\n')
                parts.append('---\n')

            # 添加 body（移除旧的 frontmatter）
            body_clean = body
            if body_clean.startswith('---'):
                parts_body = body_clean.split('---', 2)
                if len(parts_body) > 2:
                    body_clean = parts_body[2]

            parts.append(body_clean.strip())
            parts.append('\n')

            # 添加关联笔记
            if relations and '## 关联笔记' not in body and '## 关联' not in body:
                parts.append('\n---\n\n## 关联笔记\n\n')
                for rel in relations:
                    parts.append(f'- [[{rel}]]\n')

            new_content = ''.join(parts)
            new_content = self.add_emoji_numbering(new_content)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            self.processed_files.append(str(file_path))
            return True

        except Exception as e:
            self.error_files.append((str(file_path), str(e)))
            return False

    def process_directory(self, extensions: List[str] = ['.md']):
        """处理目录"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Processing: {self.base_path}")
        print("=" * 50)

        for ext in extensions:
            for file_path in self.base_path.rglob(f'*{ext}'):
                if '.obsidian' in file_path.parts:
                    continue
                if self.process_file(file_path):
                    print(f"[OK] {file_path.name}")

        print("=" * 50)
        print(f"\n[Done] Complete!")
        print(f"   [OK] Processed: {len(self.processed_files)}")
        print(f"   [--] Skipped: {len(self.skipped_files)}")
        print(f"   [X] Errors: {len(self.error_files)}")

        if self.error_files:
            print("\n[X] Errors:")
            for path, err in self.error_files:
                print(f"   {path}: {err}")

        return self.processed_files


def main():
    import sys
    if len(sys.argv) < 2:
        print(__doc__)
        base_path = "."
    else:
        base_path = sys.argv[1]

    formatter = ObsidianFormatter(base_path)
    formatter.process_directory()


if __name__ == '__main__':
    main()
