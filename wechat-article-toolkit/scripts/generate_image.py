#!/usr/bin/env python3
"""
图片生成API调用脚本

支持图片生成API:
- Gemini API (Google) - 推荐

使用方法:
    python generate_image.py --prompt "图片描述" --output output.png
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import Optional, Dict, Any


def load_config() -> Dict[str, Any]:
    """
    从统一配置文件加载配置

    配置文件位置: config/settings.json
    """
    # 获取脚本所在目录的父目录（插件根目录）
    plugin_root = Path(__file__).parent.parent
    config_path = plugin_root / "config" / "settings.json"

    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
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


class GeminiImageGenerator(ImageGenerator):
    """Gemini API图片生成器 - 使用 Google Genai SDK"""

    def __init__(self, api_key: Optional[str] = None):
        self.config = load_config().get('gemini', {})
        super().__init__(api_key)

    def _get_api_key(self) -> str:
        # 优先从配置文件读取
        api_key = self.config.get('api_key', '')
        if api_key and api_key != 'your-gemini-api-key-here':
            return api_key

        # 降级：从环境变量读取
        api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError(
                "请配置 Gemini API Key:\n"
                "  1. 在 config/settings.json 中设置 gemini.api_key\n"
                "  2. 或设置环境变量 GEMINI_API_KEY"
            )
        return api_key

    def generate(self, prompt: str, output_path: str, **kwargs) -> str:
        """
        使用 Google Genai SDK 生成图片

        参考: https://ai.google.dev/gemini-api/docs/image-generation
        """
        try:
            from google import genai
            from google.genai import types
        except ImportError:
            raise ImportError("请先安装 google-genai SDK: pip install google-genai")

        try:
            # 获取配置
            base_url = self.config.get('base_url', '')
            model = kwargs.get("model") or self.config.get("model", "gemini-2.0-flash-exp")

            # 创建客户端（支持自定义 base_url）
            client_kwargs = {"api_key": self.api_key}

            # 如果配置了自定义 base_url，添加 http_options
            if base_url and base_url != 'https://generativelanguage.googleapis.com/v1beta':
                client_kwargs["http_options"] = types.HttpOptions(base_url=base_url)
                print(f"📡 使用自定义 API 地址: {base_url}")

            client = genai.Client(**client_kwargs)

            # 生成图片
            response = client.models.generate_content(
                model=model,
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"]
                )
            )

            # 处理响应并保存图片
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    # 获取图片数据
                    image_data = part.inline_data.data
                    # 保存图片
                    with open(output_path, 'wb') as f:
                        f.write(image_data)
                    return output_path

            raise ValueError("API 响应中未找到图片数据")

        except Exception as e:
            raise RuntimeError(f"Gemini API调用失败: {str(e)}")


# ==============================================================================
# DALL-E / OpenAI 实现（已注释，如需使用请取消注释）
# ==============================================================================
#
# import base64
# import requests
#
# class DALLEImageGenerator(ImageGenerator):
#     """DALL-E API图片生成器 (OpenAI)"""
#
#     def __init__(self, api_key: Optional[str] = None):
#         self.config = load_config().get('openai', {})
#         super().__init__(api_key)
#
#     def _get_api_key(self) -> str:
#         # 优先从配置文件读取
#         api_key = self.config.get('api_key', '')
#         if api_key and api_key != 'your-openai-api-key-here':
#             return api_key
#
#         # 降级：从环境变量读取
#         api_key = os.environ.get('OPENAI_API_KEY')
#         if not api_key:
#             raise ValueError(
#                 "请配置 OpenAI API Key:\n"
#                 "  1. 在 config/settings.json 中设置 openai.api_key\n"
#                 "  2. 或设置环境变量 OPENAI_API_KEY"
#             )
#         return api_key
#
#     def generate(self, prompt: str, output_path: str, **kwargs) -> str:
#         """
#         使用DALL-E API生成图片
#
#         参考: https://platform.openai.com/docs/api-reference/images
#         """
#         base_url = self.config.get('base_url', 'https://api.openai.com/v1')
#         url = f"{base_url}/images/generations"
#
#         headers = {
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {self.api_key}"
#         }
#
#         # DALL-E 3参数
#         data = {
#             "model": kwargs.get("model") or self.config.get("model", "dall-e-3"),
#             "prompt": prompt,
#             "n": 1,
#             "size": kwargs.get("size", "1792x1024"),  # 16:9比例
#             "quality": kwargs.get("quality", "standard"),  # standard 或 hd
#             "response_format": "b64_json"  # 返回base64编码
#         }
#
#         try:
#             response = requests.post(url, json=data, headers=headers, timeout=120)
#             response.raise_for_status()
#
#             result = response.json()
#
#             # 提取图片数据
#             if "data" in result and len(result["data"]) > 0:
#                 image_data = result["data"][0].get("b64_json")
#                 if image_data:
#                     # 解码并保存图片
#                     image_bytes = base64.b64decode(image_data)
#                     with open(output_path, 'wb') as f:
#                         f.write(image_bytes)
#                     return output_path
#
#             raise ValueError(f"API返回数据格式异常: {result}")
#
#         except requests.exceptions.RequestException as e:
#             raise RuntimeError(f"DALL-E API调用失败: {str(e)}")
#
# ==============================================================================


class AnthropicImageGenerator(ImageGenerator):
    """Anthropic原生图片生成（通过Claude调用）"""

    def _get_api_key(self) -> str:
        # Claude环境下不需要单独的API key
        return "not_required"

    def generate(self, prompt: str, output_path: str, **kwargs) -> str:
        """
        使用Claude的原生图片生成能力

        注: 这个方法在claude.ai环境中可用
        """
        # 在claude.ai环境中，可以直接生成图片
        # 这里返回提示信息，实际生成由调用方处理
        return f"请使用Claude原生能力生成图片: {prompt}"


# API映射
API_GENERATORS = {
    "gemini": GeminiImageGenerator,
    "imagen": GeminiImageGenerator,  # 别名
    # "dalle": DALLEImageGenerator,  # 已注释
    # "openai": DALLEImageGenerator,  # 已注释
    "anthropic": AnthropicImageGenerator,
    "claude": AnthropicImageGenerator,  # 别名
}


def main():
    parser = argparse.ArgumentParser(
        description="调用生图API生成图片",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--prompt",
        required=True,
        help="图片生成提示词"
    )

    parser.add_argument(
        "--api",
        choices=list(API_GENERATORS.keys()),
        default="gemini",
        help="使用的API (默认: gemini)"
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

    # 获取生成器类
    generator_class = API_GENERATORS[args.api]

    try:
        # 创建生成器实例
        generator = generator_class()

        # 准备参数
        kwargs = {
            "aspect_ratio": args.aspect_ratio,
        }

        # 生成图片
        print(f"🎨 使用 {args.api.upper()} API生成图片...")
        print(f"📝 提示词: {args.prompt[:100]}..." if len(args.prompt) > 100 else f"📝 提示词: {args.prompt}")

        result_path = generator.generate(
            prompt=args.prompt,
            output_path=final_output_path,
            **kwargs
        )

        if args.api in ["anthropic", "claude"]:
            print(f"ℹ️  {result_path}")
            return 1

        print(f"✅ 图片已生成: {result_path}")
        return 0

    except Exception as e:
        print(f"❌ 生成失败: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
