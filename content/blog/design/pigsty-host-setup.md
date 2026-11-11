---
title: "Pigsty host setup: fixed names and CA trust"
linkTitle: "Pigsty host setup"
description: "A small, explicit macOS and Linux setup operation for stable Pigsty portal names and the lab's root CA."
date: 2026-11-11
weight: 72
categories: [Design]
tags: [Pigsty, DNS, Security]
icon: fa-solid fa-lock
---

**Recommend one optional host setup operation: install a fixed set of Pigsty names and trust the lab's public root CA certificate.** Keep one entry address, defaulting to `10.10.10.10`, and reuse the same CA across ordinary lab rebuilds. With unchanged names, address and CA trust, setup is a no-op and needs no elevation. This gives the common lab a mostly one-time host integration step.

**Status — 2026-11-11: proposal, not implemented.** This narrows the first delivery from the earlier [full host-DNS design](/blog/design/pigsty-host-dns/). General inventory extraction, dynamic node/PG/VIP publication, split DNS and a resident DNS service remain optional future work. Their implementation is not a prerequisite for this fixed profile. This review changed documentation only; it did not read a CA private key, install trust, modify system hosts or operate VMs.

## Publish a small, stable name profile {#fixed-names}

Proposed `core-v1` contains eight exact names. All point to one explicitly chosen entry IP; version the list so an application being enabled or disabled does not change host configuration.

| Names | Intended use |
|---|---|
| `i.pigsty` | Pigsty home, monitoring and paths served by the home portal |
| `sss.pigsty`, `m.pigsty` | Object-storage service and optional console portal |
| `adm.pigsty`, `ddl.pigsty` | Optional pgAdmin and Bytebase portals |
| `supa.pigsty`, `api.pigsty`, `cli.pigsty` | Reserved application/API aliases |
{.wide}

```text {title="Proposed core-v1 hosts payload"}
10.10.10.10 i.pigsty sss.pigsty m.pigsty adm.pigsty ddl.pigsty supa.pigsty api.pigsty cli.pigsty
```

Here `*.pigsty` describes a family of exact names. `/etc/hosts` has no wildcard matching. A new arbitrary name such as `new-app.pigsty` requires a reviewed profile update; a real wildcard resolver remains a separate option. Keep `i.pigsty` first on the line for stable canonical-name ordering.

The list builds on Pigsty's [default DNS aliases](https://github.com/pgsty/pigsty/blob/8046eb4cbd65b2eef7c9e11b4e7ba4f401bec5bd/roles/infra/defaults/main.yml) and [MinIO service name](https://github.com/pgsty/pigsty/blob/8046eb4cbd65b2eef7c9e11b4e7ba4f401bec5bd/roles/minio/defaults/main.yml). Some are deliberately reserved before the application exists. Resolving a name does not install its application, open its port or add it to Nginx. In particular, `sss.pigsty` may use port 9000, while a portal normally uses 443.

The single-entry profile fits a lab whose listed services are on, or proxied through, that entry. If storage or an application lives elsewhere without such a proxy, use an explicit static mapping for that service through the broader hosts interface. Do not discover another target from backend endpoints or select the first infra node. The address must satisfy Barn's private IPv4 `/24` and `.9`–`.254` rules. Custom subnets use an explicit `--ip`; this command does not reinterpret `admin_ip` or Jinja.

## Give the user one setup entry point {#workflow}

Put the Pigsty-specific profile in proposed `bin/sandbox-host`. Barn supplies generic hosts and certificate operations through its existing privileged boundary. All command examples below describe **new interfaces**.

```bash {title="Proposed setup, inspection and removal"}
bin/sandbox-host setup --ip 10.10.10.10 --ca files/pki/ca/ca.crt
bin/sandbox-host setup --ip 10.10.10.10 --ca files/pki/ca/ca.crt --apply
bin/sandbox-host status
bin/sandbox-host status --probe
bin/sandbox-host remove --apply
```

`setup` previews by default. The plan shows the exact names/IP, CA subject, validity and SHA-256 fingerprint, trust destination, additions/removals and ownership. `--apply` authorizes that concrete operation; combine both changes into one setup invocation and reuse one administrator-authentication session where the OS permits. System policy controls the number of authentication prompts. There is no persistent passwordless grant or background process.

`core-v1` replaces Barn's one complete hosts snapshot. If an earlier node/service snapshot exists, show the names being removed before applying; preserve every foreign hosts line. This keeps publication deterministic without silently merging stale entries.

The recommended order is: initialize Pigsty so its CA exists, obtain the public certificate, then perform this host setup once. If the repository is shared with the controller, the public certificate may already be at the shown path. Otherwise copy only `ca.crt` through the established, host-key-verified SSH connection. Optional `--dns-only` supports earlier name setup; `--ca-only` installs trust later. These are separate operations and can require separate authorization. Missing CA input must not silently apply half of a combined request.

