# Product Hunt 内容生成器配置指南

## 概述

当前项目使用**直接推送模式**：
- **`generate_markdown.yml`** - 内容生成器，直接推送到Hugo Stack仓库

## 🚀 优化功能

### 内容生成优化
- ✅ **Hugo Front Matter 自动生成** - 智能标签、关键词、封面图片
- ✅ **清洁翻译** - 无翻译说明，适合新闻阅读
- ✅ **图片自动选择** - 从 Product Hunt 获取最佳封面
- ✅ **性能优化** - 处理10个精选产品，约1-2分钟完成
- ✅ **SEO 优化** - 动态生成标题、描述、关键词

### 工作流程

```
定时触发 (UTC 9:00) → Checkout main分支 → 内容生成 → 直接推送到Hugo Stack仓库 (content/news/)
```

### 🎯 架构简化 (2025-06-18)

- ❌ **移除**: `auto-content` 分支逻辑
- ❌ **移除**: 复杂的分支同步代码
- ❌ **移除**: `publish-to-hugo.yml` 链式工作流
- ❌ **移除**: 本地文件清理步骤
- ✅ **简化**: 直接在 `main` 分支运行
- ✅ **专注**: 内容生成和直接推送

## 必需的 GitHub Secrets 配置

### 必需的 Secrets

1. **PAT**
   - 用于：直接推送到Hugo Stack仓库
   - 格式：GitHub Personal Access Token
   - 权限：对 `hugoflow/producthunt-daily-stack` 仓库的完整访问权限
   - 获取方式：
     1. 访问 GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)
     2. 点击 "Generate new token (classic)"
     3. 选择权限：`repo` (完整仓库访问权限)
     4. 复制生成的 token

2. **HUGO_REPO_URL**
   - 用于：指定目标Hugo仓库
   - 格式：`username/repo-name`
   - 值：`hugoflow/producthunt-daily-stack`

## 配置步骤

### 1. 设置 GitHub Secrets
在当前仓库 Settings > Secrets and variables > Actions 中添加：

- **PAT**：用于直接推送到Hugo Stack仓库
- **HUGO_REPO_URL**：目标Hugo仓库地址
- **PRODUCTHUNT_DEVELOPER_TOKEN**：Product Hunt API密钥
- **DEEPSEEK_API_KEY**：LLM API密钥（或其他LLM提供商）

### 2. 验证权限
确保PAT有正确的权限：
- `PAT`: 对 `hugoflow/producthunt-daily-stack` 有完整的 `repo` 权限

### 3. 测试工作流
**测试完整流程**：
```
Actions > Generate Daily Markdown > Run workflow
```

## 直接推送模式优势

### ✅ 简化配置
- 只需要一个工作流文件
- 减少了Secrets配置复杂度
- 降低了故障点

### ✅ 更快执行
- 无需等待链式触发
- 减少了API调用开销
- 直接推送，立即生效

### ✅ 易于维护
- 单一工作流，便于调试
- 日志集中，问题定位更容易
- 配置更直观

## 故障排除

### 常见问题

1. **权限错误 (403 Forbidden)**：
   - 检查 `PAT` 是否对 `hugoflow/producthunt-daily-stack` 有写入权限
   - 验证PAT是否过期
   - 确认PAT对应的用户有仓库访问权限

2. **仓库配置错误**：
   - 检查 `HUGO_REPO_URL` 格式是否正确（应为 `hugoflow/producthunt-daily-stack`）
   - 确认目标仓库存在且可访问

3. **内容生成失败**：
   - 检查 `PRODUCTHUNT_DEVELOPER_TOKEN` 是否有效
   - 验证 `DEEPSEEK_API_KEY` 或其他LLM API密钥
   - 查看工作流日志中的错误信息

4. **推送失败**：
   - 确认目标仓库的 `content/posts/` 目录存在
   - 检查是否有Git冲突
   - 验证网络连接和GitHub服务状态

### 权限验证方法

测试PAT权限：
```bash
curl -H "Authorization: token YOUR_PAT" \
     https://api.github.com/repos/hugoflow/producthunt-daily-stack
```

应该返回包含 `"permissions": {"push": true}` 的响应。

### 调试技巧

1. **查看工作流日志**：每个步骤都有详细的输出
2. **检查GitHub Secrets**：确保所有必需的Secrets都已正确设置
3. **验证API密钥**：确认所有API密钥都有效且未过期

## 工作流配置总结

### 当前配置
- **工作流文件**: `.github/workflows/generate_markdown.yml`
- **主脚本**: `scripts/scripts_product_hunt_list_to_md.py` (优化版)
- **目标仓库**: `hugoflow/producthunt-daily-stack`
- **内容路径**: `content/posts/`
- **执行时间**: 每天 UTC 9:00 (北京时间 17:00)
- **默认LLM**: `deepseek` (性能最佳)

### 必需的 Secrets
```bash
# 核心配置
PAT=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
HUGO_REPO_URL=hugoflow/producthunt-daily-stack

# API密钥
PRODUCTHUNT_DEVELOPER_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 可选配置
LLM_PROVIDER=deepseek  # 可选，默认deepseek
```

### 🎯 优化效果
- **执行时间**: 从 4-6 分钟优化到 1-2 分钟
- **内容质量**: 无翻译说明，SEO 友好
- **自动化程度**: 完全自动化，包含 Hugo Front Matter
- **图片质量**: 自动选择最佳封面，优化尺寸
- **配置简化**: 单一工作流，减少配置复杂度

### 📋 配置检查清单

- [ ] `PAT` 已设置且对目标仓库有写入权限
- [ ] `HUGO_REPO_URL` 设置为 `hugoflow/producthunt-daily-stack`
- [ ] `PRODUCTHUNT_DEVELOPER_TOKEN` 已设置且有效
- [ ] `DEEPSEEK_API_KEY` 已设置且有效
- [ ] 工作流手动测试成功
- [ ] 定时任务正常运行

配置完成后，系统将每天自动生成Product Hunt内容并直接推送到Hugo Stack仓库。
