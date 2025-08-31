import requests
import threading
import time
from utils import sha256, valid_hash

COORDINATOR = "http://<your_public_ip>:8000"  # замените на публичный IP координатора
NODE_NAME = "node-friend"
HEARTBEAT_INTERVAL = 10

def heartbeat():
    while True:
        try:
            requests.post(f"{COORDINATOR}/heartbeat", params={"node_name": NODE_NAME})
        except:
            pass
        time.sleep(HEARTBEAT_INTERVAL)

def run_node():
    # регистрация ноды
    requests.post(f"{COORDINATOR}/register_node", params={"node_name": NODE_NAME})
    print(f"🚀 Node {NODE_NAME} registered and started.")

    # запуск heartbeat в отдельном потоке
    threading.Thread(target=heartbeat, daemon=True).start()

    # основной цикл поиска PoW
    while True:
        try:
            task = requests.get(f"{COORDINATOR}/task").json()
            task_id, data, difficulty = task["task_id"], task["data"], task["difficulty"]
            print(f"🔗 Получено задание: {data}, сложность {difficulty}")

            nonce = 0
            while True:
                h = sha256(f"{data}{nonce}")
                if valid_hash(h, difficulty):
                    print(f"✨ Решение найдено: nonce={nonce}, hash={h[:20]}...")
                    requests.post(f"{COORDINATOR}/submit",
                                  params={"task_id": task_id, "nonce": nonce, "h": h, "node_name": NODE_NAME})
                    break
                nonce += 1
        except Exception as e:
            print(f"⚠ Ошибка ноды: {e}")
            time.sleep(3)

if __name__ == "__main__":
    run_node()
