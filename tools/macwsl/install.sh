#!/usr/bin/env bash
# macwsl'i PATH üzerindeki bir dizine kurar.
#
#   ./install.sh                 # ~/.local/bin/macwsl
#   ./install.sh --wsl-alias     # ayrıca `wsl` kısayolu
#   BIN_DIR=/usr/local/bin ./install.sh
set -euo pipefail

BIN_DIR="${BIN_DIR:-$HOME/.local/bin}"
SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
WSL_ALIAS=0

for arg in "$@"; do
  case "$arg" in
    --wsl-alias) WSL_ALIAS=1 ;;
    -h|--help) sed -n '2,7p' "$0"; exit 0 ;;
    *) echo "install.sh: bilinmeyen seçenek: $arg" >&2; exit 1 ;;
  esac
done

mkdir -p "$BIN_DIR"
cp "$SRC_DIR/macwsl" "$BIN_DIR/macwsl"
chmod +x "$BIN_DIR/macwsl"
echo "Kuruldu: $BIN_DIR/macwsl"

if [ "$WSL_ALIAS" = 1 ]; then
  ln -sf "$BIN_DIR/macwsl" "$BIN_DIR/wsl"
  echo "Kısayol: $BIN_DIR/wsl -> macwsl"
fi

case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *)
    echo
    echo "UYARI: $BIN_DIR PATH'te değil. ~/.zshrc dosyanıza şunu ekleyin:"
    echo "  export PATH=\"$BIN_DIR:\$PATH\""
    ;;
esac

echo
echo "Sıradaki adım: macwsl --install"
