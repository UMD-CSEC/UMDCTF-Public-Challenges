new_map = {
    "🚂":"+",
    "🚃":"-",
    "🚄":"<",
    "🚅":">",
    "🚆":"[",
    "🚇":"]",
    "🚈":".",
    "🚉":","
}

source = open("trainfuck.tf", "r")
out = open("decoded.bf", "w")

for i in source.read():
    try:
        out.write(new_map[i])
    except:
        continue
out.close()
