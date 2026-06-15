---
name: create-mobile-agent
version: 1.0.0
description: Investigates the project, asks about mobile needs, and generates a professional Mobile Developer agent in the native format of the current tool
---

# Create Mobile Agent — Generate a Specialized Mobile Developer Agent

## Overview
Investigates the project, inventories available skills/plugins, asks targeted questions about mobile development needs (iOS, Android, React Native, Flutter), and generates a complete Mobile Developer agent in the native agent format of the current tool.

## When to use
- Need a dedicated Mobile Developer agent for a cross-platform or native mobile project
- Project has a mobile app component (iOS, Android, React Native, Flutter)
- Want mobile-specific automation: builds, signing, store deployment, CI/CD for mobile

## When NOT to use
- No mobile code exists yet → use project-init first
- Mobile is handled by a separate dedicated team → overkill

## Output
- An agent file in the native format of the current tool, saved in the per-project agents directory

## Full Prompt

# CREATE MOBILE AGENT — Generate a Mobile Developer Agent

## RULE: This skill generates an agent. No application code changes.

---

## Phase 1 — Preflight

### 1.1 Inventory installed skills/plugins
```bash
ls -d skills/*/ 2>/dev/null | sed 's|skills/||;s|/||'
```
Read any skill files relevant to mobile development.

Check MCP servers:
```bash
cat opencode.json 2>/dev/null | grep -i "plugin\|mcp" || true
cat .claude/settings.json 2>/dev/null | grep -i "mcp\|plugin" || true
ls .mcp.json 2>/dev/null && head -50 .mcp.json || true
```

### 1.2 Scan project tech stack
```bash
# React Native
ls package.json 2>/dev/null && grep -i "react-native\|expo" package.json || true
# Flutter
ls pubspec.yaml 2>/dev/null && head -10 pubspec.yaml || true
# iOS
ls *.xcodeproj *.xcworkspace Podfile 2>/dev/null
# Android
ls build.gradle* app/build.gradle* settings.gradle* 2>/dev/null
# Kotlin Multiplatform
ls build.gradle.kts 2>/dev/null && grep -i "kotlin\|multiplatform" build.gradle.kts 2>/dev/null || true
# Capacitor/Cordova
ls capacitor.config.ts capacitor.config.json config.xml 2>/dev/null
```

### 1.3 Build context profile
Synthesize: mobile framework detected, build tools present, CI/CD configuration, store deployment setup, available plugins.

---

## Phase 2 — Domain Research: Mobile

```bash
# iOS-specific
ls fastlane/ Gemfile 2>/dev/null
ls ios/Podfile ios/Podfile.lock 2>/dev/null
ls exportOptions.plist 2>/dev/null

# Android-specific
ls gradlew gradle.properties local.properties 2>/dev/null

# Code signing
ls *.mobileprovision *.p12 *.keystore 2>/dev/null

# Store config
ls app/**/*.aab app/**/*.apk 2>/dev/null | head -5
ls ios/**/*.ipa 2>/dev/null | head -5

# UI testing
grep -r "detox\|maestro\|appium\|espresso\|xcuitest" --include="*.json" --include="*.yaml" --include="*.ts" --include="*.dart" 2>/dev/null | head -10
```

---

## Phase 3 — Domain Questions

Ask the user one at a time:

1. **What mobile framework are you using?** (React Native, Flutter, SwiftUI, Kotlin, Expo, Capacitor, other)
2. **Target platforms?** (iOS, Android, both, cross-platform)
3. **CI/CD for mobile?** (GitHub Actions, Bitrise, Codemagic, Fastlane, manual)
4. **Store deployment?** (TestFlight, App Store, Google Play, internal distribution, none yet)
5. **Testing strategy?** (unit tests, widget tests, integration tests, E2E with Detox/Maestro/Appium)
6. **Code signing approach?** (manual, Fastlane match, GitHub Actions signing, EAS Build)

---

## Phase 4 — Generate Agent

Create a **Mobile Developer agent** in the native format of the current tool.

The agent should include:
- Role: Mobile Developer for this project
- Available mobile-relevant skills/plugins from Phase 1
- Full prompt covering: build automation, code signing, store deployment, mobile-specific testing, performance profiling, push notifications, deep linking, offline support
- Permission: project-scoped
- Temperature: 0.3 (balanced creativity and precision)

The agent must be framework-aware: if React Native is detected, include Expo, Metro, Hermes-specific guidance. If Flutter, include widget testing, Dart analysis. If native, include Xcode/Android Studio project management.

---

## Rules
- Generate in native format of the current tool.
- Save per-project.
- Framework-specific: tailor the agent to the detected mobile framework.
- All questions in English unless user prefers otherwise.
