# 配置文件说明

## 配置加载优先级

脚本会按以下优先级加载配置：

1. **项目配置**（最高优先级）: `{项目目录}/.claude/config/settings.json`
2. **插件配置**（降级方案）: `{插件目录}/config/settings.json`

## 使用方式

### 方式一：项目级配置（推荐）

在你的项目中创建配置文件：

```bash
mkdir -p .claude/config
cp /path/to/wechat-article-toolkit/config/settings.example.json .claude/config/settings.json
# 编辑 .claude/config/settings.json 填入你的配置
```

这样每个项目可以有独立的配置（不同的公众号、不同的 API Key 等）。

### 方式二：插件级配置

如果你只有一个公众号，可以在插件目录创建配置：

```bash
cd /path/to/wechat-article-toolkit/config
cp settings.example.json settings.json
# 编辑 settings.json 填入你的配置
```

## 配置项说明

```json
{
  "jimeng": {
    "access_key_id": "火山引擎 Access Key ID",
    "secret_access_key": "火山引擎 Secret Access Key"
  },
  "gemini": {
    "api_key": "你的 Gemini API Key",
    "base_url": "API 地址（可选，用于代理）",
    "model": "模型名称"
  },
  "wechat": {
    "appid": "微信公众号 AppID（wx开头18位）",
    "appsecret": "微信公众号 AppSecret",
    "base_url": "微信API地址（一般不需要修改）"
  },
  "output": {
    "base_dir": "输出目录",
    "images_dir": "图片子目录"
  }
}
```

### 即梦 API 配置

即梦是火山引擎提供的图片生成服务，默认用于封面图生成。

**获取凭证步骤**：
1. 登录 [火山引擎控制台](https://console.volcengine.com/)
2. 进入「访问控制」→「访问密钥」
3. 创建或复制 Access Key ID 和 Secret Access Key
4. 开通「智能创作」服务并确保账户有余额

**环境变量替代方案**：
```bash
export VOLC_ACCESSKEY="your-access-key-id"
export VOLC_SECRETKEY="your-secret-access-key"
```

## 注意事项

- `settings.json` 包含敏感信息，**不要提交到 Git**
- 项目配置文件建议添加到 `.gitignore`：
  ```
  .claude/config/settings.json
  .claude/config/token_cache.json
  ```
- `settings.example.json` 是模板文件，可以提交到 Git
