# Shrek Player - Final Validation

**Deliverable:** `C:\AI\goldsrc\shrek_player\models\player\shrek\shrek.mdl`

**SHA-256:** `5287261F8E5222EA3ABF565E2318A51F11CECEA4D79A96EC5B20A53AD2BF0ED6`

**Validation date:** 2026-10-21  
**Blender:** 5.2.2 LTS  
**Toolchain:** GoldSrc Model Toolchain 1.4.3, bundled StudioMDL SC (Dec 21 2020)  
**Compiler target:** GoldSrc MDL v10 / Counter-Strike 1.6 player model

---

## 1. Result

The Shrek player model is complete and passes every build, inspection, compatibility and
round-trip check that was applied. The shipped file is a valid GoldSrc MDL v10 with the
original CS 1.6 arctic skeleton, all 111 original sequence names and all 21 original
hitboxes. It renders correctly in a real CS 1.6 client. Interactive movement animation
was not driven reliably during the in-game test and is therefore marked **not verified**
rather than passed.

| Stage | Result |
|---|---|
| StudioMDL compile | PASS |
| Independent MDL inspection | PASS |
| Strict player compatibility | PASS (0 issues) |
| Bone / sequence / hitbox equality | PASS |
| Rigid-weight audit | PASS |
| Animation channel comparison | PASS (within 1/256 unit, < 0.0001 rad) |
| Blender MDL round-trip import | PASS |
| CS 1.6 in-game load/render | PASS |
| CS 1.6 interactive animation | NOT VERIFIED |

---

## 2. Shipped artifact

| Property | Value |
|---|---|
| Path | `C:\AI\goldsrc\shrek_player\models\player\shrek\shrek.mdl` |
| Size | 2,451,200 bytes |
| Magic / version | `IDST`, version 10 |
| Internal name | `player/shrek/shrek.mdl` |
| SHA-256 | `5287261F8E5222EA3ABF565E2318A51F11CECEA4D79A96EC5B20A53AD2BF0ED6` |
| Texture | `C:\AI\goldsrc\shrek_player\models\player\shrek\shrek.bmp` (263,222 bytes) |
| Texture SHA-256 | `5FCA961F404EE04044C92DAB67B1B6FC2D0A11AC62A94656387D890DBEA77575` |
| QC | `C:\AI\goldsrc\shrek_player\source\shrek_final.qc` (33,286 bytes) |
| QC SHA-256 | `797C48B15B971633A2B6851B309E71377B738CF51DA573280615802F73EF033D` |
| Body SMD | `C:\AI\goldsrc\shrek_player\source\anims\shrek_body.smd` (800,854 bytes) |
| Body SMD SHA-256 | `DB9EFED83ACE1A8855B8CDEF3B82259F96E298735129F5F666F08A5984018F6C` |
| Blender scene | `C:\AI\goldsrc\shrek_player\shrek_player.blend` (2,324,018 bytes) |
| Blender scene SHA-256 | `8427A1C067762993C5B5731BDC8D4ADE32EA2D291399B78E71A4195417AD5D6E` |
| Contact sheet | `C:\AI\goldsrc\shrek_player\renders\final_contact_sheet.png` |
| Contact sheet SHA-256 | `457F46D35DDCD9914C6DBEADB7DE3172F33A37BD53693EB6C0723BE6BFDF8DF0` |

---

## 3. Source basis

The source was the supplied decompiled CS 1.6 player model in
`E:\goldsrc\decomp_models`:

- `arctic.mdl` - 2,395,944 bytes, 55 bones, 111 sequences, 21 hitboxes, 2 attachments,
  2 bodyparts, 2 textures.
- `arctic.qc` - original QC with the 111 sequence definitions and 21 `$hbox` lines.
- `arctic.smd` - reference body mesh, 721 triangles / 2,163 vertices / 55 nodes.
- `ARTIC_Working1.BMP`, `Backpack1.BMP` - original textures (not used for Shrek).

The decompiled directory was never modified. Reference copies were written to
`source/reference/`, and 640 animation SMDs were copied into `source/anims/`.
The Shrek body SMD replaced only the body mesh; every animation file remains the
original arctic file.

This gives the model exactly the same gameplay skeleton and sequence layout as a
stock CS 1.6 player. No bone names, sequence names, sequence order, hitbox values,
attachment values or controller values were invented or reordered.

---

## 4. Geometry and texture

| Property | Value |
|---|---|
| Compiled vertices | 1,959 |
| Compiled normals | 1,346 |
| Triangles | 3,257 |
| Triangle strips | 465 |
| Vertex groups | 55 |
| Materials | 1 (`shrek_body_material`) |
| UV layers | 1 (`UVMap`) |
| Texture | `shrek.bmp`, 512 x 512, 8-bit indexed, 31 used colours |
| Texture file size | 263,222 bytes |
| Textures embedded in MDL | 1 |
| Bounding box | -16..16 x -16..16 x 0..72 |
| Eye position | 0, 0, 64 |
| Bodyparts | 1 (`body`) |
| Model budget | under the player profile limits (2,048 verts / normals, 20,000 tris) |

