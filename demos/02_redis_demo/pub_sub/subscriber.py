import redis

# 创建 Redis 连接
r = redis.StrictRedis(host="localhost", port=6379, db=0)


# 订阅消息
def subscribe_message():
    pubsub = r.pubsub()
    pubsub.subscribe("news_channel")  # 订阅 'news_channel' 频道
    print("Subscribed to 'news_channel'...")

    # 接收消息
    for message in pubsub.listen():
        if message["type"] == "message":
            print(f"Received message: {message['data'].decode('utf-8')}")


if __name__ == "__main__":
    subscribe_message()
