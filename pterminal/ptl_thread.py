import threading, subprocess, queue, json, time, io, locale

class PtlThread(threading.Thread):
    def __init__(self):
        super().__init__()
        threading.Thread.__init__(self)

        # instruction queue
        self.instructions = queue.Queue()

        # array of all output/error
        self.loglist = []

    def run(self):
        while(True):
            if self.instructions.empty():
                # if no instruction, sleep 1 second
                time.sleep(1)
            else:
                # run by sequence
                inst = json.loads(self.instructions.get())
                self._run_command(inst)
    
    # add one instruction, will be run by sequence in thread
    def add_command(self, cmd, dir=None):
        inst = json.dumps({
            "cmd":cmd,
            "dir":dir,
        })
        self.instructions.put(inst)

    def _run_command(self, inst):
        cmd = inst["cmd"]
        dir = inst["dir"]
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=dir)
        # read stdout line by line
        while(True):
            code = p.returncode
            if code != None:
                if code == 0:
                    pass
                else:
                    raise Exception("popen return error code:"+code)
                break
            
            # get output/error
            out = ""
            for line in iter(p.stdout.readline, b''):
                out += str(line, encoding=locale.getpreferredencoding())
            err = ""
            for line in iter(p.stderr.readline, b''):
                err += str(line, encoding=locale.getpreferredencoding())

            if out:
                dict_out = {
                    "timestamp" : time.time(),
                    "msg" : out
                }
                self.loglist.append(dict_out)
            if err:
                dict_err = {
                    "timestamp" : time.time(),
                    "msg" : err
                }
                self.loglist.append(dict_err)

            # check and refresh
            p.poll()