The mesh is a single continuous skinned body: green head, trumpet ears, heavy brow,
large nose, wide grin, thick green neck, cream tunic, open brown vest, brown trousers
and simple brown shoes. The atlas is deliberately flat-coloured with stitched seams,
cloth joins and dirt marks; quantization removed smooth gradients that would band in
the indexed palette. There are no PBR maps.

### Rigid weights

A direct audit of the delivered Blender mesh reports:

- 1,959 vertices, all weighted;
- 0 vertices with more than one bone influence;
- 0 vertices with a weight other than 1.0;
- 55 vertex groups, one per bone.

Joint spheres at shoulders, elbows, wrists, hips, knees and ankles are weighted to the
corresponding helper bones so rigid seams stay covered through the original animations.
The neck shell is weighted to `-- Neck smooth`; the chin/lower lip is weighted to `Bone01`.

A small number of triangles are hidden inside the body at unused helper bone heads so
StudioMDL retains the exact 55-bone skeleton instead of pruning `Bomb` or unused helpers.
These triangles are not visible and do not affect the silhouette.

---

## 5. Skeleton (55 bones, exact arctic order)

Index, bone and parent index as read back from the shipped MDL:

```text
00. Bip01  (parent -1)
01. Bip01 Pelvis  (parent 0)
02. Bip01 Spine  (parent 1)
03. Bip01 Spine1  (parent 2)
04. Bip01 Spine2  (parent 3)
05. Bip01 Spine3  (parent 4)
06. Bip01 Neck  (parent 5)
07. Bip01 Head  (parent 6)
08. Bone01  (parent 7)
09. Bip01 L Clavicle  (parent 6)
10. Bip01 L UpperArm  (parent 9)
11. Bip01 L Forearm  (parent 10)
12. Bip01 L Hand  (parent 11)
13. Bip01 L Finger0  (parent 12)
14. Bip01 L Finger01  (parent 13)
15. Bip01 L Finger1  (parent 12)
16. Bip01 L Finger11  (parent 15)
17. -- L knuckle  (parent 15)
18. -- L Forearm twist  (parent 11)
19. -- L wrist  (parent 11)
20. -- L Elbow  (parent 10)
21. -- L bicep twist  (parent 10)
22. -- L shoulder outside  (parent 9)
23. -- L Shoulder inside  (parent 9)
24. Bip01 R Clavicle  (parent 6)
25. Bip01 R UpperArm  (parent 24)
26. Bip01 R Forearm  (parent 25)
27. Bip01 R Hand  (parent 26)
28. Bip01 R Finger0  (parent 27)
29. Bip01 R Finger01  (parent 28)
30. Bip01 R Finger1  (parent 27)
31. Bip01 R Finger11  (parent 30)
32. -- R knuckle  (parent 30)
33. -- R wrist  (parent 26)
34. -- R forearm twist  (parent 26)
35. -- R Elbow  (parent 25)
36. -- R bicep twist  (parent 25)
37. -- R Shoulder inside  (parent 24)
38. -- R shoulder outside  (parent 24)
39. -- Neck smooth  (parent 5)
40. -- R Butt  (parent 1)
41. -- L butt  (parent 1)
42. Bip01 L Thigh  (parent 1)
43. Bip01 L Calf  (parent 42)
44. Bip01 L Foot  (parent 43)
45. Bip01 L Toe0  (parent 44)
46. -- L ankle  (parent 43)
47. -- L Knee  (parent 42)
48. Bip01 R Thigh  (parent 1)
49. Bip01 R Calf  (parent 48)
50. Bip01 R Foot  (parent 49)
51. Bip01 R Toe0  (parent 50)
52. -- R Ankle  (parent 49)
53. -- R Knee  (parent 48)
54. Bomb  (parent 4)
```

The ordered name list is identical to the baseline. The MDL header reports 55 bones.

---

## 6. Sequences (111, exact arctic order)

The MDL contains **111 sequences / 3,752 frames**.
Names and order match the baseline exactly, including the eight duplicated dual-pistol
names at positions 23-30 and 66-73. Duplicate names are legal in GoldSrc and were kept
because the source model contains them; the source SMD filenames use `_1`/`_2` suffixes
only to keep the build folder unambiguous.

The full sequence manifest is in Appendix A. Core gameplay sequences include:

