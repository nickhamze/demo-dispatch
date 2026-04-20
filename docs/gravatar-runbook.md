# Gravatar runbook for Demo Dispatch authors

The dataset has no companion plugin, so the only mechanism by which the four
fictional authors get illustrated avatars in any preview environment is the
Gravatar fallback that WordPress consults at render time. This runbook is the
one-time human task that turns each author's `*@demo-dispatch.example` email
into an illustrated avatar in the wild.

This runbook is owned by the dataset maintainer. It must be re-run every
release if any avatar art changes.

## Reserved email addresses

The `demo-dispatch.example` domain is reserved for this dataset. Per
[RFC 2606](https://datatracker.ietf.org/doc/html/rfc2606) the `.example` TLD
is non-routable, so these addresses cannot receive mail and are safe to use
as Gravatar identifiers. Gravatar's account-creation flow requires email
verification, so we use a holding inbox at a real provider and forward
verification mail (see the *Provisioning* section below).

| Author             | Email                            | Avatar slug   | Avatar source file                                   |
| ------------------ | -------------------------------- | ------------- | ---------------------------------------------------- |
| Mira Halász        | `mira@demo-dispatch.example`     | paperweight   | `images/paperweight/paperweight--1x1-1200.webp`      |
| Daniyal Rashid     | `daniyal@demo-dispatch.example`  | brass-key     | `images/brass-key/brass-key--1x1-1200.webp`          |
| Akosua Mensah      | `akosua@demo-dispatch.example`   | teacup        | `images/teacup/teacup--1x1-1200.webp`                |
| Tomás Quintero     | `tomas@demo-dispatch.example`    | compass       | `images/compass/compass--1x1-1200.webp`              |

## Provisioning (one-time, then on every art change)

1. **Set up the holding inbox.** Create a single Gmail/Fastmail account named
   `demo-dispatch-maintainer@<your-real-domain>`. This is the only account
   that ever needs real email and the only contact point Gravatar will use.
2. **Configure address forwarding.** Configure the four
   `*@demo-dispatch.example` addresses as forwarders to the holding inbox via
   whichever DNS-aware mail provider you control. (Easiest: register
   `demo-dispatch.example` is impossible because `.example` is reserved;
   register a real lookalike domain like `demo-dispatch-mail.com` and
   advertise the `.example` addresses publicly while using the lookalike
   domain at provisioning time. Document this in the README so the next
   maintainer understands the forwarder.)
3. **Create the four Gravatar accounts.** For each author, sign up at
   <https://gravatar.com> with the address pair from the table above. Verify
   the email via the holding inbox.
4. **Upload the avatar.** For each account, upload the matching
   `--1x1-1200.webp` file. Crop is already 1:1, so Gravatar's editor only
   needs to confirm.
5. **Set the rating to G** (general audience).
6. **Publish.** Wait ~5 minutes for Gravatar's CDN to propagate. Verify by
   visiting:

   ```
   https://gravatar.com/avatar/$(echo -n mira@demo-dispatch.example | md5sum | cut -d' ' -f1)?s=256
   ```

   The illustrated `paperweight` avatar should render at 256x256.

## Verification

The CI guard `check_gravatars.py` (see `ci/`) hashes each author email,
fetches the corresponding gravatar URL, and asserts the response is `200 OK`
with `Content-Type: image/*`. Gravatar's `?d=404` parameter is appended so the
guard fails closed if the upload was lost. The guard runs nightly on the
GitHub Actions schedule, not on every PR, because Gravatar can rate-limit
under heavy traffic.

## Rotation policy

If maintainership transfers, the new maintainer must:

1. Recover access to the holding inbox via the previous maintainer.
2. Reset the four Gravatar passwords using "forgot password" via the holding
   inbox.
3. Update the contact field in `docs/maintainer.md`.
4. File a follow-up issue if any of the four avatars need to be re-uploaded
   (Gravatar UI sometimes loses uploaded images during account migration).

## Failure mode

If any of the four Gravatar accounts lapse, every preview will show
Gravatar's `mystery-person` placeholder for that author. This is acceptable
as a soft failure - the dataset still demonstrates the theme - but the
maintainer should aim to fix within seven days of the CI guard reporting it.

## Why this isn't automated

Gravatar's API is a one-way fetch (no upload endpoint outside the dashboard).
There is no programmatic alternative to the manual five-step provisioning
above without violating the no-companion-plugin constraint.
