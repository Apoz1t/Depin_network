from fastapi import FastAPI
from utils import sha256, valid_hash
import time

app = FastAPI()

# ----------------- Параметры -----------------
difficulty = 4
MIN_TIME = 10
MAX_TIME = 60
last_solved_times = []
current_task = {}
task_start_time = 0
active_nodes = {}

# ----------------- Задача -----------------
def new_task():
    global difficulty
    return {
        "task_id": int(time.time() * 1000),
        "data": f"block-{int(time.time())}",
        "difficulty": difficulty
    }

# ----------------- API -----------------
@app.post("/register_node")
def register_node(node_name: str):
    if node_name not in active_nodes:
        active_nodes[node_name] = {"tasks_done": 0, "last_seen": time.time()}
        print(f"🟢 Node registered: {node_name}")
    else:
        active_nodes[node_name]["last_seen"] = time.time()
    return {"status": "ok"}

@app.post("/heartbeat")
def heartbeat(node_name: str):
    if node_name in active_nodes:
        active_nodes[node_name]["last_seen"] = time.time()
        return {"status": "ok"}
    return {"status": "error", "message": "Node not registered"}

@app.get("/nodes")
def list_nodes():
    return active_nodes

@app.get("/task")
def get_task():
    global current_task, task_start_time
    task_start_time = time.time()
    if not current_task:
        current_task = new_task()
    return current_task

@app.post("/submit")
def submit_solution(task_id: int, nonce: int, h: str, node_name: str):
    global current_task, difficulty, last_solved_times, task_start_time
    solved_time = time.time() - task_start_time
    last_solved_times.append(solved_time)
    if len(last_solved_times) > 10:
        last_solved_times.pop(0)

    avg_time = sum(last_solved_times) / len(last_solved_times)

    # авто-адаптация сложности
    if avg_time < MIN_TIME:
        difficulty += 1
        print(f"⚡ Увеличиваем сложность! difficulty={difficulty}")
    elif avg_time > MAX_TIME and difficulty > 1:
        difficulty -= 1
        print(f"⚡ Уменьшаем сложность! difficulty={difficulty}")

    # обновление прогресса ноды
    if node_name in active_nodes:
        active_nodes[node_name]["tasks_done"] += 1
        active_nodes[node_name]["last_seen"] = time.time()

    print(f"✅ Решение принято от {node_name}: task={task_id}, nonce={nonce}, hash={h[:20]}..., время={solved_time:.2f}s, avg={avg_time:.2f}s")
    current_task = new_task()
    task_start_time = time.time()
    return {"status": "ok", "new_task": current_task}

# ----------------- Запуск -----------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

