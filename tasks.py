import random
import time

def generate_task():
    return {
        "task_id": int(time.time() * 1000),
        "data": f"block-{random.randint(0, 1000000)}",
        "difficulty": random.randint(4, 6)  # число ведущих нулей
    }
