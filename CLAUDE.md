# Dance Lab

Practice tools for Latin dance. Read [docs/README.md](docs/README.md) first; it says which doc covers what.

## Publishing: `main` is the live version

Pushing to `main` is the whole deploy. Nothing else needs doing:

| Site | Address | Updates |
|---|---|---|
| GitHub Pages (no search bar) | https://halbenhb.github.io/dance-lab/ | About 1 minute after the push |
| Render (full version, needs the password) | https://dance-lab.onrender.com/wheres-the-one/ | About 2–3 minutes after the push |

Work that isn't on `main` isn't live, so a finished change isn't done until the owner has decided about publishing:

1. When a change is finished, say it isn't live yet and offer to publish it. Commit and push only when the owner says so.
2. To publish, run the checklist in [docs/development.md](docs/development.md), merge any branch into `main`, and push.
3. Confirm it arrived. `https://dance-lab.onrender.com/api/status` reports the deployed `commit`, which should match `git rev-parse --short HEAD`. The first request can take a minute while the server wakes.

## Working alongside other sessions

Several sessions can share this folder. Before committing, run `git status` and `git branch --show-current`, and commit only your own changes. Check for a branch or uncommitted work from another session before you start, and don't merge or discard it without asking.

## Never commit

- Anything in `library/`, or any audio file. Songs are copyrighted and the repo is public.
- Render's settings: `DANCE_LAB_PASSWORD`, `YT_PROXY` (contains a password) and the cookies file. Never ask the owner to paste them into chat. They live only in Render's dashboard.

## Plain language

The owner is a dancer who is also a developer. Page text and error messages should make sense to dancers. Use the terms in [docs/glossary.md](docs/glossary.md).
