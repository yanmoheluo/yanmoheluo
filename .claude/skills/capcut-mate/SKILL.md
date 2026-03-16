---
name: capcut-mate
description: CapCut Mate API 剪映草稿自动化助手的使用指南，包括安装部署、API接口、操作示例
---

# CapCut Mate API 技能

> 开源免费的剪映草稿自动化助手，基于 FastAPI 构建

## 项目简介

CapCut Mate API 是一个**完全开源免费**的剪映（Jianying）草稿自动化助手，基于 **FastAPI** 开发，支持**独立部署**。

- GitHub：https://github.com/Hommy-master/capcut-mate
- API 文档：http://localhost:30000/docs

## 核心功能

- 🎬 草稿管理：创建、获取、保存草稿
- 🎥 素材添加：视频、音频、图片、贴纸、字幕、特效、蒙版
- 🔧 高级功能：关键帧控制、文本样式、动画效果
- 📤 视频导出：云渲染生成最终视频

## 快速部署

### Docker 部署（推荐）

```bash
git clone https://github.com/Hommy-master/capcut-mate.git
cd capcut-mate
docker-compose pull && docker-compose up -d
```

### 本地部署

```bash
# 安装 uv
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 克隆并安装
git clone git@github.com:Hommy-master/capcut-mate.git
cd capcut-mate
uv sync
uv pip install -e .[windows]  # Windows 额外

# 启动
uv run main.py
```

访问：http://localhost:30000/docs

## 核心 API 接口

| 分类 | 接口 | 功能 |
|------|------|------|
| 草稿 | create_draft | 创建草稿 |
| 草稿 | get_draft | 获取草稿 |
| 草稿 | save_draft | 保存草稿 |
| 素材 | add_videos | 添加视频 |
| 素材 | add_images | 添加图片 |
| 素材 | add_audios | 添加音频 |
| 素材 | add_sticker | 添加贴纸 |
| 字幕 | add_captions | 添加字幕 |
| 特效 | add_effects | 添加特效 |
| 特效 | add_keyframes | 关键帧动画 |
| 生成 | gen_video | 云渲染生成视频 |
| 生成 | gen_video_status | 查询生成状态 |

## API 使用示例

### 创建草稿

```bash
curl -X POST "http://localhost:30000/openapi/capcut-mate/v1/create_draft" \
-H "Content-Type: application/json" \
-d '{"width": 1080, "height": 1920}'
```

### 添加视频

```bash
curl -X POST "http://localhost:30000/openapi/capcut-mate/v1/add_videos" \
-H "Content-Type: application/json" \
-d '{
  "draft_url": "http://localhost:30000/.../get_draft?draft_id=xxx",
  "video_infos": [{"url": "https://example.com/video.mp4", "start": 0, "end": 1000000}]
}'
```

## Coze 集成

支持一键导入 Coze 平台构建自动化工作流：

1. 打开 https://coze.cn/home
2. 添加插件 → 导入插件
3. 上传项目中的 `openapi.yaml` 文件
4. 启用插件

## 相关资源

- [📖 详细使用说明](../01Areas/常用代码/CapCut Mate API 使用说明.md)
- [🔗 工作流示例](https://jcaigc.cn/workflow)
- [🔌 Coze 插件](https://www.coze.cn/store/plugin/7576197869707722771)
