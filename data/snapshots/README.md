# Real-data snapshots

`demo.json` is intentionally **not included** in the initial downloadable project because this build environment could not retrieve live public API records. We will not fabricate a "real" snapshot.

On a machine with Internet access, run:

```powershell
uv run python scripts/collect_snapshot.py
```

That creates `demo.json` from real Remotive and Greenhouse public GET endpoints, records `collected_at`, and includes no CV or candidate data. The app visibly labels this mode **Dated Snapshot**, never live.

Review source terms before public redistribution. Every job card links its original source.