`status` reads ownership and effective hosts/trust state without changing it. `status --probe` additionally checks system name resolution and the home portal's HTTPS chain and hostname. Report `names`, `system trust`, and `portal HTTPS` separately: an offline guest can coexist with correctly installed host configuration. A TLS check must use normal certificate verification, without insecure mode or a supplied CA override that bypasses the store being tested.

For noninteractive first trust or CA replacement, require the expected public-certificate fingerprint with proposed `--ca-sha256`; compare it before elevation. `--apply` is still required. Authorization uses a nonblocking path and fails cleanly if unavailable. Repeated identical setup requires no authentication. Normal `barn setup`, `up`, `stop` and `destroy` never implicitly import a CA.

## Trust the intended CA and preserve its identity {#ca-identity}

The source is the lab's existing `files/pki/ca/ca.crt`. Pigsty's [CA role](https://github.com/pgsty/pigsty/blob/8046eb4cbd65b2eef7c9e11b4e7ba4f401bec5bd/roles/ca/tasks/main.yml) creates or reuses this CA on the controller. Keep the controller's PKI persistent across rebuilds. The host receives only the public certificate; the private key remains with Pigsty.

Accept one bounded PEM/DER self-signed root certificate in the first version. Verify parsing, self-signature, validity, CA basic constraints and certificate-signing key usage. Reject a private-key payload, a leaf certificate, an ambiguous bundle or an unsupported intermediate chain. Identify the CA by SHA-256 of its DER bytes, not the common name `pigsty-ca`; reformatting PEM must remain a no-op. Bind the parsed certificate and hosts payload to the reviewed plan and verify them again in the privileged helper.

**System trust in this CA is broader than the eight names.** Neither these hosts entries nor the CA's display name restrict its signing authority to `.pigsty`. The setup preview must state that scope. Use TLS-specific trust on macOS where supported; do not disable hostname/expiry checks or silently change other application policies.

Importing the root also leaves server-certificate requirements intact. Pigsty's [Nginx certificate task](https://github.com/pgsty/pigsty/blob/8046eb4cbd65b2eef7c9e11b4e7ba4f401bec5bd/roles/infra/tasks/nginx.yml) includes configured portal names in SAN. It does not automatically certify every reserved core alias. Enabling a portal requires its matching virtualhost and a valid SAN-bearing leaf certificate; a wildcard certificate and wildcard DNS are independent choices. A leaf renewal under the same CA needs no host trust change.

## Use native trust stores, with explicit application coverage {#platforms}

| Platform | Proposed system adapter | Precise removal |
|---|---|---|
| macOS | System Keychain plus administrator TLS trust, using the supported `security` operations; select SSL policy, with no allowed-error exceptions | Remove this certificate's owned administrator trust, then its owned keychain item, identified by fingerprint; preserve pre-existing certificates/policies |
| Debian / Ubuntu | Own PEM `.crt` file at `/usr/local/share/ca-certificates/barn-pigsty-<sha256>.crt`; regenerate with `update-ca-certificates` | Remove only the matching owned file and regenerate/verify the store; use the platform's supported removal refresh |
| RHEL / Rocky / AlmaLinux | Own anchor at `/etc/pki/ca-trust/source/anchors/barn-pigsty-<sha256>.crt`; run `update-ca-trust extract` | Remove only the matching owned anchor, extract again and verify |
| Other Linux trust layout | Return an unsupported-adapter diagnostic and an exportable public certificate | Keep explicit manual trust installation available |
{.wide .expand}

These mechanisms follow [Apple trust settings](https://support.apple.com/en-asia/guide/keychain-access/kyca11871/mac), [Ubuntu's installation/removal procedure](https://ubuntu.com/server/docs/how-to/security/install-a-root-ca-certificate-in-the-trust-store/) and [RHEL's shared trust store](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/securing_networks/using-shared-system-certificates_securing-networks). Local macOS `security help` confirmed administrator-store selection, the SSL policy and SHA-256 item deletion syntax; no mutation command was executed. Linux adapters require capability detection, including installed CA tooling, before a combined apply.

System trust and application trust have separate acceptance results. macOS Chrome supports locally configured SSL trust in the System Keychain; Firefox supports system roots on macOS when its corresponding setting is enabled. Linux Firefox, Chrome, isolated packages and language runtimes need their own verification. The initial tool must report a browser that still rejects the CA, and provide a separate explicit import path; it must not quietly rewrite every browser profile or claim that a successful system update made every browser ready. See [Chrome's local-trust behavior and Certificate Manager](https://chromium.googlesource.com/chromium/src/+/main/net/data/ssl/chrome_root_store/faq.md) and [Mozilla's platform-specific CA integration](https://support.mozilla.org/en-US/kb/setting-certificate-authorities-firefox).

## Make repeated setup and cleanup predictable {#lifecycle}

| Event | Host action and authorization |
|---|---|
| First names + CA setup | Review both, then perform the required privileged writes |
| Same IP, names and effectively trusted CA | No-op; no sudo and no unnecessary trust-store regeneration |
| Guest stop/start/rebuild, same CA retained | No host update |
| Leaf certificate renewal under the same CA | No host update |
| Entry IP or fixed-name profile changes | Explicit hosts update; retain unchanged CA trust |
| New CA fingerprint | Stop ordinary reconciliation; require explicit proposed `--replace-ca OLD_SHA256`, with the new CA previewed/pinned |
| `destroy` or deletion of `BARN_HOME` | Keep integration until explicit removal; ownership remains recoverable outside deployment state |
| `remove --apply` | Remove owned names and trust only; preserve everything that predated setup |
{.wide}

Keep a root-owned receipt outside `BARN_HOME`: owner UID, profile version, canonical names/IP, public CA DER/fingerprint, exact trust target, prior existence, and effects this operation owns. An already trusted identical CA is `pre-existing`, not newly owned. A pre-existing conflicting trust policy needs explicit manual resolution; never broaden it automatically. If another source still trusts a removed certificate, report that remaining trust rather than removing foreign copies.

CA rotation is explicit. Validate the new root, install and verify its trust, then remove the old trust only when the receipt proves ownership and the operator requested replacement. Switching a deployment to a new CA may also require server-certificate rollout; the host command does not perform it. Reuse of a lab CA by another lab must be accounted for before old trust is retired.

Hosts and a trust store do not form one atomic transaction. Preflight both before either write; apply CA trust and then the reviewed hosts snapshot, recording each completed step. On failure, undo only changes newly made by this attempt that still match its receipt. Preserve concurrent edits and report any partial state. For normal removal, delete the owned hosts publication and then owned trust. Never restore an old whole hosts file or whole keychain/trust-settings dump.

## Keep the implementation small and reviewable {#implementation}

1. **Pigsty profile:** implement `bin/sandbox-host` with the fixed list, explicit IP and public CA input. It does not evaluate Ansible, inspect live roles or regenerate CA material. Existing `# pigsty dns` lines are reported for the explicit migration described in the [DNS study](/blog/design/pigsty-host-dns/#lifecycle-and-migration).
2. **Barn hosts boundary:** reuse the single managed block, canonical records and complete preview. Add a hosts-only consumption path for the existing `all.vars.vm_hosts` shape: no fake VM node and no second VM inventory format. Infer the one private `/24` from the literal addresses and validate its reserved range. This is a required new capability; the audited prototype currently rejects a records-only inventory. Keep ordinary VM inventory validation unchanged. Apply the earlier inventory-source guard so bare node publication cannot erase core names.
3. **Barn trust boundary:** add generic CA plan/status/install/remove operations and a combined reviewed operation for the wrapper. Extend the one existing privileged helper with bounded, typed operations and fixed platform destinations. Pigsty domain names remain outside Barn. Complete helper-side scope validation and the host-wide lock before this integration; do not grant permanent sudo access to the present helper.
4. **Acceptance:** require repository checks and real macOS and Linux acceptance before documenting the command as available. The broader exporter and DNS daemon are not release gates for this profile.
{.steps}

| Test area | Required evidence |
|---|---|
| Fixed data | Exact eight-name snapshot, custom IP, reserved-address rejection, casing/conflicts, no inventory or service dependency |
| CA input | Fingerprint identity across PEM/DER, invalid/expired/non-CA/private-key/bundle rejection, missing CA, changed input after preview |
| Repetition and ownership | Second run makes no privileged call; pre-existing trust survives removal; same-CN different-CA does not replace silently; foreign edits are preserved |
| Failure and recovery | Trust-tool failure, hosts conflict/race, interruption between steps, noninteractive authorization failure, reinstall after state removal |
| Real clients | macOS System Keychain and default TLS client; Debian-family and RHEL-family trust stores; system resolver; home portal SAN/chain; supported browsers tested separately without insecure overrides |
| Lifecycle | Leaf renewal and VM restart need no setup; CA replacement and entry-IP change show only the necessary updates; complete removal verifies owned effects are gone |
{.wide}

This revision verified source semantics and official platform mechanisms and ran documentation checks. It did not validate an installed CA adapter or a live HTTPS portal. The product default is settled: fixed names plus native system CA trust, explicit setup, no-op repetition, and owned cleanup. The eventual command release number and each advertised browser/platform combination remain acceptance decisions.
