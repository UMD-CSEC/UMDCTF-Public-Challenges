


# Counter-Strike: Global Offensive (Aimbot)

Since Jacob wasn't very good at the popular FPS game *Counter Strike*, he decided to purchase an aimbot from a shady Russian developer! 

However, it seems to be doing something weird to his game. Can you figure out what it's doing? 

(CS:GO is not required for this challenge, but you can download it for free on Steam) 

<small>Note: If you decide to actually use this challenge in CS:GO, remember to start CS:GO with the "-insecure" flag or you risk getting banned from the game!</small>

## Hints
Hint 1: It looks like the shady Russian developer accidentally leaked some of his source code: https://pastebin.com/3ZTQC6wc

Hint 2: If you try to run this aimbot, consider patching the game title and its offsets!

## Build Instructions

 1. Compile `Source.cpp` as (x86) with the Visual Studio C++ compiler.  You may need to add this setting for it to compile: ![image](https://user-images.githubusercontent.com/28967166/219470336-6e23f810-7936-4ad6-9769-1f4e9410bbb4.png)


## Files for CTFd

 - `CSGO Aimbot.exe`

## Flag

`UMDCTF{VACBAN}` or just `VACBAN`

*5 submission attempts only.*

## Writeup

 There are two ways to solve this challenge:
 
 1. Run the aimbot on CS:GO and try to see what it does
 2. Reverse engineer the aimbot 
 

 **Solution 1: Run the aimbot on CS:GO:**

 If you choose to run the aimbot on CS:GO, you need to first add the `-insecure` flag to your game launch arguments to avoid the risk of getting banned!

Afterwards, launch the game and head into any singleplayer world. You can then start the aimbot and press the DELETE key to see what it does! 

As shown by the leaked source code, the cheat attempts to shoot a message onto a wall, which is your flag (`VACBAN`).

However, according to the line below, that the cheat only works on walls facing the positive x-direction. Choose your wall accordingly - I recommend the elevator room on *Vertigo*.

`Vector3 reference = Vector3(headPos.x  +  100.0f, headPos.y, headPos.z);`

Done properly, this is what you should see...

https://user-images.githubusercontent.com/28967166/219482478-349c73ff-4507-4574-950a-897bfdf9b41e.mov

Note: If the cheat doesn't work, that means that either the game's memory offsets have changed with the latest update, or that your game's window title doesn't match the one I used. 

 - You can find updated CS:GO game offsets here, and patch them in using Ghidra: https://github.com/frk1/hazedumper/blob/master/csgo.hpp
 - You can also patch in your own game window title using Ghidra.
 
 
 
 **Solution 2: Reverse engineer using Ghidra:**


Open `CSGO Aimbot.exe` in Ghidra. 

Your first task is to locate the `int main(void)` function. Start at the `entry()` function and work your way through until you find:
![image](https://user-images.githubusercontent.com/28967166/219517495-ab973951-45d1-43a3-a63c-33ab3ca641c9.png)

Rename and retype it accordingly. 

Scroll to the bottom of the `main`. We now see code which finally resembles the leaked source code! Although there is not much we can do to make sense of:

![image](https://user-images.githubusercontent.com/28967166/219518309-882532a6-d3fe-42c8-9d98-b62f382ec8fb.png)

...we can look back at the leaked source and notice the following things:

 1. The aimbot inscribes a message by shooting in specific places
 2. The aimbot uses a massive `const` array of `Vector3` objects in order to represent points at which to shoot at
 3. `Vector3` stores **three floats per instance**. 

Therefore, if we simply __find a massive block of floats__ stored in the program binary, we can check whether the block matches up with:
`const Vector3 targets[] = {
Vector3(0, 600, 200),
Vector3(0, -40, -50),
Vector3(0, -40, -50),
/*OMITTED CODE*/
Vector3(0, 0, 50),
Vector3(0, 0, 50)
};`
...and decode the message stored within the aimbot!

Examining the global variables within `main`eventually brings us to these three floats representing the first line of our array of targets:
![image](https://user-images.githubusercontent.com/28967166/219519621-c8bd56a5-bfc0-4c72-9794-1ae5a7de9553.png)

Looking further, we see a **massive** row of undefined data right beneath it. Could this be the rest of our targets?

Changing it all to floats....

![image](https://user-images.githubusercontent.com/28967166/219520151-fef81562-8ee9-4808-8248-aff263acc3f0.png)

We now have each target coordinate listed in front of us! 

The y-coordinate of each `Vector3` object represents left-right movement across a wall perpendicular to the `x`-axis. (Note: The direction of this `y`-axis is flipped in-game)

The z-coordinate represents height.

Now, open a pixel art editor. Trace each coordinate, one-by-one, until a message emerges: 
![image](https://user-images.githubusercontent.com/28967166/219521240-9449c2ae-01bc-454d-9c12-d43f0852ed5b.png)

Congratulations! You have revealed the flag `VACBAN`, with `VAC` standing for `Valve-anti-cheat`, the program supposedly responsible for catching cheaters in CS:GO. 

Happy coding!
