from concurrent.futures import ThreadPoolExecutor
import os

pool_size = os.getenv("spy.max_thread_pool", "128")

pool = ThreadPoolExecutor(int(pool_size))