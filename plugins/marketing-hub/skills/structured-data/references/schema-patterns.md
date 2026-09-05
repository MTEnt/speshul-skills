# Structured-data patterns

Use these as field-selection guides, not paste-ready truth. Confirm the current vocabulary at Schema.org and current search-feature rules at the relevant search engine before implementation. Emit only properties supported by visible page content or an authoritative internal source.

## Organization and website

Represent the durable publisher or business once and give it a stable `@id`. Typical evidence-backed properties are name, canonical URL, logo, public contact points, and verified profile URLs. A website node may identify its publisher and, only when the site actually provides it, a working site-search action.

Do not treat a logo, social profile, or search box as proof of business identity. Avoid repeating slightly different organization objects on every page.

## Article and editorial work

Connect the page, article, author or organization, image, and breadcrumb nodes with stable identifiers. Use publication and modification dates from the content system. Match headline, author, images, and dates to what the reader can inspect.

Do not mark ordinary sales copy as journalism or invent an author profile solely for markup.

## Product, software, and offers

Keep the entity, commercial offer, seller, price, currency, availability, and review evidence distinct. A software product can include operating-system or application-category information when the product source supports it. Use aggregate ratings only when displayed first-party evidence and platform rules allow them.

Price ranges, availability, conditions, and expiration must come from the same commercial source used by the page. Do not encode a promotional state that the buying flow cannot honor.

## Local business

Choose the most specific defensible business type. Record the real public name, canonical location, contact route, service area, hours, and parent organization where relevant. For multi-location businesses, give each location its own identity and URL.

Do not publish a street address for a service-area business when it is not meant to be public.

## Events and video

For an event, distinguish online, physical, and mixed attendance; specify status, schedule, location, organizer, performer or speaker only when verified, and offers when registration is real. Update postponed, rescheduled, cancelled, or online-only state promptly.

For video, match name, description, thumbnail, upload date, duration, content URL or embed, and page placement. Add clips or key moments only when their offsets and labels are accurate.

## Breadcrumbs and collections

Use an ordered breadcrumb list that matches the page's navigational hierarchy. Collection or item-list markup should represent an actual visible set and preserve its order when order has meaning.

## Graph skeleton

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://example.test/#organization",
      "name": "Verified organization name",
      "url": "https://example.test/"
    },
    {
      "@type": "WebPage",
      "@id": "https://example.test/page/#webpage",
      "url": "https://example.test/page/",
      "name": "Visible page title",
      "isPartOf": { "@id": "https://example.test/#website" },
      "about": { "@id": "https://example.test/#organization" }
    }
  ]
}
```

Replace every example value, remove unsupported properties, and add the referenced website node or remove that relationship. A validator passing does not prove eligibility, accuracy, or search presentation.

## Implementation packet

Return the page-to-entity map, identifiers, source for each non-obvious field, final JSON-LD, injection location, rendering behavior, validation results, search-feature eligibility caveats, and an owner for freshness-sensitive fields.
