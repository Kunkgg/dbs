在分布式系统中，**分布式锁**是一种常见的解决方案，用于确保多个进程或线程在执行关键任务时不会发生竞争条件。Redis 可以通过 `SETNX`（SET if Not Exists）命令来实现分布式锁，确保同一时间只有一个进程能够执行某个任务。

以下是一个使用 Redis 实现分布式锁的 Python 演示，其中包含：
1. 获取锁（确保同一时间只有一个进程可以执行任务）。
2. 执行任务。
3. 释放锁。

## **实现思路**

1. 使用 Redis 的 `SETNX` 命令（即：`SET key value NX`）来获取锁。如果锁已存在，则返回失败。
2. 为了防止死锁，设置一个过期时间。锁会在一定时间后自动失效，从而避免锁被遗忘时造成系统阻塞。
3. 执行任务后，删除锁。

---

## **1. 安装依赖**
确保已安装 `redis-py` 库。

```bash
pip install redis
```

并且启动一个 Redis 服务。如果没有，可以通过 Docker 启动：

```bash
docker run --name redis-demo -p 6379:6379 -d redis
```

---

## **2. 分布式锁代码**

### **distributed_lock.py**
```python
import redis
import time
import uuid

# Redis 配置
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

# 锁的名称和过期时间
LOCK_KEY = 'distributed_lock'
LOCK_TIMEOUT = 5  # 锁的有效期（秒）

# 创建 Redis 连接
r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

# 获取分布式锁
def acquire_lock():
    lock_value = str(uuid.uuid4())  # 生成一个唯一的锁标识
    lock_acquired = r.set(LOCK_KEY, lock_value, nx=True, ex=LOCK_TIMEOUT)  # nx=True 表示只有锁不存在时才会设置，ex=LOCK_TIMEOUT 设置锁的过期时间
    
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

if __name__ == "__main__":
    main()
```

---

### **3. 运行演示**

#### **步骤 1**: 运行分布式锁代码

首先运行 `distributed_lock.py`，模拟任务执行。每次执行时，Redis 会确保同一时间只有一个进程（或线程）可以获得锁并执行任务。

```bash
python distributed_lock.py
```

输出可能如下：
```
Lock acquired with value: 10a89e5a-fffb-42b2-8f8f-5b7ec139c6e2
Executing task...
Task completed.
Lock released with value: 10a89e5a-fffb-42b2-8f8f-5b7ec139c6e2
```

#### **步骤 2**: 在多个进程或线程中运行

你可以启动多个进程（例如，使用 `multiprocessing` 或多个终端）来模拟并发竞争，观察 Redis 如何确保同一时间只有一个进程可以执行任务。

例如，使用 `multiprocessing` 启动多个进程：

```python
from multiprocessing import Process

if __name__ == "__main__":
    # 创建多个进程
    processes = []
    for _ in range(5):
        p = Process(target=main)
        processes.append(p)
        p.start()

    for p in processes:
        p.join()
```

每个进程会尝试获取分布式锁，只有一个进程能成功获取到锁并执行任务。

---

### **4. 代码说明**

1. **获取锁**：
   - `r.set(LOCK_KEY, lock_value, nx=True, ex=LOCK_TIMEOUT)`：`nx=True` 表示只有当 Redis 中的锁不存在时才会设置锁，`ex=LOCK_TIMEOUT` 设置锁的过期时间（防止死锁）。
   - `lock_value = str(uuid.uuid4())`：生成一个唯一的值作为锁的标识。

2. **释放锁**：
   - `r.get(LOCK_KEY)` 获取当前锁的值，确保只有持有锁的进程才能释放锁。
   - `r.delete(LOCK_KEY)` 删除锁，释放资源。

3. **模拟任务**：
   - `time.sleep(2)` 模拟一个耗时的任务，在实际应用中可以替换为任何需要串行执行的任务。

---

### **5. 总结**

通过 Redis 的 `SETNX` 命令，我们可以实现一个简单的分布式锁机制，确保在分布式环境下多个进程不会重复执行同一个任务。锁机制可以通过设置过期时间来防止死锁，并且锁的释放需要确保是持有锁的进程才能释放。通过这个简单的示例，Redis 提供的分布式锁机制非常适合用于解决分布式任务调度和资源共享的同步问题。