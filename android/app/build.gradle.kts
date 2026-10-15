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
        versionName = "1.0." + (System.getenv("GITHUB_RUN_NUMBER") ?: "0")
    }

    signingConfigs {
        // A fixed key so every build can be installed over the previous one (sideloaded app, not Play Store).
        create("sideload") {
            storeFile = rootProject.file("keys/agentic-os.keystore")
            storePassword = "agentic-os"
            keyAlias = "agentic-os"
            keyPassword = "agentic-os"
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            signingConfig = signingConfigs.getByName("sideload")
        }
        debug {
            signingConfig = signingConfigs.getByName("sideload")
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
