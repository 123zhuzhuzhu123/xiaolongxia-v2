"""调用旧系统 Downloader 服务完成采集。"""
import json
import os
from typing import Any

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

DOWNLOADER_BASE = os.environ.get("DOWNLOADER_URL", settings.crawler_base_url)
COOKIE_BRIDGE_BASE = os.environ.get("COOKIE_BRIDGE_URL", "http://127.0.0.1:8274")


def _resolve_cookies(platform: str) -> str:
    """从 CookieBridge 获取对应平台的 cookies。"""
    code = "dy" if platform in ("douyin", "dy") else platform
    url = f"{COOKIE_BRIDGE_BASE.rstrip('/')}/api/cookies/{code}"
    try:
        with httpx.Client(timeout=20.0) as client:
            resp = client.get(url)
            resp.raise_for_status()
            body = resp.json()
            return ((body.get("data") or {}).get("cookies") or "").strip()
    except Exception as exc:
        logger.warning(f"Failed to fetch cookies for {platform}: {exc}")
        return ""


def fetch_content_detail(platform: str, url: str, timeout: float = 120.0) -> dict[str, Any]:
    """调用 Downloader 抓取单个作品详情。

    Args:
        platform: douyin / xhs
        url: 作品链接
        timeout: 超时时间

    Returns:
        Downloader 返回的 JSON 数据
    """
    endpoint = f"{DOWNLOADER_BASE.rstrip('/')}/api/v1/content_detail"
    payload = {
        "platform": platform,
        "content_url": url,
        "cookies": _resolve_cookies(platform),
    }
    logger.info(f"Fetching content detail: platform={platform} url={url}")
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(
            endpoint,
            json=payload,
            headers={"User-Agent": "Mozilla/5.0 OpenClaw/1.0"},
        )
        resp.raise_for_status()
        return resp.json()
