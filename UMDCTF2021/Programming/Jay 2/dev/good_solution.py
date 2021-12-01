import socket 

def get_arr(s):
    data = ""
    a = s.recv(1024).decode()
    while not (a[-1] == '\n'):
        data += a
        a = s.recv(1024).decode()
    data += a
    data = data.split("[")[2:]
    arr = []
    for subarr in data:
        inner_arr = []
        subarr = subarr.split(']')[0].split(',')
        for a in subarr:
            inner_arr.append(int(a.strip()))
        arr.append(inner_arr)
    return arr

def n_cubed(arr):
    maxSum = 0
    for i in range(len(arr)):
        S = [0 for h in range(len(arr[i]))]
        for j in range(i,len(arr)):
            for k in range(len(S)):
                S[k] = S[k] + arr[j][k]
            M, max_start, max_end = kadanes(S)
            if (M > maxSum):
                maxSum = M
                max_sub_start_row = i
                max_sub_end_row = j
                max_sub_start_col = max_start
                max_sub_end_col = max_end
    return maxSum, max_sub_start_row, max_sub_end_row, max_sub_start_col, max_sub_end_col


# Stolen from Wikipedia lol
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
port = 65433
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
s.connect((host,port)) 

print(s.recv(1024).decode())
print(s.recv(1024).decode())
s.send("\n".encode())
arr = get_arr(s)
a, b, c, d, e = n_cubed(arr)
answer = "{}, {}, {}, {}, {}".format(a, b, c, d, e).encode()
s.send(answer)
print(s.recv(1024).decode())

