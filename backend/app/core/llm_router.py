"""
LLM Router - Multi-source LLM 抽象层 (V2.1 W7)

设计目标：
  1. 健康探测可缓存：避免每次请求都 ping 远端
  2. 透明上报：返回 used_provider 让前端 AiHealthBanner 显示真实来源
  3. 零侵入：保持 _ollama_generate 的同名兼容接口（旧调用点不必同步改）

调用链路（默认）:
  DeepSeek (api.deepseek.com)  →  None(模板)

环境变量覆盖：
  LLM_ROUTER_ORDER       - 通道顺序，逗号分隔，目前仅支持: deepseek
  LLM_ROUTER_DISABLE     - 通道禁用名单，逗号分隔
  DEEPSEEK_API_KEY       - DeepSeek key（默认从 app.core.config.LLM_API_KEY 取）
  DEEPSEEK_BASE          - DeepSeek base url（默认 https://api.deepseek.com）
  DEEPSEEK_MODEL         - DeepSeek model（默认 deepseek-chat）
"""
from __future__ import annotations

import os
import time
import threading
from typing import Optional, Tuple, List
import httpx

try:
    from loguru import logger
except Exception:  # pragma: no cover
    import logging
    logger = logging.getLogger(__name__)  # type: ignore

try:
    from app.core.config import get_settings

    _settings = get_settings()
    LLM_API_BASE = _settings.llm_api_base or "https://api.deepseek.com"
    LLM_API_KEY = _settings.llm_api_key or ""
    LLM_MODEL = _settings.llm_model or "deepseek-chat"
except Exception:  # pragma: no cover
    LLM_API_BASE = "https://api.deepseek.com"
    LLM_API_KEY = ""
    LLM_MODEL = "deepseek-chat"


# 健康探测缓存 TTL（秒）
HEALTH_CACHE_TTL = 30
# 健康探测超时
HEALTH_PROBE_TIMEOUT = 2.5

_health_cache: dict[str, Tuple[float, bool]] = {}
_lock = threading.Lock()


def _get_env_list(name: str) -> List[str]:
    raw = os.getenv(name, "")
    return [x.strip() for x in raw.split(",") if x.strip()]


def _channel_order() -> List[str]:
    custom = _get_env_list("LLM_ROUTER_ORDER")
    if custom:
        return custom
    return ["deepseek"]


def _channel_disabled() -> set:
    return set(_get_env_list("LLM_ROUTER_DISABLE"))


# ---------------------------------------------------------------------------
# Channel: DeepSeek (OpenAI 兼容)
# ---------------------------------------------------------------------------

def _deepseek_health() -> bool:
    key = os.getenv("DEEPSEEK_API_KEY", LLM_API_KEY)
    if not key:
        return False
    base = os.getenv("DEEPSEEK_BASE", LLM_API_BASE)
    base = base.rstrip("/")
    # 中转 AnyLink 网关没有 /user/balance（会返回 HTML 首页），健康探测改用 /v1/models：
    # 返回含 data 列表的 JSON 即视为可用。DeepSeek 原生也支持 /models，向后兼容。
    try:
        r = httpx.get(
            f"{base}/v1/models",
            headers={"Authorization": f"Bearer {key}"},
            timeout=HEALTH_PROBE_TIMEOUT,
        )
        if r.status_code != 200:
            return False
        try:
            data = r.json()
        except Exception:
            return False  # 返回 HTML 等非 JSON，判不健康
        return bool(data.get("data") or data.get("models") or data.get("is_available"))
    except Exception:
        return False


def _deepseek_generate(prompt: str, timeout: int = 60, temperature: float = 0.4) -> Optional[str]:
    key = os.getenv("DEEPSEEK_API_KEY", LLM_API_KEY)
    if not key:
        return None
    base = os.getenv("DEEPSEEK_BASE", LLM_API_BASE)
    model = os.getenv("DEEPSEEK_MODEL", LLM_MODEL or "deepseek-chat")
    try:
        max_tokens = int(os.getenv("LLM_MAX_TOKENS", "4096"))
    except Exception:
        max_tokens = 4096
    try:
        r = httpx.post(
            f"{base.rstrip('/')}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False,
            },
            timeout=timeout,
        )
        if r.status_code != 200:
            try:
                logger.warning(f"[LLMRouter/deepseek] HTTP {r.status_code}: {r.text[:200]}")
            except Exception:
                pass
            return None
        data = r.json()
        choices = data.get("choices") or []
        if not choices:
            return None
        return (choices[0].get("message") or {}).get("content")
    except Exception as e:
        try:
            logger.warning(f"[LLMRouter/deepseek] 调用失败: {e}")
        except Exception:
            pass
        return None


# ---------------------------------------------------------------------------
# Channel registry
# ---------------------------------------------------------------------------

def _channel_label(model_name: str) -> str:
    """通道展示 label 从真实 model 名推导，避免切模型后 banner 名不副实。"""
    m = (model_name or "").lower()
    if "opus" in m:
        return "Claude Opus"
    if "claude" in m or "sonnet" in m or "haiku" in m:
        return "Claude"
    if "deepseek" in m:
        return "DeepSeek"
    return model_name or "LLM"


def _channel_endpoints() -> dict[str, dict]:
    model_name = os.getenv("DEEPSEEK_MODEL", LLM_MODEL or "deepseek-chat")
    return {
        "deepseek": {
            "label": _channel_label(model_name),
            "health": _deepseek_health,
            "generate": _deepseek_generate,
            "model_name": model_name,
        },
    }


