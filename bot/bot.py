# -*- coding: utf-8 -*-
"""B50 QQ 机器人入口（NoneBot2 + OneBot v11）。

运行:
    python bot.py            # Windows：或双击 start_bot.bat
                             # Linux / macOS：bash start.sh

依赖 NapCat（OneBot 协议端）先启动并监听 ws://127.0.0.1:3001
（部署步骤见 bot/README.md 与 docs/DEPLOY.md）。
"""
import sys
from pathlib import Path

# 保证能 import 项目根目录的 sdgb 包与 nb_b50 插件
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import nonebot
from nonebot.adapters.onebot.v11 import Adapter

nonebot.init()
driver = nonebot.get_driver()
driver.register_adapter(Adapter)
nonebot.load_plugin("nb_b50")

if __name__ == "__main__":
    nonebot.run()
