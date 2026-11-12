# Published source preservation

Relocation note: all paths below are relative to `agents/triage_agent/`, where
the source, snapshot, tests, and outputs were moved together. Snapshot bytes are
unchanged; historical publication evidence remains applicable.

## What was saved

At the historical checkpoint, AMS **0.1.17** was verified active and downloaded into:

`ams_snapshots/0.1.17/alert_triage/`

Agent: `d4ffbfc9-696f-4a5a-b174-75daaa1c993f`, ScaleGov staging,
tenant `6a1099f9e1ca37ee1216d8c3`. Source bundle file:
`0a858aca-e684-46e9-97cd-0961b04e7a6f` (also used by 0.1.16).
The action creating the additional 0.1.17 version is not established in the
available session history; source equality is independently checked.

At that checkpoint, the downloaded **14 application source/metadata files all matched** the editable
`plugins/alert_triage/` files byte-for-byte. Only local Python bytecode caches
are extra in the editable tree; they are not application source. No editable
file was overwritten. The empty fixture has no findings to restore. No duplicate
plugin was linked or added to the active plugin configuration.

| Saved file | SHA-256 |
|---|---|
| agent.py | `5f12a39b6978dd74dbe5b4d8e0acc93f2169ed43d1d13238485d76b5ba70b6a4` |
| context_contract.py | `5f845c4438e6bfa139af904564c8052998ea3955a896e8f0266c00d5e9e2e1e7` |
| contracts.py | `2da5eee0f76966abbde4fa01eb821c4c6fb7dd2c507d46f05e77a8f964521d78` |
| export.py | `9942fefcfdb2a40507b72d39209c33a859d47a8d982e08eeb23d36266c508050` |
| file_first.py | `d1a31f05d5d356886beb7364c430ff7a0eb9c4f8ab6f2fa92b4458efeb041fb2` |
| file_output.py | `9a802d2538fb5decb27338e251886e8bea4551da1e61f9c48319b35ae081e5cb` |
| graph.py | `22aa97ca2342413f70ba68a67cdc68553330187ce8637aba30472eb9711ec00e` |
| hosted.py | `cb49ba97faf0d25c0fba5d7baf4555f89c6bbc00559710486f0457c6fd18ce14` |
| manifest.json | `b28aa5c40c7984c7b466f571153539f06bb794c1c0aad2d1a6a92026eb583212` |
| model_compat.py | `83bae1e52440f1e1938932717798087c11bfd66e3632f806d90dfda98c718c5d` |
| persona.py | `cb3e2e2d2f7936febf4f825f7a0691af2f7c8eeb8c7f61f54f01c6ec75276478` |
| progress.py | `5b50069de720e5a9f8c08d5dde55f9e748a31eedd728a0f641dfcc60d66c424b` |
| requirements.txt | `9a43329cfdf9c37a75e6e383124fc698ffb703ef9a32ac303e193810e6215a8b` |
| triage.py | `9a62b3d85c606a82bdcbc0855d239938865ec0780d03e10d02d7294a4f5bd7a4` |

## Other local project material

**Current backup scope:** staging entry is now 0.1.24. The 0.1.17 snapshot below
is historical and does not match the current working implementation. Local
`releases/staging_0_1_24/` retains the prepared staging source/provenance, while
`plugins/alert_triage/` targets Dev. A fresh downloaded current-bundle comparison
is still outstanding. See [complete AMS inventory and gaps](../AMS_INVENTORY.md).
The original input bytes are preserved as `staging_input_verification.json`;
the former fixture filename is absent. Hash and size were rechecked during cleanup.

The CLI entry point, tests/edge fixtures, original findings fixture, diagnostic
pod, documentation and local output examples remain in this directory. They are
development material and are not all carried in the published pod bundle.
The README's offline example was executed successfully into outputs/example_stub:
17 findings, seven groups, 98 observations, seven explicitly stub contexts and
zero errors. Standard-library unittest run passed with the two SDK tests skipped;
the managed-runtime run passed all 32 without skips.
The original findings content hash remains
`6b205b4b32e8bb2807a3a98292ff8dd9b49183d2ef201b17175b22a201290a4a`.

This is a source backup, **not** a container/runtime filesystem dump. Third-party
dependencies, runtime-injected credentials, platform configuration, all historical
release archives and generated SGP output files are not included. No credentials
were exported. This workspace is not a Git repository; no commit was created.

## Repeat a download safely

With AMS access connected, choose a new destination rather than overwriting edits:

```sh
sling ams pull d4ffbfc9-696f-4a5a-b174-75daaa1c993f --version 0.1.17 -o ./ams_snapshots/0.1.17/alert_triage
```

The existing destination causes a refusal unless replacement is explicitly
requested. Do not add `--force` to preserve this snapshot. An exact semantic
version avoids accidentally pulling a later release. Plugin manifest version
`0.1` is local plugin metadata, not the AMS release semver.
