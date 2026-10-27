-- Phase 1: accounts/preferences and the starter recipe catalog only.
-- No scans, image storage, saved-recipe cloud tables, or model changes.
begin;

create table public.cuisine_styles (
  id uuid primary key default gen_random_uuid(),
  name text not null unique,
  destination_name text not null unique,
  position integer not null default 0
);
create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text not null check (char_length(btrim(full_name)) between 1 and 40),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create table public.user_preferences (
  user_id uuid primary key references public.profiles(id) on delete cascade,
  servings smallint not null default 2 check (servings between 1 and 20),
  diet text not null default 'No preference' check (diet in ('No preference', 'Vegetarian', 'Halal')),
  cuisine_style_id uuid references public.cuisine_styles(id) on delete set null,
  allergies text[] not null default '{}',
  excluded_ingredients text[] not null default '{}',
  legacy_style_imported boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (cardinality(allergies) <= 50 and array_position(allergies, null) is null),
  check (cardinality(excluded_ingredients) <= 100 and array_position(excluded_ingredients, null) is null)
);
create table public.ingredients (
  id uuid primary key default gen_random_uuid(),
  name text not null unique,
  category text not null
);
create table public.ingredient_aliases (
  normalized_alias text primary key check (normalized_alias = lower(btrim(normalized_alias)) and normalized_alias <> ''),
  ingredient_id uuid not null references public.ingredients(id) on delete cascade
);
create table public.recipes (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  name text not null,
  cuisine_style_id uuid references public.cuisine_styles(id) on delete set null,
  minutes integer not null check (minutes > 0),
  servings smallint not null check (servings > 0),
  steps jsonb not null check (jsonb_typeof(steps) = 'array' and jsonb_array_length(steps) > 0),
  image_path text not null,
  version integer not null default 1 check (version > 0),
  published boolean not null default false,
  source_url text,
  license text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create table public.recipe_ingredients (
  recipe_id uuid not null references public.recipes(id) on delete cascade,
  ingredient_id uuid not null references public.ingredients(id),
  quantity_text text not null,
  is_required boolean not null default true,
  position integer not null check (position >= 0),
  primary key (recipe_id, ingredient_id),
  unique (recipe_id, position)
);
create index recipe_ingredients_ingredient_idx on public.recipe_ingredients(ingredient_id);
create index ingredient_aliases_ingredient_idx on public.ingredient_aliases(ingredient_id);
create index recipes_style_idx on public.recipes(cuisine_style_id);
create index user_preferences_style_idx on public.user_preferences(cuisine_style_id);

create function public.timpla_touch_updated_at() returns trigger language plpgsql set search_path = '' as $$
begin new.updated_at = now(); return new; end;
$$;
create trigger profiles_updated before update on public.profiles for each row execute function public.timpla_touch_updated_at();
create trigger preferences_updated before update on public.user_preferences for each row execute function public.timpla_touch_updated_at();
create trigger recipes_updated before update on public.recipes for each row execute function public.timpla_touch_updated_at();

-- Only a deferred check can validate a published recipe and its ingredient rows
-- together, without preventing them from being inserted in one transaction.
create function public.timpla_validate_published_recipe() returns trigger language plpgsql set search_path = '' as $$
declare target_id uuid;
begin
  if tg_table_name = 'recipes' then target_id := new.id;
  elsif tg_op = 'DELETE' then target_id := old.recipe_id;
  else target_id := new.recipe_id; end if;
  if exists (select 1 from public.recipes where id = target_id and published)
     and not exists (select 1 from public.recipe_ingredients where recipe_id = target_id and is_required) then
    raise exception 'A published recipe needs at least one required ingredient';
  end if;
  return null;
end;
$$;
create constraint trigger recipes_require_ingredients after insert or update on public.recipes deferrable initially deferred for each row execute function public.timpla_validate_published_recipe();
create constraint trigger ingredients_keep_recipe_valid after insert or update or delete on public.recipe_ingredients deferrable initially deferred for each row execute function public.timpla_validate_published_recipe();

-- Create private application rows for every new Auth account. This function is
-- invoked only by the Auth trigger, not directly by app clients.
create function public.timpla_create_account_rows() returns trigger language plpgsql security definer set search_path = '' as $$
begin
  insert into public.profiles(id, full_name)
  values (new.id, left(coalesce(nullif(btrim(new.raw_user_meta_data ->> 'full_name'), ''), 'Cook'), 40));
  insert into public.user_preferences(user_id) values (new.id);
  return new;
end;
$$;
revoke all on function public.timpla_create_account_rows() from public, anon, authenticated;
create trigger timpla_account_created after insert on auth.users for each row execute function public.timpla_create_account_rows();
insert into public.profiles(id, full_name)
select id, left(coalesce(nullif(btrim(raw_user_meta_data ->> 'full_name'), ''), 'Cook'), 40) from auth.users;
insert into public.user_preferences(user_id) select id from public.profiles;

insert into public.cuisine_styles(name, destination_name, position) values
('Bicolano', 'Bicol', 0), ('Ilocano', 'Ilocos', 1), ('Kapampangan', 'Pampanga', 2), ('Ilonggo', 'Iloilo', 3);

-- Import the old device-local cooking style once per account. Subsequent devices
-- cannot overwrite an existing cloud preference with their stale local setting.
create function public.timpla_import_legacy_style(style_name text) returns void language plpgsql security definer set search_path = '' as $$
declare target_style uuid;
begin
  if auth.uid() is null then raise exception 'Sign in first'; end if;
  if style_name is not null and style_name <> 'Any style' then
    select id into target_style from public.cuisine_styles where name = style_name;
    if target_style is null then raise exception 'Unknown cooking style'; end if;
  end if;
  update public.user_preferences
  set cuisine_style_id = coalesce(cuisine_style_id, target_style), legacy_style_imported = true
  where user_id = auth.uid() and not legacy_style_imported;
end;
$$;
revoke all on function public.timpla_import_legacy_style(text) from public, anon, authenticated;
grant execute on function public.timpla_import_legacy_style(text) to authenticated;

insert into public.ingredients(name, category) values
('Eggplant', 'vegetable'), ('Tomato', 'vegetable'), ('Onion', 'vegetable'),
('Salt', 'seasoning'), ('Vinegar', 'seasoning'), ('Pepper', 'seasoning'), ('Egg', 'other'), ('Oil', 'other');
insert into public.ingredient_aliases(normalized_alias, ingredient_id) select lower(name), id from public.ingredients;
insert into public.ingredient_aliases(normalized_alias, ingredient_id)
select aliases.alias, i.id from (values ('talong', 'Eggplant'), ('kamatis', 'Tomato'), ('sibuyas', 'Onion'), ('asin', 'Salt'), ('suka', 'Vinegar'), ('itlog', 'Egg'), ('eggs', 'Egg'), ('mantika', 'Oil')) aliases(alias, name)
join public.ingredients i on i.name = aliases.name;

-- Existing starter content only. No regional attribution is invented.
-- asset: identifiers resolve to the two images already bundled with Expo.
insert into public.recipes(slug, name, minutes, servings, steps, image_path, published) values
('ensaladang-talong', 'Ensaladang talong', 20, 2,
'["Grill the eggplants until tender and the skins are charred.", "Cool, peel, and chop the eggplant flesh.", "Combine with tomato, onion, and vinegar. Season with salt and pepper."]', 'asset:ensaladang-talong', true),
('tortang-talong', 'Tortang talong', 15, 2,
'["Grill the eggplants until tender. Cool and peel, keeping the stems.", "Beat the eggs with salt. Flatten each eggplant and coat it in egg.", "Heat oil in a pan. Fry each coated eggplant until the egg is set and both sides are golden."]', 'asset:tortang-talong', true);
insert into public.recipe_ingredients(recipe_id, ingredient_id, quantity_text, position)
select r.id, i.id, seed.quantity, seed.position from (values
('ensaladang-talong', 'Eggplant', '2 medium eggplants', 0),
('ensaladang-talong', 'Tomato', '1 tomato, diced', 1),
('ensaladang-talong', 'Onion', '1 small onion, sliced', 2),
('ensaladang-talong', 'Salt', 'Salt, to taste', 3),
('ensaladang-talong', 'Vinegar', '2 tablespoons vinegar', 4),
('ensaladang-talong', 'Pepper', 'Pepper, to taste', 5),
('tortang-talong', 'Eggplant', '2 medium eggplants', 0),
('tortang-talong', 'Salt', 'Salt, to taste', 1),
('tortang-talong', 'Egg', '2 eggs', 2),
('tortang-talong', 'Oil', '2 tablespoons oil', 3)
) seed(slug, name, quantity, position)
join public.recipes r on r.slug = seed.slug join public.ingredients i on i.name = seed.name;

set constraints all immediate;
alter table public.profiles enable row level security;
alter table public.user_preferences enable row level security;
alter table public.cuisine_styles enable row level security;
alter table public.ingredients enable row level security;
alter table public.ingredient_aliases enable row level security;
alter table public.recipes enable row level security;
alter table public.recipe_ingredients enable row level security;
revoke all on public.profiles, public.user_preferences, public.cuisine_styles, public.ingredients, public.ingredient_aliases, public.recipes, public.recipe_ingredients from anon, authenticated;
grant select on public.profiles, public.user_preferences, public.cuisine_styles, public.ingredients, public.ingredient_aliases, public.recipes, public.recipe_ingredients to authenticated;
grant update(full_name) on public.profiles to authenticated;
grant update(servings, diet, cuisine_style_id, allergies, excluded_ingredients) on public.user_preferences to authenticated;
create policy profiles_read_own on public.profiles for select to authenticated using (id = (select auth.uid()));
create policy profiles_update_own on public.profiles for update to authenticated using (id = (select auth.uid())) with check (id = (select auth.uid()));
create policy preferences_read_own on public.user_preferences for select to authenticated using (user_id = (select auth.uid()));
create policy preferences_update_own on public.user_preferences for update to authenticated using (user_id = (select auth.uid())) with check (user_id = (select auth.uid()));
create policy styles_read on public.cuisine_styles for select to authenticated using (true);
create policy ingredients_read on public.ingredients for select to authenticated using (true);
create policy aliases_read on public.ingredient_aliases for select to authenticated using (true);
create policy recipes_read_published on public.recipes for select to authenticated using (published);
create policy recipe_ingredients_read_published on public.recipe_ingredients for select to authenticated using (exists (select 1 from public.recipes r where r.id = recipe_id and r.published));
revoke all on function public.timpla_touch_updated_at(), public.timpla_validate_published_recipe() from public, anon, authenticated;

notify pgrst, 'reload schema';
commit;
