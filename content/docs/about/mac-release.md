---
title: Shipping the Mac Component
linkTitle: Mac Release
description: Build, sign, notarize, and verify Barn's native macOS release payload.
weight: 35
icon: fa-brands fa-apple
---

Maintainers ship the native macOS component inside the ordinary `barn_VERSION_darwin_arm64.tar.gz` archive. Since `0.9.2`, the standard installer and `pgsty/infra/barn` Homebrew formula install the CLI, its matching hosts helper, and `Barn.app` together. This page is the maintained release handbook, checked against the release scripts on 2026-11-08. For a development build, use [Build from Source](../../start/source-build/#mac-component).

## Keep one release identity {#release-identity}

The native payload and the GoReleaser archives must carry the same version and source commit. `packaging/mac-release.py` exports `MACOS.md`, `MACOS.json`, `bin/barn`, `bin/barn-hosts-helper`, and `Barn.app`; its manifest records file modes, digests, and signing state. VM disks, credentials, restore images, and installed services are outside this payload.

The app's bundle identifier is `com.pgsty.barn`; its internal executable is `barn-mac-runner`. The CLI checks the versioned runner protocol and also recognizes the earlier `Barn Mac.app` bundle name. Replacing the app preserves VM state under `$BARN_HOME/mac`.

Signing order matters because the CLI embeds the helper's digest:

1. Build and sign `barn-hosts-helper`.
2. Embed that signed helper's SHA-256 when building `barn`, then sign the CLI.
3. Sign `Barn.app` with hardened runtime and a secure timestamp.
4. Submit the CLI, helper, and app together to Apple for notarization. After acceptance, staple the app, validate its ticket, and check Gatekeeper.
5. Export and re-extract the payload, then recheck signatures and the stapled ticket. During release assembly, replace the Darwin arm64 archive's CLI/helper with these exact signed bytes and regenerate its SPDX document and checksums.
{.steps}

The payload builder and archive verifiers enforce this pairing. Signing the helper again after building the CLI changes the digest and breaks it.

## Build a formal release locally {#local-release}

Use an Apple Silicon Mac with macOS 27+, Xcode 27+, the [locked toolchain](../../start/source-build/), a Developer ID Application identity, and a stored `notarytool` profile. Select the identity with `security find-identity -v -p codesigning`; create the profile with `xcrun notarytool store-credentials`. Keep certificate private keys and passwords outside the repository.

Check out a clean source tree tagged `v$RELEASE_VERSION`, setting `RELEASE_VERSION` to the intended release version. Choose a new artifact directory outside the source repository:

```bash
export BARN_CODESIGN_IDENTITY='Developer ID Application: your organization (TEAMID)'
export BARN_NOTARY_PROFILE=barn-release
export BARN_MAC_REQUIRE_NOTARIZATION=1
VERSION="${RELEASE_VERSION:?Set RELEASE_VERSION to the checked-out release tag version}"
COMMIT="$(git rev-parse HEAD)"
export SOURCE_DATE_EPOCH="$(git show -s --format=%ct HEAD)"
export BARN_BUILD_DATE="$(date -u -r "$SOURCE_DATE_EPOCH" +%Y-%m-%dT%H:%M:%SZ)"
RELEASE_DIR="$(mktemp -d "${TMPDIR:-/tmp}/barn-release.XXXXXX")"

python3 packaging/mac-release.py build \
  "$VERSION" "$COMMIT" "$SOURCE_DATE_EPOCH" "$RELEASE_DIR/native.tar.gz"
BARN_MAC_PAYLOAD="$RELEASE_DIR/native.tar.gz" \
  make release-local VERSION="$VERSION" OUTPUT="$RELEASE_DIR/assets"
```

The formal native build and `release-local` enforce the `make catalog-check` gate before building. Synchronize and test any changed official catalog first, following the [release gates](../engineering/#release-outputs-and-gates). A snapshot or `uncommitted` payload cannot serve as a formal local release. `release-local` verifies archives, packages, SBOMs, checksums, and CLI/helper pairing, and writes the assembled assets to the specified directory.

For packaging development, `BARN_MAC_PAYLOAD=/absolute/native.tar.gz make release-snapshot` exercises native payload composition. Match the payload to the snapshot version selected by `.goreleaser.yaml`—for example, `1.0.1-next` after `v1.0.0`—and use `uncommitted` for a dirty checkout or the full commit for clean source. Snapshots accept ad-hoc signatures; formal release verification requires a notarized Developer ID payload.

## Configure automated signing {#ci-signing}

The tag workflow uses all six repository secrets below. With none configured, it skips automatic release creation so maintainers can use the local path. A partial set fails immediately; with all six present, a native build, signing, or notarization failure blocks release assembly.

| Secret | Value |
|---|---|
| `MAC_CERTIFICATE_BASE64` | Base64-encoded Developer ID Application `.p12`, including the private key |
| `MAC_CERTIFICATE_PASSWORD` | Password protecting the `.p12` |
| `MAC_CODESIGN_IDENTITY` | Imported identity name or certificate fingerprint |
| `MAC_NOTARY_KEY_BASE64` | Base64-encoded App Store Connect API `.p8` key |
| `MAC_NOTARY_KEY_ID` | API key identifier |
| `MAC_NOTARY_ISSUER` | API issuer identifier |
{.wide .expand}

The [Mac workflow](https://github.com/pgsty/barn/blob/main/.github/workflows/mac.yml) imports signing material into an ephemeral runner keychain and removes it at the end of the job. Pull requests and snapshots use ad-hoc builds. The [release workflow](https://github.com/pgsty/barn/blob/main/.github/workflows/release.yml) creates a draft after verifying the assembled payload.

## Verify installation and publish {#acceptance}

Run `make check`, `make mac-native-test`, and a full snapshot with the native payload. Exercise first installation, repeated installation, and upgrade in an isolated directory. On a supported physical Mac, verify startup, SSH, the desktop window, and normal shutdown using the packaged app. App replacement must preserve instance IDs, machine IDs, SSH keys, and host pins.

The existing [`tests/mac-live-acceptance.py`](https://github.com/pgsty/barn/blob/main/tests/mac-live-acceptance.py) requires an absolute `--barn` path, a dedicated disposable `--home`, a separate new or empty `--output` evidence directory, and explicit `--allow-test-root` authorization for that test root. Inspect the sequence with `--plan` first. `--gui` adds desktop/clipboard checks; `--allow-download` adds Apple download when no base is prepared. The harness preserves failed state and evidence. Isolate the process's home directory as well as `BARN_HOME` when testing SSH integration, because managed `~/.ssh/config` entries live outside the VM state root.

Release assembly generates `barn.rb` from `packaging/homebrew/barn.rb.tmpl`. The formula installs `barn` into `bin`, and the helper and app into `libexec`. Keep its install/test logic aligned with the tap. Versions with a suffix need an explicit `version` line because Homebrew may infer `64` from the architecture suffix; plain versions omit that line. The `0.9.1` public archive predates app delivery and supports Linux guests only.

After checking the local output, push the source and tag, upload the files to a draft GitHub Release, and verify the uploaded bytes before publishing. Mark versions below `1.0.0` and versions with a prerelease suffix as pre-releases; stable releases become latest. Update all four Homebrew platform URLs and checksums after the assets are public, then verify the public archives, installer, and Homebrew upgrade against those released bytes. Record signing, notarization, VM acceptance, and public installation results separately in the [validation history](../history/).
