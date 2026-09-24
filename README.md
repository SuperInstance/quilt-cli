# quilt-cli

> **Unified CLI surface for the Quilt substrate walker fleet.**
> 21 commands. Single dispatch. Every walker in the fleet invokable from one place.

`quilt` is the conductor's baton. Each subcommand is a substrate in the CLI's own cell architecture. The CLI itself is substrate-agnostic — it dispatches to whichever substrate owns each operation.

## Doctrine

The CLI is itself a Quilt cell. Each subcommand = a substrate. The dispatcher routes by `subprocess.run` into each repo, never re-implementing logic.

- **cells-are-scars**: every command emits receipts; every run is a witness
- **witness-log-is-prediction**: the CLI's own invocation log IS its future capability set
- **substrate-is-grown**: the CLI started as a thin shell; new commands grew from fleet-needs

## Commands (21 total)

| Command | Substrate | Purpose |
|---------|-----------|---------|
| `quilt cell` | quilt-cell-harness | One cell at a time — substrate walk |
| `quilt quilt` | quilt-cell-harness | Multi-cell compositions |
| `quilt qult` | quilt-cell-harness | Fractal composition |
| `quilt fleet` | quilt-fleet-snapshot | Fleet state operations |
| `quilt edge` | quilt-edge-node | UNO Q edge nodes |
| `quilt sim` | quilt-fleet-sim | Virtual fleet simulation |
| `quilt voice` | quilt-voice-agent | Voice agent on edge |
| `quilt mesh` | quilt-mesh-bridge | WebSocket mesh relay |
| `quilt canon` | quilt-canon-explorer | Canon archive browse |
| `quilt init` | quilt-brewer | Scaffold a new repo |
| `quilt doctor` | quilt-bootstrap | Run fleet test suites |
| `quilt version` | self | Show version + state |
| `quilt bootstrap` | quilt-bootstrap | Restore the fleet |
| `quilt brew` | quilt-brewer | Grow a walker from a recipe |
| `quilt trace` | quilt-trace | Render receipts → HTML |
| `quilt scout` | api-orchestra | List recently-pushed repos |
| `quilt chord` | multi-LLM | N-voice chord |
| `quilt legalese` | quilt-legalese | Fence a prompt through the legalese network |
| `quilt holodeck` | quilt-spreadsheet-inference | Run a scenario through Holodeck |
| `quilt vessel` | quilt-seed | Vessel mode (peck + trust cycle) |
| `quilt compose` | quilt-spreadsheet-inference | Compose a substrate walker |

## Quick start

```bash
# Restore the fleet in <90s
quilt bootstrap --mode full

# Grow a walker from a recipe in <30s
quilt brew quilt-perception /tmp/new-walker

# Render a receipt log to HTML in <5s
quilt trace receipts.jsonl --out landing.html

# Run all 7 fleet test suites and verify health
quilt doctor

# Multi-LLM chord on a question
quilt chord "What is the Reynolds number?" --voices 3
```

## Architecture

The CLI is a thin shell over `subprocess`. Each command dispatches to a substrate walker repo's main entrypoint and passes through stdout/stderr. The CLI never holds state between calls — every invocation is its own witness.

```
$ quilt <command> [...]
  → subprocess.run(["python", "-m", "<package>.<module>"], ...)
  → capture stdout → format → print
  → exit code returned as $?
```

The CLI also writes its own witness log to `~/.quilt/invocations.jsonl` — every command, every timestamp, every exit code. The log IS the substrate walk.

## Cross-references

- `quilt-bootstrap` — the fleet inventory source
- `quilt-brewer` — recipe → walker factory
- `quilt-trace` — receipts → landing pages
- `quilt-cell-harness` — cell / quilt / qult composition
- `quilt-spreadsheet-inference` — Holodeck + multi-LLM chord
- `quilt-canon-explorer` — canon archive browser

## License

Apache-2.0 — Casey / SuperInstance / Mavis × Casey session line
