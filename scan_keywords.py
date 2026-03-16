#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扫描项目所有文件，提取关键词库用于自动关联
"""

import re
from pathlib import Path
from collections import defaultdict
import json

def extract_keywords():
    """提取所有文件的标题作为关键词库"""
    base_path = Path(r"D:\BaiduSyncdisk\work_log")

    # 存储所有文件标题
    all_titles = []
    # 分类存储
    categories = defaultdict(list)

    # 需要扫描的目录
    dirs = [
        "00inbox",
        "01Areas",
        "02-Resources",
    ]

    for dir_name in dirs:
        dir_path = base_path / dir_name
        if not dir_path.exists():
            continue

        for md_file in dir_path.rglob("*.md"):
            # 跳过系统目录
            if '.obsidian' in md_file.parts or 'Excalidraw' in md_file.parts:
                continue

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 提取标题
                title = None

                # 从 frontmatter 提取
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 2:
                        fm = parts[1]
                        for line in fm.split('\n'):
                            if line.strip().startswith('title:'):
                                title = line.split('title:')[1].strip()
                                break

                # 从文件名提取
                if not title:
                    title = md_file.stem

                if title:
                    # 清理标题
                    title = re.sub(r'[\d\-]+[_\-]*', '', title)  # 移除日期前缀
                    title = title.strip()

                    # 分类
                    path_str = str(md_file)
                    if 'AI工具' in path_str or 'Claude' in path_str or 'Ollama' in path_str or 'RAG' in path_str:
                        categories['AI工具'].append(title)
                    elif '服务器' in path_str or 'Linux' in path_str or 'CentOS' in path_str:
                        categories['服务器'].append(title)
                    elif '常用代码' in path_str or 'API' in path_str:
                        categories['编程'].append(title)
                    elif '学习笔记' in path_str:
                        categories['学习'].append(title)
                    elif '读书笔记' in path_str:
                        categories['读书'].append(title)
                    elif '生活知识' in path_str:
                        categories['生活'].append(title)

                    all_titles.append(title)

            except Exception as e:
                pass

    return all_titles, categories


def build_relation_rules():
    """构建关联规则"""
    all_titles, categories = extract_keywords()

    # 基于分类建立关联规则
    rules = {}

    # 编程相关关键词
    php_keywords = [t for t in all_titles if 'php' in t.lower() or 'PHP' in t]
    mysql_keywords = [t for t in all_titles if 'mysql' in t.lower() or 'SQL' in t or 'sql' in t.lower()]
    linux_keywords = [t for t in all_titles if 'linux' in t.lower() or 'CentOS' in t]
    api_keywords = [t for t in all_titles if 'API' in t or '接口' in t]
    git_keywords = [t for t in all_titles if 'git' in t.lower()]

    # AI 相关
    ai_keywords = [t for t in all_titles if 'AI' in t or 'Claude' in t or 'Ollama' in t or 'RAG' in t or '提示词' in t]
    obsidian_keywords = [t for t in all_titles if 'Obsidian' in t or 'obsidian' in t.lower()]

    # 生成关联映射
    relations = {
        'PHP': php_keywords[:5],
        'MySQL': mysql_keywords[:5],
        'SQL': mysql_keywords[:5],
        'Linux': linux_keywords[:5],
        'CentOS': linux_keywords[:5],
        'API': api_keywords[:5],
        '接口': api_keywords[:5],
        'Git': git_keywords[:3],
        'AI': ai_keywords[:5],
        '提示词': [t for t in all_titles if '提示词' in t][:5],
        'Claude': [t for t in all_titles if 'Claude' in t][:3],
        'Ollama': [t for t in all_titles if 'Ollama' in t][:3],
        'RAG': [t for t in all_titles if 'RAG' in t][:3],
        'Obsidian': obsidian_keywords[:3],
        '笔记': [t for t in all_titles if '笔记' in t][:5],
        '学习': [t for t in all_titles if '笔记' in t or '学习' in t][:5],
        '读书': [t for t in all_titles if '读书' in t or '笔记' in t][:5],
    }

    return relations, categories


if __name__ == '__main__':
    relations, categories = build_relation_rules()

    print("=" * 50)
    print("关联规则生成完成")
    print("=" * 50)

    print("\n[分类统计]")
    for cat, titles in categories.items():
        print(f"  {cat}: {len(titles)} 个文件")

    print("\n[关联规则示例]")
    for key, values in relations.items():
        if values:
            print(f"  {key}: {values[:3]}")

    # 保存为 JSON 供脚本使用
    import json
    with open('relation_rules.json', 'w', encoding='utf-8') as f:
        # 转换为可序列化的格式
        data = {k: v for k, v in relations.items() if v}
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\n[保存] 关联规则已保存到 relation_rules.json")
