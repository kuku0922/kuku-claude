#!/usr/bin/env python3
# 依赖声明（使用 uv 临时包策略）:
#   uv run -p 3.14 --no-project --with requests --with google-genai --with pillow
"""
图片生成 API 调用脚本

支持多种图片生成 AI:
- Gemini (Google Nano Banana Pro) - 默认，支持 4K 高清图片
- 即梦 AI (火山引擎) - 国内访问稳定

运行方式:
- 使用 uv -p 3.14 --no-project --with 临时包策略
- 无需创建虚拟环境，无需安装依赖

使用方法:
    uv run -p 3.14 --no-project --with requests --with google-genai --with pillow scripts/generate_image.py --prompt "图片描述" --output output.png
    uv run -p 3.14 --no-project --with requests --with google-genai --with pillow scripts/generate_image.py --prompt "图片描述" --output output.png --provider jimeng
    uv run -p 3.14 --no-project --with requests --with google-genai --with pillow scripts/generate_image.py --prompt "图片描述" --output output.png --image-size 4K
"""

import os
import sys
import argparse
import json
import time
import hashlib
import hmac
import base64
import requests
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timezone
from io import BytesIO

# Gemini SDK imports
try:
    from google import genai
    from google.genai import types
    from PIL import Image
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


# 全局配置缓存
_config_cache: Optional[Dict[str, Any]] = None


def get_project_root() -> Path:
    """
    获取项目根目录(Claude Code 的 cwd)

    Claude Code 启动时会将 cwd 设置为项目根目录
    """
    return Path.cwd()


def load_config() -> Dict[str, Any]:
    """
    从配置文件加载配置

    配置路径: 项目目录/.claude/config/settings.json
    """
    global _config_cache
    if _config_cache is not None:
        return _config_cache

    config_path = get_project_root() / ".claude" / "config" / "settings.json"

    if not config_path.exists():
        print(f"⚠️  配置文件不存在: {config_path}", file=sys.stderr)
        print(f"   请创建配置文件并填入 API 密钥", file=sys.stderr)
        _config_cache = {}
        return _config_cache

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            _config_cache = json.load(f)
            print(f"✓ 已加载配置: {config_path}")
            return _config_cache
    except json.JSONDecodeError as e:
        print(f"❌ 配置文件格式错误: {e}", file=sys.stderr)
        _config_cache = {}
        return _config_cache
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}", file=sys.stderr)
        _config_cache = {}
        return _config_cache


def get_unique_path(output_path: str) -> str:
    """
    获取唯一的文件路径，如果文件已存在则自动加序号

    例如：
    - cover.png 已存在 → cover_1.png
    - cover_1.png 已存在 → cover_2.png
    """
    path = Path(output_path)

    if not path.exists():
        return output_path

    stem = path.stem
    suffix = path.suffix
    parent = path.parent

    counter = 1
    while True:
        new_path = parent / f"{stem}_{counter}{suffix}"
        if not new_path.exists():
            print(f"⚠️  文件已存在，自动重命名: {path.name} → {new_path.name}")
            return str(new_path)
        counter += 1


class ImageGenerator:
    """图片生成器基类"""

    name: str = "base"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    def generate(self, prompt: str, output_path: str, **kwargs) -> str:
        """生成图片并保存"""
        raise NotImplementedError