| Sequence | FPS | Frames | Loop | Blends |
|---|---:|---:|:---:|---:|
| `idle1` | 15 | 61 | true | 1 |
| `walk` | 30 | 33 | true | 1 |
| `run` | 60 | 37 | true | 1 |
| `crouch_idle` | 10 | 31 | true | 1 |
| `crouchrun` | 30 | 31 | true | 1 |
| `jump` | 36 | 61 | false | 1 |
| `longjump` | 36 | 61 | false | 1 |
| `ref_aim_rifle` | 30 | 2 | true | 9 |
| `ref_shoot_rifle` | 20 | 6 | false | 9 |
| `ref_reload_rifle` | 30 | 91 | false | 1 |
| `death1` | 30 | 36 | false | 1 |
| `death2` | 30 | 41 | false | 1 |
| `death3` | 30 | 106 | false | 1 |
| `crouch_die` | 30 | 31 | false | 1 |

The delivered Blender scene keeps 11 representative actions: `idle1`, `walk`, `run`,
`crouch_idle`, `jump`, `ref_shoot_rifle_blend4`, `ref_reload_rifle`, `death1`,
`crouch_shoot_carbine_blend4`, `crouch_reload_carbine`, `ref_aim_rifle_blend4`.
The MDL itself contains all 111 sequences.

---

## 7. Hitboxes, attachments, bodyparts and controller

All 21 hitboxes match the baseline byte-for-byte in bone-local framing:

| # | Group | Bone | Min | Max |
|---:|---:|---|---|---|
| 1 | 3 | `Bip01 Pelvis` | -4.6900, -4.4400, -6.7500 | 4.0000, 5.5600, 6.7500 |
| 2 | 6 | `Bip01 L Thigh` | 2.6600, -3.6900, -3.0900 | 18.1600, 4.8800, 3.3100 |
| 3 | 6 | `Bip01 L Calf` | 0.3800, -3.9700, -2.8400 | 17.6000, 4.0000, 2.9400 |
| 4 | 6 | `Bip01 L Foot` | 0.8500, -3.2400, -2.6400 | 5.7300, 8.5300, 3.1700 |
| 5 | 7 | `Bip01 R Thigh` | 2.4700, -3.6900, -3.1600 | 18.1300, 4.8800, 3.3800 |
| 6 | 7 | `Bip01 R Calf` | 0.3100, -3.9700, -2.8400 | 17.6000, 3.9400, 2.9700 |
| 7 | 7 | `Bip01 R Foot` | 0.8500, -3.2400, -2.6400 | 5.7300, 8.5300, 3.1700 |
| 8 | 3 | `Bip01 Spine1` | -3.2500, -5.5000, -5.5000 | 4.8300, 5.5000, 5.5000 |
| 9 | 2 | `Bip01 Spine2` | -0.0600, -5.5300, -7.5900 | 8.0000, 7.0000, 7.5900 |
| 10 | 2 | `Bip01 Spine3` | -2.2500, -6.8100, -6.3100 | 6.5000, 5.0900, 6.3100 |
| 11 | 2 | `Bip01 Neck` | -3.1100, -1.5000, -3.0000 | 2.0500, 3.5000, 3.0000 |
| 12 | 1 | `Bip01 Head` | -0.3300, -4.5000, -2.5000 | 8.0000, 4.5000, 2.5000 |
| 13 | 4 | `Bip01 L Clavicle` | 0.9400, -2.8800, -4.1300 | 5.4400, 4.2800, 3.5000 |
| 14 | 4 | `Bip01 L UpperArm` | -2.1600, -2.3400, -2.5600 | 11.5600, 3.4100, 2.3800 |
| 15 | 4 | `Bip01 L Forearm` | 0.5900, -1.8100, -2.1900 | 10.7500, 2.8400, 2.4100 |
| 16 | 4 | `Bip01 L Hand` | -0.1322, -1.9030, -2.2385 | 4.8629, 2.0782, 2.3698 |
| 17 | 5 | `Bip01 R Clavicle` | 1.3800, -2.8400, -3.5600 | 5.6900, 4.3100, 4.3100 |
| 18 | 5 | `Bip01 R UpperArm` | -1.8800, -2.4700, -2.1600 | 11.8100, 3.2800, 2.8100 |
| 19 | 5 | `Bip01 R Forearm` | 0.4400, -1.9700, -2.3400 | 10.5900, 2.7200, 2.2200 |
| 20 | 5 | `Bip01 R Hand` | -0.1322, -1.9030, -2.2385 | 4.8629, 2.0782, 2.3698 |
| 21 | 8 | `Bip01 L Hand` | -16.1000, -6.5000, -19.0000 | 10.6000, 1.5000, 33.0000 |

Attachments (exact baseline values):

