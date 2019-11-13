# pipe-terminal
A simple, light-weight input/output library for terminal in new thread

# Usage
## create and start
```
pthread = pterminal.Thread()
pthread.start()
```

## listen the pipe output/error
```
def on_pipe_out(self, sender, txtout):
    print(txtout)

def on_pipe_err(self, sender, txterr):
    print(txtout)

pthread.on(pterminal.SIGNAL_OUT, on_pipe_out)
pthread.on(pterminal.SIGNAL_ERR, on_pipe_err)
```

## exit thread
```
pthread.terminate()
```