# macOS homepage recording

`static/images/barn-first-run.cast` is a real Apple Silicon recording of
Homebrew installing Barn, followed by a four-node Pigsty lab. The typed
commands match the macOS block on both homepages:

```bash
brew install pgsty/infra/barn
cd pigsty
./configure -c full
barn up
barn status
```

The 2026-11-09 take uses Barn 1.1.0 on macOS 27.0.1, QEMU 11.1.3, and Pigsty
commit `01f3e3449a91cbb24e4a5271c421b3e1fb26e345`. All four guests use
`u24@20261017.0.1/arm64`, 2 vCPUs, 4 GiB RAM, a 64 GiB root disk and a
128 GiB `/data` disk. `barn up` completed in 52 seconds. The original take
lasts 81 seconds; the edited timeline lasts 24.2 seconds and plays in about
19 seconds at 1.25× speed. The cast is about 138 KiB.
SSH, guest architecture and `/data` were verified on all four nodes.

## Recording environment

Use an idle Apple Silicon Mac with Homebrew, QEMU, asciinema 3, Expect and
Python 3 installed. Barn's host network must already be configured, with no
VMs occupying `10.10.10.10–13`. These are the recording prerequisites.

Keep the original take, package cache, VM state and source checkout outside
Git. Use a clean archive of Pigsty's tracked source so the recording never
changes a working inventory or copies local PKI files. `demo.rc` uses a
dedicated `BARN_HOME`; the account's `HOME` remains unchanged. It also
disables Homebrew auto-update and cleanup for the session.

```bash
export BARN_CAST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/barn-homepage.XXXXXX")"
mkdir -p "$BARN_CAST_ROOT/session/pigsty" "$BARN_CAST_ROOT/barn-home" \
  "$BARN_CAST_ROOT/brew-cache"
git -C ~/pgsty/pigsty archive HEAD | tar -x -C "$BARN_CAST_ROOT/session/pigsty"
# Reuse public registry metadata; the Barn package is still downloaded afresh.
cp -R "$(brew --cache)/api" "$BARN_CAST_ROOT/brew-cache/"
BARN_HOME="$BARN_CAST_ROOT/barn-home" barn setup \
  -f "$BARN_CAST_ROOT/session/pigsty/conf/ha/full.yml" --dry-run
```

Confirm the plan needs no privileged changes. Stop any Barn guests before
uninstalling the active Barn version, then record from this site's root:

```bash
HOMEBREW_NO_INSTALL_CLEANUP=1 brew uninstall barn
# Optional: use an existing local proxy for GitHub access.
# export BARN_CAST_PROXY=http://127.0.0.1:8888
asciinema rec --headless --window-size 80x24 -f asciicast-v2 --return \
  -c "expect $PWD/bin/first-run-cast/demo.exp" "$BARN_CAST_ROOT/raw.cast"
```

The driver checks every command's exit status. It types commands into a real
interactive shell, answers the setup prompt if present, and stops on an
unexpected sudo prompt or a command failure. The successful take used the
China image repository (`BARN_CAST_REPO` can override it).

## Homepage edit

```bash
python3 bin/first-run-cast/prepare.py "$BARN_CAST_ROOT/raw.cast" "$BARN_CAST_ROOT/prepared.cast"
python3 bin/first-run-cast/typing.py "$BARN_CAST_ROOT/prepared.cast" "$BARN_CAST_ROOT/typed.cast"
python3 bin/first-run-cast/retime.py "$BARN_CAST_ROOT/typed.cast" \
  "$BARN_CAST_ROOT/homepage.cast" --max-gap 0.7 \
  --squeeze "boot 0/4 nodes:boot 4/4 nodes:8" \
  --title "Barn 1.1.0 on macOS · Homebrew → Pigsty full"
```

`prepare.py` removes this host's unrelated `youssofal/mtplx` tap warning and
the final shell `exit`, and repairs Expect's misdecoded Homebrew beer emoji.
All Barn and Pigsty output remains intact. Future takes disable Homebrew
emoji in `demo.rc`. `typing.py` spreads buffered command echoes over their
actual typing interval. `retime.py` changes timestamps only and drops the
`command` and `env` header fields. Keep the unedited take outside Git.

Check the text for private data and watch the entire edit. Copy only the
small edited cast to `static/images/barn-first-run.cast`. Set both homepage
`poster` values to the final `barn status` table (23.63 seconds in this edit).
The shortcode uses `speed="1.25"` and `idleTimeLimit="0.7"`; download and boot
progress also need timestamp compression because progress updates are not idle.

The homepage replays the same output in an 80×18 terminal with `fit="both"`.
The progress table fits completely in this viewport; earlier output scrolls
naturally. On desktop, the frame follows the adjacent text column’s height.
On smaller screens it uses a compact 16:9 playback area. Keep the raw 80×24
take as the unedited source.
Run `make check` and inspect playback on desktop and mobile, in both themes.

The raw take's SHA-256 is
`06d2b129092c9092afdd328a4a3eaf99e5413ffd6ee8e7c4330a9159748dec92`.
The homepage edit's SHA-256 is
`cb1d8e97239b6b0d144d1d8fa0c802dd6a81a4217b3774b40864ced3b1bd0e19`.
