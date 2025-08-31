from fastapi import FastAPI
from utils import sha256, valid_hash
import time

app = FastAPI()

# ----------------- Параметры -----------------
MIN_TIME = 5       # желаемое среднее время решения
MAX_TIME = 20
MAX_DIFFICULTY = 6
MIN_DIFFICULTY = 1

active_nodes = {}  # {node_name: {"tasks_done": 0, "last_seen": time.time(), "difficulty": 4}}

# ----------------- Задачи -----------------
def new_task(difficulty):
    return {
        "task_id": int(time.time() * 1000),
        "data": f"block-{int(time.time())}",
        "difficulty": difficulty
    }

@app.post("/register_node")
def register_node(node_name: str):
    if node_name not in active_nodes:
        active_nodes[node_name] = {"tasks_done": 0, "last_seen": time.time(), "difficulty": 4}
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
def get_task(node_name: str):
    if node_name in active_nodes:
        difficulty = active_nodes[node_name]["difficulty"]
    else:
        difficulty = 4
    task = new_task(difficulty)
    return task

@app.post("/submit")
def submit_solution(task_id: int, nonce: int, h: str, node_name: str, solved_time: float):
    if node_name not in active_nodes:
        return {"status": "error", "message": "Node not registered"}

    node = active_nodes[node_name]
    node["tasks_done"] += 1
    node["last_seen"] = time.time()

    # адаптация сложности под эту ноду
    if solved_time < MIN_TIME and node["difficulty"] < MAX_DIFFICULTY:
        node["difficulty"] += 1
    elif solved_time > MAX_TIME and node["difficulty"] > MIN_DIFFICULTY:
        node["difficulty"] -= 1

    print(f"✅ {node_name} solved task {task_id} in {solved_time:.2f}s. New difficulty: {node['difficulty']}")
    return {"status": "ok"}


