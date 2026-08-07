# Meta publishing boundary

Current-source review: 2026-08-07.

## Supported by the Workshop AI MCP

The current MCP can:

- publish text and link posts through `/<PAGE_ID>/feed`
- schedule text and link posts between ten minutes and thirty days ahead
- publish one photo from a public HTTPS URL through `/<PAGE_ID>/photos`
- read back and list posts for an allowlisted Page

Every supported write must go through `facebook_post_preview` and explicit user approval before `facebook_post_publish`.

## Page requirements

Meta's current Pages documentation requires a Page access token requested by a person who can perform the appropriate Page tasks. For publishing, the app needs `pages_manage_posts` and its relevant Page-read/list dependencies. The current MCP keeps the access token outside tool arguments and restricts calls to `FACEBOOK_PAGE_IDS`.

## Schedule rule

Meta's current post guide says scheduled publication must be between ten minutes and thirty days after the request. The skill and MCP enforce that window. Do not repeat older seventy-five-day guidance.

## Photo delivery

The MCP accepts only a public HTTPS photo URL with a hostname. Before preview:

1. Confirm the URL resolves without authentication.
2. Confirm it is stable long enough for Meta to fetch.
3. Prefer user-controlled object storage over an undocumented temporary job URL.
4. Confirm the final image is the approved version.

## Video publication is a separate capability

Meta's current Video API uses:

1. an App ID and User access token to create a resumable upload session
2. the User token to upload the MP4 and receive a file handle
3. the Page access token to publish that handle through the Page video endpoint

The current MCP has only the Page-token model and deliberately has no video upload tools. A generated video package must therefore use `manual_meta_business_suite` until a separately reviewed uploader implements the current flow.

Required manual handoff assets:

- final MP4
- thumbnail
- title and description
- Facebook caption and CTA
- transcript and SRT or caption plan
- AI disclosure decision
- Page ID
- factual sources and approval record

Do not report a video as posted without an actual post ID or verified Page result.

## AI-generated media transparency

Meta applies AI information labels when it detects industry signals or when a person self-discloses generated media. Generated photorealistic people, realistic synthetic speech, public-interest claims, and political or social-issue content require heightened review. The content package must record one of:

- `disclose`
- `not_required_with_reason`
- `human_review_required`

When uncertain, use `human_review_required`. Do not strip provenance metadata in order to evade labeling.

## Sources

- Meta, [Pages API: Posts](https://developers.facebook.com/documentation/pages-api/posts)
- Meta, [Pages API: Get Started](https://developers.facebook.com/documentation/pages-api/getting-started)
- Meta, [Video API: Publishing](https://developers.facebook.com/documentation/video-api/guides/publishing)
- Meta, [Permissions Reference](https://developers.facebook.com/docs/permissions/#p)
- Meta, [Our approach to labeling AI-generated content and manipulated media](https://about.fb.com/news/2024/04/metas-approach-to-labeling-ai-generated-content-and-manipulated-media/)
