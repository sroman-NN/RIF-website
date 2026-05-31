from __future__ import annotations

import re
from typing import Any

from rif import Err
from rif.plugins.gba.plugins.gba_common import args, emit_bytes

CONTEXT = None

_COND = {
    "eq": 0x0,
    "ne": 0x1,
    "cs": 0x2,
    "hs": 0x2,
    "cc": 0x3,
    "lo": 0x3,
    "mi": 0x4,
    "pl": 0x5,
    "vs": 0x6,
    "vc": 0x7,
    "hi": 0x8,
    "ls": 0x9,
    "ge": 0xA,
    "lt": 0xB,
    "gt": 0xC,
    "le": 0xD,
}

_ALU = {
    "and": 0x0,
    "xor": 0x1,
    "eor": 0x1,
    "lsl_reg": 0x2,
    "lsr_reg": 0x3,
    "asr_reg": 0x4,
    "adc": 0x5,
    "sbc": 0x6,
    "ror": 0x7,
    "tst": 0x8,
    "neg": 0x9,
    "cmp": 0xA,
    "cmn": 0xB,
    "or": 0xC,
    "orr": 0xC,
    "mul": 0xD,
    "bic": 0xE,
    "not": 0xF,
    "mvn": 0xF,
}

_REG_ALIAS = {
    "SP": 13,
    "LR": 14,
    "PC": 15,
}


def _int(value: Any, *, name: str = "valor") -> int:
    text = str(value).strip().upper()
    
    # 1. Buscar en registros del programa
    ctx = globals().get("CONTEXT")
    if ctx is not None and ctx.program is not None:
        reg_obj = next((r for r in ctx.program.regs.registers if r.name.upper() == text or (r.alias and r.alias.upper() == text)), None)
        if reg_obj is not None:
            hex_val = reg_obj.values.get("hex") or reg_obj.values.get("code")
            if hex_val:
                return _int(hex_val, name=name)

    # 2. Buscar en objetos globales del programa
    if ctx is not None and ctx.program is not None and hasattr(ctx.program, "objects"):
        obj = ctx.program.objects.get(str(value).strip())
        if obj is not None:
            val = obj.values.get("VALUE") or obj.values.get("addrs") or obj.values.get("hex")
            if val is not None:
                return _int(val, name=name)

    text_clean = text.replace("_", "")
    if not text_clean:
        raise ValueError(f"{name} vacio")
    if text_clean.startswith(("0X", "0x")):
        return int(text_clean, 16)
    if text_clean.startswith(("0B", "0b")):
        return int(text_clean[2:], 2)
    return int(text_clean, 10)


def _range(value: int, bits: int, *, name: str) -> int:
    if not 0 <= value < (1 << bits):
        raise ValueError(f"{name}={value} no cabe en u{bits}")
    return value


def _reg3(value: Any, *, name: str = "registro") -> int:
    text = str(value).strip().upper()
    if re.fullmatch(r"R[0-7]", text):
        return int(text[1:])
    if all(ch in "01" for ch in text) and 1 <= len(text) <= 3:
        return int(text, 2)
    raw = _int(text, name=name)
    if not 0 <= raw <= 7:
        raise ValueError(f"{name} debe ser R0-R7; recibido {value!r}")
    return raw


def _regnum(value: Any, *, name: str = "registro") -> int:
    text = str(value).strip().upper()
    if text in _REG_ALIAS:
        return _REG_ALIAS[text]
    if re.fullmatch(r"R(?:[0-9]|1[0-5])", text):
        return int(text[1:])
    if all(ch in "01" for ch in text) and 1 <= len(text) <= 4:
        return int(text, 2)
    raw = _int(text, name=name)
    if not 0 <= raw <= 15:
        raise ValueError(f"{name} debe ser R0-R15/SP/LR/PC; recibido {value!r}")
    return raw