class GeminiImageGenerator(ImageGenerator):
    """Gemini 图片生成器 (Google)

    使用 Gemini API 生成图片，支持文生图。

    文档: https://ai.google.dev/gemini-api/docs/image-generation
    """

    name = "gemini"

    # API 配置
    BASE_URL = "https://api.vectorengine.ai/v1beta/models"
    DEFAULT_MODEL = "gemini-3-pro-image-preview"  # Nano Banana Pro

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.gemini_config = load_config().get('gemini', {})
        self.api_key = self._get_api_key()
        self.model = self.gemini_config.get('model', self.DEFAULT_MODEL)

    def _get_api_key(self) -> str:
        """获取 Gemini API Key"""
        api_key = self.gemini_config.get('api_key', '')
        if api_key and api_key not in ['your-gemini-api-key-here', '']:
            return api_key

        api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError(
                "请配置 Gemini API Key:\n"
                "  1. 在 .claude/config/settings.json 中设置 gemini.api_key\n"
                "  2. 或设置环境变量 GEMINI_API_KEY\n"
                "  获取 API Key: https://aistudio.google.com/apikey"
            )
        return api_key

    def _parse_aspect_ratio(self, aspect_ratio: str) -> str:
        """解析宽高比，返回 Gemini 支持的格式"""
        # Gemini 支持的宽高比（Nano Banana Pro）
        supported = ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"]
        if aspect_ratio in supported:
            return aspect_ratio
        # 默认返回 16:9
        return "16:9"

    def generate(self, prompt: str, output_path: str, **kwargs) -> str:
        """
        使用 Gemini API 生成图片

        Args:
            prompt: 图片生成提示词
            output_path: 输出文件路径
            **kwargs: 额外参数
                - aspect_ratio: 宽高比（默认 16:9）
                - image_size: 图片尺寸 1K/2K/4K（默认 2K）

        Returns:
            生成的图片文件路径
        """
        aspect_ratio = kwargs.get('aspect_ratio', '16:9')
        image_size = kwargs.get('image_size', '2K')
        gemini_aspect_ratio = self._parse_aspect_ratio(aspect_ratio)

        print(f"  🤖 模型: {self.model}")
        print(f"  📐 宽高比: {gemini_aspect_ratio}")
        print(f"  📏 尺寸: {image_size}")

        url = f"{self.BASE_URL}/{self.model}:generateContent"

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }

        # 构建请求体（使用新的 imageConfig 格式）
        body = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"],
                "imageConfig": {
                    "aspectRatio": gemini_aspect_ratio,
                    "imageSize": image_size
                }
            }
        }

        print("  📤 发送生成请求...")

        try:
            response = requests.post(
                url,
                headers=headers,
                json=body,
                timeout=120
            )
        except requests.exceptions.Timeout:
            raise RuntimeError(
                "Gemini API 请求超时:\n"
                "  - 请检查网络连接\n"
                "  - 或稍后重试"
            )
        except requests.exceptions.RequestException as e:
            raise RuntimeError(
                f"Gemini API 网络请求失败:\n"
                f"  - 错误: {e}\n"
                f"  - 请检查网络连接"
            )

        # 处理响应
        if response.status_code != 200:
            error_detail = ""
            try:
                error_data = response.json()
                error_detail = error_data.get('error', {}).get('message', '')
            except:
                error_detail = response.text[:500]

            raise RuntimeError(
                f"Gemini API 请求失败:\n"
                f"  - 状态码: {response.status_code}\n"
                f"  - 错误: {error_detail}\n"
                f"  - 请检查 API Key 是否有效"
            )

        try:
            result = response.json()
        except json.JSONDecodeError:
            raise RuntimeError(
                "Gemini API 响应解析失败:\n"
                "  - 服务可能暂时不可用\n"
                "  - 请稍后重试"
            )

        # 提取图片数据
        candidates = result.get('candidates', [])
        if not candidates:
            # 检查是否有安全过滤
            prompt_feedback = result.get('promptFeedback', {})
            block_reason = prompt_feedback.get('blockReason', '')
            if block_reason:
                raise RuntimeError(
                    f"Gemini API 内容被过滤:\n"
                    f"  - 原因: {block_reason}\n"
                    f"  - 请修改提示词后重试"
                )
            raise RuntimeError(
                "Gemini API 返回数据异常:\n"
                "  - 没有生成结果\n"
                "  - 请检查提示词或稍后重试"
            )

        # 查找图片数据
        image_data = None
        for candidate in candidates:
            content = candidate.get('content', {})
            parts = content.get('parts', [])
            for part in parts:
                if 'inlineData' in part:
                    inline_data = part['inlineData']
                    if inline_data.get('mimeType', '').startswith('image/'):
                        image_data = inline_data.get('data')
                        break
            if image_data:
                break

        if not image_data:
            # 检查是否只返回了文本
            text_response = ""
            for candidate in candidates:
                content = candidate.get('content', {})
                parts = content.get('parts', [])
                for part in parts:
                    if 'text' in part:
                        text_response += part['text']

            raise RuntimeError(
                f"Gemini API 未返回图片数据:\n"
                f"  - 模型可能只返回了文本响应\n"
                f"  - 文本内容: {text_response[:200]}...\n"
                f"  - 请尝试更明确的图片生成提示词"
            )

        # 解码并保存图片
        try:
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            raise RuntimeError(
                f"图片数据解码失败:\n"
                f"  - 错误: {e}"
            )

        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'wb') as f:
                f.write(image_bytes)

            print(f"  ✓ 生成完成")
            print(f"  💾 图片大小: {len(image_bytes) / 1024:.1f} KB")
        except IOError as e:
            raise RuntimeError(
                f"图片保存失败:\n"
                f"  - 路径: {output_path}\n"
                f"  - 错误: {e}"
            )

        return output_path


