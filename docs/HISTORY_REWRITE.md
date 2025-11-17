# Repository History Rewrite: `.mdt_dlls/` Purge

What I did
- Created a local mirror backup of the repository at `..\Thorlabs_MDT-backup-20251117143723.git`.
- Created a fresh working clone at `..\Thorlabs_MDT-clean-20251117144046` and used `git-filter-repo` to remove the `.mdt_dlls/` directory from every commit.
- Garbage-collected the cleaned clone and force-pushed the rewritten history to `origin` (the remote `main` branch was updated).

Why this was done
- The `.mdt_dlls/` directory contains vendor binaries that should not be published in the repository. Removing them from history prevents accidental redistribution and reduces repo size.

Important consequences
- The repository history has been rewritten and `origin` was force-updated. This changes commit hashes and requires collaborators to take recovery steps.

Recommended actions for collaborators (choose one)

- Easiest / safest: reclone the repository fresh

```powershell
# remove your old clone (or keep it as a local archive), then:
git clone https://github.com/JovanMarkov96/Thorlabs_MDT.git
```

- If you cannot reclone and have local unpushed work

1. Save your unpushed commits/branches by creating a local branch:

```powershell
git checkout -b my-local-save
```

2. Fetch the new origin and reset your local main to match origin (this will discard local commits on `main`):

```powershell
git fetch origin
git checkout main
git reset --hard origin/main
```

3. Re-apply your saved commits if needed (cherry-pick, rebase, or apply patches):

```powershell
git cherry-pick <commit-hash-from-my-local-save>
```

Notes and support
- I created a mirror backup (bare) at `..\Thorlabs_MDT-backup-20251117143723.git` in case we need to recover the original history locally.
- If you want, I can prepare a short script or step-by-step for your collaborators to run, or create a GitHub Issue announcing the rewrite.

If you want me to also update `README.md` with a short note about the purge, tell me and I will add it.
