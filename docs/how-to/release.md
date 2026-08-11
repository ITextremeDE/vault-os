# Release Vault-OS

This procedure is for maintainers publishing an accepted version. A release is
not created merely because the working tree passes locally; publication,
tagging, and pushing require explicit authorization.

## Prepare the release

1. Confirm that `main` is clean and inspect every tracked and untracked change.
2. Fetch both configured remotes and confirm that local `main`, GitHub
   `origin/main`, and the Forgejo mirror are not unexpectedly divergent.
3. Review the complete diff for private vault content, credentials, personal
   paths, generated indexes, and unrelated changes.
4. Set `manifests/repository.json` to the intended Semantic Versioning release.
5. Move the accepted entries from `[Unreleased]` to a dated release section in
   `CHANGELOG.md`; leave an empty `[Unreleased]` section for later work.
6. Recalculate every changed package-source checksum in its owning manifest.
7. Confirm that the README status and dated validation evidence describe the
   release actually being published.

## Validate

Create the documented environment and run the complete acceptance suite:

```bash
.venv/bin/python -m unittest discover -s tests
.venv/bin/python scripts/check_portability.py
.venv/bin/python scripts/validate_portability_matrix.py
.venv/bin/python scripts/validate_manifests.py
git diff --check
```

Review the GitHub Actions acceptance result for the release commit. Record any
client that was not exercised; structural adapter tests are not a substitute
for an actual client run.

Also exercise the synchronized-device boundary in temporary vaults: install and
update a primary copy, transfer only files that the documented Obsidian Sync
profile carries, run `device-sync` on the secondary copy, and require a healthy
`doctor` result. Confirm that no hidden runtime directory had to be transferred.

## Publish

After explicit publication approval:

1. Commit only the reviewed release scope using the repository's Conventional
   Commit rules, for example `chore(release): prepare 0.1.0`.
2. Create one annotated tag matching the manifest version, for example
   `v0.1.0`.
3. Push the commit and tag to GitHub and verify the exact remote commit and tag.
4. Push the same commit and tag to Forgejo and verify it independently.
5. Create the GitHub release from the changelog section without adding
   unverified claims or private operational details.

Never force-push, reset, merge unexpected history, or publish when either
remote differs from the reviewed commit. Resolve divergence as a separate,
explicitly authorized task.

## Verify the published release

Clone the public tag into a fresh temporary directory, install its declared
dependencies, run the acceptance suite again, and perform one clean-vault
install followed by `doctor`. Confirm that the GitHub release, Git tag,
manifest version, changelog heading, and Forgejo mirror all identify the same
commit.
