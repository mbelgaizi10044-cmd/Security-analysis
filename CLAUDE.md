# ACIS Security Analysis — sync rules

This repository mirrors the live platform "ACIS Security Analysis" (التحليل الأمني), a Claude artifact:
https://claude.ai/artifact/DsU49JCHQELFXtbgarfNb4

**The owner's standing instruction: every update to the platform must reach GitHub too — code and data, every time, nothing missing.**

## When you change the platform (code)

1. Make the change and publish it to the artifact above (same URL; keep the capabilities in `artifact-capabilities.json`, adding new database rules there when a new collection is introduced).
2. In the same piece of work, run the sync below so `platform/index.html`, `index.html` and `data/snapshot.json` match what was just published.
3. If the change touches anything `tools/build_github.py` relies on (the lines it replaces), update the script in the same commit so the build still passes.
4. Commit and push to `main`.

## Sync (data and code)

```
1. Artifact read  url=https://claude.ai/artifact/DsU49JCHQELFXtbgarfNb4  path=index.html  → copy to platform/index.html
2. ArtifactData list (limit 1000, out_dir EXPORT) for each collection:
   news, countries, briefs, forecasts, weeks, weekparts, meta, reviews
3. python3 tools/build_github.py --export EXPORT --assets
   → for each id printed: Artifact read url=… path=<id> out_dir=assets/files
4. python3 tools/build_github.py --export EXPORT
5. git add -A; commit only if something changed; push to main
```

`build_github.py` refuses to run on an empty news export, and keeps `data/snapshot.json` byte-identical when the data did not change, so a sync with no news creates no commit.

## Never

- Never write to the artifact's database or delete anything from it during a sync — the sync only reads.
- Never commit the 29LT Bukra font files while the repository is public (they are licensed).
- Never put tokens, keys or credentials in any file.
