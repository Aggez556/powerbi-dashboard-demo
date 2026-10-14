# Projektinstruktioner

Vi ska bygga en Power BI-rapport med dummydata och Aubecos grafiska profil.

Aktuell fas: ett lokalt testprojekt med dummydata, TMDL och PBIR har byggts på användarens uttryckliga begäran. Fil- och datavalidering är genomförd; faktisk import, DAX-körning och visuell granskning återstår i Power BI Desktop. Publicera ingenting utan ny uttrycklig instruktion.

## Installerade skills

- `.agents/skills/semantic-model-authoring/SKILL.md`: semantisk modellering, TMDL och DAX.
- `.agents/skills/powerbi-report-cli/SKILL.md`: rapportplanering, design, PBIR/PBIP, validering och förhandsgranskning. Läs relevant mode-referens innan arbetet börjar.
- `.agents/skills/design-taste-frontend/SKILL.md`: Taste för webbdesign. Den aktuella versionen utesluter dashboards; använd Microsofts designinstruktioner för Power BI och låt Aubecos profil styra.

Microsofts gemensamma referenser finns i `.agents/common/`. Bevara dem eftersom installerade skills länkar dit.

## Lokalt rapportverktyg

Microsofts `powerbi-report-author` är installerat i `.tools/powerbi/`. Kör från projektroten:

```powershell
& ./.tools/powerbi/node_modules/.bin/powerbi-report-author.cmd --version
```

När instruktionerna använder det korta kommandot `powerbi-report-author`, använd denna lokala sökväg eller lägg `.tools/powerbi/node_modules/.bin` på PATH för den aktuella processen. Installationsstatus och källversioner finns i `docs/skills-installation.md`.
