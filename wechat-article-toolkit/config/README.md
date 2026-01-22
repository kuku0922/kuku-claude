# 配置文件说明

## 配置文件位置

配置文件路径: `{项目目录}/.claude/config/settings.json`

## 使用方式

在你的项目中创建配置文件：

```bash
mkdir -p .claude/config
cp ~/.claude/plugins/marketplaces/kuku-claude/wechat-article-toolkit/config/settings.example.json .claude/config/settings.json
# 编辑 .claude/config/settings.json 填入你的配置
```

## 配置项说明

```json
{
  "image_generation": {
    "default_provider": "图片生成 AI 提供商（gemini 或 jimeng）"
  },
  "gemini": {
    "api_key": "Google Gemini API Key",
    "model": "Gemini 模型名称（默认 gemini-3-pro-image-preview）"
  },
  "jimeng": {
    "access_key_id": "火山引擎 Access Key ID",
    "secret_access_key": "火山引擎 Secret Access Key"
  },
  "wechat": {
    "appid": "微信公众号 AppID（wx开头18位）",
    "appsecret": "微信公众号 AppSecret",
    "base_url": "微信API地址（一般不需要修改）"
  },
  "output": {
    "base_dir": "输出目录（默认 ./articles）",
    "images_dir": "图片子目录（默认 images）",
    "research_dir": "调研报告子目录（默认 research）"
  }
}
```

## 图片生成配置

### 提供商选择

通过 `image_generation.default_provider` 配置默认的图片生成 AI：

- `gemini` - Google Gemini（默认，国际访问）
- `jimeng` - 即梦 AI / 火山引擎（国内访问稳定）

### Gemini 配置（推荐）

Gemini 是 Google 提供的多模态 AI 服务，支持高质量图片生成。

**获取 API Key**:
1. 访问 [Google AI Studio](https://aistudio.google.com/apikey)
2. 登录 Google 账号
3. 创建或复制 API Key

**配置示例**:
```json
{
  "gemini": {
    "api_key": "your-gemini-api-key",
    "model": "gemini-3-pro-image-preview"
  }
}
```

**环境变量替代方案**：
```bash
export GEMINI_API_KEY="your-gemini-api-key"
# 或
export GOOGLE_API_KEY="your-gemini-api-key"
```

**支持的宽高比**: 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9

**支持的图片尺寸**: 1K, 2K, 4K（默认 2K）

### 即梦 AI 配置

即梦是火山引擎提供的图片生成服务，国内访问稳定。

**获取凭证步骤**：
1. 登录 [火山引擎控制台](https://console.volcengine.com/)
2. 进入「访问控制」→「访问密钥」
3. 创建或复制 Access Key ID 和 Secret Access Key
4. 开通「智能创作」服务并确保账户有余额

**配置示例**:
```json
{
  "jimeng": {
    "access_key_id": "your-access-key-id",
    "secret_access_key": "your-secret-access-key"
  }
}
```

**环境变量替代方案**：
```bash
export VOLC_ACCESSKEY="your-access-key-id"
export VOLC_SECRETKEY="your-secret-access-key"
```

**支持的宽高比**: 1:1, 16:9, 9:16, 4:3, 3:4, 3:2, 2:3, 21:9, 9:21

## 注意事项

- `settings.json` 包含敏感信息，**不要提交到 Git**
- 项目配置文件建议添加到 `.gitignore`：
  ```
  .claude/config/settings.json
  .claude/config/token_cache.json
  ```
- `settings.example.json` 是模板文件，可以提交到 Git
