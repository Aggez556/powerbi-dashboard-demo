# Tooltip-pilot på kundsidan

Piloten ändrar bara kundsidans tooltips. Inga mått, belopp eller periodval ändras.

- Branschdiagrammets båda vyer använder en dold rapportsida, 600 × 270 px. En tabell ersätter de upprepade standardblocken: bransch, försäljning, förändring i procent och kronor. Totalrad är avstängd eftersom branschernas procenttal inte ska summeras. Månads- och branschkontext överförs från källdiagrammet.
- Kundgruppernas försäljning och de två förändringsbryggorna använder kompakta standardtooltips med Segoe UI 11, vit ogenomskinlig bakgrund, marinblå värden och grå etiketter.
- Förändringsbryggorna visar inte längre den generella kundbehållningen, som inte beskriver det enskilda bryggsteget. Fältnamnen är förkortade till svenska visningsnamn.
- Kundtabellen har samma grundstil. KPI-kortens dubblerade standardtooltips är avstängda; deras förklaringar finns redan synliga under talen.

Kör `scripts/design-customer-tooltips.cjs` för att återställa piloten. Branschkortets byggskript kör även detta automatiskt. Tooltip-sidan är dold i läsvyn och ingår inte i sidomenyn. Faktisk hovring och filteröverföring måste granskas i Power BI Desktop.

Sidtypen anges uttryckligen som `type: "Tooltip"` i page.json. `pageBinding.type` ersätter inte denna inställning; utan sidtypen faller Desktop tillbaka till standardtooltipen även om diagrammets Canvas-koppling finns.
