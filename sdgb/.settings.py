# -*- coding: utf-8 -*-
# This file is the template for sdgb/settings.py.
# Usage: copy this file to sdgb/settings.py (gitignored) and fill in your own values.
# DO NOT share your env to others.

# ============================================================
# 服务器 / 加密配置（1.55 -> 1.56）
# ============================================================
titleServerUrl = "https://maimai-gm.wahlap.com:42081/Maimai2Servlet"
aesKey = "FKM2JX:VjZNK6hc:A0<JU:i5oR7LA]9W"
aesIv = "F>;24DjU9W6ZsRH["
obfuscateParam = "8bF76dE9"
apiVersion = "1.55"
gameSalt = "MaimaiChn"

# ============================================================
# 机厅信息
# ============================================================
clientId = "A63E01C2805"
regionId = 1403
regionName = "北京"
placeId = 1
placeName = "插电师北京王府井银泰店"
KeychipID = "A63E-01C28055905"

# ============================================================
# AIME / 二维码换 token 接口
# ============================================================
aimeUrl = "http://ai.sys-allnet.cn/wc_aime/api/get_data"
aimeSalt = "XcW5FW4cPArBXEk4vzKz3CIrMuA5EVVW"
openGameID = "MAID"

# ============================================================
# 用户（二维码登录后由 chime.qr_api 自动获取 userId/token）
# ============================================================
userId = None
qrCode = ""

# ============================================================
# 本局游玩记录（发票流程默认曲目）
# ============================================================
musicData = {
    "musicId": 417,
    "level": 3,
    "playCount": 1,
    "achievement": 1010000,
    "comboStatus": 4,
    "syncStatus": 4,
    "deluxscoreMax": 2277,
    "scoreRank": 13,
    "extNum1": 0,
}
