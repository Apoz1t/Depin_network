import requests
import threading
import time
import argparse
from utils import sha256, valid_hash

HEARTBEAT_INTERVAL = 10

def heartbeat(coordinator, node_name):
    while True:
        try:
            requests.post(f"{coordinator}/heartbeat", params={"node_name": node_name})
        except:
            pass
        time.sleep(HEARTBEAT_INTERVAL)

def run_node(coordinator, node_name):
    # регистрация ноды
    requests.post(f"{coordinator}/register_node", params={"node_name": node_name})
    print(f"🚀 Node {node_name} registered and started.")

    # запуск heartbeat в отдельном потоке
    threading.Thread(target=heartbeat, args=(coordinator, node_name), daemon=True).start()

    # основной цикл поиска PoW
    while True:
        try:
            task = requests.get(f"{coordinator}/task").json()
            task_id, data, difficulty = task["task_id"], task["data"], task["difficulty"]
            print(f"🔗 Получено задание: {data}, сложность {difficulty}")

            nonce = 0
            while True:
                h = sha256(f"{data}{nonce}")
                if valid_hash(h, difficulty):
                    print(f"✨ Решение найдено: nonce={nonce}, hash={h[:20]}...")
                    requests.post(f"{coordinator}/submit",
                                  params={"task_id": task_id, "nonce": nonce, "h": h, "node_name": node_name})
                    break
                nonce += 1
        except Exception as e:
            print(f"⚠ Ошибка ноды: {e}")
            time.sleep(3)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DePIN Node")
    parser.add_argument("--coordinator", type=str, required=True, help="URL координатора, например http://123.45.67.89:8000")
    parser.add_argument("--name", type=str, required=True, help="Уникальное имя ноды")
    args = parser.parse_args()

    run_node(args.coordinator, args.name)
