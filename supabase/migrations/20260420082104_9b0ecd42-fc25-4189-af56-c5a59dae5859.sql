-- Enable RLS on public catalog tables (policies already exist)
ALTER TABLE public.pricing_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.services ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.service_categories ENABLE ROW LEVEL SECURITY;

-- Tighten the always-true review insert policy with basic input checks
DROP POLICY IF EXISTS "Anyone can submit review" ON public.reviews;
CREATE POLICY "Anyone can submit review"
ON public.reviews
FOR INSERT
TO public
WITH CHECK (
  length(btrim(name)) BETWEEN 1 AND 100
  AND length(btrim(text)) BETWEEN 1 AND 2000
  AND rating BETWEEN 1 AND 5
  AND is_approved = false
);