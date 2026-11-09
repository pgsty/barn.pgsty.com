# First-run recording

`static/images/barn-first-run.cast` is the terminal recording on the home
page quick start. It is a real Barn first run on an Ubuntu 26.04 x86_64 host
(`m4` for the 1.1.0 take), driven from a Mac with `expect` and captured with `asciinema`.

## What the recording shows

The typed commands are exactly the Linux commands under it on the home page:
`curl … install.sh`, `bash install.sh`, `export PATH=…`, `barn version`,
`barn up` (answering the one `[Y/n]` prompt), `barn ssh` with `df -h /data`,
and `barn status`.

The 1.1.0 take uses a dedicated test Unix account with a fresh home on an idle
host. QEMU and the Barn bridge are already installed; `barn setup --dry-run`
confirms that only the new inventory needs to be written and no root action
is required. Existing users' deployments, images, and SSH files are untouched.

`demo.rc` sets the prompt, terminal size, a local HTTP proxy for GitHub, and
`BARN_REPO=https://repo.pigsty.cc/barn` so the image downloads from the China
mirror. None of it appears in the recording.

## Re-recording

1. Use a dedicated disposable Unix account on a test host with no conflicting
   guest IPs. Its `~/.local/bin`, `~/.barn`, and `~/barn-lab` must be fresh;
   do not reset another user's lab. Confirm the host dependencies and network
   with `barn setup --dry-run`, then install `demo.rc` where the test account
   can read it.
2. Record after the release assets are public (`BARN_CAST_HOST` defaults to
   `m3`). For a separate test account, set `BARN_CAST_REMOTE_COMMAND` to the
   approved SSH-side launcher, for example `sudo -H -u barn-demo bash --rcfile
   /path/to/demo.rc -i`. The account inherits its own home through sudo:

   ```bash
   asciinema rec --headless --overwrite --window-size 80x24 -f asciicast-v2 \
     -c "expect demo.exp" --return take.cast
   ```

3. Spread each command's echo over its typing time, then cap pauses and
   compress the download and boot waits. Output bytes are unchanged:

   ```bash
   python3 typing.py take.cast typed.cast
   python3 retime.py typed.cast barn-first-run.cast --max-gap 1.5 \
     --squeeze "boot 0/1 nodes:boot 1/1 nodes:5" \
     --title "Barn 1.1.0 first run on Ubuntu 26.04"
   ```

4. Adjust squeeze boundaries to the actual progress text in the take. Check the file for secrets (`retime.py` drops the `command` and `env`
   header keys), copy it to `static/images/`, and set the `poster` time in
   `data/home/*.yaml` to a frame just after `boot 1/1 nodes`.
