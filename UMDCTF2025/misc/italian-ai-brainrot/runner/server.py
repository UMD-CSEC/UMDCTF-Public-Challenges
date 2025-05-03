import runner

import pickle
import queue as pyqueue
import socketserver
import threading
import time
import uuid

queue = []
results = {}
running = set()
lock = threading.Lock()

class QueueHandler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            data = self.request.recv(32768)
            if not data:
                return
            try:
                message = pickle.loads(data)
            except Exception as e:
                self.request.sendall(b"error: invalid data")
                return

            if isinstance(message, list):
                token = str(uuid.uuid4())
                with lock:
                    queue.append((token, message))
                self.request.sendall(f"token: {token}".encode())
            elif isinstance(message, str):
                with lock:
                    if message in results:
                        self.request.sendall(f"result: {results[message]}".encode())
                    else:
                        pos = next((i + 1 for i, (t, _) in enumerate(queue) if t == message), -1)
                        if message in running:
                            self.request.sendall(b"currently running")
                        elif pos != -1:
                            self.request.sendall(f"queue position: {pos}".encode())
                        else:
                            self.request.sendall(b"error: unknown token")
        except Exception as e:
            print(e)

NUM_WORKERS = 3
task_queue = pyqueue.Queue()
worker_pool = []

def start_workers():
    models = runner.load()
    print("loaded models")
    for _ in range(NUM_WORKERS):
        threading.Thread(target=worker_loop, args=(models,), daemon=True).start()

def worker_loop(models):
    while True:
        token, data = task_queue.get()
        try:
            result = runner.run(models, data)
            with lock:
                running.remove(token)
                results[token] = result
        except:
            pass

def runner_loop():
    while True:
        time.sleep(2)
        with lock:
            if queue and task_queue.empty():
                token, data = queue.pop(0)
                running.add(token)
                task_queue.put((token, data))

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True

if __name__ == "__main__":
    start_workers()
    threading.Thread(target=runner_loop, daemon=True).start()
    server = ThreadedTCPServer(("0.0.0.0", 6967), QueueHandler)
    server.serve_forever()
