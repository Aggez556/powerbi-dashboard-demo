# Skills och beroenden

Installerat 2026-10-06 i `C:\dev\codex-labb`.

## Källor och installation

Installationsanvisningarna i båda repornas README har lästs. Codex inbyggda skill-installer användes med `--dest C:/dev/codex-labb/.agents/skills`, för projektlokal installation.

| Skill | Källa | Git-commit |
| --- | --- | --- |
| design-taste-frontend | https://github.com/Leonxlnx/taste-skill, `skills/taste-skill` | ce26fc25c0e5e8cab638f883de62d9a86ee5e45b |
| semantic-model-authoring | https://github.com/microsoft/skills-for-fabric, `skills/semantic-model-authoring` | bc42aaf734771bf752c1d7082dd91e5a6ca72b9f |
| powerbi-report-cli | https://github.com/microsoft/skills-for-fabric, `skills/powerbi-report-cli` | bc42aaf734771bf752c1d7082dd91e5a6ca72b9f |

Microsofts rapportskill innehåller lägena planning, design, authoring och management. Inga separata äldre rapportdesignskills behövs.

Microsoft beskriver även APM-installation. Här används Codex befintliga installerare i stället. Hela skillsmapparna inklusive referenser har installerats, och Microsofts `common/` har kopierats till `.agents/common/`, vilket bevarar relativa `../../common/`-länkar. Licenser medföljer. Källkopior finns i `.skill-sources/`.

## Beroendekontroll

- Python 3.12.6 och Git finns redan. Skill-installer behöver inga extra Python-paket.
- Node.js 20.17.0 finns redan och uppfyller rapportverktygets krav på Node.js 20 eller senare.
- npm 11.0.0 finns redan. Inga Power BI-verktyg hittades bland globala npm-paket eller på PATH.
- `@microsoft/powerbi-report-authoring-cli@latest` installerades lokalt med npm i `.tools/powerbi/`. Installerad version: 0.5.0. Version och visualiseringskatalog har körts utan fel.
- Verktygets beroenden, inklusive Desktop bridge och Playwright-paketet, installerades automatiskt. Ingen webbläsare har laddats ned för Playwright och ingen rapportpreview har körts.
- Taste är instruktioner och behöver inget körbart verktyg för att laddas. Webbramverk och animationsbibliotek installeras först om ett webbarbete kräver dem.
- APM, Azure CLI, .NET och Power BI Desktop kunde inte hittas genom de kontroller som gjordes (PATH, vanlig Desktop-sökväg och Appx-paket). De behövs inte för att läsa skills eller analysera grafisk profil. Detta är ingen fullständig inventering av datorn.
- Ingen Fabric-inloggning eller MCP-anslutning har skapats. Semantic-model-skill stöder lokala TMDL/PBIP-filer utan MCP. Live-modellering och publicering kräver senare arbetsflödesspecifik installation och anslutning.

## Codex-upptäckt

Projektets skills ligger i `.agents/skills/<namn>/SKILL.md`, den plats Codex söker för projektlokala skills. Varje fil har `name` och `description`. Projektets `AGENTS.md` pekar dessutom direkt till instruktionerna och det lokala rapportverktyget.

Verifierat genom att läsa alla tre SKILL.md-filerna och köra `python scripts/verify-skills.py`: tre giltiga metadatahuvuden och 222 relativa fillänkar, inga saknade filer. Skillväljaren i den redan öppna appen har inte inspekterats.

Officiell dokumentation: https://learn.chatgpt.com/docs/build-skills

Skills ska vara tillgängliga nästa tur. Om de inte visas i skillväljaren, starta om Codex.

## Nästa fas

Analysera Aubecos grafiska profil. Inga dummydata, modeller eller rapportfiler har skapats.
