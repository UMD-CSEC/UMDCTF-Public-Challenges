# Author: WittsEnd2
# Contributors: 

import angr
import claripy


def main():
    base_addr = 0x0
    p = angr.Project("./dragonPit") #main_opts={'base_addr':base_addr})
    arg_chars = [claripy.BVS('UMDCTF-{%d' % i, 8) for i in range(0x15)]
    arg = claripy.Concat(*arg_chars + [claripy.BVV(b'\n')])
    
    st = p.factory.entry_state(args=["./dragonPit"], add_options=angr.options.unicorn, stdin=arg)
    for k in arg_chars:
        st.solver.add(k > 0x20)
        st.solver.add(k < 0x7f)

    sm = p.factory.simulation_manager(st)
    sm.run()
    for i in sm.deadended:

        print(i.solver.eval(arg, cast_to=bytes))

if __name__ == "__main__":
    main()