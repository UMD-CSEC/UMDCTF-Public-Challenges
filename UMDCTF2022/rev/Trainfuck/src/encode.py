new_map = {
    "+":"🚂",
    "-":"🚃",
    "<":"🚄",
    ">":"🚅",
    "[":"🚆",
    "]":"🚇",
    ".":"🚈",
    ",":"🚉"
}

source = open("trainfuck.bf", "r")
out = open("trainfuck.tf", "w")

for i in source.read():
    try:
        out.write(new_map[i])
    except:
        continue
out.close()
