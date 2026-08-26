# Structured-data workflow

## Source of truth

Map every property to visible page content or an authoritative product, CMS, commerce, event, location, or organization record. Define owner and stale behavior for price, availability, date, rating, address, and other changing values.

## Type selection

Common families include Organization, Person, WebSite, WebPage, BreadcrumbList, Article or BlogPosting, Product and Offer, SoftwareApplication, LocalBusiness, Event, VideoObject, ImageObject, Course, JobPosting, Recipe, Review, FAQPage, HowTo, and Dataset. Verify whether the intended search engine currently supports a special presentation and whether policy restrictions apply.

Do not use a more specific type when required semantics are not true.

## Graph design

Use stable absolute `@id` values for recurring entities and connect page, organization, author, product, offer, breadcrumb, image, and video objects rather than repeating contradictory copies. Keep canonical URL and entity identity consistent.

## JSON-LD pattern

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://example.com/#organization",
      "name": "Verified organization name",
      "url": "https://example.com/"
    },
    {
      "@type": "WebPage",
      "@id": "https://example.com/page/#webpage",
      "url": "https://example.com/page/",
      "isPartOf": { "@id": "https://example.com/#website" }
    }
  ]
}
```

Replace illustrative values with inspected facts. Omit properties whose values are unknown; do not leave placeholders in production.

## Multiple types

Combine types only when the page visibly contains each entity and relationships are accurate. A product page may connect Product, Offer, Brand or Organization, AggregateRating only with valid underlying reviews, BreadcrumbList, and VideoObject. Avoid unrelated blocks added only to chase features.

## Implementation

Choose server-rendered template, CMS field mapping, commerce source, build-time generation, or client injection according to the rendering and data architecture. Define escaping, serialization, localization, currency, availability, update, and error behavior.

## Validation

1. Parse JSON and validate schema vocabulary.
2. Run the relevant official rich-result validator where applicable.
3. compare values with visible rendered content;
4. inspect final deployed source or DOM as the target crawler receives it;
5. monitor search-console reports and regressions.

Use current official policies such as Google's structured-data guidelines rather than remembered property lists.

## Output

Return selected types and rationale, property-source map, complete JSON-LD, implementation location, validation results, warnings, ownership, and monitoring.
