# Talformat efter Desktop-inläsning

KPI-korten använder explicita enheter (None, värde 1), så Antal order visas som heltal med tusentalsavskiljare utan automatisk ”t”. Beloppskorten visar hela kronor med ett fast mellanrum före kr. Procentmått har mellanrum före %. Modellens belopp behåller två decimaler för tabeller och verktygstips.

Kortens positioner, bindningar, containerinställningar, sidfiler och tema är oförändrade; detta kontrolleras av scripts/update-number-formats.py. Microsofts TMDL-parser godkänner de nya måttformaten. Användaren har bekräftat att föregående version öppnades och visade data i Desktop.

Desktop har sparat vissa visualer med schema 2.13.0 och utelämnat schemareferenser i projektets två genvägsfiler. Referenserna har återställts. Se aktuell pbir-result.json för faktisk schematäckning: ett schema som inte går att hämta innebär att full schemakontroll av berörda visualer återstår. Renderingen av dessa format behöver granskas i Desktop efter att projektet öppnats på nytt.

Stäng den öppna rapporten utan att spara den äldre versionen över filändringarna och öppna AubecoHandel.pbip igen. Kontrollera orderkortet, mellanrum före kr/% samt att beloppen ryms. Data och layout behöver inte återskapas.
