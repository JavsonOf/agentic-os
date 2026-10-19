#!/usr/bin/env bash
# Creates the private signing key for the Android app and stores it as repository secrets.
# Run it once, e.g. in the GitHub Codespace terminal:  bash scripts/new_android_key.sh
# Needs keytool (JDK) and, for the automatic step, the GitHub CLI (gh) logged in with access to the repo.
set -euo pipefail

REPO="${REPO:-JavsonOf/agentic-os}"
DIR="${HOME}/agentic-os-signing"          # outside the repository, so it can never be committed
KEYSTORE="${DIR}/agentic-os-release.keystore"

command -v keytool >/dev/null || { echo "Brak programu keytool (JDK 17+). W Codespace: sudo apt-get install -y openjdk-17-jdk-headless"; exit 1; }
if [ -e "$KEYSTORE" ]; then
  echo "Klucz już istnieje: $KEYSTORE"
  echo "Nie nadpisuję go: nowy klucz oznacza, że każdy musi odinstalować aplikację. Usuń plik ręcznie, jeśli naprawdę chcesz nowy."
  exit 1
fi

mkdir -p "$DIR" && chmod 700 "$DIR"
PASSWORD="$(head -c 32 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' | head -c 32)"
keytool -genkeypair -v -keystore "$KEYSTORE" -storetype PKCS12 -alias agentic-os -keyalg RSA -keysize 4096 \
  -validity 10000 -storepass "$PASSWORD" -keypass "$PASSWORD" -dname "CN=Agentic OS, O=Agentic OS" >/dev/null 2>&1
chmod 600 "$KEYSTORE"
echo "✅ Utworzono klucz: $KEYSTORE"

if command -v gh >/dev/null && gh auth status >/dev/null 2>&1 \
   && base64 -w0 "$KEYSTORE" | gh secret set ANDROID_KEYSTORE_BASE64 --repo "$REPO" \
   && printf '%s' "$PASSWORD" | gh secret set ANDROID_KEYSTORE_PASSWORD --repo "$REPO"; then
  echo "✅ Zapisano sekrety ANDROID_KEYSTORE_BASE64 i ANDROID_KEYSTORE_PASSWORD w $REPO."
else
  base64 -w0 "$KEYSTORE" > "${DIR}/ANDROID_KEYSTORE_BASE64.txt"
  printf '%s' "$PASSWORD" > "${DIR}/ANDROID_KEYSTORE_PASSWORD.txt"
  chmod 600 "${DIR}"/*.txt
  echo "Nie udało się zapisać sekretów automatycznie (gh nie jest zalogowane albo nie ma uprawnień)."
  echo "Dodaj je ręcznie: github.com/${REPO} → Settings → Secrets and variables → Actions → New repository secret"
  echo "  ANDROID_KEYSTORE_BASE64   = zawartość pliku ${DIR}/ANDROID_KEYSTORE_BASE64.txt"
  echo "  ANDROID_KEYSTORE_PASSWORD = zawartość pliku ${DIR}/ANDROID_KEYSTORE_PASSWORD.txt"
  echo "Potem usuń oba pliki .txt. Nie wklejaj tych wartości nigdzie indziej (czat, repozytorium)."
fi

echo
echo "⚠️  Zrób kopię zapasową pliku ${KEYSTORE} i zapamiętaj, że hasło jest w sekrecie ANDROID_KEYSTORE_PASSWORD."
echo "   Bez tego klucza kolejne wersje aplikacji nie zainstalują się na poprzednich."
