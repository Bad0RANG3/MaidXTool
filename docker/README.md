# Docker 部署（开箱即用）

`docker-compose.yml` 一次拉起两个服务：

- **NapCat**：QQ/OneBot 协议端。已通过 `MODE=ws` 预置好 OneBot v11
  **正向 WebSocket 服务端（0.0.0.0:3001）**，登录 QQ 后自动生效，**无需再手动配置网络**；
- **B50 Bot**：NoneBot2 插件 + maimai 请求端，通过 `ws://napcat:3001` 直连 NapCat。

`sdgb/settings.py`（机厅配置）在构建时打进镜像，因此镜像可脱离宿主机文件挂载独立运行；
运行时缓存放在 `b50_data` 卷。

## 首次部署（唯一手动步骤：登录 QQ）

1. 准备机厅配置（构建时需要，已 gitignore）：

   ```bash
   cp sdgb/.settings.py sdgb/settings.py   # 按需修改机厅信息
   ```

   > 安全提示：配置会打进镜像，拿到镜像即拿到机厅密钥，勿推送到公开镜像仓库。

2. 构建并启动：

   ```bash
   docker compose up -d --build
   ```

3. 取出 NapCat WebUI 地址与登录令牌（首次启动 NapCat 会把默认 token 自动升级为随机值，
   所以请以日志为准）：

   ```bash
   docker compose logs napcat | grep -E "WebUi (Token|User Panel Url)"
   ```

4. 浏览器打开日志中的 `http://127.0.0.1:6099/webui?token=...`，扫码登录机器人 QQ。
   登录成功后 NapCat 自动加载预置的 OneBot v11 配置并监听 3001，
   B50 Bot 会自动连上（日志出现 `OneBot V11 | Bot <QQ号> connected`）。

5. 验证：

   ```bash
   docker compose ps
   docker compose logs -f b50-bot
   ```

   QQ 私聊机器人发 `/help` 即返回功能菜单。

> 想固定 WebUI token：`WEBUI_TOKEN=你的强密码 docker compose up -d`（或写入 `.env`）。
> `docker-compose.yml` 默认 `WEBUI_TOKEN=${WEBUI_TOKEN:-napcat}`，
> NapCat 检测到弱默认值 `napcat` 时会自动随机化，因此不设也可以，只是要从日志取 token。

## 运维

```bash
# 看日志
docker compose logs -f

# 改完 sdgb/settings.py 后重新构建机器人镜像
docker compose up -d --build b50-bot

# 停止（保留 QQ 登录态、NapCat 配置与数据缓存）
docker compose down

# 升级
git pull && docker compose up -d --build
```

命名卷 `napcat_qq`、`napcat_config`、`b50_data` 分别保存 QQ 登录态、NapCat 配置与 B50 缓存；
`docker compose down -v` 会清空它们，需要重新登录/配置。

> 旧部署升级提示：如果之前已经用旧版（未配 `MODE=ws`）登录过 QQ，
> NapCat 已生成不带 WS 的 `onebot11_<QQ号>.json`，`MODE=ws` 不会覆盖它。
> 请删除该文件后重启 NapCat（或 WebUI 里给该账号新建一个 3001 正向 WS），
> 让预置的 `onebot11.json` 重新生效。

## 只构建机器人镜像 / 独立运行

如果 NapCat 已部署在别处，只构建机器人镜像：

```bash
docker build -t maidx-tool:latest .
```

独立运行（把 `ONEBOT_WS_URLS` 指向你的 NapCat，例如 Docker Desktop 用
`ws://host.docker.internal:3001`）：

```bash
docker run -d --name b50-bot \
  -e ONEBOT_WS_URLS='["ws://host.docker.internal:3001"]' \
  -v b50_data:/data \
  maidx-tool:latest
```

## 打包 / 迁移镜像

在服务端离线/内网部署时，可把镜像导出再导入：

```bash
docker save maidx-tool:latest mlikiowa/napcat-docker:latest | gzip > maidx-stack.tar.gz
# 到目标机器：
gunzip -c maidx-stack.tar.gz | docker load
docker compose up -d   # 不再需要 --build（镜像已存在）
```

## 国内服务器拉取镜像加速

Docker Hub 在国内常被墙/限速，`docker compose up` 拉 `mlikiowa/napcat-docker` 可能超时。两种方式任选：

1. 给 Docker daemon 配镜像加速（registry mirror），例如写 `/etc/docker/daemon.json`：

   ```json
   { "registry-mirrors": ["https://docker.m.daocloud.io", "https://docker.1ms.run", "https://dockerproxy.net"] }
   ```

   然后 `sudo systemctl restart docker`，重新 `docker compose up -d`。

2. 离线迁移：在能联网的机器上 `docker save` 两个镜像打成 tar.gz，
   拷贝到目标机 `docker load` 后 `docker compose up -d`（免拉取/免构建），见上文“打包 / 迁移镜像”。

## 发布到 Docker Hub

### ⚠️ 先看风险：镜像里带了机厅密钥

`maidx-tool` 镜像在构建时把 `sdgb/settings.py`（含 `aesKey`、`aimeSalt`、`clientId`、
`KeychipID` 等机厅/加密密钥）打进镜像。**推到公开仓库 = 密钥公开**。

- 推荐：Docker Hub 建**私有仓库**（Private），或推到自己的私有 registry；
- 若必须公开，请先确认这些密钥不敏感，或改用环境变量注入配置（可联系我改造）；
- NapCat 镜像（`mlikiowa/napcat-docker`）是官方镜像，**不需要也不应该重新发布**，
  服务器直接拉官方源即可。

### 发布步骤

1. 注册 Docker Hub 账号并登录：

   ```bash
   docker login
   ```

2. 给镜像打上你的用户名和版本标签：

   ```bash
   docker tag maidx-tool:0.1.0 bad0rang3/maidxtool:0.1.0
   docker tag maidx-tool:latest bad0rang3/maidxtool:latest
   ```

3. 推送：

   ```bash
   docker push bad0rang3/maidxtool:0.1.0
   docker push bad0rang3/maidxtool:latest
   ```

4. 服务器部署（只拉取、不构建，配合发布版编排）：

   ```bash
   docker compose -f docker-compose.release.yml up -d
   # 或指定镜像名：
   MAIDX_IMAGE=bad0rang3/maidxtool:0.1.0 docker compose -f docker-compose.release.yml up -d
   ```

   然后按“首次部署”第 3~5 步登录 QQ 即可。

> 镜像改名/推送后，本地 `docker compose up -d --build` 仍可用仓库里的源码直接构建，
> 两者互不影响。
