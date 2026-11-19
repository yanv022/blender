# Mini-usine bauxite → alumine

Atelier discontinu pour transformer de la bauxite gibbsitique (Cameroun) en **alumine assez pure pour l'électrolyse**, avec cinq appareils séparés :

| Repère | Appareil | Rôle |
|---|---|---|
| A0 | Broyeur à boulets + chariot à trémie + potence | Réduire la bauxite en poudre < 250 µm |
| R1 | Cuve agitée chauffée 50 L | Attaque à la soude, 100 °C, 2 h, pression atmosphérique |
| F | Filtre sous vide (vide limité) + pompe de transfert | Séparer les boues rouges, puis l'hydrate d'alumine |
| R2 | Cuve agitée chauffée 50 L | Précipitation par amorçage, 48 h de 60 à 50 °C |
| K | Four à moufle 1200 °C, 3 creusets | Calcination à 1050 °C : Al(OH)₃ → Al₂O₃ |

Premier lot : 5 kg de bauxite → environ 1,1 kg d'alumine ; ensuite environ 2,7 kg de bauxite par lot (la liqueur et l'amorce sont recyclées). Tous les chiffres sont calculés, à confirmer par l'essai à 200 g décrit dans le plan.

![Vue d'ensemble](rendu-realiste-ensemble.png)

## Contenu

| Fichier | Contenu |
|---|---|
| `plan-usine-bauxite-alumine.md` | Plan complet : procédé, bilans, appareils, mode opératoire, sécurité, achats |
| `plans/planche-1..4-*.svg` | Plans cotés (A3) : cuve, châssis de cuve, broyeur + chariot, filtre |
| `plans_cotes.py` | Script qui regénère les planches |
| `construire_usine.py` | Script Blender qui construit la scène 3D à l'échelle 1:1 |
| `materiaux_realistes.py` | Matériaux réels, lumière, caméras |
| `usine-bauxite-alumine-realiste.blend` | Modèle 3D réaliste prêt à ouvrir |
| `animer_usine.py`, `usine-bauxite-alumine-animation.blend` | Animation du procédé (≈ 1 min 45) : vraies ouvertures, palan, récipients étiquetés, horloge de durée réelle |
| `rendu-realiste-*.png` | Images calculées (ensemble, broyeur, cuves + filtre, pompe à vide, four, sécurité) |
| `usine-bauxite-alumine.blend`, `rendu-vue-ensemble.png`, `rendu-cuves-filtre.png` | Première version, gardée pour mémoire |
| `exporter_video.cmd`, `exporter_video.py` | Export de l'animation en MP4 (Blender + ffmpeg) |

## Regénérer

- Plans cotés : `python plans_cotes.py`
- Modèle fixe, dans Blender 5.2 (onglet **Scripting**) : exécuter `construire_usine.py`, puis `materiaux_realistes.py`
- Animation : exécuter `animer_usine.py` (il lance lui-même les deux autres scripts, qui doivent être dans le même dossier)

## Avertissement

La soude chaude est très dangereuse (brûlures graves, cécité). Lire la section sécurité du plan avant toute manipulation. Les chiffres du plan sont des estimations qui n'ont pas encore été vérifiées par un essai réel.
