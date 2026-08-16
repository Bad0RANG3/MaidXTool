# -*- coding: utf-8 -*-
"""NoneBot2 插件：maimai DX B50 完整成绩图（扫码查询）。

用法（QQ）:
    /help              查看全部命令说明
    /b50 <二维码>      完整版 B50 图（每次使用新码；查完自动登出）
    /fp <二维码> [2~5] 发票：该票库存为 0 才下发，免费，固定 1 张

凭证纪律:
    - /b50 每次使用都要新二维码换新 token，流程 登录 -> 查询 -> 登出；
      查询结束必登出（UserLogoutApi 回传登录时刻，服务器按此校验会话）。
    - 写命令（/fp）同样每次新码，流程 登录 -> 上传 -> 登出。

依赖:
    pip install nonebot2 nonebot-adapter-onebot
"""
import sys
from pathlib import Path

import httpx
from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    MessageSegment,
)
from nonebot.exception import FinishedException
from nonebot.rule import to_me

# 保证能 import 项目根目录的 sdgb 包（NoneBot 运行时 cwd 不确定）
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from sdgb.b50 import load_music_db, render_oneshot  # noqa: E402
from sdgb.records import (  # noqa: E402
    exchange_qr,
    fetch_b50_payload_full,
    load_records_cache,
    login_with_token,
    logout_session,
    music_index,
    rating_to_payload_full,
)
from sdgb.sdgb import MaimaiClient  # noqa: E402

DB = load_music_db()

b50_cmd = on_command(
    "b50", aliases={"B50", "查b50", "查B50", "b50full", "完整b50", "b50完整", "查完整b50", "完整B50"},
    rule=to_me(), priority=5, block=True,
)
help_cmd = on_command(
    "help", aliases={"帮助", "菜单", "命令", "用法"},
    rule=to_me(), priority=1, block=True,
)
fp_cmd = on_command("fp", aliases={"发票", "发功能票", "FP"}, rule=to_me(), priority=5, block=True)

HELP_TEXT = """📋 B50 机器人命令
/b50 <二维码>       完整 B50 图（FC/AP/同步/DX徽标，查完自动登出）
/fp <二维码> [2~5]  发票（无库存才下发，免费，固定 1 张）

群里需@机器人；私聊更安全；每次都要新二维码；写操作前确认是自己的账号；小黑屋等 15 分钟"""


@help_cmd.handle()
async def handle_help(bot: Bot, event: MessageEvent):
    await help_cmd.finish(HELP_TEXT)


@b50_cmd.handle()
async def handle_b50(bot: Bot, event: MessageEvent):
    """/b50 <二维码>：完整版 B50 图（每次使用新码；查完自动登出）。同账号 10 分钟内重复查询走本地缓存。"""
    parts = str(event.get_plaintext()).strip().split()
    qr = parts[1] if len(parts) > 1 else ""
    if len(qr) < 20:
        await b50_cmd.finish(
            "格式：/b50 <二维码字符串>\n"
            "（机台登录界面二维码解析出的字符串，每次查询都要新码；私聊发送更安全）"
        )
        return
    client = MaimaiClient()
    try:
        note = ""
        async with httpx.AsyncClient(verify=False) as http:
            await b50_cmd.send("扫码换取凭证…")
            user_id, token, _preview = await exchange_qr(client, http, qr)
            # 同账号 10 分钟内缓存命中则零登录（避免反复登录触发小黑屋）
            cached = load_records_cache(user_id)
            if cached and cached.get("rating") and cached.get("records"):
                payload = rating_to_payload_full(
                    cached["rating"], DB, music_index(cached["records"])
                )
                note = "（本地缓存，未登录）"
            else:
                await b50_cmd.send("登录并拉取 B50 + 成绩记录…")
                login_ts = await login_with_token(client, http, user_id, token)
                try:
                    payload = await fetch_b50_payload_full(
                        client, http, user_id, token, DB, use_cache=True
                    )
                finally:
                    # 查询结束必登出（UserLogoutApi 回传登录时刻，服务器按此校验会话）
                    try:
                        await logout_session(client, http, user_id, timestamp=login_ts)
                        note = "✅ 已登出"
                    except Exception as e:  # noqa: BLE001
                        note = f"⚠️ 登出异常：{e}"
        b35 = len(payload["calculatedEntries"]["b35"])
        b15 = len(payload["calculatedEntries"]["b15"])
        if b35 == 0 and b15 == 0:
            await b50_cmd.finish("未获取到 B50 数据（该账号无成绩或曲库缺名）。")
            return
        await b50_cmd.send(f"渲染完整 B50 图（B35={b35} / B15={b15}）…")
        img = await render_oneshot(payload)
        tail = f"\n{note}" if note else ""
        await b50_cmd.finish(MessageSegment.image(img) + tail)
    except FinishedException:
        raise
    except Exception as e:  # noqa: BLE001
        await b50_cmd.finish(f"生成失败：{e}")


@fp_cmd.handle()
async def handle_fp(bot: Bot, event: MessageEvent):
    """/fp <二维码> [Ticket ID 2~5]：发票（该票库存为 0 才下发，固定 1 张，免费；真实写操作）。"""
    parts = str(event.get_plaintext()).strip().split()
    qr = parts[1] if len(parts) > 1 else ""
    if len(qr) < 20:
        await fp_cmd.finish(
            "格式：/fp <二维码字符串> [Ticket ID 2~5]\n"
            "例：/fp SGWCMAID... 3\n"
            "（发票：该 Ticket 库存非 0 时拒绝下发；免费；固定 1 张；约 1 分钟）"
        )
        return
    charge_id = 3
    if len(parts) > 2 and parts[2].isdigit():
        charge_id = int(parts[2])
    if not 2 <= charge_id <= 5:
        await fp_cmd.finish("Ticket ID 需在 2~5 之间（3=3倍票；6 倍已废除）。")
        return

    from sdgb.write_ops import issue_ticket_with_qr

    async def say(msg: str):
        await fp_cmd.send(msg)

    try:
        msg = await issue_ticket_with_qr(qr, charge_id=charge_id, progress=say)
        await fp_cmd.finish(msg)
    except FinishedException:
        raise
    except Exception as e:  # noqa: BLE001
        await fp_cmd.finish(f"发票失败：{e}")
