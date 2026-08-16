# -*- coding: utf-8 -*-
"""把二维码字符串丢给 sdgb/chime.qr_api 换取 userID/token，输出 JSON。

用法: python run_qr.py "<qr字符串>"

兼容两种仓库形态:
- 包风格 (sdgb/__init__.py + 相对导入): from sdgb.chime import qr_api
- 旧版平铺风格 (绝对导入): from chime import qr_api
注意: 不要把 sdgb 目录本身加进 sys.path，否则 import sdgb 会命中 sdgb/sdgb.py 文件而不是包。
"""
import json
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
SDGB = os.path.join(ROOT, "sdgb")
sys.path.insert(0, ROOT)


def _load_qr_api():
    try:
        from sdgb.chime import qr_api
        return qr_api
    except Exception:
        pass
    # 旧版平铺风格（仅当包风格失败时）
    sys.path.insert(0, SDGB)
    try:
        from chime import qr_api
        return qr_api
    except Exception:
        raise


def main():
    qr = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read().strip()
    qr_api = _load_qr_api()
    result = qr_api(qr)
    # 换 token 成功后写入根目录 token_cache.json，供 CLI 调试使用
    if isinstance(result, dict) and result.get("userID", -1) > 0 and result.get("token"):
        try:
            from datetime import datetime, timedelta, timezone
            cache = {
                "qr": qr,
                "userID": result["userID"],
                "token": result["token"],
                "time": datetime.now(timezone(timedelta(hours=8))).isoformat(),
            }
            cache_path = os.path.join(ROOT, "token_cache.json")
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(json.dumps({
            "ok": False,
            "error": str(e),
            "detail": traceback.format_exc()[-3000:],
        }, ensure_ascii=False))
        sys.exit(1)
