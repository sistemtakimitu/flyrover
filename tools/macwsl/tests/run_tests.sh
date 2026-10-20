#!/usr/bin/env bash
# macwsl testleri: gerçek VM açmadan, sahte limactl/brew ile çalışır.
#   bash tools/macwsl/tests/run_tests.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
MACWSL="$HERE/../macwsl"
PASS=0
FAIL=0

setup() {
  WORK="$(mktemp -d)"
  export HOME="$WORK/home" MACWSL_CONFIG_DIR="$WORK/config"
  export FAKE_LOG="$WORK/log" FAKE_STATE="$WORK/state"
  mkdir -p "$HOME" "$WORK/bin"
  : > "$FAKE_LOG"; : > "$FAKE_STATE"
  # Sahte limactl: çağrıları kaydeder, örnekleri "ad|durum" satırları olarak tutar.
  cat > "$WORK/bin/limactl" <<'EOF'
#!/usr/bin/env bash
echo "limactl $*" >> "$FAKE_LOG"
set_status() { grep -v "^$1|" "$FAKE_STATE" > "$FAKE_STATE.tmp"; [ -n "$2" ] && echo "$1|$2" >> "$FAKE_STATE.tmp"; mv "$FAKE_STATE.tmp" "$FAKE_STATE"; }
case "$1" in
  --version) echo "limactl version 1.0.0" ;;
  list)
    if [ "$2" = --quiet ]; then cut -d'|' -f1 "$FAKE_STATE"; exit 0; fi
    fmt="$3"; name="${4:-}"
    while IFS='|' read -r n s; do
      [ -n "$name" ] && [ "$n" != "$name" ] && continue
      if [ "$fmt" = '{{.Status}}' ]; then echo "$s"; else echo "$n|$s"; fi
    done < "$FAKE_STATE" ;;
  start)
    name=""; last=""
    for a in "$@"; do case "$a" in --name=*) name="${a#--name=}" ;; esac; last="$a"; done
    set_status "${name:-$last}" Running ;;
  stop) set_status "$2" Stopped ;;
  delete) set_status "${!#}" "" ;;
  shell) echo "SHELL ${*:2}" ;;
esac
EOF
  chmod +x "$WORK/bin/limactl"
  export PATH="$WORK/bin:/usr/bin:/bin"
}

teardown() { rm -rf "$WORK"; }

run() { OUT="$("$MACWSL" "$@" 2>&1)"; CODE=$?; }

check() {
  local name="$1"; shift
  if "$@"; then
    PASS=$((PASS + 1)); echo "ok   $name"
  else
    FAIL=$((FAIL + 1)); echo "FAIL $name"; echo "     çıktı: $OUT"; echo "     log:"; sed 's/^/       /' "$FAKE_LOG"
  fi
}

has_log() { grep -qF -- "$1" "$FAKE_LOG"; }
has_out() { printf '%s' "$OUT" | grep -qF -- "$1"; }
code_is() { [ "$CODE" = "$1" ]; }

t_install_default() {
  run --install
  check "install: Ubuntu 24.04 kurar" has_log "limactl start --name=macwsl-ubuntu --tty=false --mount-writable template://ubuntu-24.04"
  check "install: varsayılanı ayarlar" [ "$(cat "$MACWSL_CONFIG_DIR/default")" = ubuntu ]
  : > "$FAKE_LOG"
  run --install Ubuntu
  check "install: ikinci kez kurmaz" sh -c "! grep -q 'start --name' '$FAKE_LOG'"
  check "install: zaten kurulu der" has_out "zaten kurulu"
}

t_install_resources() {
  MACWSL_CPUS=4 MACWSL_MEMORY=8 MACWSL_DISK=50 run --install -d Debian
  check "install: kaynak ayarlarını geçirir" has_log "--cpus=4 --memory=8 --disk=50 template://debian-12"
  check "install: -d ile dağıtım seçer" has_log "--name=macwsl-debian"
}

t_install_second_keeps_default() {
  run --install
  run --install Fedora
  check "install: ikinci dağıtım varsayılanı değiştirmez" [ "$(cat "$MACWSL_CONFIG_DIR/default")" = ubuntu ]
  check "install: ipucunda -d gösterir" has_out "macwsl -d fedora"
}

t_install_unknown() {
  run --install Windows95
  check "install: bilinmeyen dağıtım hata verir" code_is 1
  check "install: online listeye yönlendirir" has_out "--list --online"
}

t_install_needs_brew() {
  rm "$WORK/bin/limactl"
  run --install
  check "install: Homebrew yoksa açıklar" has_out "Homebrew bulunamadı"
  check "install: Homebrew yoksa hata kodu" code_is 1
}

t_install_via_brew() {
  mv "$WORK/bin/limactl" "$WORK/limactl.real"
  cat > "$WORK/bin/brew" <<EOF
#!/usr/bin/env bash
echo "brew \$*" >> "\$FAKE_LOG"
mv "$WORK/limactl.real" "$WORK/bin/limactl"
EOF
  chmod +x "$WORK/bin/brew"
  run --install
  check "install: Lima'yı brew ile kurar" has_log "brew install lima"
  check "install: brew sonrası dağıtımı kurar" has_log "template://ubuntu-24.04"
}

