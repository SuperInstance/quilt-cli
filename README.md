# quilt-cli

> **The unified CLI for the SuperInstance Quilt cellular framework.**
> One command: `quilt`. Subcommands for cells, quilts, qults, fleets, edges, canon, init.

```
$ quilt
usage: quilt [-h] [--repos REPOS] [-V] <cmd> ...

Unified CLI for the SuperInstance Quilt cellular framework

positional arguments:
  <cmd>
    cell             manage a single Quilt cell
    quilt            manage a Quilt (multi-cell community)
    qult             manage a Qult (fractal composition of Quilts)
    fleet            manage the fleet orchestrator
    edge             manage UNO Q edge nodes
    canon            canon gate + JEV client
    init             scaffold a new quilt repo
    doctor           diagnose the Quilt environment
    version          print quilt and plugin versions

$ quilt cell run --cycles 5
=== 5 cycles on cell 'alpha' ===
Canary:          cd372d0b98b0129c...
Compartments:    [('echo', 0), ('reverse', 0), ('sha256', 0), ...]
Crystallizations: 0
Alive:           False

$ quilt edge identity --ssid boat-lan
Board serial: ABX00173-serial-001
Network SSID: boat-lan
Network salt: 6e879b7e37c6dc3edc1e6da3e90f79f7ed7c39c4b5d048e2d4aff9636ac0c430
Node id:      c6420d48c69783eb0e942887549c0b5c23058452e375c473f2ddb23b589510fe
Short id:     c6420d48

$ quilt canon gate README.md
file:    README.md
length:  4300 chars
canon_p: 0.31
doctrine: 0.42
domain:  cs (conf=0.92)
depth:   0.55

$ quilt init quilt-foo --type cell --description "A new cell"
=== scaffolding 'cell' repo: quilt-foo ===
  target: /workspace/repos/quilt-foo
  description: A new cell
  ✓ wrote 12 files
  ✓ git init + initial commit
```

## What this is

A single Python package (`quilt`) that exposes a single shell command
(`quilt`). The command wraps the existing SuperInstance fleet
(`quilt-cell-harness`, `quilt-edge-node`, `quilt-edge-ml`,
`quilt-fleet-orchestrator`, `quilt-edge-observer`, `quilt-jev-toolkit`)
behind one consistent interface.

Before this CLI, running the fleet required remembering:

```bash
cd /workspace/repos/quilt-cell-harness && python3 cell.py --demo
cd /workspace/repos/quilt-edge-node && python3 examples/full_lifecycle.py
cd /workspace/repos/quilt-fleet-orchestrator && python3 examples/fleet_demo.py
cd /workspace/repos/quilt-jev-toolkit && python3 canon_gate.py /path/to/file.md
```

After:

```bash
quilt cell demo
quilt edge demo
quilt fleet demo
quilt canon gate /path/to/file.md
```

Same demos, one command.

## Subcommands

| Command             | What it does                                |
|---------------------|---------------------------------------------|
| `quilt cell run`    | Run N energy cycles on a cell               |
| `quilt cell defuse` | Reveal the cell's assembly (witness chain)  |
| `quilt cell canary` | Print the cell's canary hash                |
| `quilt cell witness`| Dump the witness chain                      |
| `quilt cell add`    | Register a new substrate on a cell          |
| `quilt cell demo`   | Run the canonical cell demo                 |
| `quilt quilt create`| Spin up a multi-cell Quilt                  |
| `quilt quilt canary`| Print the composed Quilt canary             |
| `quilt qult create` | Spin up a fractal Qult                       |
| `quilt qult demo`   | Run the canonical Qult demo                 |
| `quilt fleet demo`  | Run the canonical 4-node fleet demo         |
| `quilt fleet list`  | List known nodes                            |
| `quilt edge demo`   | Run the canonical UNO Q lifecycle demo      |
| `quilt edge identity` | Mint a network-keyed identity            |
| `quilt canon gate`  | Canon-gate a single file                    |
| `quilt canon batch` | Canon-gate a directory of files             |
| `quilt canon health`| Check JEV API health                        |
| `quilt init`        | Scaffold a new quilt-fleet repo             |
| `quilt doctor`      | Diagnose the Quilt environment              |
| `quilt version`     | Print versions of quilt and plugins         |

## Install

```bash
cd /workspace/repos/quilt-cli
pip install -e . --index-url https://pypi.org/simple/

# Now `quilt` is on PATH.
quilt version
```

## How it composes with the rest of the fleet

```
                      quilt CLI
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
   quilt-cell-harness  quilt-edge-*   quilt-fleet-orchestrator
   (cell.py, quilt.py, (UNO Q runtime  (registry, canary,
    qult.py, llm_cell)  + ML sub.)      task router, etc.)
                          │
                          └─► quilt-jev-toolkit
                              (canon gate via JEV)
```

The CLI does not duplicate logic — it imports the actual modules
from the fleet repos and exposes them through argparse subcommands.
This means:

1. **No drift.** A bug fix in `cell.py` immediately affects `quilt cell`.
2. **No mocks.** The CLI runs the real `cell.process()`, the real
   `Quilt.ask()`, the real `ZAI_SUBSTRATE`.
3. **Single source of truth.** `quilt cell demo` is the same as
   `python3 cell.py --demo`.

## Doctrines demonstrated

1. **Composing across repos beats reimplementing.** This CLI is
   1300 LoC of glue; the work is in the fleet repos it wraps.
2. **The CLI is itself a Quilt cell.** Each subcommand is a
   substrate; each `quilt <cmd> <subcmd>` invocation is a
   crystallized pattern.
3. **`init` is itself a cell.** Scaffolding = the cell growing new
   compartments.
4. **`doctor` is the cell's *self sense*.** It reads hardware +
   fleet state + JEV health and reports what it sees.
5. **`canon gate` is the cell's *survival instinct*.** It refuses
   content that doesn't pass the canon threshold.

## Files

- `src/quilt/__init__.py` — package init + fleet path constants
- `src/quilt/cli.py` — main entry point
- `src/quilt/commands/cell.py` — cell subcommands
- `src/quilt/commands/quilt_cmd.py` — quilt subcommands
- `src/quilt/commands/qult.py` — qult subcommands
- `src/quilt/commands/fleet.py` — fleet subcommands
- `src/quilt/commands/edge.py` — edge subcommands
- `src/quilt/commands/canon.py` — canon + JEV subcommands
- `src/quilt/commands/init_cmd.py` — repo scaffolder
- `src/quilt/commands/doctor.py` — environment diagnostics
- `src/quilt/commands/version.py` — version reporter
- `pyproject.toml` — package metadata + entry points

## Future work

- `quilt cell start --daemon` — long-running cell with WebSocket
- `quilt compose` — chain commands into pipelines
- `quilt replay` — replay a witness chain through a fresh cell
- Tab-completion for bash/zsh/fish
- `quilt publish` — package + push to GitHub + PyPI in one command
