# Ignition Module SDK (custom module development)

Building a first-class Ignition module (Kotlin/Java, Gradle) rather than authoring
project resources against an existing gateway. Generalizable mechanics only —
verified against one live project's Gradle build, not restated from vendor docs
from memory. Re-verify any version-sensitive number (plugin version, target
Ignition/framework version) against the target repo before trusting it here.

## 1. Project layout — one subproject per scope

A module is a Gradle multi-project build, one subproject per Ignition **scope**:

| Subproject | Scope | Typical content |
|---|---|---|
| `common` | `GD` (or `GCD` if a Vision component exists) | Shared engine/DTO code, no UI — trim scope to what's actually needed, don't default to `GCD` |
| `gateway` | `G` | Data providers (JDBC etc.), RPC implementation, gateway hook, scripting functions |
| `designer` | `D` | Designer hook, palette/property-panel registration |
| `perspective` | `GD` | Kotlin component registration; a Perspective component's actual UI is often a **separate JS/TS bundle** (React/webpack or similar) invoked from Gradle via an `Exec` task, not a Kotlin/Gradle-native build — its output lands under the module's `resources/mounted/js|css/` before `processResources` |
| `vision` | `C` (+`D` for the palette entry) | Vision client component, if the module ships one |

Scope shorthand is a string matching `^[AGCD]+$` (**A**ll, **G**ateway, **C**lient/
Vision, **D**esigner) — it's not plumbing, it gates what the module loader
instantiates per JVM. Trim it to exactly what each subproject needs.

## 2. Build / package / sign loop

Standard tooling: the `io.ia.sdk.modl` Gradle plugin, resolved from Inductive
Automation's own Nexus (`https://nexus.inductiveautomation.com/repository/public/`).
Root `build.gradle.kts` defines one `ignitionModule {}` block covering every
subproject — `name`, `fileName`, `id` (reverse-DNS), `moduleVersion`,
`requiredIgnitionVersion`, `requiredFrameworkVersion`, a `projectScopes` map
(subproject path → scope string), a `hooks` map (fully-qualified hook class →
scope string), `moduleDependencies` (e.g. `com.inductiveautomation.perspective` →
`GD`), `freeModule`.

- `gradle build -x test` → compiles everything, produces a **signed** `.modl`
  (needs a local keystore configured).
- `gradle build -PskipModlSigning` → produces an **unsigned** `.modl`, no keystore
  needed — the usual fresh-clone/dev-loop path.
- Signed-by-default-when-configured, explicit-opt-out-otherwise is the sane
  default shape: `skipModlSigning.set(hasProperty("skipModlSigning") || !haveSigningConfig)`
  — a fresh clone with no keystore should never hard-fail `gradle build`.
- A Perspective/Vision subproject with a JS bundle typically wires `npm ci && npm
  run build` as a plain `Exec` task ahead of `processResources` — not a
  node-Gradle plugin. No pinned Node version is guaranteed; check the target repo.

**Signing mechanics** (mechanism only; never record real keys):

- The plugin reads signing inputs as Gradle project properties under an
  `ignition.signing.*`-shaped namespace: keystore file, keystore password, cert
  file, cert alias, cert password.
- Precedence: `-P` flag / env / `gradle.properties` first; fall back to an
  **untracked** local properties file loaded manually in `build.gradle.kts` (only
  when not already set). Keystore/cert files and the local signing-properties
  file belong in `.gitignore` — commit a README on how to regenerate them, never
  the material itself.
- The IA-provided module signer does **not** validate the trust chain at sign
  time — a self-signed cert produces a validly-signed `.modl`. The payoff: a
  gateway with `-Dignition.allowunsignedmodules` off still accepts a signed
  module with only a one-time "certificate not trusted" click-through, instead of
  the hard block an unsigned module gets. That's the entire point of doing the
  signing work even with a self-signed cert.

**Reaching the gateway**: no scripted deploy should be assumed — check whether
the target repo's `Deploy` task block is actually wired (`-Phost`/`deployModl`
properties) or just an unused import. The universal fallback path always works:
Gateway web UI → Config → Modules → "Install or Upgrade a Module…" → upload the
`.modl`.

## 3. Recurring Module-SDK gotchas

- **Signing flags vs `sign.props`.** The Gradle plugin may want signing inputs as CLI flags
  (`--keystoreFile/--keystorePassword/--certFile/--certAlias/--certPassword`) and ignore a
  `sign.props` file a README describes; the task is `signModule`, not `buildModule`, and
  `skipModlSigning` may need flipping to `false` in the build script. Verify against the
  target repo's plugin version.
- **Windows MAX_PATH.** Clone SDK example projects to a short path (e.g. `C:\ignsdk`); a deep
  temp dir breaks the clone.
- **One `.modl`, many components.** Register every `ComponentDescriptor` in both the gateway
  and designer hooks, plus a `ComponentMeta` in the JS bundle.
- **Ground component geometry in manufacturer datasheets**, not generic web images (plausible
  but wrong proportions); CAD/STEP/DWG are unusable as inputs. Verify component JS offline with
  node before installing.
- **Transitive Kotlin-stdlib version skew.** An IA-provided dependency (e.g.
  `perspective-gateway`) can pull a different `kotlin-stdlib` version than the
  project's own Kotlin plugin version, producing a "kotlin-stdlib exists in
  multiple versions" failure at `zipModule`. Fix: force-resolve the stdlib
  version project-wide —
  `configurations.all { resolutionStrategy.force("org.jetbrains.kotlin:kotlin-stdlib:<pinned>") }`
  in `subprojects {}`.
- **Stale jar caching after a partial build.** The same "multiple versions"
  symptom can recur even after the force-resolution fix if a stale jar is
  sitting in the module-content build output from a prior partial build. Fix is
  `gradle clean` + rebuild, not more resolution-strategy tweaking — don't chase
  this one with dependency config changes a second time.
- **Manifest/signing property names aren't reliably documented.** The
  `ignitionModule{}` block's exact property surface and the signing-property
  namespace are worth confirming with `javap` against the plugin jar directly
  when behavior doesn't match what's written, rather than trusting the plugin's
  own docs as complete.
- **Scope trimming is a correctness decision, not cleanup.** Don't default a
  subproject to a wide scope string "to be safe" — an unnecessary `C` scope on a
  subproject with no Vision component, for example, is wrong, not just untidy.

## 4. Toolchain baseline (verify per project, this is a starting point)

- JDK 17 (Temurin), pinned via an explicit toolchain env file, not system JDK.
- Gradle 8.10.x.
- `io.ia.sdk.modl` plugin — pin the exact version; property surface has shifted
  across plugin versions.
- Kotlin version forced project-wide via `subprojects {}` to dodge stdlib skew.
- Target `requiredIgnitionVersion` / `requiredFrameworkVersion` — read from the
  target repo's `ignitionModule{}` block, never assumed.
- A Perspective/Vision component subproject needs system Node for its JS build
  step — check for a pinned Node version before assuming any particular one.