def _is_channel_healthy(name: str, force: bool = False) -> bool:
    """带缓存的健康探测，TTL 30s。"""
    now = time.time()
    with _lock:
        if not force:
            cached = _health_cache.get(name)
            if cached and (now - cached[0]) < HEALTH_CACHE_TTL:
                return cached[1]
    chans = _channel_endpoints()
    chan = chans.get(name)
    if not chan:
        return False
    try:
        ok = bool(chan["health"]())
    except Exception:
        ok = False
    with _lock:
        _health_cache[name] = (now, ok)
    return ok


def _invalidate_cache(name: Optional[str] = None) -> None:
    with _lock:
        if name is None:
            _health_cache.clear()
        else:
            _health_cache.pop(name, None)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def is_any_available(force: bool = False) -> bool:
    """V2.1 W6 AiHealthBanner 探测点：任一通道可用即返回 True。"""
    disabled = _channel_disabled()
    for name in _channel_order():
        if name in disabled:
            continue
        if _is_channel_healthy(name, force=force):
            return True
    return False


def status_snapshot(force: bool = False) -> dict:
    """返回所有通道健康度快照，供前端 banner / debug 端点使用。"""
    disabled = _channel_disabled()
    order = _channel_order()
    chans = _channel_endpoints()
    items = []
    any_ok = False
    primary = None
    for name in order:
        if name in disabled:
            items.append({"name": name, "label": chans.get(name, {}).get("label", name),
                          "model": chans.get(name, {}).get("model_name", ""),
                          "available": False, "disabled": True})
            continue
        ok = _is_channel_healthy(name, force=force)
        items.append({
            "name": name,
            "label": chans.get(name, {}).get("label", name),
            "model": chans.get(name, {}).get("model_name", ""),
            "available": ok,
            "disabled": False,
        })
        if ok:
            any_ok = True
            if primary is None:
                primary = name
    return {
        "any_available": any_ok,
        "primary": primary,
        "channels": items,
        "fallback_to_template": not any_ok,
    }


def generate(prompt: str, timeout: int = 60, temperature: float = 0.4) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """链式尝试每个通道直到成功。

    Returns: (response_text, used_provider_name, model_name) — 任一为 None 表示全部失败
    """
    disabled = _channel_disabled()
    chans = _channel_endpoints()
    for name in _channel_order():
        if name in disabled:
            continue
        if not _is_channel_healthy(name):
            continue
        chan = chans.get(name)
        if not chan:
            continue
        try:
            resp = chan["generate"](prompt, timeout=timeout, temperature=temperature)
        except TypeError:
            # 兼容旧签名
            resp = chan["generate"](prompt)  # type: ignore
        except Exception as e:
            try:
                logger.warning(f"[LLMRouter] 通道 {name} 抛异常: {e}")
            except Exception:
                pass
            resp = None
        if resp:
            return resp.strip(), name, chan.get("model_name")
        # 该通道失败：标记缓存为 unhealthy 让后续短期跳过
        _invalidate_cache(name)
    return None, None, None


def generate_with_image(
    prompt: str,
    image_b64: str,
    image_mime: str = "image/jpeg",
    timeout: int = 90,
    temperature: float = 0.3,
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """多模态生成：文字 prompt + 一张图（base64）。走 OpenAI vision 兼容格式。

    现网关 xchai.xyz + claude-opus-4-8 已实测可吃 image_url(data URI)。
    与 generate() 解耦：vision 仅本通道（deepseek 名义实跑 Opus 4.8）支持，
    不做多通道链式回退——其它通道不保证多模态，宁可明确失败也不静默退化。

    Returns: (response_text, used_provider_name, model_name)；任一 None 表示失败。
    """
    key = os.getenv("DEEPSEEK_API_KEY", LLM_API_KEY)
    if not key:
        return None, None, None
    base = os.getenv("DEEPSEEK_BASE", LLM_API_BASE)
    model = os.getenv("DEEPSEEK_MODEL", LLM_MODEL or "deepseek-chat")
    try:
        max_tokens = int(os.getenv("LLM_MAX_TOKENS", "4096"))
    except Exception:
        max_tokens = 4096
    try:
        r = httpx.post(
            f"{base.rstrip('/')}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:{image_mime};base64,{image_b64}"},
                            },
                        ],
                    }
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False,
            },
            timeout=timeout,
        )
        if r.status_code != 200:
            try:
                logger.warning(f"[LLMRouter/vision] HTTP {r.status_code}: {r.text[:200]}")
            except Exception:
                pass
            return None, None, None
        data = r.json()
        choices = data.get("choices") or []
        if not choices:
            return None, None, None
        text = (choices[0].get("message") or {}).get("content")
        if not text:
            return None, None, None
        return text.strip(), "deepseek", model
    except Exception as e:
        try:
            logger.warning(f"[LLMRouter/vision] 调用失败: {e}")
        except Exception:
            pass
        return None, None, None


# ---------------------------------------------------------------------------
# 兼容层：保留 _ollama_generate / _ollama_available 的旧名字，让老调用点继续 work
# 实际路由仅 DeepSeek，本地 Ollama 通道 2026-05-27 已废弃
# ---------------------------------------------------------------------------

def legacy_ollama_available() -> bool:
    return is_any_available()


def legacy_ollama_generate(prompt: str, model: str = "", timeout: int = 60) -> Optional[str]:
    text, _, _ = generate(prompt, timeout=timeout)
    return text
