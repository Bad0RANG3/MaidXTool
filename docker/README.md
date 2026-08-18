# Compose deployment

`docker-compose.yml` launches both required services:

- **NapCat** for the QQ/OneBot connection;
- **B50 Bot** for the NoneBot plugin and maimai requests.

`sdgb/settings.py` (arcade config) is baked into the image at build time, so the
image runs standalone without any host file mounts. Runtime caches still live in
the `b50_data` volume.

## First deployment

1. Install Docker Engine / Docker Desktop with the Compose plugin.
2. Make sure `sdgb/settings.py` exists locally with the arcade configuration
   (start from the template, edit it, and keep it out of Git):

   ```bash
   cp sdgb/.settings.py sdgb/settings.py
   ```

   On PowerShell:

   ```powershell
   Copy-Item sdgb/.settings.py sdgb/settings.py
   ```

   > Security note: because the settings are baked in, anyone with the image has
   > the keys. Do not push this image to a public registry.
3. Build and start the stack:

   ```bash
   docker compose up -d --build
   ```
4. Retrieve the NapCat WebUI token and open the local WebUI to log in the bot QQ account:

   ```bash
   docker compose logs napcat
   ```

   Open `http://127.0.0.1:6099/webui` on the Docker host. Keep this port private; do not publish it to the internet.
5. Verify both services:

   ```bash
   docker compose ps
   docker compose logs -f b50-bot
   ```

   A successful OneBot connection is logged as `OneBot V11 | Bot <QQ number> connected`.

## Operations

```bash
# Follow logs
docker compose logs -f

# Rebuild the bot after changing sdgb/settings.py (baked into the image)
docker compose up -d --build b50-bot

# Stop while keeping QQ login/configuration and data caches
docker compose down

# Upgrade/rebuild the bot from a newer checkout
git pull
docker compose up -d --build
```

The named volumes `napcat_qq`, `napcat_config`, and `b50_data` preserve QQ login state, NapCat configuration, and B50 caches. `docker compose down -v` deletes them and requires logging in/configuring again.

## Build only the bot image

If NapCat is already deployed elsewhere, build the application image directly:

```bash
docker build -t maidx-tool:latest .
```

Run it standalone with a writable `/data` volume and `ONEBOT_WS_URLS` set to that NapCat instance, for example `ws://host.docker.internal:3001` on Docker Desktop:

```bash
docker run -d --name b50-bot   -e ONEBOT_WS_URLS='["ws://host.docker.internal:3001"]'   -v b50_data:/data   maidx-tool:latest
```
