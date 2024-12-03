import redis
import time

# 创建 Redis 连接
r = redis.StrictRedis(host="localhost", port=6379, db=0)


# 发布消息到频道
def publish_message():
    while True:
        message = input("Enter a message to publish: ")
        r.publish("news_channel", message)  # 发布到 'news_channel' 频道
        print(f"Message '{message}' published to 'news_channel'")
        time.sleep(1)


if __name__ == "__main__":
    print("Publisher started...")
    publish_message()
