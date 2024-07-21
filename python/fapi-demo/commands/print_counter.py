
import argparse
import asyncio
from core import logger
from core.task_manager import TaskManager
from core.request_context import getRequestContext
from core.resource_loader import getResourceLoader


async def print_counter(count_to: int = 10, count_interval: int = 5):
    async with TaskManager() as _:
        ctx = getRequestContext()
        ctx['order_id'] = 123        
        for i in range(count_to):
            print(f"counting: #{i}")
            getLogger().info(f"counting: #{i}")
            await asyncio.sleep(count_interval)


def getLogger():
    return logger.get_logger('print_counter')

if __name__ == "__main__":
    #sh py3.sh commands/print_counter.py value1 value2 --extra value3
    parser = argparse.ArgumentParser(description="demo script")
    parser.add_argument("arg1", help="first param")
    parser.add_argument("arg2", help="second param")
    parser.add_argument("--extra", help="extra param")
    args = parser.parse_args()
    print("first param:", args.arg1)
    print("second param:", args.arg2)
    if args.extra:
         print("extra param:", args.extra)

    async def main():
        # initial
        await getResourceLoader().loadAll()

        # task 
        await print_counter(10, 5)


        # clean up
        await getResourceLoader().releaseAll()


    asyncio.run(main())


