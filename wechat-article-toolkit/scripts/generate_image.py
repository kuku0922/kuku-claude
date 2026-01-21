#!/usr/bin/env -S uv run -p 3.14 --no-project --script
# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "requests",
# ]
# ///
"""
图片生成API调用脚本

使用即梦 AI (火山引擎) 生成图片，国内访问稳定。

使用方法:
    uv run -p 3.14 --no-project --with requests generate_image.py --prompt "图片描述" --output output.png
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
from typing import Optional, Dict, Any
from datetime import datetime, timezone


def get_plugin_root() -> Path:
    """获取插件根目录"""
    return Path(__file__).parent.parent


def get_project_root() -> Path:
    """
    获取项目根目录（Claude Code 的 cwd）

    Claude Code 启动时会将 cwd 设置为项目根目录
    """
    return Path.cwd()


def load_config() -> Dict[str, Any]:
    """
    从配置文件加载配置

    配置加载优先级:
    1. 项目目录/.claude/config/settings.json (最高优先级)
    2. 插件目录/config/settings.json (降级方案)
    """
    # 优先级1: 项目目录配置
    project_config = get_project_root() / ".claude" / "config" / "settings.json"
    if project_config.exists():
        with open(project_config, 'r', encoding='utf-8') as f:
            return json.load(f)

    # 优先级2: 插件目录配置
    plugin_config = get_plugin_root() / "config" / "settings.json"
    if plugin_config.exists():
        with open(plugin_config, 'r', encoding='utf-8') as f:
            return json.load(f)

    return {}


def get_unique_path(output_path: str) -> str:
    """
    获取唯一的文件路径，如果文件已存在则自动加序号

    例如：
    - cover.png 已存在 → cover_1.png
    - cover_1.png 已存在 → cover_2.png

    Args:
        output_path: 原始输出路径

    Returns:
        唯一的文件路径
    """
    path = Path(output_path)

    if not path.exists():
        return output_path

    # 文件已存在，需要加序号
    stem = path.stem  # 文件名（不含扩展名）
    suffix = path.suffix  # 扩展名
    parent = path.parent  # 父目录

    counter = 1
    while True:
        new_path = parent / f"{stem}_{counter}{suffix}"
        if not new_path.exists():
            print(f"⚠️  文件已存在，自动重命名: {path.name} → {new_path.name}")
            return str(new_path)
        counter += 1


class ImageGenerator:
    """图片生成器基类"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or self._get_api_key()

    def _get_api_key(self) -> str:
        """从环境变量获取API密钥"""
        raise NotImplementedError

    def generate(self, prompt: str, output_path: str, **kwargs) -> str:
        """生成图片并保存"""
        raise NotImplementedError


