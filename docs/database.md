# Account settings and recipe database

Implemented on 22 October 2026 in Supabase project `hkjngwjujjxzqrpluflh`.

## Applied scope

The migration at `supabase/migrations/202610220001_profiles_and_catalog.sql` was
applied through the Supabase SQL editor. It is a transaction for a fresh schema,
not a script to rerun against existing tables. SQL editor execution does not
register Supabase CLI migration history; reconcile that history before adopting
CLI deployments on this existing project.

Seven application tables are live, all with RLS enabled:

| Table | Initial content / access |
| --- | --- |
| `profiles` | Existing Auth accounts backfilled; each user reads/updates only their own name |
| `user_preferences` | One row per account; owner reads/updates servings, diet, regional style, allergies and exclusions |
| `cuisine_styles` | Bicolano/Bicol, Ilocano/Ilocos, Kapampangan/Pampanga, Ilonggo/Iloilo |
| `ingredients` | Eight canonical ingredients from the current starter recipes |
| `ingredient_aliases` | Canonical spellings and starter Filipino/English aliases |
| `recipes` | Ensaladang talong and Tortang talong |
| `recipe_ingredients` | Ten ingredient requirement rows, retaining original quantity text and order |

The last five tables are read-only to authenticated app users. Only published
recipes and their requirements are visible. Anonymous/preview app access has no
database grants. Profile ownership IDs, timestamps, import flags and catalog data
cannot be edited by ordinary clients. Account deletion cascades profile/settings
rows. Recipe constraints reject publishing a dish with no required ingredients.

## Registration and existing accounts

The Auth insert trigger `timpla_account_created` creates profile and preference rows
for a newly registered account. Existing accounts were backfilled when the
migration ran. A nonempty name is trimmed and capped at the app's 40-character
limit; missing legacy names become `Cook`. The trigger has an empty search path
and is not directly executable by app clients.

`profiles.full_name` is canonical after migration. Email, password hashing,
confirmation, recovery and session handling remain managed by Supabase Auth.
Updating a profile name does not rewrite registration metadata.

## Application behavior

- `useAccountSettings` loads profile/settings for a confirmed, non-recovery session.
  A failed read offers Retry/Log out and blocks editing rather than replacing
  cloud data with defaults.
- Profile editors keep local drafts. Save/Done awaits a successful server response
  before changing the shared settings and returning. Back discards an unsaved draft.
- The servings selector on recipe details saves through the same owner-scoped
  service. It prevents overlapping taps while saving and reports a failed save.
- Existing account-scoped local cooking style is imported once through
  `timpla_import_legacy_style`. A server-owned import marker prevents another
  device's stale local value from overwriting the preference on later logins.
  Clearing to Any style stores a null style foreign key.
- `useRecipeCatalog` loads published recipes and destination/style metadata from
  Supabase for signed-in users. Failed requests show Retry; they do not silently
  substitute the bundled preview catalog.
- Stable recipe slugs remain route/bookmark IDs. Database recipe rows have UUID
  primary keys. Existing local bookmarks continue to resolve.
- The two recipe images remain bundled assets, referenced by `asset:` identifiers
  stored with their database recipes. Future HTTPS image URLs are supported.
- Skip for now remains development-only. Preview has no user/session, uses bundled
  recipes, saves no cloud settings, and keeps its own local cooking-style key.

These are the existing two starter recipes, not a comprehensive or independently
validated recipe dataset. No regional provenance was invented for them. Regional
browse can remain empty until reviewed regional variants are added.

Scan history, image Storage, cloud bookmarks and ingredient hunts were deliberately
left out of this phase. The comprehensive [database design](database-design.md)
still describes those future tables.

## Verification

```sh
npm run typecheck
npm run lint
npm run test:auth
npm run test:database
```

The automated tests mock transport; they do not create real accounts or send
emails. Database access was also checked live using
`supabase/tests/phase1-access.sql` as postgres in the SQL editor. That script inserts
a temporary Auth row to exercise the profile/default-preference trigger, then uses
transaction-local role/JWT-claim simulation to check owner read/write access,
different-account isolation, anonymous denial and catalog write denial. Every
test mutation, including that temporary row, rolls back. No password, identity,
session or email is created. This checks database policies, not the JWT issuer or an
end-to-end phone login.

Manual acceptance on the target iPhone remains necessary:

1. Register with an accessible email, enter the confirmation code, and reach Home.
2. Change the name, servings, diet, cooking style, allergies and exclusions; save
   each edited section.
3. Log out and log back in. Confirm all saved settings return.
4. Open Reverse cooking, both recipe details, and the Talong highlight. Confirm
   recipe content loads from the database and existing bookmarks still resolve.
5. Request Forgot password, verify the recovery code, submit a new password, and
   log in with it. The user must enter and submit their own new credential.
6. Exit the account, choose Skip for now, and verify preview remains available and
   isolated from the account's data.

Stop and restart Expo if it is running an older bundle:

```sh
npx expo start --clear
```
