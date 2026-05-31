

from __future__ import annotations

from typing import Any

from rif import REG, Err, Expr, Line, Operators, Placeholder, RuleIndicator


def _clean(value: Any) -> str:
    if hasattr(value, "value"):
        value = value.value
    return str(value).strip()


def main():
    if Line.elements != 2:
        return Err("Error, se esperaba un elemento extra")

    Line.Advance()  
    target = _clean(Line.Advance())
    Line.expects(" ", "\n")

    if not target:
        return Err("Se esperaba un operador")

    op = Operators.Load(target, RuleIndicator.current)
    privtype = getattr(op.type, "PRIVTYPE", op.type.get("PRIVTYPE", "unknown"))
    name = op.type.get("NAME", getattr(op, "name", target))



    if not getattr(op, "resolved", False):
        return Expr([
            "exists",
            Placeholder(
                target=target,
                kind=privtype or "unknown",
                reason="existencia diferida",
                rule_name=RuleIndicator.current,
                line=getattr(Line, "line", None),
            ),
        ])

    if privtype == "symbol":
        return Expr([
            "exists",
            Placeholder(
                target=name,
                kind="symbol",
                reason="símbolo diferido",
                rule_name=RuleIndicator.current,
                line=getattr(Line, "line", None),
            ),
        ])

    if privtype == "register":
        if not REG.exists(name):
            return Err("El registro no existe")
        return 0

    if privtype == "subregister":
        if not REG.exists(name):
            return Err("El subregistro no existe")
        return 0

    return Expr([
        "exists",
        Placeholder(
            target=target,
            kind=privtype or "unknown",
            reason="valor desconocido",
            rule_name=RuleIndicator.current,
            line=getattr(Line, "line", None),
        ),
    ])


def _start():
    return main()
