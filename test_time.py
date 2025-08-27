from logger import get_logger

logger = get_logger()

logger.info("utcnow: %s", dt.datetime.utcnow().isoformat() + "Z")
logger.info("local (naive) now: %s", dt.datetime.now().isoformat())
logger.info("zone-aware now: %s", dt.datetime.now(TZ).isoformat())
logger.info("time.tzname: %s", time.tzname)
