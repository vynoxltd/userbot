import time
from utils.mongo import check_mongo_health

START_TIME = time.time()

# =====================
# UPTIME
# =====================
def get_uptime():
    seconds = int(time.time() - START_TIME)

    mins, sec = divmod(seconds, 60)
    hrs, mins = divmod(mins, 60)
    days, hrs = divmod(hrs, 24)

    if days:
        return f"{days}d {hrs}h {mins}m"
    if hrs:
        return f"{hrs}h {mins}m"
    if mins:
        return f"{mins}m {sec}s"
    return f"{sec}s"

# =====================
# MONGO STATUS
# =====================
def mongo_status():
    status = check_mongo_health()
    if status["ok"]:
        return f"✅ Connected ({status['time']})"
    return f"❌ Error: {status['error']}"
