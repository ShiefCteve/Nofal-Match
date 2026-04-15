# 🎮 Nofal Match - HD Edition

Nofal Match er et tyngdekrafts-baseret puzzle-spil bygget i Python med Pygame. Det er mit første selvstændige kode-projekt, bygget for at lære om logik, fysiksimulering og spil-loops.

## 📝 Om spillet
Fjern skruerne fra de hængende plader og saml dem i din værktøjskasse. Når du samler tre skruer af samme farve, forsvinder de! 
Men pas på: Værktøjskassen har kun plads til 7 skruer. Fylder du den op, uden at lave et match, taber du spillet. Hver gang en plade tømmes for skruer, falder den af skærmen med en fysik-animation. Spillet bliver sværere for hvert niveau med flere plader og farver.

## 🚀 Sådan spiller du

**Den nemme måde (Windows):**
1. Gå til **Releases** ude i højre side på denne side.
2. Download `.zip` filen under nyeste version.
3. Udpak filen og dobbeltklik på `screwmatchnofal.exe` for at spille!

**For udviklere (Kør fra kildekode):**
1. Sørg for at have Python 3 og Pygame installeret (`pip install pygame`).
2. Download `screwmatchnofal.py`.
3. Kør spillet via terminalen: `python screwmatchnofal.py`.

## 🧠 Hvad jeg lærte
I dette projekt har jeg arbejdet med:
* Objektorienteret programmering (OOP) for at styre `Screw`, `Plate` og `Game` states.
* Matematik og fysik til at beregne klik-radius (`math.hypot`) og polygon-kollisioner.
* Håndtering af Game States (Menu, Playing, Won, Lost, Settings).
* UI/UX elementer som menuer, volumen-kontrol og dynamiske timers.