t_list() {
  run --install
  run --install Debian
  echo "default|Running" >> "$FAKE_STATE"   # macwsl'e ait olmayan Lima örneği
  limactl stop macwsl-debian >/dev/null
  run -l
  check "list: varsayılanı işaretler" has_out "ubuntu (varsayılan)"
  check "list: diğerlerini gösterir" has_out "debian"
  check "list: yabancı örnekleri gizler" sh -c "! printf '%s' \"\$1\" | grep -qx default" _ "$OUT"
  run -l -v
  check "list -v: durum gösterir" has_out "* ubuntu"
  check "list -v: durdurulmuş gösterir" has_out "Stopped"
}

t_list_empty() {
  run --list
  check "list: boşken kurulum önerir" has_out "macwsl --install"
}

t_list_online() {
  run --list --online
  check "list --online: Ubuntu var" has_out "Ubuntu-22.04"
}

t_shell_autostart() {
  run --install
  limactl stop macwsl-ubuntu >/dev/null
  : > "$FAKE_LOG"
  run
  check "shell: durmuşsa başlatır" has_log "limactl start --tty=false macwsl-ubuntu"
  check "shell: kabuk açar" has_out "SHELL macwsl-ubuntu"
}

t_exec() {
  run --install
  run -e uname -a
  check "exec: komutu çalıştırır" has_out "SHELL macwsl-ubuntu uname -a"
  run -- ls -la
  check "--: komutu çalıştırır" has_out "SHELL macwsl-ubuntu ls -la"
  run echo merhaba
  check "çıplak komut çalıştırır" has_out "SHELL macwsl-ubuntu echo merhaba"
}

t_cd() {
  run --install
  mkdir -p "$HOME/proje"
  (cd "$HOME" && "$MACWSL" --cd proje -e pwd) > "$WORK/out" 2>&1
  OUT="$(cat "$WORK/out")"
  check "--cd: göreli yolu mutlak yapar" has_out "SHELL --workdir=$HOME/proje macwsl-ubuntu pwd"
  run --cd "~"
  check "--cd ~: Linux ev dizininde açar" has_out "SHELL --workdir=/ macwsl-ubuntu sh -c"
}

t_distribution_missing() {
  run --install
  run -d debian
  check "-d: kurulu değilse hata" code_is 1
  check "-d: kurulum komutunu önerir" has_out "macwsl --install debian"
}

t_not_installed() {
  run
  check "shell: hiç kurulu yoksa yönlendirir" has_out "macwsl --install"
}

t_set_default() {
  run --install
  run --install Debian
  run --set-default Debian
  check "set-default: kaydeder" [ "$(cat "$MACWSL_CONFIG_DIR/default")" = debian ]
  run -e true
  check "set-default: sonra o kullanılır" has_out "SHELL macwsl-debian true"
  run -s yok
  check "set-default: kurulu olmayanı reddeder" code_is 1
}

t_shutdown_terminate() {
  run --install
  run --install Debian
  echo "default|Running" >> "$FAKE_STATE"
  run --shutdown
  check "shutdown: kendi örneklerini durdurur" has_log "limactl stop macwsl-debian"
  check "shutdown: yabancı örneğe dokunmaz" sh -c "! grep -q 'stop default' '$FAKE_LOG'"
  check "shutdown: sayıyı bildirir" has_out "2 dağıtım durduruldu"
  run -t ubuntu
  check "terminate: durmuşsa söyler" has_out "zaten durmuş"
}

t_unregister() {
  run --install
  run --unregister ubuntu < /dev/null
  check "unregister: onaysız etkileşimsizde reddeder" code_is 1
  check "unregister: silmez" sh -c "! grep -q delete '$FAKE_LOG'"
  run --unregister ubuntu -y
  check "unregister: -y ile siler" has_log "limactl delete --force macwsl-ubuntu"
  check "unregister: varsayılanı temizler" [ ! -f "$MACWSL_CONFIG_DIR/default" ]
}

t_misc() {
  run --frobnicate
  check "bilinmeyen seçenek hata verir" code_is 1
  run -d
  check "değersiz -d hata verir" code_is 1
  run --help
  check "help çalışır" has_out "Kullanım: macwsl"
  run --version
  check "version Lima sürümünü gösterir" has_out "limactl version 1.0.0"
  run -d "../kötü"
  check "geçersiz adı reddeder" has_out "Geçersiz dağıtım adı"
}

t_install_script() {
  BIN_DIR="$WORK/kurulum" bash "$HERE/../install.sh" --wsl-alias > "$WORK/out" 2>&1
  check "install.sh: macwsl kopyalar" [ -x "$WORK/kurulum/macwsl" ]
  check "install.sh: wsl kısayolu" [ -L "$WORK/kurulum/wsl" ]
}

for t in $(declare -F | awk '{print $3}' | grep '^t_'); do
  setup
  "$t"
  teardown
done

echo
echo "$PASS geçti, $FAIL başarısız"
[ "$FAIL" = 0 ]
