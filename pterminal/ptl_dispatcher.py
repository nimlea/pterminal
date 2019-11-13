
connectors = {}
count = 0

def connect(signal, handler):
    if signal == None:
        raise Exception("connect() - signal is None, handler=%r"%(handler))

    receiver = {}
    receiver["signal"]  = signal
    receiver["handler"] = handler
    global count
    count += 1
    id = str(count)
    connectors[id] = receiver
    return 

def remove(id):
    del connectors[id]

def send(signal, sender, *args):
    if signal == None:
        raise Exception("send() - signal is None, sender=%r, args=%r"%(sender, args))

    for id, receiver in connectors.items():
        handler = None
        if receiver and receiver["signal"] == signal:
            handler = receiver["handler"]
        
        if handler:
            try:
                handler(sender, *args)
            except Exception as e:
                print(e)
