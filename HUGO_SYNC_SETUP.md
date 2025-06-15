# 优化版链式工作流配置指南

## 概述

您的 GitHub Actions 现在使用优化版链式触发模式：
1. **`generate_markdown.yml`** - 优化版内容生成器（主工作流）
2. **`publish-to-hugo.yml`** - Hugo 发布器（下游工作流）

## 🚀 优化功能

### 内容生成优化
- ✅ **Hugo Front Matter 自动生成** - 智能标签、关键词、封面图片
- ✅ **清洁翻译** - 无翻译说明，适合新闻阅读
- ✅ **图片自动选择** - 从 Product Hunt 获取最佳封面
- ✅ **性能优化** - 处理10个精选产品，约1-2分钟完成
- ✅ **SEO 优化** - 动态生成标题、描述、关键词

### 工作流程

```
定时触发 (UTC 7:01) → 优化版内容生成 → 提交到当前仓库 → 触发Hugo发布 → 推送到Hugo仓库 (content/news/)
```

## 必需的 GitHub Secrets 配置

### 必需的 Secrets

1. **PAT** (已有)
   - 用于：推送到当前仓库 + 触发下游工作流
   - 权限：需要 `repo` 和 `actions:write` 权限

2. **HUGO_PUSH_TOKEN** (新增)
   - 用于：推送到 Hugo 仓库
   - 格式：GitHub Personal Access Token
   - 权限：对 `hugoflow/producthunt-daily-stack` 仓库的 `Contents: Write` 权限
   - 获取方式：
     1. 访问 GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)
     2. 点击 "Generate new token (classic)"
     3. 选择权限：`repo` (如果是私有仓库) 或 `public_repo` (如果是公开仓库)
     4. 复制生成的 token

## 配置步骤

### 1. 设置 GitHub Secrets
在当前仓库 Settings > Secrets and variables > Actions 中添加：

- **PAT** (如果还没有)：用于推送和触发工作流
- **HUGO_PUSH_TOKEN** (新增)：用于推送到 Hugo 仓库

### 2. 验证权限
确保 tokens 有正确的权限：
- `PAT`: 对当前仓库有 `repo` 和 `actions:write` 权限
- `HUGO_PUSH_TOKEN`: 对 `hugoflow/producthunt-daily-stack` 有写入权限

### 3. 测试工作流
1. **测试完整流程**：
   ```
   Actions > Generate Daily Markdown > Run workflow
   ```

2. **测试独立发布**：
   ```
   Actions > Publish to Hugo > Run workflow
   ```

## 链式工作流优势

### ✅ 职责分离
- **生成器**：专注内容生成和数据处理
- **发布器**：专注内容发布和部署

### ✅ 独立控制
- 可以单独重新发布内容（不重新生成）
- 可以单独测试发布功能
- 故障隔离：一个环节失败不影响另一个

### ✅ 灵活扩展
- 未来可以添加更多下游工作流
- 可以添加不同的发布目标

## 故障排除

### 常见问题

1. **工作流触发失败**：
   - 检查 `PAT` 是否有 `actions:write` 权限
   - 确认 API 调用返回 200 状态码
   - 查看 `generate_markdown.yml` 的日志

2. **Hugo 发布失败**：
   - 检查 `HUGO_PUSH_TOKEN` 权限
   - 确认目标仓库 `hugoflow/producthunt-daily-stack` 存在
   - 查看 `publish-to-hugo.yml` 的日志

3. **内容未更新**：
   - 确认 `data/` 目录中有新的 .md 文件
   - 检查文件是否被正确复制到 Hugo 仓库
   - 验证 Git 提交是否成功

### 手动触发发布

如果自动触发失败，可以手动触发 Hugo 发布：
```
Actions > Publish to Hugo > Run workflow
```

### 调试技巧

1. **查看工作流日志**：每个步骤都有详细的输出
2. **检查 GitHub API 限制**：确保没有超出 API 调用限制
3. **验证文件路径**：确认文件被复制到正确的位置

## 工作流配置总结

### 当前配置
- **主脚本**: `scripts/scripts_product_hunt_list_to_md.py` (优化版)
- **目标仓库**: `hugoflow/producthunt-daily-stack`
- **内容路径**: `content/news/`
- **触发事件**: `content-generated`
- **源文件路径**: `data/*.md`
- **默认LLM**: `deepseek` (性能最佳)

### 需要的 Secrets
```
PAT: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
HUGO_PUSH_TOKEN: ghp_yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
LLM_PROVIDER: deepseek (可选，默认deepseek)
DEEPSEEK_API_KEY: sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
PRODUCTHUNT_DEVELOPER_TOKEN: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 🎯 优化效果
- **执行时间**: 从 4-6 分钟优化到 1-2 分钟
- **内容质量**: 无翻译说明，SEO 友好
- **自动化程度**: 完全自动化，包含 Hugo Front Matter
- **图片质量**: 自动选择最佳封面，优化尺寸

这样配置后，每次内容生成完成都会自动触发优化版 Hugo 发布流程。
