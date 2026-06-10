## evm-trace

small utility to pull geth-style evm traces apart — converts the messy nested json into flat call frames and lets you filter by target address.

mostly used for mev analysis, debugging failed tx bundles, and sanity-checking what a transaction *actually* does vs what it claims to do.

### usage

```bash
python trace_decoder.py trace.json
python trace_decoder.py trace.json 0xsome_address
```

input format: standard geth `debug_traceTransaction` output with `callTracer` option.

### todo
- [ ] nethermind parity tracer support
- [ ] gas accounting breakdown
- [ ] graphviz export for call trees
