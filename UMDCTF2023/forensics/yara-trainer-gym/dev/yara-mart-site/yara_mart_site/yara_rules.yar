import "elf"
import "math"

rule rule1 {
    meta:
        description = "Detect that it is an ELF file"
    condition:
        uint32(0) == 0x464c457f
}

rule rule2 {
    meta:
        description = "Detect a specific section in ELF file"
    strings:
        $rocket1 = "jessie"
        $rocket2 = "james"
        $rocket3 = "meowth"

    condition:
        all of ($rocket*)
}

rule rule3 {
    meta:
        description = "Number of sections in a binary"
     condition:
        elf.number_of_sections == 40
}

rule rule4 {
    meta:
        description = "Detect a specific section in ELF file"
    strings:
        $hex1 = {73 6f 6d 65 74 68 69 6e 67 73 6f 6d 65 74 68 69 6e 67 6d 61 6c 77 61 72 65}
        $hex2 = {5445414d524f434b4554}
        $hex3 = {696d20736f207469726564}
        $hex4 = {736c656570792074696d65}

    condition:
        ($hex1 and $hex2) or ($hex3 and $hex4)
}

rule rule5 {
    meta:
        description = "Detect a specific section in ELF file"
    condition:
        math.entropy(0, filesize) >= 6
}

rule rule6 {
    meta:
        description = "Detect a specific section in ELF file"
    strings:
        $xor = "aqvkpjmdofazwf{lqjm1310<" xor
    condition:
        $xor
}

rule rule7 {
    meta:
        description = "Detect a specific section in ELF file"
    condition:
        for any section in elf.sections : (section.name == "poophaha")
}

rule rule8 {
    meta:
        description = "Detect a specific section in ELF file"
    condition:
        filesize < 2MB and filesize > 1MB
}

