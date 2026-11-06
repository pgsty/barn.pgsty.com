# First-run recording

`static/images/barn-first-run.cast` is the terminal recording on the home
page quick start. It is a real Barn first run on an Ubuntu 26.04 x86_64 host
(`m3`), driven from a Mac with `expect` and captured with `asciinema`.

## What the recording shows

The typed commands are exactly the Linux commands under it on the home page:
`curl … install.sh`, `bash install.sh`, `export PATH=…`, `barn version`,
`barn up` (answering the one `[Y/n]` prompt), `barn ssh` with `df -h /data`,
and `barn status`.

The Barn host network was installed beforehand with
`barn network install --yes` over SSH without a terminal. On a terminal,
Barn 1.0.0 authenticates with `sudo -v`, which asks for a password on hosts
whose sudo policy mixes `NOPASSWD: ALL` with a password rule, so a scripted
take cannot pass that step. The recording therefore starts from a host whose
network is ready, and the `barn up` plan shows only the `config` row.

`demo.rc` sets the prompt, terminal size, a local HTTP proxy for GitHub, and
`BARN_REPO=https://repo.pigsty.cc/barn` so the image downloads from the China
mirror. None of it appears in the recording.

## Re-recording

1. Reset the host: destroy the demo lab, delete the cached image under
   `~/.barn/images/`, remove the `~/.local/bin` install, and leave
   `~/barn-lab` empty. Copy `demo.rc` to `/tmp/barn-demo.rc` on the host.
2. Record (`BARN_CAST_HOST` defaults to `m3`):

   ```bash
   asciinema rec --headless --overwrite --window-size 80x24 -f asciicast-v2 \
     -c "expect demo.exp" --return take.cast
   ```

3. Spread each command's echo over its typing time, then cap pauses and
   compress the download and boot waits. Output bytes are unchanged:

   ```bash
   python3 typing.py take.cast typed.cast
   python3 retime.py typed.cast barn-first-run.cast --max-gap 1.5 \
     --squeeze "Downloading image u24:Verifying downloaded image:6" \
     --squeeze "0/1 nodes ready:1 node ready:3" \
     --title "Barn 1.0.0 first run on Ubuntu 26.04"
   ```

4. Check the file for secrets (`retime.py` drops the `command` and `env`
   header keys), copy it to `static/images/`, and set the `poster` time in
   `data/home/*.yaml` to a frame just after `1 node ready`.
