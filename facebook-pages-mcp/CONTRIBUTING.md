# Contributing

## Before opening a change

Run:

```bash
npm install
npm run verify
```

Every behavioral change needs tests. Tests must mock Facebook and must never require a real access token or create a live post.

## Security invariants

Changes must preserve these rules unless the maintainers explicitly approve a documented threat-model revision:

- Tokens never appear in tool schemas, tool results, URLs, logs, or fixtures.
- Graph API calls use `Authorization: Bearer`.
- Page IDs are checked against `FACEBOOK_PAGE_IDS` before every network call.
- Every write uses a single-use preview and explicit commit.
- Ambiguous write results are not blindly retried.
- No unauthenticated network transport is added.
- Destructive, Messenger, moderation, arbitrary-path, and local-file tools remain out of scope.

## Pull-request checklist

- Explain the user-visible behavior and external side effects.
- Link the current official Meta documentation supporting each Graph API field or endpoint change.
- Add or update failure-path tests.
- Run `npm run verify`.
- Confirm `npm pack --dry-run` contains no credentials, `.env` file, test artifacts, or workspace files.
