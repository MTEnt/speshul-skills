# Post package schema

The durable handoff is JSON. Validate it with `scripts/validate-post-package.mjs`.

## Required top-level fields

```json
{
  "schema_version": "1.0",
  "campaign_id": "stable-slug",
  "brand_profile": "profile-slug",
  "status": "draft | ready_for_preview | manual_handoff | scheduled | published",
  "objective": {},
  "page": {},
  "content": {},
  "media": [],
  "publication": {},
  "evidence": {},
  "disclosure": {},
  "qa": {},
  "approvals": {}
}
```

## Objective

```json
{
  "type": "awareness | education | consideration | conversion | community",
  "audience": "specific audience",
  "primary_cta": "one desired action"
}
```

## Page and content

```json
{
  "page": {"id": "123456789", "name": "Approved Page name"},
  "content": {
    "format": "text | link | photo | video",
    "caption": "final Facebook caption",
    "link": null,
    "title": null,
    "description": null,
    "alt_text": "meaningful visual description or null",
    "language": "en"
  }
}
```

## Media

Every media asset has:

```json
{
  "asset_id": "stable-approved-id",
  "type": "image | video | thumbnail | captions",
  "role": "primary | thumbnail | captions | reference",
  "source": "higgsfield_job | user_supplied | owned_storage",
  "local_path": null,
  "delivery_url": "https://public.example/final.jpg",
  "ai_generated": true,
  "approval": "approved"
}
```

Photo publication through the MCP requires an approved primary image with a public HTTPS `delivery_url`. Video manual handoff requires an approved primary MP4, thumbnail, and captions or transcript plan.

## Publication

Supported MCP package:

```json
{
  "transport": "theworkshopai_mcp",
  "action": "publish_now | schedule",
  "scheduled_at": null
}
```

Video handoff:

```json
{
  "transport": "manual_meta_business_suite",
  "action": "manual_handoff",
  "scheduled_at": null
}
```

The package never contains the MCP approval phrase. That phrase is created only by the live preview tool and expires.

## Evidence, disclosure, QA, and approvals

```json
{
  "evidence": {
    "claims_review": "passed | human_review_required",
    "sources": [{"title": "", "url": "", "supports": ""}]
  },
  "disclosure": {
    "ai": "disclose | not_required_with_reason | human_review_required",
    "reason": "",
    "identity_consent": "confirmed | not_applicable | human_review_required"
  },
  "qa": {
    "brand": "passed | failed | human_review_required",
    "continuity": "passed | failed | not_applicable",
    "technical": "passed | failed",
    "policy": "passed | failed | human_review_required",
    "accessibility": "passed | failed"
  },
  "approvals": {
    "brief": "approved | pending",
    "references": "approved | not_applicable | pending",
    "final_asset": "approved | not_applicable | pending",
    "final_copy": "approved | pending",
    "publish": "pending_mcp_preview | manual_handoff | approved | completed"
  }
}
```

`ready_for_preview` requires completed evidence, QA, and creative approvals. It does not mean the user has approved the live Facebook preview.
