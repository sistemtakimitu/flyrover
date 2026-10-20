# macwsl — Mac için WSL benzeri Linux terminali

Windows'taki `wsl` komutunun Mac karşılığı. Tek komutla Ubuntu (veya Debian, Fedora, Arch) kurar, `macwsl` yazınca Linux terminaline girersiniz.

Arkada [Lima](https://lima-vm.io) ve Apple'ın kendi sanallaştırma altyapısı (Virtualization.framework) çalışır. Linux, hafif bir sanal makinede açılır:

- Mac'teki ev dizininiz (`~`) Linux içinde aynı yolda ve **yazılabilir** olarak görünür.
- Sanal makine ilk komutta kendiliğinden açılır, `macwsl --shutdown` ile kapanır.
- Apple Silicon (M1–M4) Mac'lerde ARM64 Linux çalışır. Intel Mac'lerde x86_64.

## Gereksinimler

- macOS 13 (Ventura) veya üstü
- [Homebrew](https://brew.sh). Lima'yı kurmak için kullanılır, `macwsl --install` Lima'yı kendisi kurar.

## Kurulum

```bash
cd tools/macwsl
./install.sh               # ~/.local/bin/macwsl
./install.sh --wsl-alias   # isterseniz ayrıca `wsl` komutu
macwsl --install           # Lima + Ubuntu 24.04
macwsl                     # Linux terminali
```

İlk `--install` Ubuntu imajını indirdiği için birkaç dakika sürer.

## WSL karşılıkları

| Windows (WSL)                 | Mac (macwsl)                   |
|-------------------------------|--------------------------------|
| `wsl --install`               | `macwsl --install`             |
| `wsl --install -d Debian`     | `macwsl --install Debian`      |
| `wsl`                         | `macwsl`                       |
| `wsl -d Debian`               | `macwsl -d debian`             |
| `wsl -e uname -a`             | `macwsl -e uname -a`           |
| `wsl --cd ~`                  | `macwsl --cd ~`                |
| `wsl -l -v`                   | `macwsl -l -v`                 |
| `wsl -l -o`                   | `macwsl -l -o`                 |
| `wsl -s Debian`               | `macwsl -s debian`             |
| `wsl -t Ubuntu`               | `macwsl -t ubuntu`             |
| `wsl --shutdown`              | `macwsl --shutdown`            |
| `wsl --unregister Ubuntu`     | `macwsl --unregister ubuntu`   |
| `wsl --update`                | `macwsl --update`              |

Tüm seçenekler için: `macwsl --help`

## Kaynak ayarları

CPU, bellek ve disk kurulum sırasında ayarlanır:

```bash
MACWSL_CPUS=4 MACWSL_MEMORY=8 MACWSL_DISK=60 macwsl --install
```

Kurulumdan sonra değiştirmek için `limactl edit macwsl-ubuntu` kullanılabilir.

## Nasıl çalışır

`macwsl`, Lima'nın `limactl` komutunu saran tek bir bash betiğidir. Her dağıtım `macwsl-<ad>` isimli bir Lima örneğidir (`macwsl-ubuntu`, `macwsl-debian`…). macwsl'e ait olmayan Lima örneklerine dokunulmaz. Varsayılan dağıtım `~/.config/macwsl/default` dosyasında saklanır.

## Testler

Gerçek sanal makine açmadan, sahte `limactl` ve `brew` ile çalışır (Linux'ta da çalışır):

```bash
bash tools/macwsl/tests/run_tests.sh
```
