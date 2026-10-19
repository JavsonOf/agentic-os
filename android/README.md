# Agentic OS na Androida

Aplikacja na Androida otwiera Twój War Room na pełnym ekranie, bez paska przeglądarki. Ma własną ikonę na
ekranie głównym i pozwala wysyłać pliki, np. przy imporcie pamięci z ChatGPT czy Claude.

Agenci działają na **Twoim serwerze** (Oracle, Hetzner, OmGithub albo Termux na tym telefonie). Aplikacja
przechowuje tylko adres tego serwera, więc nie obciąża telefonu.

## Instalacja

1. Na telefonie otwórz **https://github.com/JavsonOf/agentic-os/releases/latest**.
2. Stuknij plik **AgenticOS_vX.Y.Z.apk** (X.Y.Z to numer wersji, np. `AgenticOS_v0.2.5.apk`), żeby go pobrać.
3. Otwórz pobrany plik. Android zapyta, czy zezwolić przeglądarce na instalowanie aplikacji: zezwól.
4. Uruchom **Agentic OS** i wpisz adres swojego serwera, np. `https://1-2-3-4.sslip.io`.
5. Zaloguj się hasłem do War Room.

Nowe wersje instalujesz tak samo, na wierzch starej. Ustawienia i logowanie zostają.

## Obsługa

- **Wstecz:** cofa się w War Room. Na pierwszym ekranie zamyka aplikację.
- **Przytrzymaj Wstecz:** zmiana adresu serwera.
- **Brak połączenia:** pojawi się ekran z przyciskami „Spróbuj ponownie” i „Zmień adres serwera”.
- Linki do innych stron otwierają się w przeglądarce.

## Dla deweloperów

Aplikację buduje GitHub Actions (`.github/workflows/android.yml`) przy każdej zmianie w `android/` i
publikuje APK w Releases. Lokalnie:

```bash
export ANDROID_HOME=/ścieżka/do/android-sdk   # platforms;android-35, build-tools;35.0.0
gradle -p android assembleRelease             # Gradle 8.14, JDK 17+
# APK: android/app/build/outputs/apk/release/app-release.apk
```

Kod to jedna klasa: `app/src/main/java/os/agentic/warroom/MainActivity.java` (WebView, bez dodatkowych
bibliotek). Wydania są podpisane prywatnym kluczem z sekretów GitHuba, a nie kluczem z repozytorium: opisuje to `keys/README.md`.
