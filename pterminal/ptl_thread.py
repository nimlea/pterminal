import threading, subprocess, queue, json, time, io, locale
from . import ptl_dispatcher
from .ptl_signal import *

class PtlThread(threading.Thread):
    def __init__(self):
        super().__init__()
        threading.Thread.__init__(self)

        # status
        self._is_running = True

        # instruction queue
        self.instructions = queue.Queue()
        # instruction sequence id, auto increment
        self.seqid = 0

        # array of all output/error
        self.loglist = []

    def run(self):
        while(self._is_running):
            if self.instructions.empty():
                # if no instruction, sleep 1 second
                time.sleep(1)
            else:
                # run by sequence
                inst = json.loads(self.instructions.get())
                self._run_command(inst)
    
    def terminate(self):
        if(self.is_alive()):
            self._is_running = False
    
    # add one instruction, will be run by sequence in thread
    def add_command(self, cmd, dir=None):
        self.seqid += 1
        inst = json.dumps({
            "id"  : self.seqid, 
            "cmd" : cmd,
            "dir" : dir,
        })
        self.instructions.put(inst)
        return self.seqid

    def on(self, signal, handler):
        return ptl_dispatcher.connect(signal, handler)
    
    def off(self, id):
        ptl_dispatcher.remove(id)

    def _run_command(self, inst):
        id = inst["id"]
        cmd = inst["cmd"]
        dir = inst["dir"]
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=dir)
        ptl_dispatcher.send(SIGNAL_ECHO, self, cmd, dir)
        # read stdout line by line
        while(True):
            code = p.returncode
            if code != None:
                if code == 0:
                    pass
                else:
                    raise Exception("popen return error code:"+str(code))
                p.terminate()
                p.wait()
                # dispatch finished signal
                ptl_dispatcher.send(SIGNAL_FINISHED, self, id, dir)
                break
            
            # get output/error
            out = ""
            for linebytes in iter(p.stdout.readline, b''):
                line = str(linebytes, encoding=locale.getpreferredencoding())
                out += line
                ptl_dispatcher.send(SIGNAL_OUT, self, line)
            err = ""
            for linebytes in iter(p.stderr.readline, b''):
                line = str(linebytes, encoding=locale.getpreferredencoding())
                err += line
                ptl_dispatcher.send(SIGNAL_ERR, self, line)

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