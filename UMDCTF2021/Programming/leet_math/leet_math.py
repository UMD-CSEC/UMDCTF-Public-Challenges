#!/usr/bin/env python

import threading
import socket
import os
import random

MIN_QUESTIONS = 8
MAX_QUESTIONS = 10
MAX_DELAY = 2
 
ones = ["", "0n3", "7w0", "7hr33", "f0ur", "f1v3", "51x", "$3v3n", "31gh7", "n1n3", "73n", "3l3v3n", "7w3lv3", "7h1r733n", "f0ur733n", "f1f733n", "$1x733n", "$3v3n733n", "31gh733n", "n1n3733n"]
tens = ["", "", "7w3n7y", "th1r7y", "f0ur7y", "f1fty", "$1x7y", "$3v3n7y", "31gh7y", "n1n37y"]
others = ["hundr3ed", "7h0u54nd", "m1ll10n", '81ll10n', '7r1ll10n']
ops = ['plu$','m1nu$','P1u$','M1Nu$','71m3$','d1v1d3d by','m0d','4nd','0r']
plain_ops = ['+','-','+','-','*','/','%','&','|']

def leet_number(input_int):
  leet_num = ""
  current_tr = 0
  current_b = 0
  current_m = 0
  current_t = 0
  current_h = 0
  current_d = 0
  if input_int > 1000000000000000:
    return leet_number(input_int/1000000000000000)+" "+leet_number(input_int%1000000000000000)
  if input_int < 1000000000000000:
    current_tr = input_int / 1000000000000
    remainder_tr = input_int % 1000000000000
    if remainder_tr > 0:
      current_b = remainder_tr / 1000000000
      remainder_b = remainder_tr % 1000000000
      if remainder_b > 0:
        current_m = remainder_b / 1000000
        remainder_m = remainder_b % 1000000
        if remainder_m > 0:
          current_t = remainder_m / 1000
          remainder_t = remainder_m % 1000
          if remainder_t > 0: 
            current_h = remainder_t / 100
            remainder_h = remainder_t % 100
            if remainder_h > 0:
              current_d = remainder_h / 10
              remainder_d = remainder_h % 10
              if current_d == 1 or current_d == 0:
                leet_num = ones[remainder_h]
              else:
                leet_num = tens[current_d]
                if ones[remainder_d]:
                  leet_num += " " + ones[remainder_d]
  if current_h > 0:
    prefix = leet_number(current_h)
    leet_num = prefix + " " + others[0] + " " + leet_num
  if current_t > 0:
    prefix = leet_number(current_t)
    leet_num = prefix + " " + others[1] + " " + leet_num
  if current_m > 0:
    prefix = leet_number(current_m)
    leet_num = prefix + " " + others[2] + " " + leet_num
  if current_b > 0:
    prefix = leet_number(current_b)
    leet_num = prefix + " " + others[3] + " " + leet_num
  if current_tr > 0:
    prefix = leet_number(current_tr)
    leet_num = prefix + " " + others[4] + " " + leet_num
  return leet_num

def leet_operation(opcode):
  return ops[opcode % len(ops)]

def generate_system(numvar):
  equation = ""
  plain_equation = ""
  eq_vars = []
  operators = []
  plain_operators = []
  for var in range(0,numvar):
    eq_vars.append("var" + str(var))
  for o in range(0, numvar - 1):
    temp = random.randint(0,100)
    plain_operators.append(plain_ops[temp % len(plain_ops)])
    operators.append(leet_operation(temp))
  equation = eq_vars + operators
  equation[::2] = eq_vars
  equation[1::2] = operators
  plain_equation = eq_vars + plain_operators
  plain_equation[::2] = eq_vars
  plain_equation[1::2] = plain_operators
  return ["RESULT = "+" ".join(equation), " ".join(plain_equation)]

def get_equations_for_iter():
  equations = []
  plain_equations = []
  num_equations = random.randint(2,5)
  for eq in range(0, num_equations):
    numbers = []
    plain_numbers = []
    num_numbers = random.randint(2,6)
    operators = []
    plain_operators = []
    num_operators = num_numbers - 1 
    for n in range(0, num_numbers):
      temp = random.randint(1,10000000)
      plain_numbers.append(str(temp))
      numbers.append(leet_number(temp))
    for o in range(0, num_operators):
      temp = random.randint(0,100)
      plain_operators.append(plain_ops[temp % len(plain_ops)])
      operators.append(leet_operation(temp))
    var_i = "var" + str(eq)
    equation = numbers + operators
    equation[::2] = numbers
    equation[1::2] = operators
    equations.append(var_i + " = " + " ".join(equation))
    p_equation = plain_numbers + plain_operators
    p_equation[::2] = plain_numbers
    p_equation[1::2] = plain_operators
    plain_equations.append(var_i + " = " + " ".join(p_equation))
  syseq = generate_system(num_equations)
  equations.append(syseq[0])
  plain_equations.append(syseq[1])
  return (equations, plain_equations)

def solve_equations(plain_equations):
  answers = []
  for i in range(0, len(plain_equations)-1):
    operation = plain_equations[i].split("=")[1]
    answers.append( eval(operation) )
    tmp = plain_equations[-1].replace("var"+str(i),str(answers[i]))
    plain_equations[-1] = tmp
  print("Our answers: " + str(answers))
  print("And our final equation: " + plain_equations[-1])
  print("And our answer: " + str(eval(plain_equations[-1])))
  return eval(plain_equations[-1])
 
class ClientThread(threading.Thread):
  def __init__(self, clientAddress, clientSocket):
    threading.Thread.__init__(self)
    self.csocket = clientSocket
    print("New connection added: ", clientAddress)
  def run(self):
    c = self.csocket
    c.settimeout(2.0)
    result = False
    c.send("4r3 y0u r34dy 4 s0m3 m4th?   ")
    data = c.recv(1024)
    if not data:
      print("See you later aligator!\n")
      return
    else:
      num_qs = random.randint(MIN_QUESTIONS, MAX_QUESTIONS)
      for i in range(0, num_qs):
        equations, plain_equations = get_equations_for_iter()
        solution = solve_equations(plain_equations)
        equation_string = '\n'.join(equations)
        c.send("H3r3'5 Pr0b13m "+str(i)+": \n")
        c.send(equation_string+'\n'+"What is RESULT?  ")
        # implement a quick timeout
        data = c.recv(1024)
        result_int = int(data)
        # make sure that the answer they send is not leeted. 
        # (Maybe send them something along those lines)
        if result_int == solution:
          c.send("Congragulations! Only " + str(num_qs-(i+1)) + " more equations to go!\n")
          if num_qs-(i+1) == 0:
            c.send("OMG WOW!! YOU DID IT!! WASN'T THAT SO MUCH FUN??\n")
            result = True
        else:
          c.send("00f, b3tt3r luck n3xt t1m3!\n")
          result = False
          break 
    if result == True:
      c.send("UMDCTF-{h4h4_w311_4t_134$7_th4ts_f1n4lly_0v3r_r1gh7?}")
    client.close()

def server():
  host = ""
  port = 8888
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  s.bind((host, port))
  s.listen(20)
  while True:
    client, addr = s.accept()
    print("Client connected to :", addr[0], ':', addr[1])
    newthread = ClientThread(addr, client)
    newthread.start()
  s.close()

def main():
  server()

if __name__ == "__main__":
  main()

