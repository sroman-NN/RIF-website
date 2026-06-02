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
    "al": 0xE,
}

_DP = {
    "and": 0x0,
    "eor": 0x1,
    "xor": 0x1,
    "sub": 0x2,
    "rsb": 0x3,
    "add": 0x4,
    "adc": 0x5,
    "sbc": 0x6,
    "rsc": 0x7,
    "tst": 0x8,
    "teq": 0x9,
    "cmp": 0xA,
    "cmn": 0xB,
    "orr": 0xC,
    "or": 0xC,
    "mov": 0xD,
    "bic": 0xE,
    "mvn": 0xF,
}

_REG_ALIAS = {
    "SP": 13,
    "LR": 14,
    "PC": 15,
}

_SHIFT = {
    "lsl": 0,
    "lsr": 1,
    "asr": 2,
    "ror": 3,
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


def _reg(value: Any, *, name: str = "registro") -> int:
    text = str(value).strip().upper()
    if text in _REG_ALIAS:
        return _REG_ALIAS[text]
    if re.fullmatch(r"R(?:[0-9]|1[0-5])", text):
        return int(text[1:])
    raw = _int(text, name=name)
    if not 0 <= raw <= 15:
        raise ValueError(f"{name} debe ser R0-R15/SP/LR/PC")
    return raw


def _cond(value: Any = "al") -> int:
    text = str(value).strip().lower()
    if text not in _COND:
        raise ValueError(f"condicion ARM no soportada: {value}")
    return _COND[text]


def _ror(value: int, amount: int) -> int:
    amount &= 31
    return ((value >> amount) | (value << (32 - amount))) & 0xFFFFFFFF


def _rol(value: int, amount: int) -> int:
    amount &= 31
    return ((value << amount) | (value >> (32 - amount))) & 0xFFFFFFFF


def _imm12(value: Any) -> int:
    raw = _range(_int(value, name="imm"), 32, name="imm")
    for rotate in range(16):
        imm8 = _rol(raw, rotate * 2) & 0xFF
        if _ror(imm8, rotate * 2) == raw:
            return (rotate << 8) | imm8
    raise ValueError(f"imm={raw} no cabe como inmediato rotado ARM")


def _reglist_mask(value: Any) -> int:
    text = str(value).strip()
    if not text.startswith("{"):
        return _range(_int(text, name="mask"), 16, name="mask")
    if not text.endswith("}"):
        raise ValueError("lista de registros debe cerrar con }")
    mask = 0
    for item in text[1:-1].split(","):
        part = item.strip()
        if not part:
            continue
        if "-" in part:
            start_text, end_text = [chunk.strip() for chunk in part.split("-", 1)]
            start = _reg(start_text)
            end = _reg(end_text)
            if start > end:
                raise ValueError(f"rango de registros invalido: {part}")
            for reg in range(start, end + 1):
                mask |= 1 << reg
        else:
            mask |= 1 << _reg(part)
    return mask


def _is_gpr(value: Any) -> bool:
    val = str(value).strip().upper()
    if val in _REG_ALIAS:
        return True
    if re.fullmatch(r"R(?:[0-9]|1[0-5])", val):
        return True
    
    ctx = globals().get("CONTEXT")
    if ctx is not None and ctx.program is not None:
        reg_obj = next((r for r in ctx.program.regs.registers if r.name.upper() == val or (r.alias and r.alias.upper() == val)), None)
        if reg_obj is not None:
            is_gpr = reg_obj.values.get("GNP") == "yes" or str(reg_obj.values.get("type")) == "0"
            return is_gpr
    return False


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



def _get_endianness() -> str:
    ctx = globals().get("CONTEXT")
    if ctx is not None and getattr(ctx, "program", None) is not None and hasattr(ctx.program, "world"):
        raw = ctx.program.world.values.get("endianness", ctx.program.world.values.get("endianess", "little"))
        if isinstance(raw, int):
            return "big" if raw else "little"
        text = str(raw).strip().lower()
        if text in {"big", "be", "1"}:
            return "big"
    return "little"

def _emit32(opcode: int):
    return emit_bytes(int(opcode & 0xFFFFFFFF).to_bytes(4, _get_endianness()))


def _branch(target: Any, *, link: bool, cond: int) -> int:
    destination = _label_offset(str(target).strip())
    if destination is None:
        offset = 0
    else:
        delta = destination - (_current_byte() + 8)
        if delta % 4:
            raise ValueError(f"branch ARM hacia {target!r} no cae en word")
        offset = delta // 4
        if not -(1 << 23) <= offset < (1 << 23):
            raise ValueError(f"branch ARM hacia {target!r} fuera de rango")
    return (cond << 28) | (0x0B000000 if link else 0x0A000000) | (offset & 0x00FFFFFF)


def _ldr_label(rd: int, target: Any, *, cond: int) -> int:
    destination = _label_offset(str(target).strip())
    if destination is None:
        offset = 0
        up = True
    else:
        delta = destination - (_current_byte() + 8)
        up = delta >= 0
        offset = abs(delta)
        if offset > 0xFFF:
            raise ValueError(f"literal ARM hacia {target!r} fuera de rango")
    return (cond << 28) | 0x051F0000 | (int(up) << 23) | (rd << 12) | offset


def _dp_reg(ins: str, rd: int, rn: int, rm: int, *, cond: int, s: bool = False) -> int:
    op = _DP[ins]
    flag_s = s or ins in {"cmp", "cmn", "tst", "teq"}
    if ins in {"mov", "mvn"}:
        rn = 0
    if ins in {"cmp", "cmn", "tst", "teq"}:
        rd = 0
    return (cond << 28) | (op << 21) | (int(flag_s) << 20) | (rn << 16) | (rd << 12) | rm


def _dp_shift(ins: str, rd: int, rn: int, rm: int, shift: str, amount: Any, *, cond: int, by_reg: bool = False) -> int:
    op = _DP[ins]
    flag_s = ins in {"cmp", "cmn", "tst", "teq"}
    if ins in {"mov", "mvn"}:
        rn = 0
    if ins in {"cmp", "cmn", "tst", "teq"}:
        rd = 0
    shift_code = _SHIFT[str(shift).strip().lower()]
    if by_reg:
        rs = _reg(amount, name="rs")
        operand2 = (rs << 8) | (shift_code << 5) | 0x10 | rm
    else:
        imm = _range(_int(amount, name="shift"), 5, name="shift")
        operand2 = (imm << 7) | (shift_code << 5) | rm
    return (cond << 28) | (op << 21) | (int(flag_s) << 20) | (rn << 16) | (rd << 12) | operand2


def _dp_imm(ins: str, rd: int, rn: int, imm: Any, *, cond: int, s: bool = False) -> int:
    op = _DP[ins]
    flag_s = s or ins in {"cmp", "cmn", "tst", "teq"}
    if ins in {"mov", "mvn"}:
        rn = 0
    if ins in {"cmp", "cmn", "tst", "teq"}:
        rd = 0
    return (cond << 28) | 0x02000000 | (op << 21) | (int(flag_s) << 20) | (rn << 16) | (rd << 12) | _imm12(imm)


def _single_transfer(ins: str, rd: int, rn: int, imm: Any, *, cond: int) -> int:
    raw = _int(imm, name="imm")
    offset = abs(raw)
    _range(offset, 12, name="imm")
    load = ins.startswith("ldr")
    byte = ins.endswith("b")
    up = raw >= 0
    return (cond << 28) | 0x05000000 | (int(up) << 23) | (int(byte) << 22) | (int(load) << 20) | (rn << 16) | (rd << 12) | offset


def _half_transfer(ins: str, rd: int, rn: int, imm: Any, *, cond: int) -> int:
    raw = _int(imm, name="imm")
    offset = abs(raw)
    _range(offset, 8, name="imm")
    up = raw >= 0
    code = {"strh": 0xB0, "ldrh": 0xB0, "ldrsb": 0xD0, "ldrsh": 0xF0}[ins]
    load = ins != "strh"
    return (
        (cond << 28)
        | 0x01400000
        | (int(up) << 23)
        | (int(load) << 20)
        | (rn << 16)
        | (rd << 12)
        | ((offset & 0xF0) << 4)
        | (offset & 0x0F)
        | code
    )


def main():
    if getattr(globals().get("CONTEXT"), "phase", None) == "parse":
        return None
    pack = args()
    if not pack:
        return Err("arm_ins requiere tipo de instruccion")
    ins = pack[0].strip().lower()
    cond = 0xE
    if len(pack) > 1 and str(pack[-1]).strip().lower() in _COND and ins not in {"b", "bl"}:
        cond = _cond(pack.pop())
    try:
        if ins == "raw":
            if len(pack) != 2:
                return Err("arm raw requiere word")
            return _emit32(_int(pack[1], name="word"))

        if ins in {"bx", "thumb"}:
            if len(pack) != 2:
                return Err("arm bx requiere rm")
            return _emit32((cond << 28) | 0x012FFF10 | _reg(pack[1], name="rm"))

        if ins in {"b", "bl"}:
            if len(pack) not in {2, 3}:
                return Err(f"arm {ins} requiere etiqueta")
            if len(pack) == 3:
                cond = _cond(pack[2])
            return _emit32(_branch(pack[1], link=ins == "bl", cond=cond))

        if ins == "swi":
            if len(pack) != 2:
                return Err("arm swi requiere imm24")
            return _emit32((cond << 28) | 0x0F000000 | _range(_int(pack[1], name="imm"), 24, name="imm"))

        if ins in {"mul", "muls"}:
            if len(pack) != 4:
                return Err("arm mul requiere rd, rm, rs")
            rd = _reg(pack[1], name="rd")
            rm = _reg(pack[2], name="rm")
            rs = _reg(pack[3], name="rs")
            return _emit32((cond << 28) | (int(ins == "muls") << 20) | (rd << 16) | (rs << 8) | 0x90 | rm)

        if ins in {"mla", "mlas"}:
            if len(pack) != 5:
                return Err("arm mla requiere rd, rm, rs, rn")
            rd = _reg(pack[1], name="rd")
            rm = _reg(pack[2], name="rm")
            rs = _reg(pack[3], name="rs")
            rn = _reg(pack[4], name="rn")
            return _emit32((cond << 28) | 0x00200000 | (int(ins == "mlas") << 20) | (rd << 16) | (rn << 12) | (rs << 8) | 0x90 | rm)

        if ins in {"umull", "umlal", "smull", "smlal"}:
            if len(pack) != 5:
                return Err(f"arm {ins} requiere rdlo, rdhi, rm, rs")
            rdlo = _reg(pack[1], name="rdlo")
            rdhi = _reg(pack[2], name="rdhi")
            rm = _reg(pack[3], name="rm")
            rs = _reg(pack[4], name="rs")
            signed = ins in {"smull", "smlal"}
            accumulate = ins in {"umlal", "smlal"}
            return _emit32((cond << 28) | 0x00800090 | (int(signed) << 22) | (int(accumulate) << 21) | (rdhi << 16) | (rdlo << 12) | (rs << 8) | rm)

        if ins in {"dp_shift", "dp_shift_reg"}:
            if len(pack) != 7:
                return Err(f"arm {ins} requiere op, rd, rn, rm, shift, amount")
            op = str(pack[1]).strip().lower()
            if op not in _DP:
                raise ValueError(f"data processing no soportado: {op}")
            return _emit32(_dp_shift(op, _reg(pack[2], name="rd"), _reg(pack[3], name="rn"), _reg(pack[4], name="rm"), pack[5], pack[6], cond=cond, by_reg=ins.endswith("_reg")))

        if ins.endswith("_imm") and ins[:-4] in _DP:
            op = ins[:-4]
            if op in {"mov", "mvn"}:
                if len(pack) != 3:
                    return Err(f"arm {ins} requiere rd, imm")
                return _emit32(_dp_imm(op, _reg(pack[1], name="rd"), 0, pack[2], cond=cond))
            if op in {"cmp", "cmn", "tst", "teq"}:
                if len(pack) != 3:
                    return Err(f"arm {ins} requiere rn, imm")
                return _emit32(_dp_imm(op, 0, _reg(pack[1], name="rn"), pack[2], cond=cond))
            if len(pack) != 4:
                return Err(f"arm {ins} requiere rd, rn, imm")
            return _emit32(_dp_imm(op, _reg(pack[1], name="rd"), _reg(pack[2], name="rn"), pack[3], cond=cond))

        if ins in _DP:
            if ins in {"mov", "mvn"}:
                if len(pack) != 3:
                    return Err(f"arm {ins} requiere rd, rm")
                if _is_gpr(pack[2]):
                    return _emit32(_dp_reg(ins, _reg(pack[1], name="rd"), 0, _reg(pack[2], name="rm"), cond=cond))
                else:
                    return _emit32(_dp_imm(ins, _reg(pack[1], name="rd"), 0, pack[2], cond=cond))
            if ins in {"cmp", "cmn", "tst", "teq"}:
                if len(pack) != 3:
                    return Err(f"arm {ins} requiere rn, rm")
                if _is_gpr(pack[2]):
                    return _emit32(_dp_reg(ins, 0, _reg(pack[1], name="rn"), _reg(pack[2], name="rm"), cond=cond))
                else:
                    return _emit32(_dp_imm(ins, 0, _reg(pack[1], name="rn"), pack[2], cond=cond))
            if len(pack) != 4:
                return Err(f"arm {ins} requiere rd, rn, rm")
            if _is_gpr(pack[3]):
                return _emit32(_dp_reg(ins, _reg(pack[1], name="rd"), _reg(pack[2], name="rn"), _reg(pack[3], name="rm"), cond=cond))
            else:
                return _emit32(_dp_imm(ins, _reg(pack[1], name="rd"), _reg(pack[2], name="rn"), pack[3], cond=cond))

        if ins in {"ldr", "str", "ldrb", "strb"}:
            if len(pack) != 4:
                return Err(f"arm {ins} requiere rd, rn, imm")
            return _emit32(_single_transfer(ins, _reg(pack[1], name="rd"), _reg(pack[2], name="rn"), pack[3], cond=cond))

        if ins == "ldr_label":
            if len(pack) != 3:
                return Err("arm ldr_label requiere rd, etiqueta")
            return _emit32(_ldr_label(_reg(pack[1], name="rd"), pack[2], cond=cond))

        if ins in {"ldrh", "strh", "ldrsb", "ldrsh"}:
            if len(pack) != 4:
                return Err(f"arm {ins} requiere rd, rn, imm")
            return _emit32(_half_transfer(ins, _reg(pack[1], name="rd"), _reg(pack[2], name="rn"), pack[3], cond=cond))

        if ins in {"ldmia", "stmia", "ldmia_w", "stmia_w", "ldmfd", "stmfd"}:
            if len(pack) < 3:
                return Err(f"arm {ins} requiere rn, mask/lista")
            rn = _reg(pack[1], name="rn")
            regs = ",".join(pack[2:])
            mask = _reglist_mask(regs)
            if ins == "ldmia":
                base = 0x08900000
            elif ins == "stmia":
                base = 0x08800000
            elif ins == "ldmia_w":
                base = 0x08B00000
            elif ins == "stmia_w":
                base = 0x08A00000
            elif ins == "ldmfd":
                base = 0x08B00000
            else:
                base = 0x09200000
            return _emit32((cond << 28) | base | (rn << 16) | mask)

        if ins == "mrs":
            if len(pack) != 3:
                return Err("arm mrs requiere rd, cpsr/spsr")
            psr = str(pack[2]).strip().lower()
            if psr not in {"cpsr", "spsr"}:
                raise ValueError("mrs acepta cpsr o spsr")
            return _emit32((cond << 28) | 0x010F0000 | (int(psr == "spsr") << 22) | (_reg(pack[1], name="rd") << 12))

        return Err(f"arm_ins: instruccion no soportada '{ins}'")
    except ValueError as exc:
        return Err(f"arm_ins {ins}: {exc}")
    except Exception as exc:
        return Err(f"arm_ins {ins}: {exc}")


def _start():
    return main()
