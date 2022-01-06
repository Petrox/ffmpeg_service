import logging
from typing import List
import psutil
import time
from redis import Redis
from enum import IntEnum

from common.config import Config

logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

config: Config = Config.create()


class RedisDb(IntEnum):
    MAIN = 0
    SERVICE = 1
    SOURCES = 2
    EVENTBUS = 3


def crate_redis_connection(db: RedisDb, decode_responses: bool) -> Redis:
    return Redis(host=config.redis.host, port=config.redis.port, charset='utf-8', db=int(db),
                 decode_responses=decode_responses)


# todo: it should replace with pids.
def kill_all_python_processes(except_list: List[int]):
    if except_list is None:
        except_list = []
    proc_name = "python"
    for proc in psutil.process_iter():
        if proc.pid not in except_list and proc.name().startswith(proc_name):
            try:
                proc.kill()
                time.sleep(.33)
            except BaseException as ex:
                logger.error('An error occurred during killing other python process, detail: ' + str(ex))
