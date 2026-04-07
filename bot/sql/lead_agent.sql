create extension if not exists pgcrypto;

create table if not exists leads (
  id uuid primary key default gen_random_uuid(),
  company_name text not null,
  website text,
  domain text unique,
  email text,
  telegram text,
  phone text,
  city text default 'Ташкент',
  source text default 'manual',
  score integer default 0,
  status text default 'new' check (status in ('new','contacted','meeting','proposal','won','lost')),
  notes text,
  outreach_channel text default 'telegram,email',
  last_contacted_at timestamptz,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table if not exists lead_activity (
  id uuid primary key default gen_random_uuid(),
  lead_id uuid not null references leads(id) on delete cascade,
  channel text not null check (channel in ('telegram','email','call','other')),
  activity_type text not null check (activity_type in ('outreach','reply','meeting','proposal','note')),
  payload jsonb,
  created_at timestamptz default now()
);

create index if not exists idx_leads_status on leads(status);
create index if not exists idx_leads_score on leads(score desc);
create index if not exists idx_leads_city on leads(city);
create index if not exists idx_lead_activity_lead_id on lead_activity(lead_id);

alter table leads enable row level security;
alter table lead_activity enable row level security;

do $$
begin
  if not exists (
    select 1 from pg_policies where schemaname = 'public' and tablename = 'leads' and policyname = 'leads_select_all'
  ) then
    create policy leads_select_all on leads for select using (true);
  end if;
end $$;

do $$
begin
  if not exists (
    select 1 from pg_policies where schemaname = 'public' and tablename = 'leads' and policyname = 'leads_insert_all'
  ) then
    create policy leads_insert_all on leads for insert with check (true);
  end if;
end $$;

do $$
begin
  if not exists (
    select 1 from pg_policies where schemaname = 'public' and tablename = 'leads' and policyname = 'leads_update_all'
  ) then
    create policy leads_update_all on leads for update using (true);
  end if;
end $$;

do $$
begin
  if not exists (
    select 1 from pg_policies where schemaname = 'public' and tablename = 'lead_activity' and policyname = 'lead_activity_select_all'
  ) then
    create policy lead_activity_select_all on lead_activity for select using (true);
  end if;
end $$;

do $$
begin
  if not exists (
    select 1 from pg_policies where schemaname = 'public' and tablename = 'lead_activity' and policyname = 'lead_activity_insert_all'
  ) then
    create policy lead_activity_insert_all on lead_activity for insert with check (true);
  end if;
end $$;
