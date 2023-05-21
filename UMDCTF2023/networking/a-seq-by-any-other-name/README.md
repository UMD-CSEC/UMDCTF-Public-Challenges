# A Seq By Any Other Name

**Flag**: `UMDCTF{a_seq_is_an_ack_if_you_try_hard_enough}`

**Difficulty**: Hard

**Challenge description**: Sorry about this: our TCP server has got some of its wires crossed. I'm sure you'll figure it out though.

**Setup**:
`docker build . -t aseq -f Dockerfile.aseq`

Running it: 
`docker run --privileged -it --rm -p 80:80 aseq`

If you curl the IP address and do not receive a response, that is the correct behavior. 

If you do not want to give privileged, you need at least CAP NET ADMIN.

Note that you cannot test it over localhost: it must be tested over the network (this is a limitation of iptables & netfilterqueue). 
