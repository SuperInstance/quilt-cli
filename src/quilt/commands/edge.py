"""quilt edge — manage UNO Q edge nodes.

Subcommands:
    quilt edge demo                 run the canonical lifecycle demo
    quilt edge identity --ssid S    mint a network-keyed identity
    quilt edge provision --ssid S --password P  provision a board over USB-C
"""
from __future__ import annotations

import sys

from quilt import QUILT_EDGE_NODE


def register(sub):
    p = sub.add_parser("edge", help="manage UNO Q edge nodes")
    sp = p.add_subparsers(dest="edge_subcmd", metavar="<sub>")

    sp.add_parser("demo", help="run the canonical edge lifecycle demo").set_defaults(
        func=lambda a: demo_cmd(a))

    p_id = sp.add_parser("identity", help="mint a network-keyed identity")
    p_id.add_argument("--ssid", required=True)
    p_id.add_argument("--bssid", default="00:00:00:00:00:00")
    p_id.add_argument("--serial", default=None,
                      help="override board serial (default: read from /proc)")
    p_id.set_defaults(func=lambda a: identity_cmd(a))

    p_prov = sp.add_parser("provision", help="provision a board over USB-C")
    p_prov.add_argument("--ssid", required=True)
    p_prov.add_argument("--password", required=True)
    p_prov.add_argument("--serial", default=None)
    p_prov.set_defaults(func=lambda a: provision_cmd(a))


def _import_quilt_edge_module():
    if not QUILT_EDGE_NODE.exists():
        raise SystemExit(f"quilt-edge-node not found at {QUILT_EDGE_NODE}")
    sys.path.insert(0, str(QUILT_EDGE_NODE / "src"))
    return __import__("quilt_node_identity")


def demo_cmd(args) -> int:
    import subprocess
    demo_path = QUILT_EDGE_NODE / "examples" / "full_lifecycle.py"
    if not demo_path.exists():
        raise SystemExit(f"demo not found: {demo_path}")
    return subprocess.call([sys.executable, str(demo_path)])


def identity_cmd(args) -> int:
    qi = _import_quilt_edge_module()
    serial = args.serial or qi.read_board_serial()
    rec = qi.bond(serial, args.ssid, args.bssid)
    print(f"Board serial: {serial}")
    print(f"Network SSID: {args.ssid}")
    print(f"Network salt: {rec.network_salt}")
    print(f"Node id:      {rec.node_id}")
    print(f"Short id:     {qi.short_id(rec.node_id)}")
    return 0


def provision_cmd(args) -> int:
    """Provision a board over USB-C (requires adb on PATH)."""
    import subprocess
    # The provisioner uses ADB; we just call it.
    prov_path = QUILT_EDGE_NODE / "src" / "quilt_usb_provision.py"
    if not prov_path.exists():
        raise SystemExit(f"provisioner not found: {prov_path}")
    cmd = [sys.executable, str(prov_path),
           "--ssid", args.ssid,
           "--password", args.password]
    if args.serial:
        cmd.extend(["--serial", args.serial])
    return subprocess.call(cmd)
