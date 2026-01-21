# API 配置指南

本文档说明如何配置即梦 AI API 密钥，以便插件能够直接调用 API 生成图片。

## 支持的生图 API

目前插件支持以下生图 API：

- **即梦 AI（火山引擎）** - 推荐，国内访问稳定

## 配置步骤

### 即梦 AI API（火山引擎）

#### 1. 获取 API 凭证

1. 登录 [火山引擎控制台](https://console.volcengine.com/)
2. 进入「访问控制」→「访问密钥」
3. 创建或复制 Access Key ID 和 Secret Access Key
4. 开通「智能创作」服务并确保账户有余额

#### 2. 配置方式

**方式一：配置文件（推荐）**

编辑 `config/settings.json`：

```json
{
  "jimeng": {
    "access_key_id": "your-access-key-id-here",
    "secret_access_key": "your-secret-access-key-here"
  }
}
```

**方式二：环境变量**

```bash
export VOLC_ACCESSKEY="your-access-key-id"
export VOLC_SECRETKEY="your-secret-access-key"
```

#### 3. 测试配置

```bash
uv run -p 3.14 --no-project \
  --with requests \
  scripts/generate_image.py \
  --prompt "A simple blue gradient background" \
  --output test.png
```

如果看到 `✅ 图片已生成: test.png`，说明配置成功！

#### 价格参考

- 即梦 4.0：约 ¥0.1 per image
- 国内访问稳定，无需代理

## 在插件中使用

### 自动检测配置

插件会按以下优先级加载配置：

1. 项目配置：`{项目目录}/.claude/config/settings.json`
2. 插件配置：`{插件目录}/config/settings.json`
3. 环境变量：`VOLC_ACCESSKEY` 和 `VOLC_SECRETKEY`

## 成本估算

假设一篇文章需要生成 3 张 AI 图片：

| API | 单张价格 | 3 张总价 | 质量 | 速度 |
|-----|---------|---------|------|------|
| 即梦 AI | ~¥0.1 | ~¥0.3 | ⭐⭐⭐⭐ | ⚡⚡⚡ |

## 常见问题

### Q: 如何查看我的 API 配额？

访问 [火山引擎控制台](https://console.volcengine.com/) → 费用中心 → 账户总览

### Q: API 调用失败怎么办？

1. **检查 API 凭证是否正确**
   ```bash
   echo $VOLC_ACCESSKEY
   echo $VOLC_SECRETKEY
   ```

2. **查看错误信息**
   脚本会显示详细的错误信息，如：
   - `401 Unauthorized` → API 凭证无效
   - `429 Too Many Requests` → 超过配额限制
   - `503 Service Unavailable` → API 服务暂时不可用

3. **降级方案**
   如果 API 不可用，插件会自动降级为输出提示词占位符，供用户手动生成。

### Q: 生成的图片保存在哪里？

默认保存在 `output/images/` 目录，可通过 `config/settings.json` 中的 `output.images_dir` 配置。

## 最佳实践

1. **使用项目级配置**
   - 不同项目可以有不同的 API 配置
   - 配置文件不要提交到 Git

2. **做好错误处理**
   - 图片生成失败不会阻断整体流程
   - 失败时会输出占位符和提示词

3. **缓存生成的图片**
   - 相同提示词不重复生成
   - 节省成本和时间

## 安全提醒

⚠️ **不要将 API 密钥提交到版本控制**

在 `.gitignore` 中添加：
```
.claude/config/settings.json
config/settings.json
```

---

配置完成后，插件就能自动调用即梦 AI 生成精美的配图了！🎨
