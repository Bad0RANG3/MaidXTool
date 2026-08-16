# 机器人运行环境（bot/）

NoneBot2 + `nb_b50` 插件的运行环境与启动脚本（Windows / Linux / macOS 通用）。

## 架构

```
手机QQ(小号) ⇄ NapCat(OneBot v11 WS, 127.0.0.1:3001)
             ⇄ NoneBot2（bot.py, 端口 8080, 加载 ../nb_b50 插件）
             ⇄ sdgb 包 → 成绩接口 → B50 渲染
```

## 目录说明

| 路径 | 说明 |
|------|------|
| `bot.py` / `.env` / `.venv/` | NoneBot2 入口 / 连接配置 / 虚拟环境 |
| `start_bot.bat` / `start.sh` | 启动 NoneBot（Windows / Linux） |
| `start_wrapper.py` | 崩溃自动重启守护（跨平台） |
| `../napcat/` | NapCat 协议端（start/stop 脚本 + shell/） |
| `../启动机器人.bat` / `../start.sh` | 一键启动 NapCat + NoneBot |

## 安装

```bash
# Linux / macOS
python3 -m venv .venv
.venv/bin/pip install -r ../requirements.txt nonebot2 nonebot-adapter-onebot websockets

# Windows（PowerShell）
python -m venv .venv
.venv\Scripts\pip install -r ..\requirements.txt nonebot2 nonebot-adapter-onebot websockets
```

## 启动

- Windows：双击 `../启动机器人.bat`（或 `start_bot.bat`）
- Linux / macOS：`bash ../start.sh`（或 `bash start.sh`，需 NapCat 已运行）

NoneBot 日志出现 `OneBot V11 | Bot <小号QQ> connected` 即链路打通。
小号掉线：打开 `http://127.0.0.1:6099/webui` 扫码。

## 命令

见 `../nb_b50/README.md`（`/help` 也有一份精简版）。要点：

- 私聊直接发命令，群里需 @机器人
- `/b50 <二维码>` 完整 B50 图：每次新码，查完自动登出
- `/fp` 是写操作：真实改账号数据，每次带新二维码，用前确认是自己的二维码

## 排障

- **反向 WS 404**：确认 venv 装了 `websockets`（pip install websockets）
- **小黑屋（isLogin=1）**：等 15 分钟自动解除；期间 `/b50`（免登录）可用
- **无法同时跑主号 QQ（Windows）**：QQ NT 单实例限制，机器人运行时桌面 QQ 需关闭
- **Linux 下 NapCat**：本机部署需 node 环境；也可 Docker 部署后把 WS 地址指向 127.0.0.1:3001

## 安全

- `token_cache.json` / `records_cache.json` 含账号数据，勿外传
- NapCat 端口（3001/6099/8080）勿暴露公网
- QQ 小号风控自负；二维码字符串是登录凭证，建议私聊发送