class JimengImageGenerator(ImageGenerator):
    """即梦 AI 图片生成器 (火山引擎)

    即梦4.0是即梦同源的图像生成能力，支持文生图、图像编辑及多图组合生成。
    使用异步 API：先提交任务获取 task_id，然后轮询获取结果。

    文档: https://www.volcengine.com/docs/85621/1817045
    """

    # API 配置
    BASE_URL = "https://visual.volcengineapi.com"
    REGION = "cn-north-1"
    SERVICE = "cv"
    VERSION = "2022-08-31"
    REQ_KEY = "jimeng_t2i_v40"

    def __init__(self, api_key: Optional[str] = None):
        self.config = load_config().get('jimeng', {})
        super().__init__(api_key)

    def _get_api_key(self) -> str:
        """获取 Access Key ID"""
        ak = self.config.get('access_key_id', '') or self.config.get('ak', '')
        if ak and ak not in ['your-access-key-id-here', '']:
            return ak

        ak = os.environ.get('VOLC_ACCESSKEY') or os.environ.get('JIMENG_AK')
        if not ak:
            raise ValueError(
                "请配置即梦 Access Key ID:\n"
                "  1. 在 config/settings.json 中设置 jimeng.access_key_id\n"
                "  2. 或设置环境变量 VOLC_ACCESSKEY"
            )
        return ak

    def _get_secret_key(self) -> str:
        """获取 Secret Access Key"""
        sk = self.config.get('secret_access_key', '') or self.config.get('sk', '')
        if sk and sk not in ['your-secret-access-key-here', '']:
            return sk

        sk = os.environ.get('VOLC_SECRETKEY') or os.environ.get('JIMENG_SK')
        if not sk:
            raise ValueError(
                "请配置即梦 Secret Access Key:\n"
                "  1. 在 config/settings.json 中设置 jimeng.secret_access_key\n"
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

        # 时间戳
        now = datetime.now(timezone.utc)
        amz_date = now.strftime('%Y%m%dT%H%M%SZ')
        date_stamp = now.strftime('%Y%m%d')

        # 请求参数
        host = "visual.volcengineapi.com"
        canonical_uri = "/"
        canonical_querystring = f"Action={action}&Version={self.VERSION}"

        # 计算 body 的 SHA256
        body_hash = hashlib.sha256(body.encode('utf-8')).hexdigest()

        # 标准化头部
        canonical_headers = (
            f"content-type:application/json\n"
            f"host:{host}\n"
            f"x-content-sha256:{body_hash}\n"
            f"x-date:{amz_date}\n"
        )
        signed_headers = "content-type;host;x-content-sha256;x-date"

        # 标准化请求
        canonical_request = (
            f"{method}\n"
            f"{canonical_uri}\n"
            f"{canonical_querystring}\n"
            f"{canonical_headers}\n"
            f"{signed_headers}\n"
            f"{body_hash}"
        )

        # 待签名字符串
        algorithm = "HMAC-SHA256"
        credential_scope = f"{date_stamp}/{self.REGION}/{self.SERVICE}/request"
        string_to_sign = (
            f"{algorithm}\n"
            f"{amz_date}\n"
            f"{credential_scope}\n"
            f"{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
        )

        # 计算签名
        signing_key = self._get_signature_key(sk, date_stamp, self.REGION, self.SERVICE)
        signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

        # 授权头
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
            "force_single": True,  # 强制生成单图，节省时间和费用
        }
        body = json.dumps(body_data, ensure_ascii=False)

        headers = self._create_authorization_header("POST", "CVSync2AsyncSubmitTask", body)

        response = requests.post(url, data=body.encode('utf-8'), headers=headers, timeout=30)
        result = response.json()

        if result.get('code') != 10000:
            error_msg = result.get('message', 'Unknown error')
            raise RuntimeError(f"即梦 API 提交任务失败: {error_msg} (code: {result.get('code')})")

        task_id = result.get('data', {}).get('task_id')
        if not task_id:
            raise RuntimeError("即梦 API 返回数据异常：缺少 task_id")

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

        response = requests.post(url, data=body.encode('utf-8'), headers=headers, timeout=30)
        return response.json()

    def _wait_for_result(self, task_id: str, max_wait: int = 120, interval: int = 2) -> Dict[str, Any]:
        """轮询等待任务完成"""
        start_time = time.time()

        while time.time() - start_time < max_wait:
            result = self._query_task(task_id, return_url=False)

            if result.get('code') != 10000:
                # 检查是否是任务还在处理中
                status = result.get('data', {}).get('status', '')
                if status in ['in_queue', 'generating']:
                    print(f"  ⏳ 任务处理中 ({status})...")
                    time.sleep(interval)
                    continue
                else:
                    error_msg = result.get('message', 'Unknown error')
                    raise RuntimeError(f"即梦 API 查询失败: {error_msg} (code: {result.get('code')})")

            # 检查任务状态
            status = result.get('data', {}).get('status', '')
            if status == 'done':
                return result
            elif status in ['in_queue', 'generating']:
                print(f"  ⏳ 任务处理中 ({status})...")
                time.sleep(interval)
            elif status == 'not_found':
                raise RuntimeError("即梦 API 任务未找到，可能已过期")
            elif status == 'expired':
                raise RuntimeError("即梦 API 任务已过期，请重新提交")
            else:
                print(f"  ⏳ 等待中 (status: {status})...")
                time.sleep(interval)

        raise RuntimeError(f"即梦 API 任务超时，等待超过 {max_wait} 秒")

    def generate(self, prompt: str, output_path: str, **kwargs) -> str:
        """
        使用即梦 AI API 生成图片

        参考: https://www.volcengine.com/docs/85621/1817045
        """
        # 解析宽高比参数
        aspect_ratio = kwargs.get('aspect_ratio', '16:9')
        width, height = self._parse_aspect_ratio(aspect_ratio)

        print(f"  📐 输出尺寸: {width}x{height}")

        # 1. 提交任务
        print("  📤 提交生成任务...")
        task_id = self._submit_task(prompt, width=width, height=height)
        print(f"  ✓ 任务已提交 (task_id: {task_id[:16]}...)")

        # 2. 等待结果
        print("  ⏳ 等待生成完成...")
        result = self._wait_for_result(task_id, max_wait=120, interval=2)

        # 3. 获取图片数据
        data = result.get('data', {})
        binary_data_list = data.get('binary_data_base64', [])

        if not binary_data_list:
            raise RuntimeError("即梦 API 返回数据异常：缺少图片数据")

        # 取第一张图片
        image_base64 = binary_data_list[0]
        image_bytes = base64.b64decode(image_base64)

        # 4. 保存图片
        with open(output_path, 'wb') as f:
            f.write(image_bytes)

        return output_path

    def _parse_aspect_ratio(self, aspect_ratio: str) -> tuple:
        """解析宽高比，返回对应的尺寸

        即梦支持的推荐尺寸：
        - 2K: 2048x2048 (1:1), 2560x1440 (16:9), 2304x1728 (4:3)
        - 4K: 4096x4096 (1:1), 5404x3040 (16:9)
        """
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


# API映射（仅支持即梦 AI）
API_GENERATORS = {
    "jimeng": JimengImageGenerator,
    "volcengine": JimengImageGenerator,  # 别名
}


def main():
    parser = argparse.ArgumentParser(
        description="使用即梦 AI 生成图片",
        formatter_class=argparse.RawDescriptionHelpFormatter
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
        "--aspect-ratio",
        default="16:9",
        help="图片宽高比 (默认: 16:9)"
    )

    parser.add_argument(
        "--no-auto-rename",
        action="store_true",
        help="禁用自动重命名（默认会自动避免覆盖已有文件）"
    )

    args = parser.parse_args()

    # 创建输出目录
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 处理文件名冲突
    final_output_path = str(output_path)
    if not args.no_auto_rename:
        final_output_path = get_unique_path(final_output_path)

    try:
        # 创建即梦生成器实例
        generator = JimengImageGenerator()

        # 准备参数
        kwargs = {
            "aspect_ratio": args.aspect_ratio,
        }

        # 生成图片
        print(f"🎨 使用即梦 AI 生成图片...")
        print(f"📝 提示词: {args.prompt[:100]}..." if len(args.prompt) > 100 else f"📝 提示词: {args.prompt}")

        result_path = generator.generate(
            prompt=args.prompt,
            output_path=final_output_path,
            **kwargs
        )

        print(f"✅ 图片已生成: {result_path}")
        return 0

    except Exception as e:
        print(f"❌ 生成失败: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
