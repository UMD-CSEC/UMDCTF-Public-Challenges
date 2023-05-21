%Solution to beep-boop (UMDCTF2023, author: Assgent)

%{
This script should output:
Char #0: U
Char #1: M
Char #2: D
Char #3: C
Char #4: T
Char #5: F
Char #6: >{
Char #7: d¨
Char #8: oµ
Char #9: &_
Char #10: <y
Char #11: oµ
Char #12: 9u
Char #13: &_
Char #14: (a
Char #15: c§
Char #16: 8t
Char #17: 9u
Char #18: (a
Char #19: l²
Char #20: l²
Char #21: <y
Char #22: &_
Char #23: eª
Char #24: n´
Char #25: j°
Char #26: oµ
Char #27: <y
Char #28: &_
Char #29: sº
Char #30: i®
Char #31: g¬
Char #32: n´
Char #33: (a
Char #34: l²
Char #35: &_
Char #36: p·
Char #37: r¹
Char #38: oµ
Char #39: c§
Char #40: eª
Char #41: sº
Char #42: sº
Char #43: i®
Char #44: n´
Char #45: g¬
Char #46: &_
Char #47: ?}
Char #48: ?}
Char #49: ?}
Char #50: @}

(Flag: UMDCTF{do_you_actually_enjoy_signal_processing_???})
%}

close
clear all

%=======================
%We first define the lengths of:
%   -The initial gap before sound begins (INITIAL_GAP)
%   -The size of each tone (TONE_SIZE)
%   -The size of each soundless gap between tones (GAP_SIZE)
%These defintions are in terms of vector indicies. Run plot(sound) to find
%them!
INITIAL_GAP = 2031;
TONE_SIZE = 8202;
GAP_SIZE = 4094;
%=======================

%Read our sound as a vector (an array of values). "Fs" represents the
%sampling rate of 8192.
[sound, Fs] = audioread("sound.wav");

%Let the variable "i" take us through the sound vector. 
%We set it to INITIAL_GAP to skip the leading whitespace in our sound.wav.
i = INITIAL_GAP; 
reading_tone = 1; %The first thing we read will be a tone, not whitespace.
characters_decyphered = 0;

%Iterate through the sound vector
while i < length(sound) - TONE_SIZE
    if reading_tone %Check if we are about to read a tone. If not, skip to the next one.

        %Seperate our tone from the rest of our sound. Let this tone be a
        %smaller array called "s".
        s = sound(i : i + TONE_SIZE); 

        N = length(s);
        k = 0 : N-1;
        F = (k / N) * Fs;

        S = abs(fft(s)); %Get the DFT of our tone. We only care about its magnitude

        S_half = S(1 : round(N / 2)); %Cut off the upper half of the magnitude plot

        %Now, get the strongest frequency from our magnitude plot. 
        %Although each individual character is encoded into a tone with TWO
        %frequencies, we only need to look at one of the frequencies in
        %order to figure out which character the tone refers to.
        [y, freq] = max(S_half);

        %The frequency corresponds to a character within our flag. The two
        %lines below map the frequency back to a character. Since there's
        %no guarentee which frequency appears FIRST in our magnitude plot,
        %we need to consider both mappings
        char_1 = char(get_char_from_frequency_1_mapping(freq));
        char_2 = char(get_char_from_frequency_2_mapping(freq));
        
        %Finally, display char_1 and char_2. One of these will be a
        %character belonging to our flag. It should be easy to read 
        %out the flag since the other character will appear
        %as garbage. 
        disp("Char #" + characters_decyphered + ": " + char_1 + char_2);

        %Increment our variables
        i = i + TONE_SIZE - GAP_SIZE;
        characters_decyphered = characters_decyphered + 1;
    end

    reading_tone = ~reading_tone; %Prepare ourselves to skip the whitespace trailing each tone
    i = i + GAP_SIZE;
end

disp(characters_decyphered + " characters found!")

function char = get_char_from_frequency_1_mapping(freq)
    char = round(freq / 13);
end

function char = get_char_from_frequency_2_mapping(freq)
    char = round(freq / 11) + 50;
end