| # | Bone | Origin |
|---:|---|---|
| 0 | `Bip01 R Hand` | 10.855000, -0.416715, 1.870680 |
| 1 | `Bip01 L Hand` | 10.855000, -0.416715, 1.870680 |

Controller: `$controller 4 "Bone01" ZR 0.000000 30.000000`, identical to the baseline.

The model has one bodypart, `body`, with one model `shrek_body` and one mesh.
The baseline backpack bodygroup is intentionally omitted; strict player compatibility
passed with that layout.

---

## 8. Compile

The final compile used the Toolchain's bundled StudioMDL and a flat staging folder,
`work/final/build/`, containing the QC, `shrek_body.smd`, 640 animation SMDs and
`shrek.bmp`. The QC used for the shipped build is `source/shrek_final.qc`.

StudioMDL output:

```text
StudioMDL SC (Dec 21 2020 23:14:21)
Studio Model Compiler for Sven Co-op

writing player/shrek/shrek.mdl:
bones       7276 bytes (55)
sequences 2103324 bytes (3752 frames) [2:20]
vertices   42968 bytes (1959 vertices, 1346 normals)
mesh       34448 bytes (3257 tris, 465 strips)
models     77604 bytes
textures  262996 bytes
total     2451200 bytes
```

The full log is `reports/final_compile.log`. StudioMDL prints one non-fatal note:
`$cliptotextures` is ignored by this compiler version. The directive is inherited from
the source QC and has no effect on the shipped model.

`compile_contract` was not used for the final build. The Toolchain contract validator
rejects the source model's duplicate sequence names and its loop audit false-fails the
root-motion `walk` / `run` / `crouchrun` endpoints. The source data is valid for
StudioMDL and was compiled through the Toolchain SMD exporter and bundled compiler,
then validated with the Toolchain inspection and compatibility APIs.

---

## 9. Independent inspection of the shipped file

`reports/final_inspect_delivery.json` was produced by inspecting
`models/player/shrek/shrek.mdl`, not the build copy. Key header fields:

| Field | Value |
|---|---|
| Magic | `IDST` |
| Version | 10 |
| Length | 2,451,200 bytes |
| Bone count | 55 |
| Hitbox count | 21 |
| Sequence count | 111 |
| Sequence groups | 1 |
| Texture count | 1 |
| Bodypart count | 1 |
| Attachment count | 2 |
| Controller count | 1 |
| Sound count | 0 |

The mesh record reports 1,959 vertices, 1,346 normals and one mesh. The texture record
reports a 512 x 512 `shrek.bmp`. Skin family count is 1. The ordered bone list, hitbox
list and attachment list are identical to the baseline; the sequence list differs only
in the three `linear_movement` metadata values described below.

---

## 10. Strict player compatibility

`validate_model_compatibility(candidate, baseline, "player")` returned:

- **status: pass**
- issues: 0
- baseline sequences: 111, candidate: 111
- baseline bones: 55, candidate: 55
- appended sequences: []

The only differences reported are `linear_movement` values:

| Sequence | Baseline | Candidate | Delta |
|---|---:|---:|---:|
| `walk` | 64.000000 | 62.060608 | -1.939392 (-3.03%) |
| `run` | 150.000015 | 145.945953 | -4.054062 (-2.70%) |
| `crouchrun` | 75.000000 | 72.580643 | -2.419357 (-3.23%) |

These values are derived from the same root-motion animation and differ only because
the Toolchain exporter re-quantizes the root translation. The engine still gets valid
`LX` movement for walk/run/crouchrun and the compatibility validator treats them as
metadata differences, not errors.

---

## 11. Animation equality vs official arctic

`reports/animation_diff_vs_official.json` compares every animation channel of all 111
sequences against the official CS 1.6 arctic MDL at
`D:\Goldsrc\hlds-server\cstrike\models\player\arctic\arctic.mdl`.

- sequences compared: **111**
- total frames: **3,752**
- maximum position delta: **0.003906369 units** (1/256 unit quantization)
- maximum rotation delta: **0.0000962897 rad** (about 0.005517 degrees)
- worst position sequence: `dummy` at 0.003906369
- worst rotation sequence: `ref_shoot2_dualpistols` at 0.0000962897 rad
- sequences exceeding 0.004 units or 0.0001 rad: **0**

Every sequence is within one 1/256-unit position quantum and below 0.0001 radians of
rotation error. This confirms that the original animation data is preserved, not
re-authored.

---

## 12. Round-trip import

The shipped MDL was imported into a separate headless Blender 5.2.2 session with the
Toolchain MDL importer (`source/verify_roundtrip.py`). The import produced:

