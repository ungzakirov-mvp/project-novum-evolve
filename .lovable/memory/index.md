# Memory: index.md
Updated: now

# Project Memory

## Core
Novum Tech — IT outsourcing Tashkent (5-150 seats). SLA 95%. Support: support@novumtech.uz
Dark theme (#0A0A0F), high contrast, white headings, blue accents. Glassmorphism and Lucide icons.
No horizontal scroll. Strict touch targets and mobile spacing.
Node.js 24.x, Vercel, Supabase.
RLS ENABLED on all public tables. Catalog tables (pricing_plans, services, service_categories) have public-read + admin-write policies.
Hardcoded domain: novumtech.uz. 404 is noindex.

## Memories
- [Project identity](mem://project/identity) — Business context, SLA 95%, contact details and channels
- [Visual identity](mem://style/visual-identity) — Dark theme, blue accents, glassmorphism, premium cards
- [Typography and icons](mem://style/typography-and-icons) — Font sizes (+30% nav, +15% hero), Lucide icons
- [Quality standards](mem://constraints/quality-standards) — Mobile touch targets, no horiz scroll, form functionality
- [Multilingual support](mem://features/multilingual-support) — RU/UZ/EN via React Context, localStorage
- [i18n helpers](mem://technical/i18n-helpers) — getLocalizedField helper for DB suffixes (_ru, _uz, _en)
- [Admin auth](mem://features/admin-panel/authentication) — /admin route, email/pass, session tokens, env vars
- [Admin content logic](mem://features/admin-panel/content-management) — Exclusive Recommended flag, inline category creation
- [Admin leads](mem://features/admin-panel/leads-management) — RLS restricts request viewing to admin role
- [Pricing plans](mem://features/pricing-plans) — Syncs with Supabase pricing_plans, no hardcoded prices
- [Service catalog](mem://features/service-catalog) — DB is source of truth, 11 categories
- [Contact system](mem://features/contact-system) — Minimal fields, email placeholder bypass, Resend notifications
- [Cost calculator](mem://features/cost-calculator) — PC count, resident engineer forces PRO plan
- [Tariff constructor](mem://features/tariff-builder) — Two-step wizard, formula: selected services price * months
- [Clients & reviews](mem://features/clients-and-testimonials) — Admin moderation required, no organization names
- [Admin API security](mem://technical/admin-api-security) — RLS enabled on catalog tables with public-read + admin-write
- [Deployment & hosting](mem://technical/deployment-hosting) — Node 24.x, Vercel, Supabase
- [SEO optimization](mem://technical/seo-optimization) — SEOHead.tsx, structured data, canonical domains
- [Category mapping](mem://technical/service-category-mapping) — ID 'cabling' for SCS
- [SEO strategy](mem://features/seo-content-strategy) — 300-600 word neutral SEO blocks at bottom of key pages
