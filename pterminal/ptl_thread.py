import threading, subprocess, queue, json, time

class PtlThread(threading.Thread):
    def __init__(self):
        super().__init__()
        threading.Thread.__init__(self)

        # 指令队列
        self.instructions = queue.Queue()

    def run(self):
        while(True):
            print("thread run...")
            time.sleep(1)
    
    # 添加一条指令到队列，队列里的指令会在线程里顺序执行
    def add_command(self, cmd, dir=None):
        inst = json.dumps({
            "type":"command",
            "cmd":cmd,
            "dir":dir,
        })
        self.instructions.put(inst)