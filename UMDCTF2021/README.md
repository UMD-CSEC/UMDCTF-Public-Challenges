# UMDCTF-2021-Challenges
Challenges created for UMDCTF 2021. UMDCTF 2021 took place on April 16-18. 2021.

# About
Each challenge is the respective work of the listed author. The flags are not listed in plaintext so that developers can test eachother's challenges prior to the competition. The `SHA-256` sum of every flag is included so you can check your work.

__NOTE__: Not every challenge in this repository is testable on your own, some require live servers or hardware that was used during the competition.
  * Hardware challenges
  * Web challenges
  * Pwn challenges
  * Some misc challenges
  * Some sponsor challenges

# Challenge authors
  * [t0pc4r](https://github.com/bencarlisle15)
  * [drkmrin78](https://github.com/drkmrin78)
  * [WittsEnd2](https://github.com/WittsEnd2)
  * [1umpus](https://github.com/1umpus)
  * [itsecgary](https://github.com/itsecgary)
  * [birch](https://github.com/aldenschmidt)
  * [sydocon](https://github.com/sydocon)
  * [amanthanvi](https://github.com/amanthanvi)
  * [shricubed](https://github.com/shricubed)
  * [azeemsm](https://github.com/azeemsm)
  * [matlac](https://github.com/mglac)
  * [lisichka](https://github.com/angcheng27)

# Reuse
Feel free to use these challenges to help learn and teach others after the end of the competition; just provide attribution.

# Checking your flags
As mentioned above, the flags are not included. If you wish to check your answer, you may sha256sum it and compare it with the given sum.

To properly generate the sha256 hash for each flag, you may use following:

    echo -n "UMDCTF-{unique_part_of_a_flag}" | sha256sum

which would generate the following hash: `6fe5d2a3ff1465d5eaad91deba29b7879ccc46697dfc250a0736ff4fc1f7c9cf`
