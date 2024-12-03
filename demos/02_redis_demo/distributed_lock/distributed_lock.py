import redis
import time
import uuid
from multiprocessing import Process

# Redis 配置
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

# 锁的名称和过期时间
LOCK_KEY = "distributed_lock"
LOCK_TIMEOUT = 5  # 锁的有效期（秒）

# 创建 Redis 连接
r = redis.StrictRedis(
    host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
)


# 获取分布式锁
def acquire_lock():
    lock_value = str(uuid.uuid4())  # 生成一个唯一的锁标识
    lock_acquired = r.set(
        LOCK_KEY, lock_value, nx=True, ex=LOCK_TIMEOUT
    )  # nx=True 表示只有锁不存在时才会设置，ex=LOCK_TIMEOUT 设置锁的过期时间

    if lock_acquired:
        print(f"Lock acquired with value: {lock_value}")
        return lock_value  # 返回锁的标识值，后续释放锁时需要用到
    else:
        print("Failed to acquire lock, try again later.")
        return None


# 释放分布式锁
def release_lock(lock_value):
    # 获取 Redis 中的锁值，并且与当前的 lock_value 比对，确保是自己持有的锁才释放
    current_lock_value = r.get(LOCK_KEY)

    if current_lock_value == lock_value:
        r.delete(LOCK_KEY)
        print(f"Lock released with value: {lock_value}")
    else:
        print("Failed to release lock, lock is held by another process.")


# 模拟任务
def execute_task():
    print("Executing task...")
    time.sleep(2)  # 模拟一个耗时任务
    print("Task completed.")


# 主流程
def main():
    # 获取锁
    lock_value = acquire_lock()

    if lock_value:
        try:
            # 执行任务
            execute_task()
        finally:
            # 释放锁
            release_lock(lock_value)
    else:
        print("Unable to execute task due to lock being held by another process.")


# if __name__ == "__main__":
#     main()

if __name__ == "__main__":
    # 创建多个进程
    processes = []
    for _ in range(5):
        p = Process(target=main)
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