| Property | Result |
|---|---|
| Armature | `shrek_ARM` |
| Bones | 55 |
| Mesh | `shrek_body_0_shrek_body` |
| Vertices | 1,959 |
| Polygons / triangles | 3,257 / 3,257 |
| Vertex groups | 55 |
| UV layers | UVMap |
| Actions generated | 639 |
| Image | shrek_shrek.bmp_IMAGE 512 x 512, packed=True |

The importer sanitizes spaces in bone names to underscores, as expected; all 55 names
are present and unique. The 639 actions come from the importer expanding the 9-way
blended sequences into individual `blend0`..`blend8` actions plus the single-track
sequences. The geometry and texture round-trip without loss.

Raw evidence: `reports/final_roundtrip_delivery.json` and `reports/final_roundtrip.log`.

---

## 13. CS 1.6 in-game test

Test client: `E:\CS 1.6 GoldClient\hl.exe` (GoldSrc / Counter-Strike 1.6).

Method: all 9 standard `cstrike` and all 11 `cstrike_hd` team player MDLs were replaced
temporarily with the Shrek MDL, renamed to each team name. The client was launched on
`de_dust2` in a window with `+thirdperson` and camera cvars. Screenshots were captured
from front, side and back camera angles.

**Confirmed in the real engine:** the model loads, the embedded texture renders, and
Shrek is visible in third person from multiple angles. See:

- `renders/cs_ingame_front_crop.png`
- `renders/cs_ingame_side_crop.png`
- `renders/cs_ingame_back_crop.png`

**Not confirmed:** interactive movement, weapon poses and death animation playback.
Synthetic keyboard/mouse injection could not reliably dismiss the CS menu or drive the
player, so the test proves engine load/render but not interactive animation. No claim of
in-game animation verification is made.

**Client restored:** the 9 standard and 11 HD files were copied back from
`work/client_backup/` and all 20 restored files match their backups by SHA-256. No Shrek
files remain in the client's player folders.

---

## 14. Visual evidence

The final contact sheet is `renders/final_contact_sheet.png` and contains:

- Blender previews of `idle1`, `walk`, `run`, `crouch_idle`, `jump`, rifle shoot blend,
  rifle reload and `death1`;
- three CS 1.6 in-game captures (front, side, back);
- the 512 x 512 indexed diffuse atlas.

Baseline comparison renders `renders/baseline_arctic_idle_front.png` and
`renders/baseline_arctic_walk.png` show the original arctic body under the same
actions. The Shrek mesh follows the same skeleton pose, including the base
T-pose-ish arm placement in walk/run. The visual check found no missing limbs,
inverted normals, detached parts or texture seams that would indicate a broken
skinning/export step.

The Blender scene stores a preview camera, three lights, a floor and a hidden
`Reference` collection containing the original arctic body and backpack meshes.
The armature object carries the GoldSrc root-rest compensation
(-90 degrees Z, location 0.234, -2.252, 38.192) so imported MDL actions preview
correctly. That object transform is a Blender preview aid and is not baked into the
compiled MDL.

---

## 15. Reproducibility

| Item | Path |
|---|---|
| Build staging | `work/final/build/` (QC + 641 SMDs + BMP) |
| Modeling source | `work/modeling_scene.blend`, `source/shrek_player_source.blend` |
| Mesh builder | `source/build_shrek.py` |
| QC generator | `source/make_qc.py` |
| Texture generator | `source/make_texture.py` |
| Body SMD | `source/anims/shrek_body.smd` |
| Final QC | `source/shrek_final.qc` |
| Shipped model | `models/player/shrek/shrek.mdl` |

The body SMD must be exported in the reference arctic node order, not Blender armature
order; otherwise animation bone indices bind incorrectly. The delivered SMD already uses
the correct order.

---

## 16. Checksums

Full manifest: `reports/checksums.sha256`.

| File | SHA-256 |
|---|---|
| `models/player/shrek/shrek.mdl` | `5287261F8E5222EA3ABF565E2318A51F11CECEA4D79A96EC5B20A53AD2BF0ED6` |
| `models/player/shrek/shrek.bmp` | `5FCA961F404EE04044C92DAB67B1B6FC2D0A11AC62A94656387D890DBEA77575` |
| `shrek_player.blend` | `8427A1C067762993C5B5731BDC8D4ADE32EA2D291399B78E71A4195417AD5D6E` |
| `source/shrek_final.qc` | `797C48B15B971633A2B6851B309E71377B738CF51DA573280615802F73EF033D` |
| `source/anims/shrek_body.smd` | `DB9EFED83ACE1A8855B8CDEF3B82259F96E298735129F5F666F08A5984018F6C` |
| `textures/shrek_atlas.png` | `9BB4F942C6428024F8F6244061700B09015FDD6D039191A81CA11283859E7AA5` |
| `renders/final_contact_sheet.png` | `457F46D35DDCD9914C6DBEADB7DE3172F33A37BD53693EB6C0723BE6BFDF8DF0` |

