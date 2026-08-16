# -*- coding: utf-8 -*-
"""AIME 二维码字符串 -> userID / token。

通过 ai.sys-allnet.cn 的 wc_aime 接口，用机台二维码字符串换取登录凭证。
所有配置（KeychipID、aimeUrl、aimeSalt、openGameID）均来自 settings.py，
支持运行时注入，便于 Web 平台按请求传参。
"""
import hashlib
import json
from datetime import datetime
from urllib.parse import urlparse

import httpx
import pytz

from .settings import KeychipID, aimeUrl, aimeSalt, openGameID


def qr_api(qr_code: str, keychip_id: str = None, url: str = None,
           salt: str = None, game_id: str = None) -> dict:
    """用二维码字符串换取 {userID, token}。"""
    keychip_id = keychip_id or KeychipID
    url = url or aimeUrl
    salt = salt or aimeSalt
    game_id = game_id or openGameID

    if len(qr_code) > 64:
        qr_code = qr_code[-64:]

    time_stamp = datetime.now(pytz.timezone("Asia/Tokyo")).strftime("%y%m%d%H%M%S")
    auth_key = hashlib.sha256(
        (keychip_id + time_stamp + salt).encode("UTF-8")
    ).hexdigest().upper()

    param = {
        "chipID": keychip_id,
        "openGameID": game_id,
        "key": auth_key,
        "qrCode": qr_code,
        "timestamp": time_stamp,
    }
    host = urlparse(url).netloc
    headers = {
        "Contention": "Keep-Alive",
        "Host": host,
        "User-Agent": "WC_AIME_LIB",
    }
    res = httpx.post(
        url,
        data=json.dumps(param, separators=(",", ":")),
        headers=headers,
        timeout=10.0,
    )
    assert res.status_code == 200, f"二维码换 token 失败: HTTP {res.status_code}"
    return json.loads(res.content)
