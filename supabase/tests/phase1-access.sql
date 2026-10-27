-- Run in the SQL editor as postgres after the phase-1 migration.
-- All test writes roll back, including the temporary Auth row below. No emails,
-- passwords, identities or sessions are created, and no test account is retained.
begin;
do $$
declare fixture_id uuid := gen_random_uuid();
begin
  insert into auth.users(id, raw_user_meta_data) values (fixture_id, '{"full_name":"Timpla transaction test"}');
  if not exists (select 1 from public.profiles where id = fixture_id and full_name = 'Timpla transaction test') then raise exception 'New-account profile trigger failed'; end if;
  if not exists (select 1 from public.user_preferences where user_id = fixture_id and servings = 2 and diet = 'No preference' and cuisine_style_id is null) then raise exception 'New-account defaults trigger failed'; end if;
  perform set_config('request.jwt.claim.sub', fixture_id::text, true);
end;
$$;
set local role authenticated;
do $$
declare denied boolean := false; affected integer;
begin
  if auth.uid() is null then raise exception 'Missing test account context'; end if;
  if (select count(*) from public.profiles) <> 1 then raise exception 'Owner profile isolation failed'; end if;
  if (select count(*) from public.user_preferences) <> 1 then raise exception 'Owner preference isolation failed'; end if;
  update public.profiles set full_name = 'Timpla access test' where id = auth.uid();
  get diagnostics affected = row_count;
  if affected <> 1 then raise exception 'Owner cannot update profile'; end if;
  update public.user_preferences set servings = 3, allergies = array['Eggs'] where user_id = auth.uid();
  if not exists (select 1 from public.user_preferences where servings = 3 and allergies = array['Eggs']) then raise exception 'Preference write/read failed'; end if;
  if (select count(*) from public.recipes where published) <> 2 then raise exception 'Starter recipe catalog missing'; end if;
  if (select count(*) from public.recipe_ingredients) <> 10 then raise exception 'Recipe requirements missing'; end if;
  begin
    update public.recipes set name = 'Client must not change catalog';
  exception when insufficient_privilege then denied := true;
  end;
  if not denied then raise exception 'Catalog write was not denied'; end if;
  if has_column_privilege('authenticated', 'public.profiles', 'id', 'UPDATE') then raise exception 'Owner ID must not be editable'; end if;
  if has_column_privilege('authenticated', 'public.user_preferences', 'legacy_style_imported', 'UPDATE') then raise exception 'Import marker must not be client writable'; end if;
end;
$$;
reset role;
select set_config('request.jwt.claim.sub', '00000000-0000-0000-0000-000000000001', true);
set local role authenticated;
do $$
declare affected integer;
begin
  if exists (select 1 from public.profiles) or exists (select 1 from public.user_preferences) then raise exception 'A different account can read private rows'; end if;
  update public.profiles set full_name = 'Must not affect anyone';
  get diagnostics affected = row_count;
  if affected <> 0 then raise exception 'A different account can update private rows'; end if;
end;
$$;
reset role;
set local role anon;
do $$
declare denied boolean := false;
begin
  begin
    perform 1 from public.profiles;
  exception when insufficient_privilege then denied := true;
  end;
  if not denied then raise exception 'Anonymous profile access was not denied'; end if;
end;
$$;
reset role;
rollback;

select 'PASS: new-account trigger, owner access, account isolation, anonymous denial, catalog write denial; test writes rolled back' as verification,
  (select count(*) from public.profiles) as profiles,
  (select count(*) from public.user_preferences) as preference_rows,
  (select count(*) from public.cuisine_styles) as cuisine_styles,
  (select count(*) from public.ingredients) as ingredients,
  (select count(*) from public.recipes where published) as published_recipes,
  (select count(*) from public.recipe_ingredients) as recipe_ingredients,
  (select bool_and(c.relrowsecurity) from pg_class c join pg_namespace n on n.oid = c.relnamespace where n.nspname = 'public' and c.relname in ('profiles','user_preferences','cuisine_styles','ingredients','ingredient_aliases','recipes','recipe_ingredients')) as all_rls_enabled;
