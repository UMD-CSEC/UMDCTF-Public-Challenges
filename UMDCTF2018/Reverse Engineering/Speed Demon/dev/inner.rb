U = "\x55"
M = "\x4D"
D = "\x44"
C = "\x43"
T = "\x54"
F = "\x46"
q1 = ?-
qx = ?{
q2 = ?N
q3 = ?E
q4 = ?S
q5 = T
q6 = q3
q7 = D
q8 = ?B
q9 = ?Y
q10 = q5
q11 = q6
q12 = C
q13 = ?O
q14 = q7
q15 = q11
qy = ?}

if false
puts U+M+D+C+T+F+[q1, qx, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, qy].join
else
puts "NTS: Deoptimize prints later."
end
