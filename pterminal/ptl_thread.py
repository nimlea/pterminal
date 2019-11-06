import threading, subprocess, queue, json, time, io, locale
from . import ptl_dispatcher

class PtlThread(threading.Thread):
    signal_output  = "PTL_THREAD_SIGNAL_OUTPUT"
    signal_error   = "PTL_THREAD_SIGNAL_ERROR"

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

    def on(self, signal, handler):
        return ptl_dispatcher.connect(signal, handler)
    
    def off(self, id):
        ptl_dispatcher.remove(id)

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
            for linebytes in iter(p.stdout.readline, b''):
                line = str(linebytes, encoding=locale.getpreferredencoding())
                out += line
                ptl_dispatcher.send(PtlThread.signal_output, self, line)
            err = ""
            for linebytes in iter(p.stderr.readline, b''):
                line = str(linebytes, encoding=locale.getpreferredencoding())
                err += str(line, encoding=locale.getpreferredencoding())
                ptl_dispatcher.send(PtlThread.signal_error, self, line)

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