---

## 17. CT/T installation

The tested method is client-side replacement of the team player models. Back up
each file before overwriting it.

1. Copy `models/player/shrek/shrek.mdl` over the CT model you use, for example
   `cstrike/models/player/urban/urban.mdl`.
2. Copy `models/player/shrek/shrek.bmp` beside it as
   `cstrike/models/player/urban/shrek.bmp`.
3. For the T side, do the same with `terror/terror.mdl`.
4. To replace every stock team selection, repeat for CT (`urban`, `sas`, `gign`,
   `gsg9`), T (`terror`, `leet`, `arctic`, `guerilla`) and VIP (`vip`).
5. If the client has HD player models, repeat under
   `cstrike_hd/models/player/<team>/<team>.mdl`.

The compiled MDL carries its texture internally, so renaming the MDL to a team
name works; keep `shrek.bmp` in the folder as an external fallback. To use the
intact `shrek` folder instead, install it at
`cstrike/models/player/shrek/` and set the model with an AMX Mod X/CSX plugin via
`cs_set_user_model(id, "shrek")`. The plugin route was not part of the in-game
test; the replacement method was the one verified.

Uninstall by restoring the backed-up team MDLs and removing the extra
`shrek.bmp` copies. Full commands and rollback paths are in `README.md`.

---

## Appendix A - all 111 sequences in order

Format: index, public name, FPS, frame count, loop flag, blend count.

