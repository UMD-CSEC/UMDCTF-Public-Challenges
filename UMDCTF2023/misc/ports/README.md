
# Ports

You are a network packet transporting *sensitive information* to a very important user. Unfortunately, your human forgot to tell you which port to use. This is a problem as there are 65335 different ports! Luckily, each of these ports might tell you something...

Note: The password to each encrypted .zip file is the corresponding port number.
For example:
Password to `port-16.txt.zip` is simply `16`.

## Build Instructions

 1. Simply edit and run `builder.py` accordingly!

## Files for CTFd

 - `ports.zip`

## Flag

`UMDCTF{dDSA-d_23+t0ta11y_n0t_NSFW_tCp_pAcKET-0_0-15039254&((*#@!}`

## Writeup

`Ports.zip` is a collection of 65335 different .zip files, each representing a unique network port! Each port .zip file contains a reference to another port .zip file, arranged such that searching along to the contents of each file will quickly lead you to the *correct* port (`42237`)!

To see how the *"trail of ports"* is structured, see `range_1.txt` and `range_2.txt`. 

When solving this challenge, **I highly recommend** writing a script. You can use the **7zip** command line utility to extract files (https://www.7-zip.org/) by calling `7z [your arguments]` from your script. A good Python program is capable of solving this challenge in under 5 minutes!

For documentation on how 7zip works in the command line: https://www.dotnetperls.com/7-zip-examples