class JimengImageGenerator(ImageGenerator):
    """即梦 AI 图片生成器 (火山引擎)

    即梦4.0是即梦同源的图像生成能力，支持文生图、图像编辑及多图组合生成。
    使用异步 API：先提交任务获取 task_id，然后轮询获取结果。

    文档: https://www.volcengine.com/docs/85621/1817045
    """

    name = "jimeng"

    # API 配置
    BASE_URL = "https://visual.volcengineapi.com"
    REGION = "cn-north-1"
    SERVICE = "cv"
    VERSION = "2022-08-31"
    REQ_KEY = "jimeng_t2i_v40"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.jimeng_config = load_config().get('jimeng', {})
        self.api_key = self._get_api_key()

    def _get_api_key(self) -> str:
        """获取 Access Key ID"""
        ak = self.jimeng_config.get('access_key_id', '') or self.jimeng_config.get('ak', '')
        if ak and ak not in ['your-access-key-id-here', '']:
            return ak

        ak = os.environ.get('VOLC_ACCESSKEY') or os.environ.get('JIMENG_AK')
        if not ak:
            raise ValueError(
                "请配置即梦 Access Key ID:\n"
                "  1. 在 .claude/config/settings.json 中设置 jimeng.access_key_id\n"
                "  2. 或设置环境变量 VOLC_ACCESSKEY"
            )
        return ak

    def _get_secret_key(self) -> str:
        """获取 Secret Access Key"""
        sk = self.jimeng_config.get('secret_access_key', '') or self.jimeng_config.get('sk', '')
        if sk and sk not in ['your-secret-access-key-here', '']:
            return sk

        sk = os.environ.get('VOLC_SECRETKEY') or os.environ.get('JIMENG_SK')
        if not sk:
            raise ValueError(
                "请配置即梦 Secret Access Key:\n"
                "  1. 在 .claude/config/settings.json 中设置 jimeng.secret_access_key\n"
                "  2. 或设置环境变量 VOLC_SECRETKEY"
            )
        return sk

    def _sign(self, key: bytes, msg: str) -> bytes:
        """HMAC-SHA256 签名"""
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    def _get_signature_key(self, secret_key: str, date_stamp: str, region: str, service: str) -> bytes:
        """生成签名密钥"""
        k_date = self._sign(secret_key.encode('utf-8'), date_stamp)
        k_region = self._sign(k_date, region)
        k_service = self._sign(k_region, service)
        k_signing = self._sign(k_service, 'request')
        return k_signing

    def _create_authorization_header(self, method: str, action: str, body: str) -> Dict[str, str]:
        """创建火山引擎 API 授权头"""
        ak = self.api_key
        sk = self._get_secret_key()

        now = datetime.now(timezone.utc)
        amz_date = now.strftime('%Y%m%dT%H%M%SZ')
        date_stamp = now.strftime('%Y%m%d')

        host = "visual.volcengineapi.com"
        canonical_uri = "/"
        canonical_querystring = f"Action={action}&Version={self.VERSION}"

        body_hash = hashlib.sha256(body.encode('utf-8')).hexdigest()

        canonical_headers = (
            f"content-type:application/json\n"
            f"host:{host}\n"
            f"x-content-sha256:{body_hash}\n"
            f"x-date:{amz_date}\n"
        )
        signed_headers = "content-type;host;x-content-sha256;x-date"

        canonical_request = (
            f"{method}\n"
            f"{canonical_uri}\n"
            f"{canonical_querystring}\n"
            f"{canonical_headers}\n"
            f"{signed_headers}\n"
            f"{body_hash}"
        )

        algorithm = "HMAC-SHA256"
        credential_scope = f"{date_stamp}/{self.REGION}/{self.SERVICE}/request"
        string_to_sign = (
            f"{algorithm}\n"
            f"{amz_date}\n"
            f"{credential_scope}\n"
            f"{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
        )

        signing_key = self._get_signature_key(sk, date_stamp, self.REGION, self.SERVICE)
        signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

        authorization = (
            f"{algorithm} Credential={ak}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, "
            f"Signature={signature}"
        )

        return {
            "Content-Type": "application/json",
            "Host": host,
            "X-Date": amz_date,
            "X-Content-Sha256": body_hash,
            "Authorization": authorization
        }

    def _submit_task(self, prompt: str, width: int = 2560, height: int = 1440) -> str:
        """提交生成任务，返回 task_id"""
        url = f"{self.BASE_URL}?Action=CVSync2AsyncSubmitTask&Version={self.VERSION}"

        body_data = {
            "req_key": self.REQ_KEY,
            "prompt": prompt,
            "width": width,
            "height": height,
            "force_single": True,
        }
        body = json.dumps(body_data, ensure_ascii=False)

        headers = self._create_authorization_header("POST", "CVSync2AsyncSubmitTask", body)

        try:
            response = requests.post(url, data=body.encode('utf-8'), headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
        except requests.exceptions.Timeout:
            raise RuntimeError(
                "即梦 API 提交任务超时:\n"
                "  - 请检查网络连接\n"
                "  - 或稍后重试"
            )
        except requests.exceptions.RequestException as e:
            raise RuntimeError(
                f"即梦 API 网络请求失败:\n"
                f"  - 错误: {e}\n"
                f"  - 请检查网络连接"
            )
        except json.JSONDecodeError:
            raise RuntimeError(
                "即梦 API 响应解析失败:\n"
                "  - 服务可能暂时不可用\n"
                "  - 请稍后重试"
            )

        code = result.get('code')
        message = result.get('message', 'Unknown error')

        if code != 10000:
            error_hints = {
                10001: "参数错误，请检查提示词是否有效",
                10002: "签名错误，请检查 API 密钥配置",
                10003: "访问频率超限，请稍后重试",
                10004: "余额不足，请充值",
                10005: "服务暂时不可用，请稍后重试",
            }
            hint = error_hints.get(code, "请检查 API 配置或访问火山引擎控制台")

            raise RuntimeError(
                f"即梦 API 提交任务失败:\n"
                f"  - 错误码: {code}\n"
                f"  - 错误信息: {message}\n"
                f"  - 建议: {hint}"
            )

        task_id = result.get('data', {}).get('task_id')
        if not task_id:
            raise RuntimeError(
                "即梦 API 返回数据异常:\n"
                "  - 缺少 task_id\n"
                f"  - 响应: {json.dumps(result, ensure_ascii=False)[:200]}"
            )

        return task_id

    def _query_task(self, task_id: str, return_url: bool = False) -> Dict[str, Any]:
        """查询任务结果"""
        url = f"{self.BASE_URL}?Action=CVSync2AsyncGetResult&Version={self.VERSION}"

        req_json = json.dumps({"return_url": return_url})
        body_data = {
            "req_key": self.REQ_KEY,
            "task_id": task_id,
            "req_json": req_json
        }
        body = json.dumps(body_data, ensure_ascii=False)

        headers = self._create_authorization_header("POST", "CVSync2AsyncGetResult", body)

        try:
            response = requests.post(url, data=body.encode('utf-8'), headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            return {"code": -1, "message": "请求超时"}
        except requests.exceptions.RequestException as e:
            return {"code": -1, "message": f"网络请求失败: {e}"}
        except json.JSONDecodeError:
            return {"code": -1, "message": "响应数据解析失败"}

    def _wait_for_result(self, task_id: str, max_wait: int = 120, interval: int = 2) -> Dict[str, Any]:
        """轮询等待任务完成"""
        start_time = time.time()
        retry_count = 0
        max_retries = 3

        while time.time() - start_time < max_wait:
            elapsed = int(time.time() - start_time)
            result = self._query_task(task_id, return_url=False)

            code = result.get('code')
            data = result.get('data', {})
            status = data.get('status', '') if isinstance(data, dict) else ''
            message = result.get('message', '')

            print(f"  ⏳ [{elapsed}s] 查询状态: code={code}, status={status}")

            if code == -1:
                retry_count += 1
                if retry_count >= max_retries:
                    raise RuntimeError(f"即梦 API 查询失败（重试 {max_retries} 次）: {message}")
                print(f"  ⚠️  查询失败，重试中 ({retry_count}/{max_retries})...")
                time.sleep(interval)
                continue

            retry_count = 0

            if code == 10000:
                if status == 'done':
                    print(f"  ✓ 任务完成，耗时 {elapsed} 秒")
                    return result
                elif status in ['in_queue', 'generating']:
                    time.sleep(interval)
                    continue
                elif status == 'not_found':
                    raise RuntimeError(
                        f"即梦 API 任务未找到 (task_id: {task_id[:16]}...)，"
                        f"可能已过期或 task_id 无效"
                    )
                elif status == 'expired':
                    raise RuntimeError(
                        f"即梦 API 任务已过期 (task_id: {task_id[:16]}...)，"
                        f"请重新提交任务"
                    )
                elif status == 'failed':
                    fail_msg = data.get('fail_message', '未知错误')
                    raise RuntimeError(f"即梦 API 任务失败: {fail_msg}")
                else:
                    time.sleep(interval)
                    continue
            else:
                if code in [50001, 50002]:
                    time.sleep(interval)
                    continue

                raise RuntimeError(
                    f"即梦 API 错误:\n"
                    f"  - 错误码: {code}\n"
                    f"  - 错误信息: {message}\n"
                    f"  - 任务 ID: {task_id[:16]}...\n"
                    f"  - 请检查 API 密钥配置或访问火山引擎控制台查看详情"
                )

        raise RuntimeError(
            f"即梦 API 任务超时:\n"
            f"  - 等待时间: {max_wait} 秒\n"
            f"  - 任务 ID: {task_id[:16]}...\n"
            f"  - 建议: 请稍后重试或检查火山引擎控制台任务状态"
        )

    def _parse_aspect_ratio(self, aspect_ratio: str) -> Tuple[int, int]:
        """解析宽高比，返回对应的尺寸"""
        ratio_map = {
            "1:1": (2048, 2048),
            "16:9": (2560, 1440),
            "9:16": (1440, 2560),
            "4:3": (2304, 1728),
            "3:4": (1728, 2304),
            "3:2": (2496, 1664),
            "2:3": (1664, 2496),
            "21:9": (3024, 1296),
            "9:21": (1296, 3024),
        }
        return ratio_map.get(aspect_ratio, (2560, 1440))

    def generate(self, prompt: str, output_path: str, **kwargs) -> str:
        """使用即梦 AI API 生成图片"""
        aspect_ratio = kwargs.get('aspect_ratio', '16:9')
        width, height = self._parse_aspect_ratio(aspect_ratio)

        print(f"  📐 输出尺寸: {width}x{height}")

        print("  📤 提交生成任务...")
        task_id = self._submit_task(prompt, width=width, height=height)
        print(f"  ✓ 任务已提交 (task_id: {task_id[:16]}...)")

        print("  ⏳ 等待生成完成...")
        result = self._wait_for_result(task_id, max_wait=120, interval=2)

        data = result.get('data', {})
        binary_data_list = data.get('binary_data_base64', [])

        if not binary_data_list:
            raise RuntimeError(
                "即梦 API 返回数据异常:\n"
                "  - 缺少图片数据 (binary_data_base64)\n"
                f"  - 任务 ID: {task_id[:16]}...\n"
                "  - 请检查火山引擎控制台查看任务详情"
            )

        image_base64 = binary_data_list[0]

        try:
            image_bytes = base64.b64decode(image_base64)
        except Exception as e:
            raise RuntimeError(
                f"图片数据解码失败:\n"
                f"  - 错误: {e}\n"
                f"  - 任务 ID: {task_id[:16]}..."
            )

        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'wb') as f:
                f.write(image_bytes)

            print(f"  💾 图片大小: {len(image_bytes) / 1024:.1f} KB")
        except IOError as e:
            raise RuntimeError(
                f"图片保存失败:\n"
                f"  - 路径: {output_path}\n"
                f"  - 错误: {e}"
            )

        return output_path


# 图片生成器映射
GENERATORS = {
    "gemini": GeminiImageGenerator,
    "google": GeminiImageGenerator,  # 别名
    "jimeng": JimengImageGenerator,
    "volcengine": JimengImageGenerator,  # 别名
}

# 默认生成器
DEFAULT_PROVIDER = "gemini"


def get_default_provider() -> str:
    """从配置文件获取默认生成器"""
    config = load_config()
    image_config = config.get('image_generation', {})
    return image_config.get('default_provider', DEFAULT_PROVIDER)


def create_generator(provider: Optional[str] = None) -> ImageGenerator:
    """创建图片生成器实例"""
    if provider is None:
        provider = get_default_provider()

    provider = provider.lower()

    if provider not in GENERATORS:
        available = ', '.join(GENERATORS.keys())
        raise ValueError(
            f"不支持的图片生成器: {provider}\n"
            f"  可用选项: {available}"
        )

    return GENERATORS[provider]()


def main():
    parser = argparse.ArgumentParser(
        description="AI 图片生成工具（支持 Gemini Nano Banana Pro 和即梦）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --prompt "一只可爱的猫咪" --output cat.png
  %(prog)s --prompt "科技感封面" --output cover.png --aspect-ratio 16:9
  %(prog)s --prompt "产品海报" --output poster.png --provider jimeng
  %(prog)s --prompt "高清壁纸" --output wallpaper.png --image-size 4K

配置文件: 项目目录/.claude/config/settings.json

  {
    "image_generation": {
      "default_provider": "gemini"
    },
    "gemini": {
      "api_key": "your-gemini-api-key",
      "model": "gemini-3-pro-image-preview"
    },
    "jimeng": {
      "access_key_id": "your-access-key-id",
      "secret_access_key": "your-secret-access-key"
    }
  }
"""
    )

    parser.add_argument(
        "--prompt",
        required=True,
        help="图片生成提示词"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="输出图片路径"
    )

    parser.add_argument(
        "--provider",
        choices=["gemini", "jimeng"],
        help="图片生成 AI 提供商（默认从配置文件读取，未配置则为 gemini）"
    )

    parser.add_argument(
        "--aspect-ratio",
        default="16:9",
        choices=["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"],
        help="图片宽高比 (默认: 16:9)"
    )

    parser.add_argument(
        "--image-size",
        default="2K",
        choices=["1K", "2K", "4K"],
        help="图片尺寸 (默认: 2K，仅 Gemini 支持)"
    )

    parser.add_argument(
        "--no-auto-rename",
        action="store_true",
        help="禁用自动重命名（默认会自动避免覆盖已有文件）"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="显示详细调试信息"
    )

    args = parser.parse_args()

    # 显示运行环境信息
    print(f"🚀 AI 图片生成器")
    print(f"   工作目录: {Path.cwd()}")

    # 创建输出目录
    output_path = Path(args.output)
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"❌ 创建输出目录失败: {e}", file=sys.stderr)
        return 1

    # 处理文件名冲突
    final_output_path = str(output_path)
    if not args.no_auto_rename:
        final_output_path = get_unique_path(final_output_path)

    try:
        # 创建生成器实例
        generator = create_generator(args.provider)

        provider_name = generator.name.upper()
        print(f"🎨 使用 {provider_name} 生成图片...")
        print(f"📝 提示词: {args.prompt[:100]}..." if len(args.prompt) > 100 else f"📝 提示词: {args.prompt}")

        # 准备参数
        kwargs = {
            "aspect_ratio": args.aspect_ratio,
            "image_size": args.image_size,
        }

        # 生成图片
        result_path = generator.generate(
            prompt=args.prompt,
            output_path=final_output_path,
            **kwargs
        )

        print(f"✅ 图片已生成: {result_path}")
        return 0

    except ValueError as e:
        print(f"\n❌ 配置错误:\n{e}", file=sys.stderr)
        print(f"\n💡 请检查配置文件: {get_project_root()}/.claude/config/settings.json", file=sys.stderr)
        return 1

    except RuntimeError as e:
        print(f"\n❌ 生成失败:\n{e}", file=sys.stderr)
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1

    except KeyboardInterrupt:
        print(f"\n⚠️  用户取消操作", file=sys.stderr)
        return 130

    except Exception as e:
        print(f"\n❌ 未知错误: {e}", file=sys.stderr)
        if args.debug:
            import traceback
            traceback.print_exc()
        else:
            print(f"   使用 --debug 参数查看详细信息", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
