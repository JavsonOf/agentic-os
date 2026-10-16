# OpenCode 2 na telefonie (Termux) jako agent w Agentic OS

OpenCode to agent do programowania: czyta i zmienia pliki projektu i uruchamia komendy. Agentic OS nie
uruchamia go u siebie, bo serwer przechowuje klucze API. OpenCode działa obok, a Agentic OS zleca mu zadania
przez **mostek** (`scripts/opencode_bridge.py`), tak jak każdemu agentowi zewnętrznemu.

Na Androidzie OpenCode nie działa bezpośrednio w Termux. Działa w Debianie uruchomionym w Termux przez
`proot-distro`. Wszystko poniżej robisz na telefonie, bez komputera.

## 1. Debian w Termux

W Termux (z F-Droid albo GitHub, nie ze Sklepu Play):

```bash
pkg update && pkg upgrade -y
pkg install proot-distro -y
proot-distro install debian
proot-distro login debian
```

Od tej chwili jesteś w Debianie (znak zachęty się zmieni). Następne kroki robisz tutaj.

## 2. OpenCode 2 w Debianie

```bash
apt update && apt install -y curl ca-certificates python3 git
curl -fsSL https://opencode.ai/v2/install | bash
exec bash            # żeby powłoka zobaczyła nową komendę
opencode --version   # powinno pokazać 2.x
```

Podłącz dostawcę modelu (np. ten sam co w Agentic OS). Klucz wpisujesz tylko w OpenCode na telefonie:

```bash
opencode auth login
```

Szybka próba: `opencode run "Napisz jedno zdanie po polsku"`.

## 3. Mostek

Pobierz mostek i ustaw stały token (wymyśl długi, losowy ciąg albo użyj komendy poniżej):

```bash
curl -fsSLO https://raw.githubusercontent.com/JavsonOf/agentic-os/main/scripts/opencode_bridge.py
echo "export OPENCODE_BRIDGE_TOKEN=$(python3 -c 'import secrets; print(secrets.token_urlsafe(24))')" >> ~/.bashrc
source ~/.bashrc
python3 opencode_bridge.py --workdir ~/opencode-projekty
```

Mostek pokaże adres `http://127.0.0.1:8765`. Zostaw to okno otwarte. Pliki, które OpenCode tworzy i zmienia,
lądują w folderze `~/opencode-projekty` (inny folder wskażesz przez `--workdir`). Token odczytasz komendą
`echo $OPENCODE_BRIDGE_TOKEN`.

Opcje: `--model anthropic/claude-sonnet-4-5` (który model ma używać OpenCode), `--timeout 280` (limit jednego
zadania w sekundach, musi być poniżej 300, bo tyle Agentic OS czeka na odpowiedź).

## 4. Połączenie z Agentic OS

**Agentic OS w Termux na tym samym telefonie:** w War Room otwórz **Ty → Agenci → 🔌 Podłącz zewnętrznego
agenta**, w polu „Gotowy szablon” wybierz **OpenCode** i wpisz:

- adres: `http://127.0.0.1:8765`
- klucz: token mostka

**Agentic OS w chmurze (Oracle, Hetzner…):** serwer nie widzi telefonu, więc mostek potrzebuje publicznego adresu
przez tunel, np. w drugim oknie Termux: `pkg install cloudflared` i `cloudflared tunnel --url http://127.0.0.1:8765`.
Tunel poda adres `https://….trycloudflare.com`, który wpisujesz w War Room razem z tokenem. Bez tokenu mostek
odrzuca każde zadanie.

## Żeby działało w tle

- W Termux przesuń powiadomienie w dół i wybierz **Acquire wakelock**, a w ustawieniach Androida wyłącz
  oszczędzanie baterii dla Termux. Inaczej system uśpi mostek po wyłączeniu ekranu.
- Każdy program (Agentic OS, mostek, tunel) działa w osobnym oknie Termux: przesuń od lewej krawędzi i wybierz
  **New session**.

## Bezpieczeństwo

- OpenCode może uruchamiać komendy na telefonie. Debian w `proot` to wygoda, a nie zabezpieczenie: OpenCode ma te
  same uprawnienia co Termux. Jeśli Agentic OS działa na tym samym telefonie, pliki z jego kluczami są w zasięgu
  OpenCode. Daj OpenCode osobny folder (`--workdir`) i zlecaj mu tylko zadania programistyczne.
- Mostek domyślnie słucha tylko na tym telefonie (`127.0.0.1`). Nie zmieniaj tego na `0.0.0.0` w publicznej sieci
  Wi-Fi. Do dostępu z zewnątrz używaj tunelu.
- Tokenu nie wklejaj w czat ani do repozytorium. Gdy wycieknie, ustaw nowy w `~/.bashrc` i zmień go w War Room.
