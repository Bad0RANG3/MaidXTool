# 部署文档（Windows / Linux）

B50 Bot 由两部分组成：

1. **协议端 NapCat**：登录机器人 QQ 小号，提供 OneBot v11 WebSocket 服务（`127.0.0.1:3001`）
2. **机器人端 NoneBot2**：加载 `nb_b50` 插件，连接 NapCat，处理 `/b50`、`/fp` 命令

```
手机QQ(机器人小号) ⇄ NapCat(127.0.0.1:3001) ⇄ NoneBot2(:8080) ⇄ sdgb → 成绩接口/渲染服务
```

## 环境要求

| 组件 | Windows | Linux / macOS |
|------|---------|---------------|
| Python | 3.10+ | 3.10+ |
| Node.js | 18+（NapCat 需要） | 18+（NapCat 本机部署时） |
| QQ | 桌面版 QQ NT | 无需（NapCat 独立运行） |
| 网络 | 可访问游戏服务器与渲染服务 | 同左 |

---

## 一、Windows 部署

### 1. 协议端 NapCat

1. 下载 NapCat Windows 包，把内容解压到 `napcat/shell/`
   （需含 `NapCatWinBootMain.exe`、`napcat.mjs`、`loadNapCat.js`、`qqnt.json`、`NapCatWinBootHook.dll`）
2. 本机安装桌面版 QQ NT（机器人运行时桌面 QQ 会被占用，主号需退出）
3. 配置 `napcat/shell/config/onebot11_<机器人QQ号>.json`：
   `websocketServers` 开启一个端口为 `3001` 的服务端
4. 首次启动后打开 `http://127.0.0.1:6099/webui` 扫码登录机器人 QQ

### 2. 机器人端 NoneBot2

```bat
python -m venv bot\.venv
bot\.venv\Scripts\pip install -r requirements.txt nonebot2 nonebot-adapter-onebot websockets
copy sdgb\.settings.py sdgb\settings.py
```

编辑 `sdgb\settings.py`，填写机厅信息：`clientId` / `regionId` / `regionName` /
`placeId` / `placeName` / `KeychipID` / `aimeSalt`。

### 3. 启动

```bat
双击 启动机器人.bat
```

验证：NoneBot 日志出现 `OneBot V11 | Bot <QQ号> connected` 即链路打通。

### 4. 守护进程（可选，自动重启）

- `python napcat_guard.py`：NapCat 崩溃自动重启
- `python bot\start_wrapper.py`：NoneBot 崩溃自动重启

---

## 二、Linux / macOS 部署

### 1. 协议端 NapCat（二选一）

- **Docker（推荐）**：按 NapCat 官方说明以容器运行，把 OneBot v11 WebSocket
  服务端映射到宿主机 `127.0.0.1:3001`（机器人端直连即可，无需 `napcat/` 目录）
- **本机 node**：把 NapCat Linux 包放进 `napcat/shell/`（需含 `napcat.mjs` 等），
  然后 `bash napcat/start_napcat.sh`

> 仓库根目录的 `start.sh` 会自动探测：找不到本机 NapCat 时跳过并提示，
> 因此 Docker 部署同样兼容。

### 2. 机器人端 NoneBot2

```bash
python3 -m venv bot/.venv
bot/.venv/bin/pip install -r requirements.txt nonebot2 nonebot-adapter-onebot websockets
cp sdgb/.settings.py sdgb/settings.py
```

编辑 `sdgb/settings.py`，填写机厅信息（字段同 Windows）。

### 3. 启动

```bash
bash start.sh          # 本机 NapCat + NoneBot 一起拉
bash bot/start.sh      # NapCat 已在跑（含 Docker）时只拉 NoneBot
```

验证：NoneBot 日志出现 `OneBot V11 | Bot <QQ号> connected`。

### 4. 守护进程（可选，自动重启）

- `python napcat_guard.py`：Linux 下以 `node napcat.mjs` 方式守护
- `python bot/start_wrapper.py`：NoneBot 崩溃自动重启（跨平台）

---

## 三、Docker 部署（推荐）

仓库已提供一键编排（`docker-compose.yml`），同时拉起 NapCat（OneBot 协议端）与 B50 机器人，适合 Linux 服务器 / NAS / Windows Docker Desktop。

### 1. 准备机厅配置

```bash
cp sdgb/.settings.py sdgb/settings.py   # 然后填写机厅信息
```

`sdgb/settings.py` 含密钥，已在本地填写好后**直接打进镜像**（已加入 `.gitignore`，不进 Git 仓库）。注意：镜像里带有机厅密钥，切勿推送到公开镜像仓库。

### 2. 构建并启动

```bash
docker compose up -d --build
```

首次启动后登录机器人 QQ：

```bash
docker compose logs napcat   # 查看 WebUI Token
```

打开 `http://127.0.0.1:6099/webui` 扫码登录（该端口仅建议本机访问，勿暴露公网）。

### 3. 验证

```bash
docker compose ps
docker compose logs -f b50-bot
```

NoneBot 日志出现 `OneBot V11 | Bot <QQ号> connected` 即链路打通。

### 4. 运维

- 改完 `sdgb/settings.py` 后重新构建并重启：`docker compose up -d --build b50-bot`
- `docker compose down`：停止（保留 QQ 登录态与数据卷）
- `git pull && docker compose up -d --build`：升级

QQ 登录态、NapCat 配置与 B50 缓存分别保存在命名卷 `napcat_qq`、`napcat_config`、`b50_data` 中；`docker compose down -v` 会删除它们，需重新登录。

> 仅构建机器人镜像：`docker build -t maidx-tool:latest .`，独立运行方式见 `docker/README.md`。

## 四、验证与使用

1. QQ 里私聊机器人发 `/help`，返回菜单即成功
2. 机台登录界面拍下二维码，用任意扫码工具解析出字符串（SGWCMAID...）
3. 发 `/b50 <二维码字符串>` → 收到完整 B50 图，图片下方附「✅ 已登出」

---

## 五、常见问题

| 现象 | 处理 |
|------|------|
| NoneBot 反复报 `Error while setup websocket to ws://127.0.0.1:3001` | NapCat 未启动/未登录；打开 `http://127.0.0.1:6099/webui` 扫码 |
| 反向 WS 404 | venv 里装 `websockets`：`pip install websockets` |
| `/b50` 报「凭证可能已过期」 | 二维码 10 分钟有效，换新码重试 |
| `isLogin=1`（小黑屋） | 等 15 分钟自动解除，期间不要反复登录；同账号 10 分钟内重复 `/b50` 走本地缓存 |
| Linux 下 NapCat 起不来 | 改用 Docker 部署，确认 WS 服务端可达 `127.0.0.1:3001` |
| 群里发命令没反应 | 群聊需 @机器人；私聊直接发 |
| Windows 无法同时跑主号 QQ | QQ NT 单实例限制：机器人运行时桌面主号 QQ 需关闭 |

## 安全提示

- `settings.py` / `token_cache.json` / `records_cache.json` 含密钥与账号数据，勿提交、勿外传
- NapCat 端口（3001/6099/8080）勿暴露公网
- QQ 小号风控自负；二维码字符串是登录凭证，建议私聊发送
