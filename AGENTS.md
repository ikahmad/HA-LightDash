# Instructions

## Version bumps, commits, and pushes

When making changes, ALWAYS:
1. Bump the version in `addons/lightdash/config.yaml`
2. Update `addons/lightdash/CHANGELOG.md` with a technical summary of what changed
3. Update `RELEASE.md` with a user-friendly, non-technical summary — brief intro sentence categorising the type of change, then bulletpoints describing what it means for the user (not implementation details). **One section per PR to `main`** — consolidate all changes since the last release, do not group by intermediate version bumps. Lead with a header like `# Release Notes for v0.0.0 (YYYY-MM-DD)` followed by a natural one-sentence intro summarising the release, then bulletpoints.
4. Commit the changes with a descriptive message including the new version
5. Push to the current branch
