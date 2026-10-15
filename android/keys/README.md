# Signing key for the sideloaded Android app

`agentic-os.keystore` signs every build of the Agentic OS Android app, so a new APK installs over the
previous one without uninstalling it. Its password is in `app/build.gradle.kts`.

This key is public on purpose: the app is a thin WebView over **your own** server and is sideloaded, not
published on Google Play. Anyone could sign an APK with this key, so install updates only from this
repository's Releases page. Before publishing on Google Play, create a new private key and keep it out of git.
