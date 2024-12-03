"""
我们实现一个简单的实时排行榜，用于存储和查询用户的分数（如游戏排名）。支持以下功能：

增加用户分数。
查询某个用户的排名。
获取前 N 名用户
"""

import redis

# 连接 Redis 服务
r = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)

# 排行榜的键名
LEADERBOARD_KEY = "game_leaderboard"


# 增加用户分数（如果用户已存在，增加其分数；否则添加新用户）
def add_score(user, score):
    r.zincrby(LEADERBOARD_KEY, score, user)
    print(f"Updated {user}'s score by {score} points.")


# 查询用户排名（排名从 0 开始，+1 表示实际排名）
def get_rank(user):
    rank = r.zrevrank(LEADERBOARD_KEY, user)
    if rank is not None:
        print(f"{user} is ranked #{rank + 1}.")
        return rank + 1
    else:
        print(f"{user} is not in the leaderboard.")
        return None


# 获取前 N 名用户及其分数
def get_top_n(n):
    top_users = r.zrevrange(LEADERBOARD_KEY, 0, n - 1, withscores=True)
    print(f"Top {n} users:")
    for rank, (user, score) in enumerate(top_users, start=1):
        print(f"#{rank}: {user} - {score} points")


# 清空排行榜
def reset_leaderboard():
    r.delete(LEADERBOARD_KEY)
    print("Leaderboard reset.")


# 演示
if __name__ == "__main__":
    reset_leaderboard()

    # 添加用户分数
    add_score("Alice", 100)
    add_score("Bob", 200)
    add_score("Charlie", 150)

    # 查询用户排名
    get_rank("Alice")
    get_rank("Bob")

    # 获取前 3 名
    get_top_n(3)

    # 更新分数后再查询
    add_score("Alice", 200)
    get_rank("Alice")
    get_top_n(3)
