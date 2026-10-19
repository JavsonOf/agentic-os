# Klucz podpisu aplikacji na Androida

Każda wersja aplikacji jest podpisana tym samym **prywatnym** kluczem. Dzięki temu nowa wersja instaluje się
na poprzedniej, a nikt inny nie może wydać aplikacji, którą Android uzna za aktualizację Twojej.

Klucz nie jest w repozytorium. Żyje tylko w sekretach repozytorium na GitHubie, a automat (`android.yml`)
odkodowuje go na czas budowania wydania:

| Sekret | Co zawiera |
|---|---|
| `ANDROID_KEYSTORE_BASE64` | plik klucza (`.keystore`) zakodowany w base64 |
| `ANDROID_KEYSTORE_PASSWORD` | hasło do klucza |

Bez tych sekretów zwykłe buildy (np. w pull requestach) dostają tymczasowy klucz testowy, a publikacja
wydania kończy się błędem, żeby nigdy nie wyszła wersja podpisana złym kluczem.

## Jak utworzyć klucz (raz)

W terminalu GitHub Codespace, w folderze repozytorium:

```bash
gh auth login            # jeśli jeszcze nie jesteś zalogowany; wybierz GitHub.com i zaloguj przez przeglądarkę
bash scripts/new_android_key.sh
```

Skrypt tworzy klucz z losowym hasłem w `~/agentic-os-signing/` (poza repozytorium) i sam zapisuje oba
sekrety. Jeśli nie da rady, pokaże, jak dodać je ręcznie w **Settings → Secrets and variables → Actions**.
Wartości wklejasz tylko tam, nigdy do czatu ani do repozytorium.

**Zrób kopię zapasową** pliku `~/agentic-os-signing/agentic-os-release.keystore`, np. pobierz go z Codespace
i trzymaj w bezpiecznym miejscu. Po usunięciu Codespace plik zniknie, a bez klucza kolejne wersje nie
zainstalują się na poprzednich.

## Budowanie lokalne

```bash
export ANDROID_HOME=/ścieżka/do/android-sdk
gradle -p android assembleRelease          # bez klucza: APK z kluczem testowym, tylko do prób
# z kluczem:
ANDROID_KEYSTORE_PATH=~/agentic-os-signing/agentic-os-release.keystore ANDROID_KEYSTORE_PASSWORD=… \
  gradle -p android assembleRelease
```

## Dawny klucz

Do wersji v0.3.0 aplikacja była podpisywana kluczem, który leżał publicznie w repozytorium. Ten klucz
należy uznać za spalony i nie wolno go już używać. Wersje podpisane nowym kluczem nie zainstalują się na
starych, więc przed pierwszą instalacją nowej wersji trzeba raz odinstalować aplikację (adres serwera
i logowanie trzeba wtedy podać ponownie).
