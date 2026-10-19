"""The Android signing key must stay out of the repository (it lives in GitHub secrets, see android/keys/README.md)."""

import re
from pathlib import Path

ANDROID = Path(__file__).resolve().parent.parent / "android"


def test_no_keystore_is_committed():
    assert not [p for p in ANDROID.rglob("*") if p.suffix in {".keystore", ".jks"}]


def test_gradle_reads_signing_secrets_from_the_environment():
    gradle = (ANDROID / "app" / "build.gradle.kts").read_text(encoding="utf-8")
    assert not re.search(r'(storePassword|keyPassword)\s*=\s*"', gradle), "no hardcoded signing passwords"
    assert 'System.getenv("ANDROID_KEYSTORE_PATH")' in gradle
