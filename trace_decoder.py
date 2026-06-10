"""Parse raw Geth/Nethermind EVM traces into structured call frames."""

import json
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class CallFrame:
    type: str          # CALL, DELEGATECALL, STATICCALL, CREATE
    from_addr: str
    to_addr: str
    value: int
    gas_used: int
    input_data: str
    depth: int
    children: list = field(default_factory=list)

    def flatten(self):
        """Flatten tree into ordered list (dfs pre-order)."""
        frames = [self]
        for child in self.children:
            frames.extend(child.flatten())
        return frames


def parse_geth_trace(raw_trace: dict) -> CallFrame:
    """Recursively parse a Geth-style structLog trace."""

    def _parse(node: dict, depth: int = 0) -> CallFrame:
        action = node.get("action", {})
        frame = CallFrame(
            type=action.get("callType") or action.get("type", "CALL"),
            from_addr=action.get("from", ""),
            to_addr=action.get("to", ""),
            value=int(action.get("value", "0x0"), 16),
            gas_used=int(node.get("result", {}).get("gasUsed", "0x0"), 16),
            input_data=action.get("input", "0x"),
            depth=depth,
        )
        for sub_call in node.get("calls", []):
            frame.children.append(_parse(sub_call, depth + 1))
        return frame

    return _parse(raw_trace)


def filter_by_target(frames: list[CallFrame], address: str) -> list[CallFrame]:
    """Filter flattened frames by target address (case-insensitive)."""
    addr = address.lower()
    return [f for f in frames if f.to_addr.lower() == addr]


def summarize(frames: list[CallFrame]) -> str:
    """One-line per call summary."""
    lines = []
    for f in frames:
        indent = "  " * f.depth
        sig = f.input_data[:10] if len(f.input_data) > 10 else f.input_data
        lines.append(f"{indent}[{f.type}] {f.from_addr[:10]}... → {f.to_addr[:10]}... | {sig} | gas={f.gas_used}")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("usage: python trace_decoder.py <trace.json> [filter_address]")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        raw = json.load(f)

    root = parse_geth_trace(raw)
    flattened = root.flatten()

    if len(sys.argv) >= 3:
        flattened = filter_by_target(flattened, sys.argv[2])

    print(summarize(flattened))
    print(f"\n--- {len(flattened)} call frames total (depth {root.depth})")
