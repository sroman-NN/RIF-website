import sys
from pathlib import Path
sys.path.insert(0, str(Path("c:/Users/Kentucky/Desktop/AMST/Retargetable-ISA-Foundry-RIF-").resolve()))
from rif.linker import build_file, Linker
from rif.compiler import Compiler

try:
    linker = Linker("c:/Users/Kentucky/Desktop/AMST/Retargetable-ISA-Foundry-RIF-/rif/plugins/gba/packs/example/gba.pack")
    linked = linker.link(write=False)
    with open("c:/Users/Kentucky/Desktop/AMST/gba/code/game.rif") as f:
        lines = f.readlines()
    compiler = Compiler(linked.program)
    for line in lines:
        line = line.strip()
        if not line or line.startswith(";"):
            continue
        try:
            res = compiler.compile_line(line)
        except Exception as e:
            print(f"FALLO EN: {line} -> {e}")
            break
    print("FIN")
except Exception as e:
    import traceback
    traceback.print_exc()
