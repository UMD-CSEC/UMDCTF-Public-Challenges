# Blockchain 2 - Chungus Coin

`Author` -- itsecgary

`Points` -- 955

`Solves` -- 23

Chungus Coin is a PoW blockchain that holds indefinite value. There is a reward for those who mine!

*NOTE:* The PoW required for this blockchain is `{p0}{p1}` s.t.

- p0 = proof of previous block
- p1 = proof of block being created
- `sha256(f'{p0}{p1}')[:5] == '00000'`

*HINT: Make sure your name isn't the same as anyone already on the network*

`nc 0.cloud.chals.io 24797`



