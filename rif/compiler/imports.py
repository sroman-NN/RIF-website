

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rif.errors import PackError
from rif.expr import UnresolvedExpression, eval_int_expr
from rif.models import (
    CompileResult,
    EmitChunk,
    EmitInstruction,
    Err,
    Expr,
    FlowInstruction,
    GLOBAL_STATE_LOCK,
    Line,
    MemoryRegion,
    OperandValue,
    Operators,
    Placeholder,
    PluginContext,
    Program,
    REG,
    RuleIndicator,
    Relocation,
    Statement,
    Table,
    TableRow,
    TYPES_MAP,
    TypeDefinition,
    TypeInfo,
)
from rif.bitbuffer import BitBuffer
from rif.memory import memory_region_from_values
from rif.parser import Parser, load_plugins, parse_packer_config, run_precompilers
from rif.resolver import PlaceholderResolver

# construir el __all__ que a mí me da paja