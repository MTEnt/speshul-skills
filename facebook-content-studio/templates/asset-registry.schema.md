# Asset registry schema

`asset-registry.json` identifies every approved or rejected production asset. It contains no credentials.

```json
{
  "schema_version": "1.0",
  "campaign_id": "campaign-slug",
  "assets": [
    {
      "asset_id": "character-host-v1-front",
      "entity_id": "character-host-v1",
      "version": 1,
      "type": "image",
      "role": "identity_anchor",
      "source": "user_supplied | higgsfield_job | owned_storage",
      "path_or_job_id": "/absolute/path/or-completed-job-id",
      "delivery_url": null,
      "sha256": null,
      "approval": "candidate | approved | rejected",
      "approved_by": null,
      "approved_at": null,
      "locked_attributes": [],
      "notes": ""
    }
  ]
}
```

Rules:

- `asset_id` never changes after another file references it.
- Revisions get a new asset ID and incremented version.
- Only `approved` assets can enter final shot manifests or a ready post package.
- Absolute local paths remain local production metadata. Do not publish the registry.
- `delivery_url` is set only for an approved public copy intended for platform delivery.
- The registry must not contain Facebook tokens, Higgsfield session credentials, passwords, private OAuth data, or MCP approval phrases.
