import json

with open('c:\\Users\\Kentucky\\Desktop\\AMST\\Retargetable-ISA-Foundry-RIF-\\rif\\plugins\\atari2600\\plugins\\mos6502_opcodes.json') as f:
    opcodes = json.load(f)

words = ['| NAME            | hex |']
for mnem, modes in opcodes.items():
    mnem = mnem.lower()
    for mode, opcode in modes.items():
        if mode == 'IMPL' or mode == 'ACC' or mode == 'REL':
            words.append(f'| {mnem:15} | |')
        elif mode == 'IMM':
            words.append(f'| {mnem}_imm{chr(32)*11} | |')
        elif mode == 'ZP':
            words.append(f'| {mnem}_zp{chr(32)*12} | |')
        elif mode == 'ZPX':
            words.append(f'| {mnem}_zpx{chr(32)*11} | |')
        elif mode == 'ZPY':
            words.append(f'| {mnem}_zpy{chr(32)*11} | |')
        elif mode == 'ABS':
            words.append(f'| {mnem}_abs{chr(32)*11} | |')
            words.append(f'| {mnem}_abs_addr{chr(32)*6} | |')
        elif mode == 'ABSX':
            words.append(f'| {mnem}_absx{chr(32)*10} | |')
            words.append(f'| {mnem}_absx_addr{chr(32)*5} | |')
        elif mode == 'ABSY':
            words.append(f'| {mnem}_absy{chr(32)*10} | |')
            words.append(f'| {mnem}_absy_addr{chr(32)*5} | |')
        elif mode == 'IND':
            words.append(f'| {mnem}_ind{chr(32)*11} | |')
            words.append(f'| {mnem}_ind_addr{chr(32)*6} | |')
        elif mode == 'INDX':
            words.append(f'| {mnem}_indx{chr(32)*10} | |')
        elif mode == 'INDY':
            words.append(f'| {mnem}_indy{chr(32)*10} | |')

words.append('| rompad_to_vectors | |')
words.append('| vectors           | |')

with open('c:\\Users\\Kentucky\\Desktop\\AMST\\Retargetable-ISA-Foundry-RIF-\\rif\\plugins\\atari2600\\packs\\example\\atari2600.words.pack', 'w') as f:
    f.write('\n'.join(words))

