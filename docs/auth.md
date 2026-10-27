# Timpla authentication

The Expo app uses Supabase Auth for email/password registration, confirmation,
login, password recovery, session refresh, and logout. Supabase sends the branded
emails through the project's configured Brevo SMTP connection.

## Local configuration

Copy `.env.example` to `.env.local` and set the Supabase project URL and its
**publishable** key. The current local workspace is already configured. Never use
a secret/service-role key, database password, or Brevo SMTP key in Expo.

After changing environment variables or installing dependencies, stop the old
Expo process and restart it:

```sh
npx expo start --clear
```

## Registration test

1. Choose **Sign up** on the login screen.
2. Enter your name, an accessible email, and a password of at least eight characters.
3. Submit **Create account**. No app session is granted until email verification.
4. Enter the six-digit code from the confirmation email in Timpla. The email's
   confirmation button also works when its return URL matches the allowlist.
5. Confirm that Home uses your name and Profile shows your email.
6. Log out, then log in with the same credentials.

Use **Forgot password?** to request a recovery email. Verify the recovery code,
choose a new password, then log in again. A recovery session does not open app
screens before the password-reset flow completes.

## Development preview

**Skip for now** remains available in development builds and Expo Go. It opens an
in-memory preview, creates no Supabase user/session, and is disabled in production.
Use **Profile → Exit preview** to return to login. Preview saved recipes and
cooking style use their own local storage keys.

## Email links and codes

The live confirmation and recovery templates include both `{{ .ConfirmationURL }}`
and `{{ .Token }}`. Editable copies are under `supabase/templates/`. Edit the live
templates through Supabase Authentication → Emails → Templates.

The app constructs `/auth/callback` with `expo-linking`. An optional
`EXPO_PUBLIC_AUTH_REDIRECT_URL` overrides it. The callback handles URL-fragment
sessions and authorization codes; tokens are not logged or included in app routes.

The project currently allows the exact callback URLs for:

- `timpla://auth/callback` for development/installed builds.
- `exp://192.168.1.5:8081/--/auth/callback` for the current Expo Go LAN address.
- `http://localhost:8081/auth/callback` for the usual local web server.
- `http://localhost:8082/auth/callback` and `http://127.0.0.1:8082/auth/callback`
  for the separate verification server.

If the LAN address, port, tunnel, or deployed web domain changes, add its exact
callback URL in Supabase Authentication → URL Configuration. Entering the emailed
code works in Expo Go without depending on its changing return URL. Configure the
production Site URL and callback when a production host/build is available.

## Data scope

Supabase manages the account in `auth.users`. Registration supplies `full_name`
metadata; the account-creation trigger copies it into `public.profiles.full_name`.
The profile table is now the app's canonical name source. Profile edits update that
table, not an independently editable metadata copy. Auth tokens are persisted by
Supabase; native storage uses AsyncStorage and web uses the SDK's browser storage.
Passwords are submitted to Supabase and are not saved by the app.

Profiles and cooking preferences now load from Supabase with owner-only RLS.
Signed-in recipe screens load the published database catalog. Saved recipe IDs
remain scoped to the user ID in local storage; scans and ingredient hunts remain
in memory. Changing users remounts the cooking state and aborts pending scan
requests. Preview uses bundled recipes and never writes cloud user data.

See [database setup and checks](database.md) for the migration, catalog, and
live access verification.

## Verification

```sh
npm run typecheck
npm run lint
npm run test:auth
npm run test:database
```

Auth tests use a mocked transport and do not create accounts or send emails. The
real registration, email-code verification, and final password update should also
be tested on the target iPhone with the user's own credentials.
