# Supabase Setup For F1bot Backend

## 1) Environment Variables

Set these in `backend/.env`:

```env
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_AUTH_ENABLED=true
```

Keep your existing app/reddit/gemini variables as-is.

If you are developing locally and want to avoid sending Supabase transactional emails,
set `SUPABASE_AUTH_ENABLED=false` (or leave it unset while `APP_ENV=development`).

## 2) SQL Schema

Run this in Supabase SQL Editor:

```sql
create table if not exists profiles (
  user_id text primary key,
  business_description text not null,
  keywords jsonb not null default '[]'::jsonb,
  subreddits jsonb not null default '[]'::jsonb,
  updated_at timestamptz not null default now()
);

create table if not exists leads (
  id uuid primary key,
  user_id text not null,
  status text not null check (status in ('new', 'contacted', 'qualified', 'ignored')),
  post_id text not null,
  title text not null,
  body text not null default '',
  subreddit text not null,
  url text not null,
  author text not null,
  post_created_utc timestamptz not null,
  reddit_score integer not null default 0,
  num_comments integer not null default 0,
  lead_score numeric(5,2) not null,
  qualification_reason text not null,
  suggested_outreach text not null,
  scan_id uuid not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_leads_user_id on leads (user_id);
create index if not exists idx_leads_status on leads (status);
create index if not exists idx_leads_score_desc on leads (lead_score desc);
```

## 3) Optional RLS

If you enable RLS, create policies according to your auth model. Current backend uses service role key and handles filtering by `user_id` in API queries.

## 4) Auth Behavior

- If Supabase is configured and `SUPABASE_AUTH_ENABLED=true`, auth routes use Supabase (`sign_in_with_password` and `sign_up`).
- If Supabase auth is disabled (for example local development), backend falls back to demo local auth responses and does not trigger Supabase auth emails.
