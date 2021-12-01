import socket 

def get_arr(s):
    data = ""
    a = s.recv(1024).decode()
    while not (a[-1] == '\n'):
        data += a
        a = s.recv(1024).decode()
    data += a
    data = data.split("[")[1].split("]")[0].split(",") 
    arr = []
    for part in data:
        arr.append(int(part.strip()))
    return arr

def kadanes(numbers):
    """Find a contiguous subarray with the largest sum."""
    best_sum = 0  # or: float('-inf')
    best_start = best_end = 0  # or: None
    current_sum = 0
    for current_end, x in enumerate(numbers):
        if current_sum <= 0:
            # Start a new sequence at the current element
            current_start = current_end
            current_sum = x
        else:
            # Extend the existing sequence with the current element
            current_sum += x
        
        if current_sum > best_sum:
            best_sum = current_sum
            best_start = current_start
            best_end = current_end

    return best_sum, best_start, best_end


host = '127.0.0.1'
port = 65432
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
s.connect((host,port)) 

print(s.recv(1024).decode())
print(s.recv(1024).decode())
s.send("\n".encode())
arr = get_arr(s)
summ, i, j = kadanes(arr)
answer = "{}, {}, {}".format(summ, i, j).encode()
s.send(answer)
print(s.recv(1024).decode())

