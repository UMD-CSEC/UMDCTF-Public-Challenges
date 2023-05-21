import "elf"

rule rule1 {
    meta:
        description = "Detect that it is an ELF file"
    condition:
        uint32(0) == 0x464c457f and elf.machine == elf.EM_X86_64
}

rule rule2 {
    meta:
        description = "Detect a specific section in ELF file"
    strings:
        $section_name = "Poop"
    condition:
        $section_name
}

rule rule3 {
    meta:
        description = "Detect a specific section in ELF file"
    strings:
        $section_name = "Testing"
    condition:
        $section_name
}

rule rule4 {
    meta:
        description = "Detect a specific section in ELF file"
    strings:
        $section_name = "Testing"
    condition:
        $section_name
}

rule rule5 {
    meta:
        description = "Detect a specific section in ELF file"
    strings:
        $section_name = "Testing"
    condition:
        $section_name
}

rule rule6 {
    meta:
        description = "Detect a specific section in ELF file"
    strings:
        $section_name = "Testing"
    condition:
        $section_name
}

rule rule7 {
    meta:
        description = "Detect a specific section in ELF file"
    strings:
        $section_name = "Testing"
    condition:
        $section_name
}

rule rule8 {
    meta:
        description = "Detect a specific section in ELF file"
    strings:
        $section_name = "ugh"
    condition:
        $section_name
}

