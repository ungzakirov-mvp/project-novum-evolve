

## Problem

The `Pricing.tsx` component has all pricing plans **hardcoded directly in the code** (lines 27+). When you update prices/plans in the admin panel, the database changes correctly, but the public website never reads from the database -- it always shows the same static values.

## Solution

Refactor `Pricing.tsx` to fetch pricing plans from the database (`pricing_plans` table) on mount, replacing the hardcoded `plans` array with live data from the backend.

### Changes

1. **`src/components/Pricing.tsx`** -- Replace static `plans` array with a `useEffect` + `useState` that fetches from `pricing_plans` table, ordered by `sort_order`, filtered by `is_active = true`. Map database fields (`price`, `name`, `computers`, `sla`, `tickets`, `refills`, `highlight`, `badge`, `extra_features`, `service_desk_basic`, `service_desk_mobile`, `cta_key`) to the existing rendering logic. Show a loading skeleton while data loads.

2. No database changes needed -- RLS is already disabled on these tables, so public reads will work.