rules = []
for mnem, modes in opcodes.items():
    mnem = mnem.lower()
    for mode, opcode in modes.items():
        if mode == 'IMPL' or mode == 'ACC':
            rules.append(f'{mnem}:')
            rules.append(f'    emit {opcode:08b}')
            rules.append('')
        elif mode == 'IMM':
            rules.append(f'{mnem}_imm:')
            rules.append(f'    need REG, VALUE, SYMBOL, imm')
            rules.append(f'    bitfit imm.binary, 8')
            rules.append(f'    zext _imm8, imm.binary, 8')
            rules.append(f'    emit {opcode:08b}')
            rules.append(f'    emit _imm8')
            rules.append('')
        elif mode == 'ZP':
            rules.append(f'{mnem}_zp:')
            rules.append(f'    need REG, VALUE, SYMBOL, addr')
            rules.append(f'    bitfit addr.binary, 8')
            rules.append(f'    zext _addr8, addr.binary, 8')
            rules.append(f'    emit {opcode:08b}')
            rules.append(f'    emit _addr8')
            rules.append('')
        elif mode == 'ZPX':
            rules.append(f'{mnem}_zpx:')
            rules.append(f'    need REG, VALUE, SYMBOL, addr')
            rules.append(f'    need REG, x_reg')
            rules.append(f'    bitfit addr.binary, 8')
            rules.append(f'    zext _addr8, addr.binary, 8')
            rules.append(f'    emit {opcode:08b}')
            rules.append(f'    emit _addr8')
            rules.append('')
        elif mode == 'ZPY':
            rules.append(f'{mnem}_zpy:')
            rules.append(f'    need REG, VALUE, SYMBOL, addr')
            rules.append(f'    need REG, y_reg')
            rules.append(f'    bitfit addr.binary, 8')
            rules.append(f'    zext _addr8, addr.binary, 8')
            rules.append(f'    emit {opcode:08b}')
            rules.append(f'    emit _addr8')
            rules.append('')
        elif mode == 'ABS':
            rules.append(f'{mnem}_abs:')
            rules.append(f'    need LABEL, target')
            rules.append(f'    emit {opcode:08b}')
            rules.append(f'    reloc abs, target, 16')
            rules.append('')
            rules.append(f'{mnem}_abs_addr:')
            rules.append(f'    need REG, VALUE, SYMBOL, addr')
            rules.append(f'    bitfit addr.binary, 16')
            rules.append(f'    zext _addr16, addr.binary, 16')
            rules.append(f'    emit {opcode:08b}')
            rules.append(f'    emit _addr16')
            rules.append('')
        elif mode == 'ABSX':
            rules.append(f'{mnem}_absx:')
            rules.append(f'    need LABEL, target')
            rules.append(f'    need REG, x_reg')
            rules.append(f'    emit {opcode:08b}')
            rules.append(f'    reloc abs, target, 16')
            rules.append('')
            rules.append(f'{mnem}_absx_addr:')
            rules.append(f'    need REG, VALUE, SYMBOL, addr')
            rules.append(f'    need REG, x_reg')
            rules.append(f'    bitfit addr.binary, 16')
            rules.append(f'    zext _addr16, addr.binary, 16')
            rules.append(f'    emit {opcode:08b}')
            rules.append(f'    emit _addr16')
            rules.append('')
        elif mode == 'ABSY':
            rules.append(f'{mnem}_absy:')
            rules.append(f'    need LABEL, target')
            rules.append(f'    need REG, y_reg')
            rules.append(f'    emit {opcode:08b}')
            rules.append(f'    reloc abs, target, 16')
            rules.append('')
            rules.append(f'{mnem}_absy_addr:')
            rules.append(f'    need REG, VALUE, SYMBOL, addr')
            rules.append(f'    need REG, y_reg')
            rules.append(f'    bitfit addr.binary, 16')
            rules.append(f'    zext _addr16, addr.binary, 16')
            rules.append(f'    emit {opcode:08b}')
            rules.append(f'    emit _addr16')
            rules.append('')
        elif mode == 'IND':
            rules.append(f'{mnem}_ind:')
            rules.append(f'    need LABEL, target')
            rules.append(f'    emit {opcode:08b}')
            rules.append(f'    reloc abs, target, 16')
            rules.append('')
            rules.append(f'{mnem}_ind_addr:')
            rules.append(f'    need REG, VALUE, SYMBOL, addr')
            rules.append(f'    bitfit addr.binary, 16')
            rules.append(f'    zext _addr16, addr.binary, 16')
            rules.append(f'    emit {opcode:08b}')
            rules.append(f'    emit _addr16')
            rules.append('')
        elif mode == 'INDX':
            rules.append(f'{mnem}_indx:')
            rules.append(f'    need REG, VALUE, SYMBOL, addr')
            rules.append(f'    need REG, x_reg')
            rules.append(f'    bitfit addr.binary, 8')
            rules.append(f'    zext _addr8, addr.binary, 8')
            rules.append(f'    emit {opcode:08b}')
            rules.append(f'    emit _addr8')
            rules.append('')
        elif mode == 'INDY':
            rules.append(f'{mnem}_indy:')
            rules.append(f'    need REG, VALUE, SYMBOL, addr')
            rules.append(f'    need REG, y_reg')
            rules.append(f'    bitfit addr.binary, 8')
            rules.append(f'    zext _addr8, addr.binary, 8')
            rules.append(f'    emit {opcode:08b}')
            rules.append(f'    emit _addr8')
            rules.append('')
        elif mode == 'REL':
            rules.append(f'{mnem}:')
            rules.append(f'    need LABEL, target')
            rules.append(f'    emit {opcode:08b}')
            rules.append(f'    reldis ., target, 8')
            rules.append('')

rules.append('rompad_to_vectors:')
rules.append('    atari_pad_to 4090')
rules.append('')
rules.append('vectors:')
rules.append('    need LABEL, target')
rules.append('    atari_vectors target')

with open('c:\\Users\\Kentucky\\Desktop\\AMST\\Retargetable-ISA-Foundry-RIF-\\rif\\plugins\\atari2600\\packs\\example\\atari2600.rules.pack', 'w') as f:
    f.write('\n'.join(rules))

