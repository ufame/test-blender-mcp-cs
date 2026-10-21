"""Build the final shrek.qc from the decompiled arctic.qc.

Keeps every original sequence block, source SMD, FPS, loop flag, blend and
event exactly as decompiled.  The only sequence edits are the decompiler's
`_1`/`_2` suffixes on the duplicated dual-pistol names: the baseline MDL has
both blocks under the same public name, in the same order.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(r"C:\AI\goldsrc\shrek_player")
REFERENCE_QC = ROOT / "source" / "reference" / "arctic.qc"
BASELINE_JSON = ROOT / "reports" / "baseline_inspect.json"
OUTPUT_QC = ROOT / "source" / "shrek.qc"

DUAL_BASES = {
    "crouch_aim_dualpistols",
    "crouch_shoot_dualpistols",
    "crouch_shoot2_dualpistols",
    "crouch_reload_dualpistols",
    "ref_aim_dualpistols",
    "ref_shoot_dualpistols",
    "ref_shoot2_dualpistols",
    "ref_reload_dualpistols",
}


def public_sequence_name(name: str) -> str:
    match = re.fullmatch(r"(.+)_[12]", name)
    if match and match.group(1) in DUAL_BASES:
        return match.group(1)
    return name


def main() -> None:
    baseline = json.loads(BASELINE_JSON.read_text(encoding="utf-8"))
    bone_names = [bone["name"] for bone in baseline["bones"]]
    expected_sequences = [sequence["name"] for sequence in baseline["sequences"]]

    text = REFERENCE_QC.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Drop the decompiled backpack bodygroup block.
    filtered: list[str] = []
    skipping = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('$bodygroup "backpack"'):
            skipping = True
            continue
        if skipping:
            if stripped == "}":
                skipping = False
            continue
        filtered.append(line)
    lines = filtered

    out: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("$modelname "):
            out.append('$modelname "player/shrek/shrek.mdl"')
        elif stripped.startswith("$cd "):
            out.append('$cd "anims"')
        elif stripped.startswith("$cdtexture "):
            out.append('$cdtexture "../textures"')
        elif stripped.startswith("$body "):
            out.append('$body "body" "shrek_body"')
        elif stripped.startswith("$sequence "):
            match = re.match(r'(\$sequence\s+")([^"]+)(".*)$', line)
            if match:
                name = public_sequence_name(match.group(2))
                line = match.group(1) + name + match.group(3)
            out.append(line)
        else:
            out.append(line)

    # Insert bbox/cbox/eye and the exact 21 baseline hitboxes after the body.
    body_index = next(index for index, line in enumerate(out)
                      if line.strip().startswith('$body "body"'))
    hitbox_lines = [
        "",
        "$bbox -16 -16 0 16 16 72",
        "$cbox 0 0 0 0 0 0",
        "$eyeposition 0 0 64",
        "",
    ]
    for hitbox in baseline["hitboxes"]:
        bone = bone_names[hitbox["bone"]]
        values = [*hitbox["min"], *hitbox["max"]]
        hitbox_lines.append(
            f'$hbox {hitbox["group"]} "{bone}" '
            + " ".join(f"{float(value):.6f}" for value in values)
        )
    hitbox_lines.append("")
    out[body_index + 1:body_index + 1] = hitbox_lines

    result = "\n".join(out).rstrip() + "\n"
    OUTPUT_QC.write_text(result, encoding="utf-8", newline="\n")

    written_sequences = re.findall(r'^\$sequence "([^"]+)"', result, re.MULTILINE)
    print("wrote", OUTPUT_QC)
    print("sequences", len(written_sequences))
    print("names match baseline order:", written_sequences == expected_sequences)
    if written_sequences != expected_sequences:
        for index, (actual, expected) in enumerate(zip(written_sequences, expected_sequences)):
            if actual != expected:
                print("first mismatch", index, repr(actual), "!=", repr(expected))
                break
        print("extra/missing", len(written_sequences), len(expected_sequences))
    print("hitboxes", len(baseline["hitboxes"]))


if __name__ == "__main__":
    main()
