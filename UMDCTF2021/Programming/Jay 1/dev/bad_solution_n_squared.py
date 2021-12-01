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

def bad_solution(numbers):
    """Find a contiguous subarray with the largest sum."""
    best_sum = 0  # or: float('-inf')
    best_start = best_end = 0  # or: Non
    for i in range(len(numbers)-1):
        curr_sum = numbers[i]
        if curr_sum > best_sum:
            best_start = i
            best_end = i
            best_sum = curr_sum
        for j in range(i+1,len(numbers)):
            curr_sum += numbers[j]
            if curr_sum > best_sum:
                best_start = i
                best_end = j
                best_sum = curr_sum

    return best_sum, best_start, best_end


host = '127.0.0.1'
port = 65432
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
s.connect((host,port)) 

print(s.recv(1024).decode())
print(s.recv(1024).decode())
s.send("\n".encode())
arr = get_arr(s)
summ, i, j = bad_solution(arr)
answer = "{}, {}, {}".format(summ, i, j).encode()
print("Answer: " + answer.decode())
s.send(answer)
print(s.recv(1024).decode())

