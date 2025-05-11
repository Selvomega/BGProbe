from datetime import datetime
from zoneinfo import ZoneInfo

def get_current_time() -> str:
    """
    Return the current time in the form of a string
    """
    tz_beijing = ZoneInfo("Asia/Shanghai")
    now = datetime.now(tz_beijing)
    return now.strftime("%Y-%m-%d_%H-%M-%S")
