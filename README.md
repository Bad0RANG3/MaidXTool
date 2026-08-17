# B50 Bot — maimai DX 成绩查询 QQ 机器人

以 QQ 机器人为交互界面的 maimai DX 成绩查询工具：
扫码即可查询完整 B50 成绩图（FC/AP/同步/DX 徽标），查完自动登出；
并保留发票票务命令。

```
QQ 私聊/群聊 @机器人
   ⇄ NapCat（QQ 协议端，OneBot v11 WS）
   ⇄ NoneBot2（bot/，加载 nb_b50 插件）
   ⇄ sdgb/（客户端包：加密管道 / 二维码换凭证 / 登录查询登出）
   ⇄ 成绩接口 + 渲染服务生成 B50 图
```

## 命令一览

| 命令 | 说明 | 登录 |
|------|------|------|
| `/help` | 全部命令说明 | - |
| `/b50 <二维码>` | 完整 B50 图（FC/AP/同步/DX 徽标；查完自动登出） | 登录态（每次新码） |
| `/fp <二维码> [2~5]` | 发票（库存为 0 才下发，免费，固定 1 张） | 写（每次新码） |

- 群里需 @机器人，私聊直接发
- `/b50` 每次查询都要新二维码，查完自动登出；同账号 10 分钟内重复查询走本地缓存
- 写命令（`/fp`）会真实改写账号数据，确认二维码是自己的账号再发

## 凭证纪律

1. `/b50`、`/fp` 每次都要新二维码换新 token；`/b50` 查询结束必登出
   （UserLogoutApi 回传登录时刻，服务器按此校验会话），不留登录态。
2. 登录返回的 cookie（JSESSIONID）与 token 共同参与会话校验，缺一不可。
3. 写命令（`/fp`）流程 登录 → 上传 → 登出；
   中间任何一步出错/中断都会导致账号被强制 isLogin=1（15 分钟冷却）。

## 小黑屋（isLogin）防护

isLogin=1 = 玩家登不上去的返回：服务器判定该账号当前有发票（刷票）嫌疑
（或会话校验失败）而拒绝登录，强制 15 分钟冷却，到期自动解除。

- isLogin=1 期间不要反复尝试登录，等 15 分钟
- `/b50` 同账号 10 分钟内重复查询走本地缓存，命中零登录
- 登录失败（凭证过期/小黑屋）请换新二维码重试

## 快速开始（Windows）

```bat
pip install -r requirements.txt
copy sdgb\.settings.py sdgb\settings.py    :: 填写机厅信息
双击 启动机器人.bat
```

## 快速开始（Linux / macOS）

```bash
python3 -m venv bot/.venv
bot/.venv/bin/pip install -r requirements.txt nonebot2 nonebot-adapter-onebot websockets
cp sdgb/.settings.py sdgb/settings.py      # 填写机厅信息
# NapCat（OneBot v11 WS，监听 127.0.0.1:3001）可 Docker 部署或本机 node 运行
bash start.sh
```

> 完整部署步骤（NapCat 配置、守护进程、排障）见 [docs/DEPLOY.md](docs/DEPLOY.md)。

二维码：机台登录界面屏幕上的二维码（SGWCMAID... 字符串，10 分钟有效），
拍下后用任意扫码工具解析成字符串，发 `/b50 <二维码>` 查完整 B50 图。

## 目录结构

```
├── sdgb/                    # 核心客户端包
│   ├── encrypt.py           # AES-CBC + zlib 加密管道、API hash、CalcRandom
│   ├── chime.py             # 二维码字符串 -> userID / token
│   ├── sdgb.py              # MaimaiClient：call_api / login / query / logout
│   ├── payload.py           # 请求体构建（登录/登出/UserAll/票据/playlog 等）
│   ├── records.py           # 成绩记录 + 扫码登录/登出 + B50 渲染数据
│   ├── b50.py               # B50 渲染（曲库 + oneshot 渲染）
│   ├── write_ops.py         # 写流程：发票（登录 -> 上传 -> 登出）
│   ├── music_data_cache.json # 曲名库缓存（缺失时自动下载，gitignore）
│   └── .settings.py         # 配置模板（复制为 settings.py）
├── nb_b50/                  # NoneBot2 插件（全部 / 命令）
├── bot/                     # 机器人运行环境（venv / bot.py / .env / 启动脚本）
├── napcat/                  # NapCat 协议端（QQ 小号托管，gitignore）
├── docs/
│   └── DEPLOY.md            # Windows / Linux 部署文档
├── b50_cli.py               # B50 渲染 CLI（--uid 免登录，调试）
├── napcat_guard.py          # NapCat 守护进程（Windows / Linux 通用）
├── 启动机器人.bat            # Windows 一键启动 NapCat + NoneBot
├── start.sh                 # Linux / macOS 一键启动
├── requirements.txt         # 核心依赖
└── LICENSE
```

## 注意事项

1. `settings.py` / `token_cache.json` / `records_cache.json` 含密钥与账号数据，勿提交、勿外传
2. 二维码 10 分钟有效；`/b50` 每次查询都要新码
3. 发票（`/fp`）可用 2/3/4/5 号票（默认 3；6 倍已废除）
4. `/fp` 目标 Ticket 库存非 0 时拒绝下发、免费（price=0）、固定 1 张
5. 写命令会真实改写账号数据，操作前确认账号

## 免责声明

WE ARE NOT RESPONSIBLE FOR YOUR ACCOUNT.
使用本项目产生的任何后果自负。

> 怂别用，用别怂。

## Copyright

MIT License.
