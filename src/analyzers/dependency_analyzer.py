"""
Dependency analyzer: extract imports and simple external call patterns.
"""
from __future__ import annotations

import re
from typing import List

from ..interfaces.base_interfaces import Dependency


class DependencyAnalyzer:
    """Finds dependencies via simple regex scans.

    - Python: import/from import
    - JS/TS: import/export require()
    - Java: import statements
    """

    def detect(self, code: str, language: str) -> List[Dependency]:
        deps: List[Dependency] = []
        lines = code.splitlines()

        def add(name: str, kind: str, source: str | None = None):
            deps.append(Dependency(name=name, type=kind, source=source))

        if language == 'python':
            for ln in lines:
                m = re.match(r"\s*import\s+([\w\.]+)", ln)
                if m:
                    add(m.group(1), 'import')
                m = re.match(r"\s*from\s+([\w\.]+)\s+import\s+([\w\*,\s]+)", ln)
                if m:
                    add(m.group(1), 'import')
        elif language in ('javascript', 'typescript'):
            for ln in lines:
                m = re.match(r"\s*import\s+.*from\s+['\"]([^'\"]+)['\"]", ln)
                if m:
                    add(m.group(1), 'import')
                m = re.match(r"\s*const\s+\w+\s*=\s*require\(['\"]([^'\"]+)['\"]\)\s*;?", ln)
                if m:
                    add(m.group(1), 'import')
        elif language == 'java':
            for ln in lines:
                m = re.match(r"\s*import\s+([\w\.\*]+);", ln)
                if m:
                    add(m.group(1), 'import')

        return deps
