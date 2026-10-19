plugins {
    id("com.android.application")
}

android {
    namespace = "os.agentic.warroom"
    compileSdk = 35

    defaultConfig {
        applicationId = "os.agentic.warroom"
        minSdk = 26
        targetSdk = 35
        versionCode = (System.getenv("GITHUB_RUN_NUMBER") ?: "1").toInt()
        versionName = System.getenv("APP_VERSION") ?: "0.0.0-dev"  // release version from CHANGELOG.md
    }

    // Releases are signed with a private key that never enters git: CI decodes it from repository secrets
    // and passes its path and passwords here (see keys/README.md). Without it (pull requests, local
    // builds) the APK gets the throwaway debug key and cannot update an installed release.
    val keystorePath = System.getenv("ANDROID_KEYSTORE_PATH")
    signingConfigs {
        if (keystorePath != null) {
            create("private") {
                storeFile = file(keystorePath)
                storePassword = System.getenv("ANDROID_KEYSTORE_PASSWORD")
                keyAlias = System.getenv("ANDROID_KEY_ALIAS") ?: "agentic-os"
                keyPassword = System.getenv("ANDROID_KEY_PASSWORD") ?: System.getenv("ANDROID_KEYSTORE_PASSWORD")
            }
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            signingConfig = signingConfigs.findByName("private") ?: signingConfigs.getByName("debug")
        }
    }

    lint {
        checkReleaseBuilds = false  // lint pulls in many extra downloads; run `gradle lint` on demand
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

dependencies {
    testImplementation("junit:junit:4.13.2")
}