types = '''| NAME   | bits | array | sizeset | longset |
| b8     | 8    | false | false   | false   |
| addr8  | 8    | false | false   | false   |
| addr16 | 16   | false | false   | false   |
'''
with open('c:\\Users\\Kentucky\\Desktop\\AMST\\Retargetable-ISA-Foundry-RIF-\\rif\\plugins\\atari2600\\packs\\example\\atari2600.types.pack', 'w') as f:
    f.write(types)

sections = '''| NAME | type | perms | align | fill | emit | order | voffset |
| zp   | data | rw    | 1     | 00   | no   | 0     | 0x0000  |
| ram  | data | rw    | 1     | 00   | no   | 0     | 0x0080  |
| rom  | code | rx    | 1     | 00   | yes  | 0     | 0xF000  |
'''
with open('c:\\Users\\Kentucky\\Desktop\\AMST\\Retargetable-ISA-Foundry-RIF-\\rif\\plugins\\atari2600\\packs\\example\\atari2600.sections.pack', 'w') as f:
    f.write(sections)

regs = '''| NAME  | id     | TYPE   |
| A     | a_reg  | b8     |
| X     | x_reg  | b8     |
| Y     | y_reg  | b8     |
| SP    | sp_reg | b8     |

| VSYNC  | 0x0000 | addr16 |
| VBLANK | 0x0001 | addr16 |
| WSYNC  | 0x0002 | addr16 |
| RSYNC  | 0x0003 | addr16 |
| NUSIZ0 | 0x0004 | addr16 |
| NUSIZ1 | 0x0005 | addr16 |
| COLUP0 | 0x0006 | addr16 |
| COLUP1 | 0x0007 | addr16 |
| COLUPF | 0x0008 | addr16 |
| COLUBK | 0x0009 | addr16 |
| CTRLPF | 0x000A | addr16 |
| REFP0  | 0x000B | addr16 |
| REFP1  | 0x000C | addr16 |
| PF0    | 0x000D | addr16 |
| PF1    | 0x000E | addr16 |
| PF2    | 0x000F | addr16 |
| RESP0  | 0x0010 | addr16 |
| RESP1  | 0x0011 | addr16 |
| RESM0  | 0x0012 | addr16 |
| RESM1  | 0x0013 | addr16 |
| RESBL  | 0x0014 | addr16 |
| AUDC0  | 0x0015 | addr16 |
| AUDC1  | 0x0016 | addr16 |
| AUDF0  | 0x0017 | addr16 |
| AUDF1  | 0x0018 | addr16 |
| AUDV0  | 0x0019 | addr16 |
| AUDV1  | 0x001A | addr16 |
| GRP0   | 0x001B | addr16 |
| GRP1   | 0x001C | addr16 |
| ENAM0  | 0x001D | addr16 |
| ENAM1  | 0x001E | addr16 |
| ENABL  | 0x001F | addr16 |
| HMP0   | 0x0020 | addr16 |
| HMP1   | 0x0021 | addr16 |
| HMM0   | 0x0022 | addr16 |
| HMM1   | 0x0023 | addr16 |
| HMBL   | 0x0024 | addr16 |
| VDELP0 | 0x0025 | addr16 |
| VDELP1 | 0x0026 | addr16 |
| VDELBL | 0x0027 | addr16 |
| RESMP0 | 0x0028 | addr16 |
| RESMP1 | 0x0029 | addr16 |
| HMOVE  | 0x002A | addr16 |
| HMCLR  | 0x002B | addr16 |
| CXCLR  | 0x002C | addr16 |

| SWCHA  | 0x0280 | addr16 |
| SWACNT | 0x0281 | addr16 |
| SWCHB  | 0x0282 | addr16 |
| SWBCNT | 0x0283 | addr16 |
| INTIM  | 0x0284 | addr16 |
| TIM1T  | 0x0294 | addr16 |
| TIM8T  | 0x0295 | addr16 |
| TIM64T | 0x0296 | addr16 |
| T1024T | 0x0297 | addr16 |
'''
with open('c:\\Users\\Kentucky\\Desktop\\AMST\\Retargetable-ISA-Foundry-RIF-\\rif\\plugins\\atari2600\\packs\\example\\atari2600.regs.pack', 'w') as f:
    f.write(regs)
print('All packs regenerated cleanly.')