def _scaled_imm(value: Any, scale: int, bits: int, *, name: str) -> int:
    raw = _int(value, name=name)
    if raw % scale:
        raise ValueError(f"{name}={raw} debe estar alineado a {scale}")
    return _range(raw // scale, bits, name=name)


def _reglist_mask(value: Any, *, bits: int = 8, name: str = "reglist", lr: bool = False, pc: bool = False) -> int:
    text = str(value).strip()
    if not text:
        raise ValueError(f"{name} vacio")
    if not text.startswith("{"):
        return _range(_int(text, name=name), bits, name=name)
    if not text.endswith("}"):
        raise ValueError(f"{name} debe cerrar con }}")
    mask = 0
    for item in text[1:-1].split(","):
        part = item.strip()
        if not part:
            continue
        if "-" in part:
            start_text, end_text = [chunk.strip() for chunk in part.split("-", 1)]
            start = _regnum(start_text, name=name)
            end = _regnum(end_text, name=name)
            if start > end:
                raise ValueError(f"rango de registros invalido: {part}")
            for reg in range(start, end + 1):
                if not 0 <= reg <= 7:
                    raise ValueError(f"{name} solo acepta rangos R0-R7")
                mask |= 1 << reg
            continue
        reg = _regnum(part, name=name)
        if 0 <= reg <= 7:
            mask |= 1 << reg
        elif lr and reg == 14:
            mask |= 1 << 8
        elif pc and reg == 15:
            mask |= 1 << 8
        else:
            special = "LR" if lr else "PC" if pc else "R0-R7"
            raise ValueError(f"{name} solo acepta R0-R7 o {special}")
    return _range(mask, bits, name=name)


def _pc_relative_label(target: Any, *, name: str) -> int:
    destination = _label_offset(str(target).strip())
    if destination is None:
        return 0
    base = (_current_byte() + 4) & ~3
    delta = destination - base
    if delta < 0:
        raise ValueError(f"{name} hacia {target!r} debe apuntar hacia adelante")
    if delta % 4:
        raise ValueError(f"{name} hacia {target!r} no esta alineado a word")
    return _range(delta // 4, 8, name="imm")


def _current_byte() -> int:
    ctx = globals().get("CONTEXT")
    rt = getattr(ctx, "runtime", None)
    if rt is None:
        return 0
    current_bits = int(getattr(rt, "base_offset_bits", 0)) + len(getattr(rt, "bits", ""))
    if current_bits % 8:
        raise ValueError("la posicion actual no esta alineada a byte")
    return current_bits // 8


def _label_offset(label: str) -> int | None:
    ctx = globals().get("CONTEXT")
    rt = getattr(ctx, "runtime", None)
    if rt is not None and label in getattr(rt, "labels", {}):
        return int(rt.labels[label])
    compiler = getattr(ctx, "compiler", None)
    if compiler is not None:
        item = getattr(compiler, "labels", {}).get(label)
        if isinstance(item, dict) and "offset" in item:
            return int(item["offset"])
    return None


def _branch_offset(target: str, bits: int) -> int:
    destination = _label_offset(str(target).strip())
    if destination is None:
        return 0
    delta = destination - (_current_byte() + 4)
    if delta % 2:
        raise ValueError(f"branch Thumb hacia {target!r} no cae en halfword")
    offset = delta // 2
    minimum = -(1 << (bits - 1))
    maximum = (1 << (bits - 1)) - 1
    if not minimum <= offset <= maximum:
        raise ValueError(f"branch hacia {target!r} fuera de rango para offset{bits}")
    return offset & ((1 << bits) - 1)


def _emit16(opcode: int):
    return emit_bytes(int(opcode & 0xFFFF).to_bytes(2, "little"))


def _emit_hi(op: int, rd_value: Any, rs_value: Any, *, name: str):
    rd = _regnum(rd_value, name="rd")
    rs = _regnum(rs_value, name="rs")
    return _emit16(0x4400 | (op << 8) | ((rd & 8) << 4) | ((rs & 8) << 3) | ((rs & 7) << 3) | (rd & 7))


def main():
    if getattr(globals().get("CONTEXT"), "phase", None) == "parse":
        return None
    pack = args()
    if not pack:
        return Err("thumb_ins requiere tipo de instruccion")

    ins = pack[0].strip().lower()

    try:
        if ins in {"db", "u8"}:
            if len(pack) != 2:
                return Err("db requiere 1 argumento")
            return emit_bytes(bytes([_range(_int(pack[1], name="db"), 8, name="db")]))

        if ins in {"dh", "u16"}:
            if len(pack) != 2:
                return Err("dh requiere 1 argumento")
            return emit_bytes(_range(_int(pack[1], name="dh"), 16, name="dh").to_bytes(2, "little"))

        if ins in {"dw", "u32"}:
            if len(pack) != 2:
                return Err("dw requiere 1 argumento")
            return emit_bytes(_range(_int(pack[1], name="dw"), 32, name="dw").to_bytes(4, "little"))

        if ins in {"store", "mov_imm"}:
            if len(pack) != 3:
                return Err("store requiere rd, imm8")
            rd = _reg3(pack[1], name="rd")
            imm = _range(_int(pack[2], name="imm"), 8, name="imm")
            return _emit16(0x2000 | (rd << 8) | imm)

        if ins == "cmp_imm":
            if len(pack) != 3:
                return Err("cmp_imm requiere rd, imm8")
            rd = _reg3(pack[1], name="rd")
            imm = _range(_int(pack[2], name="imm"), 8, name="imm")
            return _emit16(0x2800 | (rd << 8) | imm)

        if ins in {"add_imm", "sub_imm"}:
            if len(pack) != 3:
                return Err(f"{ins} requiere rd, imm8")
            rd = _reg3(pack[1], name="rd")
            imm = _range(_int(pack[2], name="imm"), 8, name="imm")
            base = 0x3000 if ins == "add_imm" else 0x3800
            return _emit16(base | (rd << 8) | imm)

        if ins in {"move", "mov"}:
            if len(pack) != 3:
                return Err("move requiere rd, rs")
            return _emit_hi(0x2, pack[1], pack[2], name="mov_hi")

        if ins in {"add", "sub"}:
            if len(pack) != 4:
                return Err(f"{ins} requiere rd, rs, rn")
            rd = _reg3(pack[1], name="rd")
            rs = _reg3(pack[2], name="rs")
            rn = _reg3(pack[3], name="rn")
            base = 0x1800 if ins == "add" else 0x1A00
            return _emit16(base | (rn << 6) | (rs << 3) | rd)

        if ins in {"add3_imm", "sub3_imm"}:
            if len(pack) != 4:
                return Err(f"{ins} requiere rd, rs, imm3")
            rd = _reg3(pack[1], name="rd")
            rs = _reg3(pack[2], name="rs")
            imm = _range(_int(pack[3], name="imm"), 3, name="imm")
            base = 0x1C00 if ins == "add3_imm" else 0x1E00
            return _emit16(base | (imm << 6) | (rs << 3) | rd)

        if ins == "add_hi":
            if len(pack) != 3:
                return Err("add_hi requiere rd, rs")
            return _emit_hi(0x0, pack[1], pack[2], name="add_hi")

        if ins == "cmp_hi":
            if len(pack) != 3:
                return Err("cmp_hi requiere rd, rs")
            return _emit_hi(0x1, pack[1], pack[2], name="cmp_hi")

        if ins in _ALU:
            if len(pack) != 3:
                return Err(f"{ins} requiere rd, rs")
            if ins == "cmp":
                rd_num = _regnum(pack[1], name="rd")
                rs_num = _regnum(pack[2], name="rs")
                if rd_num > 7 or rs_num > 7:
                    return _emit_hi(0x1, pack[1], pack[2], name="cmp_hi")
            rd = _reg3(pack[1], name="rd")
            rs = _reg3(pack[2], name="rs")
            return _emit16(0x4000 | (_ALU[ins] << 6) | (rs << 3) | rd)

        if ins in {"lsl", "lsr", "asr"}:
            if len(pack) != 4:
                return Err(f"{ins} requiere rd, rs, imm5")
            rd = _reg3(pack[1], name="rd")
            rs = _reg3(pack[2], name="rs")
            imm = _range(_int(pack[3], name="imm"), 5, name="imm")
            base = {"lsl": 0x0000, "lsr": 0x0800, "asr": 0x1000}[ins]
            return _emit16(base | (imm << 6) | (rs << 3) | rd)

        if ins in {"str", "strh", "strb", "ldr", "ldrh", "ldrb", "ldsb", "ldsh"}:
            if len(pack) != 4:
                return Err(f"{ins} requiere rd, rb, ro")
            rd = _reg3(pack[1], name="rd")
            rb = _reg3(pack[2], name="rb")
            ro = _reg3(pack[3], name="ro")
            base = {
                "str": 0x5000,
                "strh": 0x5200,
                "strb": 0x5400,
                "ldsb": 0x5600,
                "ldr": 0x5800,
                "ldrh": 0x5A00,
                "ldrb": 0x5C00,
                "ldsh": 0x5E00,
            }[ins]
            return _emit16(base | (ro << 6) | (rb << 3) | rd)

        if ins in {"str_imm", "ldr_imm", "strb_imm", "ldrb_imm", "strh_imm", "ldrh_imm"}:
            if len(pack) != 4:
                return Err(f"{ins} requiere rd, rb, imm")
            rd = _reg3(pack[1], name="rd")
            rb = _reg3(pack[2], name="rb")
            scale = 4 if ins in {"str_imm", "ldr_imm"} else 2 if ins in {"strh_imm", "ldrh_imm"} else 1
            imm = _scaled_imm(pack[3], scale, 5, name="imm")
            base = {
                "str_imm": 0x6000,
                "ldr_imm": 0x6800,
                "strb_imm": 0x7000,
                "ldrb_imm": 0x7800,
                "strh_imm": 0x8000,
                "ldrh_imm": 0x8800,
            }[ins]
            return _emit16(base | (imm << 6) | (rb << 3) | rd)

        if ins in {"ldr_pc", "str_sp", "ldr_sp", "adr", "add_sp"}:
            if len(pack) != 3:
                return Err(f"{ins} requiere rd, imm")
            rd = _reg3(pack[1], name="rd")
            imm = _scaled_imm(pack[2], 4, 8, name="imm")
            base = {
                "ldr_pc": 0x4800,
                "str_sp": 0x9000,
                "ldr_sp": 0x9800,
                "adr": 0xA000,
                "add_sp": 0xA800,
            }[ins]
            return _emit16(base | (rd << 8) | imm)

        if ins in {"ldr_pc_label", "adr_label"}:
            if len(pack) != 3:
                return Err(f"{ins} requiere rd, etiqueta")
            rd = _reg3(pack[1], name="rd")
            imm = _pc_relative_label(pack[2], name=ins)
            base = 0x4800 if ins == "ldr_pc_label" else 0xA000
            return _emit16(base | (rd << 8) | imm)

        if ins in {"add_sp_imm", "sub_sp_imm"}:
            if len(pack) != 2:
                return Err(f"{ins} requiere imm")
            imm = _scaled_imm(pack[1], 4, 7, name="imm")
            base = 0xB000 if ins == "add_sp_imm" else 0xB080
            return _emit16(base | imm)

        if ins == "bx":
            if len(pack) != 2:
                return Err("bx requiere rm")
            rm = _regnum(pack[1], name="rm")
            return _emit16(0x4700 | (rm << 3))

        if ins == "push":
            if len(pack) != 2:
                return Err("push requiere rd/LR")
            reg = _regnum(pack[1], name="push")
            if reg == 14:
                return _emit16(0xB500)
            if not 0 <= reg <= 7:
                raise ValueError("push solo acepta R0-R7 o LR")
            return _emit16(0xB400 | (1 << reg))

        if ins in {"push_mask", "push_list"}:
            if len(pack) < 2:
                return Err(f"{ins} requiere mask/lista")
            regs = ",".join(pack[1:])
            mask = _reglist_mask(regs, bits=9, name="mask", lr=True)
            return _emit16(0xB400 | mask)

        if ins == "pop":
            if len(pack) != 2:
                return Err("pop requiere rd/PC")
            reg = _regnum(pack[1], name="pop")
            if reg == 15:
                return _emit16(0xBD00)
            if not 0 <= reg <= 7:
                raise ValueError("pop solo acepta R0-R7 o PC")
            return _emit16(0xBC00 | (1 << reg))

        if ins in {"pop_mask", "pop_list"}:
            if len(pack) < 2:
                return Err(f"{ins} requiere mask/lista")
            regs = ",".join(pack[1:])
            mask = _reglist_mask(regs, bits=9, name="mask", pc=True)
            return _emit16(0xBC00 | mask)

        if ins in {"stmia", "ldmia", "stmia_list", "ldmia_list"}:
            if len(pack) < 3:
                return Err(f"{ins} requiere rb, mask")
            rb = _reg3(pack[1], name="rb")
            regs = ",".join(pack[2:])
            mask = _reglist_mask(regs, bits=8, name="mask")
            base = 0xC000 if ins in {"stmia", "stmia_list"} else 0xC800
            return _emit16(base | (rb << 8) | mask)

        if ins in {"b", "jump"}:
            if len(pack) != 2:
                return Err("jump requiere etiqueta")
            off = _branch_offset(pack[1], 11)
            return _emit16(0xE000 | off)

        if ins == "swi":
            if len(pack) != 2:
                return Err("swi requiere imm8")
            imm = _range(_int(pack[1], name="imm"), 8, name="imm")
            return _emit16(0xDF00 | imm)

        if ins == "bcond" or (ins.startswith("b") and ins[1:] in _COND):
            if ins == "bcond":
                if len(pack) != 3:
                    return Err("bcond requiere condicion, etiqueta")
                cond_name = pack[1].strip().lower()
                target = pack[2]
            else:
                if len(pack) != 2:
                    return Err(f"{ins} requiere etiqueta")
                cond_name = ins[1:]
                target = pack[1]
            if cond_name not in _COND:
                return Err(f"condicion Thumb no soportada: {cond_name}")
            off = _branch_offset(target, 8)
            return _emit16(0xD000 | (_COND[cond_name] << 8) | off)

        if ins in {"call", "bl"}:
            if len(pack) != 2:
                return Err("call requiere etiqueta")
            destination = _label_offset(str(pack[1]).strip())
            if destination is None:
                return emit_bytes(b"\x00\x00\x00\x00")
            delta = destination - (_current_byte() + 4)
            if delta % 2:
                raise ValueError(f"BL hacia {pack[1]!r} no cae en halfword")
            off = delta // 2
            if not -(1 << 22) <= off < (1 << 22):
                raise ValueError(f"BL hacia {pack[1]!r} fuera de rango")
            off &= 0x3FFFFF
            hi = (off >> 11) & 0x7FF
            lo = off & 0x7FF
            return emit_bytes((0xF000 | hi).to_bytes(2, "little") + (0xF800 | lo).to_bytes(2, "little"))

        return Err(f"thumb_ins: instruccion no soportada '{ins}'")
    except ValueError as exc:
        return Err(f"thumb_ins {ins}: {exc}")
    except Exception as exc:
        return Err(f"thumb_ins {ins}: {exc}")


def _start():
    return main()