```text
001. dummy | 24 fps | 61 frames | loop=true | blends=1
002. idle1 | 15 fps | 61 frames | loop=true | blends=1
003. crouch_idle | 10 fps | 31 frames | loop=true | blends=1
004. walk | 30 fps | 33 frames | loop=true | blends=1
005. run | 60 fps | 37 frames | loop=true | blends=1
006. crouchrun | 30 fps | 31 frames | loop=true | blends=1
007. jump | 36 fps | 61 frames | loop=false | blends=1
008. longjump | 36 fps | 61 frames | loop=false | blends=1
009. swim | 30 fps | 51 frames | loop=true | blends=1
010. treadwater | 24 fps | 61 frames | loop=true | blends=1
011. crouch_aim_carbine | 30 fps | 2 frames | loop=true | blends=9
012. crouch_shoot_carbine | 15 fps | 5 frames | loop=false | blends=9
013. crouch_reload_carbine | 30 fps | 61 frames | loop=false | blends=1
014. ref_aim_carbine | 30 fps | 2 frames | loop=true | blends=9
015. ref_shoot_carbine | 15 fps | 5 frames | loop=false | blends=9
016. ref_reload_carbine | 30 fps | 61 frames | loop=false | blends=1
017. crouch_aim_onehanded | 30 fps | 2 frames | loop=true | blends=9
018. crouch_shoot_onehanded | 15 fps | 7 frames | loop=false | blends=9
019. crouch_reload_onehanded | 30 fps | 61 frames | loop=false | blends=1
020. ref_aim_onehanded | 30 fps | 2 frames | loop=true | blends=9
021. ref_shoot_onehanded | 15 fps | 7 frames | loop=false | blends=9
022. ref_reload_onehanded | 30 fps | 61 frames | loop=false | blends=1
023. crouch_aim_dualpistols | 10 fps | 31 frames | loop=true | blends=9
024. crouch_shoot_dualpistols | 30 fps | 31 frames | loop=false | blends=9
025. crouch_shoot2_dualpistols | 30 fps | 31 frames | loop=false | blends=9
026. crouch_reload_dualpistols | 30 fps | 71 frames | loop=false | blends=1
027. ref_aim_dualpistols | 10 fps | 31 frames | loop=true | blends=9
028. ref_shoot_dualpistols | 30 fps | 31 frames | loop=false | blends=9
029. ref_shoot2_dualpistols | 30 fps | 31 frames | loop=false | blends=9
030. ref_reload_dualpistols | 30 fps | 71 frames | loop=false | blends=1
031. crouch_aim_rifle | 30 fps | 2 frames | loop=true | blends=9
032. crouch_shoot_rifle | 20 fps | 6 frames | loop=false | blends=9
033. crouch_reload_rifle | 30 fps | 91 frames | loop=false | blends=1
034. ref_aim_rifle | 30 fps | 2 frames | loop=true | blends=9
035. ref_shoot_rifle | 20 fps | 6 frames | loop=false | blends=9
036. ref_reload_rifle | 30 fps | 91 frames | loop=false | blends=1
037. crouch_aim_mp5 | 30 fps | 2 frames | loop=true | blends=9
038. crouch_shoot_mp5 | 15 fps | 5 frames | loop=false | blends=9
039. crouch_reload_mp5 | 30 fps | 46 frames | loop=false | blends=1
040. ref_aim_mp5 | 30 fps | 2 frames | loop=true | blends=9
041. ref_shoot_mp5 | 15 fps | 5 frames | loop=false | blends=9
042. ref_reload_mp5 | 30 fps | 46 frames | loop=false | blends=1
043. crouch_aim_shotgun | 30 fps | 2 frames | loop=true | blends=9
044. crouch_shoot_shotgun | 30 fps | 31 frames | loop=false | blends=9
045. crouch_reload_shotgun | 30 fps | 76 frames | loop=false | blends=1
046. ref_aim_shotgun | 30 fps | 2 frames | loop=true | blends=9
047. ref_shoot_shotgun | 30 fps | 31 frames | loop=false | blends=9
048. ref_reload_shotgun | 30 fps | 76 frames | loop=false | blends=1
049. crouch_aim_m249 | 10 fps | 2 frames | loop=true | blends=9
050. crouch_shoot_m249 | 30 fps | 6 frames | loop=true | blends=9
051. crouch_reload_m249 | 30 fps | 71 frames | loop=false | blends=1
052. ref_aim_m249 | 10 fps | 11 frames | loop=true | blends=9
053. ref_shoot_m249 | 30 fps | 6 frames | loop=true | blends=9
054. ref_reload_m249 | 30 fps | 71 frames | loop=false | blends=1
055. I_am_a_stupid_placeholder | 30 fps | 2 frames | loop=true | blends=1
056. so_am_I | 30 fps | 31 frames | loop=false | blends=1
057. ref_aim_grenade | 20 fps | 31 frames | loop=true | blends=9
058. ref_shoot_grenade | 45 fps | 31 frames | loop=false | blends=9
059. crouch_aim_grenade | 20 fps | 31 frames | loop=true | blends=9
060. crouch_shoot_grenade | 45 fps | 31 frames | loop=false | blends=9
061. crouch_aim_c4 | 30 fps | 2 frames | loop=true | blends=9
062. crouch_shoot_c4 | 30 fps | 121 frames | loop=false | blends=1
063. ref_aim_c4 | 30 fps | 2 frames | loop=true | blends=9
064. ref_shoot_c4 | 30 fps | 151 frames | loop=false | blends=1
065. ref_reload_c4 | 30 fps | 31 frames | loop=false | blends=1
066. crouch_aim_dualpistols | 10 fps | 31 frames | loop=true | blends=9
067. crouch_shoot_dualpistols | 30 fps | 31 frames | loop=false | blends=9
068. crouch_shoot2_dualpistols | 30 fps | 31 frames | loop=false | blends=9
069. crouch_reload_dualpistols | 30 fps | 71 frames | loop=false | blends=1
070. ref_aim_dualpistols | 10 fps | 31 frames | loop=true | blends=9
071. ref_shoot_dualpistols | 30 fps | 31 frames | loop=false | blends=9
072. ref_shoot2_dualpistols | 30 fps | 31 frames | loop=false | blends=9
073. ref_reload_dualpistols | 30 fps | 71 frames | loop=false | blends=1
074. crouch_aim_knife | 12 fps | 2 frames | loop=true | blends=9
075. crouch_shoot_knife | 30 fps | 41 frames | loop=false | blends=9
076. ref_aim_knife | 12 fps | 31 frames | loop=true | blends=9
077. ref_shoot_knife | 30 fps | 41 frames | loop=true | blends=9
078. crouch_aim_ak47 | 30 fps | 2 frames | loop=true | blends=9
079. crouch_shoot_ak47 | 30 fps | 5 frames | loop=false | blends=9
080. crouch_reload_ak47 | 30 fps | 91 frames | loop=false | blends=1
081. ref_aim_ak47 | 30 fps | 2 frames | loop=true | blends=9
082. ref_shoot_ak47 | 30 fps | 6 frames | loop=false | blends=9
083. ref_reload_ak47 | 30 fps | 91 frames | loop=false | blends=1
084. crouch_aim_shieldgren | 20 fps | 2 frames | loop=true | blends=9
085. crouch_shoot_shieldgren | 45 fps | 31 frames | loop=false | blends=9
086. ref_aim_shieldgren | 20 fps | 2 frames | loop=true | blends=9
087. ref_shoot_shieldgren | 45 fps | 31 frames | loop=false | blends=9
088. crouch_aim_shieldknife | 12 fps | 2 frames | loop=true | blends=9
089. crouch_shoot_shieldknife | 30 fps | 41 frames | loop=false | blends=9
090. ref_aim_shieldknife | 12 fps | 2 frames | loop=true | blends=9
091. ref_shoot_shieldknife | 30 fps | 41 frames | loop=true | blends=9
092. crouch_aim_shieldgun | 30 fps | 2 frames | loop=true | blends=9
093. crouch_shoot_shieldgun | 30 fps | 16 frames | loop=false | blends=9
094. crouch_reload_shieldgun | 30 fps | 61 frames | loop=false | blends=1
095. ref_aim_shieldgun | 30 fps | 2 frames | loop=true | blends=9
096. ref_shoot_shieldgun | 30 fps | 16 frames | loop=false | blends=9
097. ref_reload_shieldgun | 30 fps | 61 frames | loop=false | blends=1
098. crouch_aim_shielded | 20 fps | 2 frames | loop=true | blends=9
099. ref_aim_shielded | 20 fps | 2 frames | loop=true | blends=9
100. gut_flinch | 30 fps | 2 frames | loop=false | blends=9
101. head_flinch | 30 fps | 2 frames | loop=false | blends=9
102. death1 | 30 fps | 36 frames | loop=false | blends=1
103. death2 | 30 fps | 41 frames | loop=false | blends=1
104. death3 | 30 fps | 106 frames | loop=false | blends=1
105. head | 30 fps | 56 frames | loop=false | blends=1
106. gutshot | 30 fps | 54 frames | loop=false | blends=1
107. left | 30 fps | 66 frames | loop=false | blends=1
108. back | 30 fps | 56 frames | loop=false | blends=1
109. right | 30 fps | 66 frames | loop=false | blends=1
110. forward | 30 fps | 37 frames | loop=false | blends=1
111. crouch_die | 30 fps | 31 frames | loop=false | blends=1
```

