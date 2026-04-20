DROP POLICY IF EXISTS "Anyone can submit contact request" ON public.contact_requests;
CREATE POLICY "Anyone can submit contact request"
ON public.contact_requests
FOR INSERT
TO public
WITH CHECK (
  length(btrim(name)) BETWEEN 1 AND 200
  AND length(btrim(company)) BETWEEN 1 AND 200
  AND length(btrim(email)) BETWEEN 3 AND 320
  AND length(btrim(phone)) BETWEEN 1 AND 50
  AND (message IS NULL OR length(message) <= 5000)
);

DROP POLICY IF EXISTS "Anyone can insert visits" ON public.site_visits;
CREATE POLICY "Anyone can insert visits"
ON public.site_visits
FOR INSERT
TO public
WITH CHECK (
  length(page) BETWEEN 1 AND 500
  AND (user_agent IS NULL OR length(user_agent) <= 1000)
  AND (referrer IS NULL OR length(referrer) <= 2000)
  AND (session_id IS NULL OR length(session_id) <= 100)
);