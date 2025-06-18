# Product Hunt 每日热榜部署指南

## ⚡ 快速开始（10分钟部署）

### 🎯 最小化配置清单

只需要这5个 Token 即可开始：

1. **Product Hunt Token** → [立即获取](https://www.producthunt.com/v2/oauth/applications)
2. **DeepSeek API Key** → [立即获取](https://platform.deepseek.com/api_keys)
3. **GitHub PAT (主仓库)** → [立即获取](https://github.com/settings/tokens/new)
4. **GitHub PAT (Hugo仓库)** → [立即获取](https://github.com/settings/tokens/new)
5. **配置 GitHub Secrets** → 在仓库设置中添加

### 💰 成本估算
- **Product Hunt**: 免费
- **DeepSeek**: 每天 < 0.1元
- **GitHub**: 免费
- **总成本**: 每月 < 3元

---

## 📋 详细部署指南

### 必需的账户和服务

1. **GitHub 账户** - 用于代码托管和 Actions 运行
2. **Product Hunt 开发者账户** - 获取 API Token
3. **LLM 服务账户** - 推荐 DeepSeek（性价比最高）
4. **Hugo 网站仓库** - 目标发布仓库

## 🔑 第一步：获取必需的 API Keys

### 1. Product Hunt Developer Token

**直接链接**: [https://www.producthunt.com/v2/oauth/applications](https://www.producthunt.com/v2/oauth/applications)

**详细步骤**:
1. 访问 [Product Hunt OAuth Applications](https://www.producthunt.com/v2/oauth/applications)
2. 使用您的 Product Hunt 账户登录
3. 点击 **"Create an application"** 按钮
4. 填写应用信息：
   - **Name**: `Product Hunt Daily Bot`
   - **Redirect URI**: `http://localhost` (可以是任意值)
   - **Description**: `Automated daily Product Hunt content generator`
5. 点击 **"Create application"**
6. 在应用详情页面，复制 **"API key"**
7. 保存格式：`xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` (32位字符串)

**注意**: 如果没有开发者权限，可能需要先申请。通常个人用户可以直接创建应用。

### 2. DeepSeek API Key（推荐）

**直接链接**: [https://platform.deepseek.com/api_keys](https://platform.deepseek.com/api_keys)

**详细步骤**:
1. 访问 [DeepSeek 平台](https://platform.deepseek.com/)
2. 点击右上角 **"登录"** 或 **"注册"**
3. 如果是新用户：
   - 选择注册方式（邮箱/手机号）
   - 完成验证和账户创建
   - 新用户通常有免费额度
4. 登录后，直接访问 [API Keys 页面](https://platform.deepseek.com/api_keys)
5. 点击 **"创建 API Key"** 按钮
6. 填写 API Key 信息：
   - **名称**: `Product Hunt Daily`
   - **权限**: 保持默认（通常是全部权限）
7. 点击 **"创建"**
8. **立即复制并保存** API Key（只显示一次！）
9. 保存格式：`sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

**费用说明**: DeepSeek 价格非常便宜，每天处理约30次调用成本不到0.1元。

### 3. GitHub Personal Access Token

#### 创建 PAT（用于主仓库操作）

**直接链接**: [https://github.com/settings/tokens/new](https://github.com/settings/tokens/new)

**详细步骤**:
1. 访问 [GitHub Personal Access Tokens](https://github.com/settings/tokens/new)
2. 如果未登录，先登录 GitHub 账户
3. 填写 Token 信息：
   - **Note**: `Product Hunt Daily - Main Repo`
   - **Expiration**: 选择 `No expiration` 或 `1 year`
4. 选择权限范围：
   - ✅ **repo** (完整仓库权限)
     - ✅ repo:status
     - ✅ repo_deployment
     - ✅ public_repo
     - ✅ repo:invite
     - ✅ security_events
   - ✅ **workflow** (工作流权限)
   - ✅ **write:packages** (如果需要)
5. 点击 **"Generate token"**
6. **立即复制并保存** Token（只显示一次！）
7. 保存格式：`ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

#### 创建 HUGO_PUSH_TOKEN（用于Hugo仓库操作）

**直接链接**: [https://github.com/settings/tokens/new](https://github.com/settings/tokens/new)

**详细步骤**:
1. 再次访问 [GitHub Personal Access Tokens](https://github.com/settings/tokens/new)
2. 填写 Token 信息：
   - **Note**: `Product Hunt Daily - Hugo Push`
   - **Expiration**: 选择 `No expiration` 或 `1 year`
3. 选择权限范围：
   - ✅ **public_repo** (公开仓库权限，适用于 `hugoflow/producthunt-daily-stack`)
   - 或者 ✅ **repo** (如果目标仓库是私有的)
4. 点击 **"Generate token"**
5. **立即复制并保存** Token
6. 保存格式：`ghp_yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy`

**重要提醒**:
- 两个 Token 必须不同，分别用于不同的用途
- Token 只在创建时显示一次，务必立即保存
- 建议在安全的密码管理器中保存这些 Token

### 4. 可选的其他 LLM 提供商

#### OpenAI API Key（可选）

**直接链接**: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

**详细步骤**:
1. 访问 [OpenAI API Keys](https://platform.openai.com/api-keys)
2. 登录您的 OpenAI 账户（需要先注册）
3. 点击 **"Create new secret key"**
4. 填写信息：
   - **Name**: `Product Hunt Daily`
   - **Project**: 选择默认项目或创建新项目
5. 点击 **"Create secret key"**
6. **立即复制并保存** API Key
7. 保存格式：`sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

**注意**: OpenAI 需要绑定信用卡，费用相对较高。

#### Gemini API Key（可选）

**直接链接**: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

**详细步骤**:
1. 访问 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 使用 Google 账户登录
3. 点击 **"Create API key"**
4. 选择项目或创建新项目
5. 复制生成的 API Key
6. 保存格式：`xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

**注意**: Gemini 有免费额度，但可能有地区限制。

#### OpenRouter API Key（可选）

**直接链接**: [https://openrouter.ai/keys](https://openrouter.ai/keys)

**详细步骤**:
1. 访问 [OpenRouter Keys](https://openrouter.ai/keys)
2. 注册并登录 OpenRouter 账户
3. 点击 **"Create Key"**
4. 填写 Key 名称：`Product Hunt Daily`
5. 复制生成的 API Key
6. 保存格式：`sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

**优势**: OpenRouter 提供多种模型选择，价格灵活。

### 🚀 快速获取 Token 总结

| Token 类型 | 必需性 | 直接链接 | 预计时间 | 费用 |
|-----------|--------|----------|----------|------|
| **Product Hunt** | ✅ 必需 | [创建应用](https://www.producthunt.com/v2/oauth/applications) | 2分钟 | 免费 |
| **DeepSeek** | ✅ 必需 | [API Keys](https://platform.deepseek.com/api_keys) | 3分钟 | 极低 |
| **GitHub PAT** | ✅ 必需 | [创建Token](https://github.com/settings/tokens/new) | 2分钟 | 免费 |
| **Hugo Push Token** | ✅ 必需 | [创建Token](https://github.com/settings/tokens/new) | 2分钟 | 免费 |
| **OpenAI** | ⚪ 可选 | [API Keys](https://platform.openai.com/api-keys) | 3分钟 | 较高 |
| **Gemini** | ⚪ 可选 | [AI Studio](https://aistudio.google.com/app/apikey) | 2分钟 | 免费额度 |
| **OpenRouter** | ⚪ 可选 | [Keys](https://openrouter.ai/keys) | 3分钟 | 中等 |

**总计时间**: 约 10-15 分钟可获取所有必需的 Token

## ⚙️ 第二步：配置 GitHub Secrets

### 在当前仓库中设置 Secrets

1. 进入仓库 Settings > Secrets and variables > Actions
2. 点击 "New repository secret"
3. 添加以下 Secrets：

#### 必需的 Secrets

```bash
# 基础配置
PAT=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
HUGO_PUSH_TOKEN=ghp_yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
PRODUCTHUNT_DEVELOPER_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# LLM配置（推荐DeepSeek）
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### 可选的 Secrets（其他LLM提供商）

```bash
# OpenAI（如果需要）
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o-2024-08-06

# Gemini（如果需要）
GEMINI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GEMINI_MODEL=gemini-2.0-flash

# OpenRouter（如果需要）
OPENROUTER_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENROUTER_MODEL=deepseek/deepseek-chat-v3-0324
```

### Secrets 配置详细说明

| Secret 名称 | 必需性 | 说明 | 示例值 |
|------------|--------|------|--------|
| `PAT` | ✅ 必需 | 主仓库操作权限 | `ghp_xxxx...` |
| `HUGO_PUSH_TOKEN` | ✅ 必需 | Hugo仓库推送权限 | `ghp_yyyy...` |
| `PRODUCTHUNT_DEVELOPER_TOKEN` | ✅ 必需 | Product Hunt API访问 | `xxxx...` |
| `LLM_PROVIDER` | ✅ 必需 | LLM提供商选择 | `deepseek` |
| `DEEPSEEK_API_KEY` | ✅ 必需 | DeepSeek API密钥 | `sk-xxxx...` |
| `OPENAI_API_KEY` | ⚪ 可选 | OpenAI API密钥 | `sk-xxxx...` |
| `GEMINI_API_KEY` | ⚪ 可选 | Gemini API密钥 | `xxxx...` |
| `OPENROUTER_API_KEY` | ⚪ 可选 | OpenRouter API密钥 | `sk-xxxx...` |

## 🎯 第三步：验证 Hugo 仓库配置

### 确认目标仓库信息

1. **仓库地址**: `hugoflow/producthunt-daily-stack`
2. **目标路径**: `content/news/`
3. **分支**: `main`

### 验证权限

1. 确保 `HUGO_PUSH_TOKEN` 对应的账户对目标仓库有写入权限
2. 测试方法：
   ```bash
   curl -H "Authorization: token YOUR_HUGO_PUSH_TOKEN" \
        https://api.github.com/repos/hugoflow/producthunt-daily-stack
   ```

## 🚀 第四步：部署验证

### 1. 手动触发测试

1. 进入 GitHub Actions 页面
2. 选择 "Generate Daily Markdown" 工作流
3. 点击 "Run workflow"
4. 选择分支并运行

### 2. 检查执行日志

监控以下关键步骤：
- ✅ 环境变量加载
- ✅ Product Hunt 数据获取
- ✅ LLM 内容处理
- ✅ Hugo Front Matter 生成
- ✅ 文件生成和提交
- ✅ Hugo 发布工作流触发

### 3. 验证输出结果

#### 检查当前仓库
- 文件路径：`data/producthunt-daily-YYYY-MM-DD.md`
- 内容包含：Hugo Front Matter + 产品列表

#### 检查 Hugo 仓库
- 仓库：`hugoflow/producthunt-daily-stack`
- 文件路径：`content/news/producthunt-daily-YYYY-MM-DD.md`
- 提交信息：`auto: publish Product Hunt daily YYYY-MM-DD HH:MM:SS UTC`

## 📅 第五步：定时任务配置

### 当前定时设置

- **执行时间**: 每天 UTC 9:00 (北京时间 17:00)
- **Cron 表达式**: `'0 9 * * *'`

### 自定义执行时间（可选）

如需修改执行时间，编辑 `.github/workflows/generate_markdown.yml`：

```yaml
schedule:
  - cron: '0 9 * * *'  # 修改这里
```

常用时间设置：
- `'0 8 * * *'` - 每天 UTC 8:00 (北京时间 16:00)
- `'0 10 * * *'` - 每天 UTC 10:00 (北京时间 18:00)
- `'0 0 * * *'` - 每天 UTC 0:00 (北京时间 8:00)

## 🔧 第六步：故障排除

### 常见问题及解决方案

#### 1. Product Hunt API 调用失败
```
错误：获取Product Hunt数据失败
解决：检查 PRODUCTHUNT_DEVELOPER_TOKEN 是否正确
```

#### 2. LLM API 调用失败
```
错误：LLM调用失败
解决：检查对应的 API Key 和提供商配置
```

#### 3. Hugo 仓库推送失败
```
错误：推送到Hugo仓库失败 (403 Forbidden)
解决：检查 PAT 权限和 HUGO_REPO_URL 配置
```

#### 4. 仓库配置错误
```
错误：未配置HUGO_REPO_URL
解决：在GitHub Secrets中设置HUGO_REPO_URL为 hugoflow/producthunt-daily-stack
```

### 调试命令

#### 测试 API 连接
```bash
# 测试 Product Hunt API
curl -H "Authorization: Bearer YOUR_PH_TOKEN" \
     https://api.producthunt.com/v2/api/graphql

# 测试 DeepSeek API
curl -H "Authorization: Bearer YOUR_DEEPSEEK_KEY" \
     https://api.deepseek.com/v1/models
```

#### 查看工作流日志
1. 进入 GitHub Actions 页面
2. 点击具体的工作流运行
3. 查看详细的步骤日志

## 📊 第七步：监控和维护

### 监控指标

1. **执行成功率** - 工作流是否正常完成
2. **执行时间** - 是否在预期的1-2分钟内
3. **内容质量** - 生成的内容是否符合预期
4. **API 使用量** - 避免超出配额限制

### 定期维护

1. **每周检查**：
   - 工作流执行状态
   - 生成内容质量
   - API 使用情况

2. **每月检查**：
   - API Key 有效期
   - 仓库权限状态
   - 性能优化机会

## ✅ 部署检查清单

### 部署前检查
- [ ] Product Hunt Developer Token 已获取
- [ ] DeepSeek API Key 已获取
- [ ] GitHub PAT 已创建（对Hugo仓库有完整repo权限）
- [ ] HUGO_REPO_URL 已设置为 `hugoflow/producthunt-daily-stack`
- [ ] 所有 Secrets 已在 GitHub 仓库中配置

### 部署后验证
- [ ] 手动触发工作流成功执行
- [ ] 当前仓库生成了 data/producthunt-daily-*.md 文件
- [ ] Hugo 仓库收到了 content/posts/producthunt-daily-*.md 文件
- [ ] 生成的内容包含完整的 Hugo Front Matter
- [ ] 翻译内容无翻译说明，质量良好
- [ ] 图片链接有效且已优化

### 长期运行验证
- [ ] 定时任务正常执行（等待下一个执行周期）
- [ ] 内容持续直接推送到 Hugo 仓库
- [ ] Hugo 网站自动更新显示新内容

---

**部署完成后，系统将每天自动生成高质量的 Product Hunt 热榜内容！** 🎉

如有问题，请查看 GitHub Actions 日志或参考故障排除部分。