## Appendix B - all 55 bones in order

```text
00. Bip01 (parent -1)
01. Bip01 Pelvis (parent 0)
02. Bip01 Spine (parent 1)
03. Bip01 Spine1 (parent 2)
04. Bip01 Spine2 (parent 3)
05. Bip01 Spine3 (parent 4)
06. Bip01 Neck (parent 5)
07. Bip01 Head (parent 6)
08. Bone01 (parent 7)
09. Bip01 L Clavicle (parent 6)
10. Bip01 L UpperArm (parent 9)
11. Bip01 L Forearm (parent 10)
12. Bip01 L Hand (parent 11)
13. Bip01 L Finger0 (parent 12)
14. Bip01 L Finger01 (parent 13)
15. Bip01 L Finger1 (parent 12)
16. Bip01 L Finger11 (parent 15)
17. -- L knuckle (parent 15)
18. -- L Forearm twist (parent 11)
19. -- L wrist (parent 11)
20. -- L Elbow (parent 10)
21. -- L bicep twist (parent 10)
22. -- L shoulder outside (parent 9)
23. -- L Shoulder inside (parent 9)
24. Bip01 R Clavicle (parent 6)
25. Bip01 R UpperArm (parent 24)
26. Bip01 R Forearm (parent 25)
27. Bip01 R Hand (parent 26)
28. Bip01 R Finger0 (parent 27)
29. Bip01 R Finger01 (parent 28)
30. Bip01 R Finger1 (parent 27)
31. Bip01 R Finger11 (parent 30)
32. -- R knuckle (parent 30)
33. -- R wrist (parent 26)
34. -- R forearm twist (parent 26)
35. -- R Elbow (parent 25)
36. -- R bicep twist (parent 25)
37. -- R Shoulder inside (parent 24)
38. -- R shoulder outside (parent 24)
39. -- Neck smooth (parent 5)
40. -- R Butt (parent 1)
41. -- L butt (parent 1)
42. Bip01 L Thigh (parent 1)
43. Bip01 L Calf (parent 42)
44. Bip01 L Foot (parent 43)
45. Bip01 L Toe0 (parent 44)
46. -- L ankle (parent 43)
47. -- L Knee (parent 42)
48. Bip01 R Thigh (parent 1)
49. Bip01 R Calf (parent 48)
50. Bip01 R Foot (parent 49)
51. Bip01 R Toe0 (parent 50)
52. -- R Ankle (parent 49)
53. -- R Knee (parent 48)
54. Bomb (parent 4)
```

## Appendix C - evidence index

| Evidence | File |
|---|---|
| StudioMDL output | `reports/final_compile.log` |
| Independent inspection | `reports/final_inspect_delivery.json` |
| Strict compatibility | `reports/final_compatibility_delivery.json` |
| Animation channel diff | `reports/animation_diff_vs_official.json` |
| Round-trip import | `reports/final_roundtrip_delivery.json`, `reports/final_roundtrip.log` |
| Checksums | `reports/checksums.sha256` |
| Contact sheet | `renders/final_contact_sheet.png` |
| In-game captures | `renders/cs_ingame_front_crop.png`, `renders/cs_ingame_side_crop.png`, `renders/cs_ingame_back_crop.png` |

