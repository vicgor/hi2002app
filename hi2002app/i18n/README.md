# Internationalisation (i18n)

This directory contains Qt Linguist translation files for HI2002 App.

## Adding a new language

1. Copy `hi2002app_en.ts` to `hi2002app_XX.ts` (XX = ISO 639-1 code, e.g. `de`, `fr`, `pl`).
2. Open the new `.ts` file in **Qt Linguist** (`linguist hi2002app_XX.ts`).
3. Translate all `<source>` strings and mark them as **Finished**.
4. Compile to binary: `lrelease hi2002app_XX.ts` → produces `hi2002app_XX.qm`.
5. Place the `.qm` file next to the `.ts` file.
6. Add the new locale to `SettingsDialog` language combo-box in `hi2002app/ui/settings_dlg.py`.
7. Reload the app — the new language will be selectable in Settings.

## Build all .qm files at once

```bash
lrelease hi2002app/i18n/hi2002app_en.ts
lrelease hi2002app/i18n/hi2002app_ru.ts
```

Or add a `lrelease` step to the CI workflow if compiled translations are needed in the build.

## File listing

| File | Language | Status |
|------|----------|--------|
| `hi2002app_en.ts` | English | ✅ Complete |
| `hi2002app_ru.ts` | Russian | ✅ Complete |
