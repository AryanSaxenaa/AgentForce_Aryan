"""
Complexity analyzer: compute basic code metrics.
"""
from __future__ import annotations

from typing import List

from ..interfaces.base_interfaces import ComplexityMetrics


class ComplexityAnalyzer:
    """Computes very lightweight complexity metrics from code text.

    - cyclomatic: count control-flow keywords
    - cognitive: heuristic proportional to nesting markers
    - lines_of_code: non-empty lines
    - maintainability_index: simple inverse function
    """

    CONTROL_TOKENS = (
        'if ', 'elif ', 'else:', 'for ', 'while ', 'case ', 'switch ', 'try:', 'except', 'catch', '&&', '||'
    )

    def analyze(self, code: str) -> ComplexityMetrics:
        loc = sum(1 for ln in code.splitlines() if ln.strip())
        cyclo = 1
        for tok in self.CONTROL_TOKENS:
            cyclo += code.count(tok)
        cognitive = max(0, cyclo - 1)
        # Simple maintainability index heuristic: higher is better
        mi = max(0.0, 100.0 - (cyclo * 2 + cognitive * 1.5) - (loc * 0.1))
        return ComplexityMetrics(
            cyclomatic_complexity=cyclo,
            cognitive_complexity=cognitive,
            lines_of_code=loc,
            maintainability_index=round(mi, 2),
        )
