
import asyncio
from core import logbook
from core.task_manager import TaskManager


async def send_message(count_to: int = 10, count_interval: int = 5):
    async with TaskManager() as _:
        for i in range(count_to):
            print(f"message sent: #{i}")
            getLogger().info(f"message sent: #{i}")
            await asyncio.sleep(count_interval)


def getLogger():
    return logbook.get_logger('send_message')

