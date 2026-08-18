# Compose deployment

`docker-compose.yml` launches both required services:

- **NapCat** for the QQ/OneBot connection;
- **B50 Bot** for the NoneBot plugin and maimai requests.

## First deployment

1. Install Docker Engine / Docker Desktop with the Compose plugin.
2. Create the site-specific settings file (it is deliberately ignored by Git):

   ```bash
   cp sdgb/.settings.py sdgb/settings.py
   ```

   On PowerShell:

   ```powershell
   Copy-Item sdgb/.settings.py sdgb/settings.py
   ```

   Edit `sdgb/settings.py` and fill in the arcade configuration before continuing.
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

# Restart only the bot after changing settings
docker compose restart b50-bot

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

Run it with `sdgb/settings.py` mounted read-only, a writable `/data` volume, and `ONEBOT_WS_URLS` set to that NapCat instance, for example `ws://host.docker.internal:3001` on Docker Desktop.
