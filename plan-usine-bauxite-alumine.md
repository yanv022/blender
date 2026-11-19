# Mini-usine bauxite → alumine : plan de construction (version 2)

Atelier discontinu (« batch ») composé de 5 appareils séparés : broyeur, cuve d'attaque R1, filtre, cuve de précipitation R2, four. On charge un appareil, on regarde ce qui en sort, on passe au suivant.

**Objectif : alumine assez pure pour faire de l'aluminium.** D'où le choix de la précipitation par amorçage (voir §1).

**Taille d'un lot (cuves de 50 L) :**
- **premier lot** : 5 kg de bauxite + 4,3 kg de soude → environ **1,1 kg d'alumine** (le reste de l'alumine dissoute repart avec la liqueur) ;
- **lots suivants (régime établi)** : environ **2,7 kg de bauxite** par lot + un appoint de soude → environ **1,1 à 1,2 kg d'alumine** par lot.

Pour traiter 5 kg de bauxite à **chaque** lot, il faut des cuves de 100 L (voir §9). C'est le prix de la précipitation par amorçage : elle ne récupère qu'une partie de l'alumine à chaque passage, mais elle donne une alumine plus pure et la soude se réutilise.

Toutes les valeurs sont des **calculs**, pas des mesures : l'essai à 200 g (§11) doit les confirmer avant tout achat.

---

## 1. Les choix de procédé (et pourquoi)

L'industrie utilise le procédé Bayer : attaque à la soude en autoclave (140–250 °C sous pression), décantation, précipitation par amorçage pendant 24–72 h, calcination. Voici la version simplifiée retenue :

| Étape | Industrie | Ici | Pourquoi |
|---|---|---|---|
| Attaque | Autoclave 140–250 °C, 5–35 bar | Cuve **ouverte** à 100 °C, 2 h | Aucun appareil sous pression. Fonctionne pour la bauxite **gibbsitique** (Cameroun, Guinée, Ghana, Brésil…) |
| Séparation des boues | Décanteurs + filtres sous pression | Décantation dans la cuve + filtre sous **vide faible** | La liqueur est presque bouillante : un vide fort la ferait bouillir (§5) |
| Précipitation | Amorçage, 24–72 h, ~50 % par passe | **Amorçage**, 48 h, de 60 à 50 °C | Alumine pauvre en sodium (objectif aluminium), soude réutilisée |
| Calcination | Calcinateur | Four à moufle 1200 °C, 1050 °C | Un four de laboratoire du commerce suffit |

**Pourquoi plus de CO₂ dans la voie principale.** La version 1 précipitait au CO₂ (rapide, tout l'alumine en une fois). Deux problèmes pour faire de l'aluminium : l'alumine obtenue reste trop riche en sodium (une étude ICSOBA 2025 n'arrive qu'à ~0,6 % Na₂O après lavages répétés), et au-dessus de 65 °C il se forme de la dawsonite, une impureté sodique. En plus, toute la soude devient du carbonate (≈ 4,6 kg à gérer par lot). Le CO₂ reste décrit en variante (§13) pour d'autres usages de l'alumine.

Astuce de construction : l'attaque et la précipitation se font dans **le même modèle de cuve agitée chauffée**, en deux exemplaires.

### Chimie

```
Attaque        Al(OH)3 + NaOH      →  NaAl(OH)4          (100 °C)
Précipitation  NaAl(OH)4           →  Al(OH)3 ↓ + NaOH   (amorce, 60 → 50 °C, 48 h)
Calcination    2 Al(OH)3           →  Al2O3 + 3 H2O ↑    (1050 °C)
```

La précipitation est l'inverse de l'attaque : en refroidissant et en ajoutant des cristaux d'hydrate (l'amorce), l'alumine ressort de la liqueur et **la soude est libérée**. La liqueur épuisée repart attaquer le lot suivant.

Le fer, le titane et la silice ne se dissolvent pas (ou reprécipitent) : ils partent dans les **boues rouges**.

---

## 2. Vue d'ensemble

```
 Bauxite (5 kg au 1er lot, ~2,7 kg ensuite)
     │
 ┌───▼────────────┐
 │ A0 BROYEUR     │  chariot à trémie → fût → 1–2 h → grille + palan → bac
 └───┬────────────┘
     │ poudre < 250 µm         eau 19 L + soude 4,3 kg (1er lot)
 ┌───▼────────────┐◄─────────── ou liqueur recyclée + appoint de soude
 │ R1 ATTAQUE     │  100 °C, 2 h, agitation
 └───┬────────────┘
     │ pulpe chaude (≥ 85 °C)
 ┌───▼────────────┐
 │ F  FILTRE      │──► boues rouges ≈ 2 kg sec (1er lot) → lavage → neutralisation
 └───┬────────────┘   vide limité à −0,2 bar
     │ liqueur claire ≈ 27 L   ──pompe──►
 ┌───▼────────────┐◄── amorce Al(OH)3 ≈ 3,5 kg (réutilisée à chaque lot)
 │ R2 PRÉCIPITAT. │  60 → 50 °C, 48 h, agitation
 └───┬────────────┘
     │ suspension blanche
 ┌───▼────────────┐
 │ F  FILTRE      │──► liqueur épuisée ≈ 27 L → évaporer ~8–10 L → retour à R1
 └───┬────────────┘
     │ hydrate : on garde ≈ 3,5 kg comme amorce, ≈ 1,7 kg vont au four
 ┌───▼────────────┐
 │ K  FOUR        │  3 creusets empilés, palier 400 °C puis 1050 °C
 └───┬────────────┘
     ▼
 ALUMINE ≈ 1,1 kg par lot
```

### Bilan matière (calculé, à vérifier par l'essai)

Hypothèse : bauxite gibbsitique à ~50 % Al₂O₃ total, dont ~45 % extractible, ~2,5 % de silice réactive, ~20 % Fe₂O₃. **À recalculer avec ton analyse réelle.**

| | Premier lot | Lots suivants |
|---|---|---|
| Bauxite sèche | 5,0 kg | ≈ 2,7 kg |
| Soude NaOH | 4,3 kg | appoint ≈ 0,3–0,5 kg (pertes dans les boues et les lavages) |
| Eau | 19 L d'attaque + ≈ 15 L de lavages | appoint pour remplacer l'évaporation |
| Amorce Al(OH)₃ | 3,5 kg (achetée une fois) | la même, gardée à chaque lot |
| Alumine obtenue | ≈ 1,1 kg | ≈ 1,1–1,2 kg |
| Boues rouges (sec) | ≈ 2 kg | ≈ 1,1 kg |
| Liqueur recyclée | ≈ 27 L (contient ≈ 1,2 kg d'Al₂O₃ dissoute) | idem |
| Électricité | ≈ 35–45 kWh (dont 48 h d'agitation et l'évaporation) | idem |

**Contrôle du dosage de soude.** En fin d'attaque, la liqueur contient environ 107 g/L d'Al₂O₃ pour 270 g/L de soude (comptée en Na₂CO₃), soit un rapport A/C ≈ 0,39. Un brevet sur ces bauxites situe la liqueur d'attaque **sous 0,45**. La version 1 (3,5 kg de soude) arrivait à ≈ 0,48 : trop près de la limite, avec un risque d'attaque incomplète et de reprécipitation dans les boues. D'où les 4,3 kg.

---

## 3. Appareil A0 — Broyeur à boulets

But : poudre sèche passant au tamis de 250 µm. Plus c'est fin, plus l'attaque est complète.

1. **Séchage** : 105 °C quelques heures (four de cuisine dédié, ou soleil).
2. **Concassage** à < 10 mm : masse sur plaque d'acier dans un sac de toile, ou petit concasseur à mâchoires.
3. **Broyage** (plan coté : planche 3) :
   - **Tambour** : tube acier **Ø 273 × 6 mm** (DN 250), longueur 400 mm, fond soudé. Un fût de peinture en tôle fine ne tiendrait pas les chocs de 10 kg de billes.
   - **3 releveurs** plats 20 × 12 mm soudés à l'intérieur sur toute la longueur : ils remontent les billes pour qu'elles retombent (sans eux, les billes glissent et broient mal).
   - **Couvercle affleurant** : disque de 12 mm, même diamètre que le tube, avec joint, poignée, **charnière plate** côté arrière et **3 grenouillères plates**. Rien ne doit dépasser de plus de 8 mm : les arbres des rouleaux passent à 10 mm de la paroi.
   - **Rouleaux** : 2 arbres Ø 20 mm sur 4 paliers à semelle ; manchons caoutchouc Ø 40 mm qui s'arrêtent **avant le couvercle**.
   - **Charge** : 10–12 kg de billes d'acier Ø 20–40 mm + la bauxite (≈ 40 % du volume).
   - **Vitesse** : 55–60 tr/min (≈ 70 % de la vitesse critique 42,3/√D). Motoréducteur 180–250 W, courroie sous carter.
   - **Durée** : 1–2 h.
4. **Chargement : chariot à trémie** — trémie inox 300 × 300 mm en haut, goulotte en U inclinée à 44°, longueur 450 mm, sur poteau à base roulante. On ouvre le couvercle, on avance le chariot jusqu'à ce que la goulotte entre dans le fût, on verse la bauxite puis les billes, on recule le chariot, on referme.
5. **Vidange : grille + palan** — on pose une grille (barreaux tous les 33 mm) dans l'ouverture, on visse deux tourillons M16 dans les **bossages** du tube, on accroche l'étrier du palan, on soulève le fût et on l'incline au-dessus du bac. La poudre tombe, les billes restent.
6. **Potence et palan** (le fût chargé pèse ≈ 18 kg) : potence sur colonne Ø 100 mm, flèche tournante de 1,3 m à 1,85 m de haut, chariot et **palan à chaîne manuel** (charge 50–100 kg), **étrier** à deux tourillons. Les vrais broyeurs de laboratoire ont de même un dispositif de levage pour le chargement et la vidange.
7. **Tamisage** à 250 µm (tamis 60 mesh) ; le refus retourne au broyeur.

Masque FFP3 pendant le broyage et le tamisage.

---

## 4. Appareil R — Cuve agitée chauffée (2 exemplaires : R1 et R2)

Plan coté : planches 1 et 2.

```
              moteur-réducteur 150–250 W, 100–300 tr/min
                    ┌───┐
   portique acier ══╪═══╪══════════════
                    │   │        évent Ø25 → extérieur (JAMAIS fermé)
   trappe Ø76  ┐    │   │   ┌─ doigt de gant + sonde
          ╔════╧════╪═══╪═══╧════╗  couvercle inox
          ║         │arbre Ø14   ║
   laine  ║         │            ║  marmite inox 304/316, 50 L
   de     ║ chicane │            ║  Ø 400 × H 400 mm, fond épais
   roche  ║  │      │            ║
   50 mm  ║  │   ╱──┴──╲ turbine ║
          ║  │   4 pales 45°     ╠═► vanne HAUTE DN25 (axe à 75 mm du fond)
          ║      Ø 130 mm        ║     = soutirage du liquide clair
          ╚══════════════════════╩═► vanne BASSE DN25 (axe à 22 mm du fond)
          ▓▓▓▓ plaque électrique 3 kW ▓▓▓▓     = vidange des boues / solides
          ───── châssis acier, fond de cuve à 90 cm du sol ─────
          ═════ bac de rétention ≥ 50 L sous l'ensemble ═════
```

### Liste des pièces (par cuve)

| Pièce | Spécification | Remarque |
|---|---|---|
| Cuve | Marmite inox 304 ou 316, 50 L, fond sandwich | Volume utile 18–35 L |
| Vannes (×2) | Robinet à boisseau sphérique inox DN25 **passage intégral**, sièges PTFE | Manchon soudé TIG, ou traversée de paroi vissée avec joints PTFE/EPDM |
| Couvercle | Inox, percé : arbre (Ø 20 avec bague PTFE), trappe Ø 76, doigt de gant, évent Ø 25 | La cuve reste toujours à pression atmosphérique |
| Trappe de chargement | Collerette inox Ø 76 × 30 mm soudée sur le trou + couvercle Ø 100 à charnière et bouton | Tout entre par là : eau, soude, poudre, liqueur, amorce |
| Agitateur | Motoréducteur 150–250 W à vitesse variable ; arbre inox Ø 14 ; turbine 4 pales inclinées Ø 130 mm, à 65 mm du fond | Pousse vers le bas. Doit tourner 48 h d'affilée sur R2 |
| Chicanes | 3 plats inox 35 × 300 mm | Empêchent le vortex et les dépôts |
| Chauffage | Plaque électrique résistive 2,5–3 kW | Pilotée par relais |
| Régulation | Régulateur PID + relais statique 40 A + sonde PT100 dans un doigt de gant inox | Thermostat de sécurité indépendant à 115 °C. Sur R2, le PID suit une **descente** de 60 à 50 °C |
| Isolation | Laine de roche 50 mm + tôle inox | Sur R2, elle ralentit le refroidissement : c'est voulu |
| Châssis | Cornière acier 40 × 40, peinte époxy | Vanne basse au-dessus du filtre |

R1 et R2 sont identiques. R2 n'a plus de ligne CO₂.

### Matériaux : permis et interdits avec la soude chaude

- **Oui** : inox 304/316 (jusqu'à ~100 °C à cette concentration), PTFE, EPDM, polypropylène (jusqu'à ~80 °C).
- **Jamais** : aluminium (dégage de l'hydrogène, se perce), zinc / acier galvanisé, laiton, étain, verre ordinaire, joints Viton (FKM), silicone en contact prolongé.
- Acier ordinaire : acceptable à froid, à éviter au-dessus de ~65 °C (fissuration caustique).

---

## 5. Appareil F — Filtre (1 exemplaire, 2 toiles)

Plan coté : planche 4.

```
        pulpe
          ▼
   ┌──────────────┐  cuve supérieure inox 30 L
   │▒▒▒▒▒▒▒▒▒▒▒▒▒▒│  toile filtrante polypropylène, serrée par un cerclage
   │● ● ● ● ● ● ● │  fond percé Ø 5 mm, entraxe 15 mm (ou tôle perforée)
   └──────┬───────┘
     joint EPDM
   ┌──────┴───────┐
   │  fût inox    │──► vacuomètre + vanne de mise à l'air
   │  30–50 L     │──► piège à liquide 5 L ──► pompe à vide à membrane (avec réglage)
   │  (filtrat)   │──► vanne de vidange ──► pompe de transfert ──► trappe de R2 (ou de R1)
   └──────────────┘
```

**Le vide doit rester faible pour la liqueur chaude.** La liqueur sort de R1 à 85 °C ou plus. Sous −0,6 bar, elle bouillirait vers 80–85 °C : projections de soude dans le récepteur. L'industrie filtre cette liqueur chaude sous pression pour cette raison.

| Filtration | Température | Vide maximum |
|---|---|---|
| Liqueur + boues rouges (après l'attaque) | ≥ 85 °C | **−0,2 bar** (l'eau bout alors vers 93 °C, la liqueur un peu au-dessus) |
| Hydrate (après la précipitation) | ≈ 50 °C | −0,5 bar |

Si la filtration des boues est trop lente à −0,2 bar : petit **filtre-presse** (filtration sous pression), ou laisser simplement égoutter plus longtemps.

- **Récepteur** : fût à bière inox (conçu pour la pression, il tient le vide). Jamais de seau plastique sous vide avec du liquide chaud.
- **Toiles** : une toile PP ~5–10 µm pour les boues rouges, une toile PP ~10–25 µm pour l'hydrate. Ne jamais les mélanger, sinon l'alumine sera rose.
- **Sortie des gâteaux** : la galette sort par le haut de la cuve filtrante, avec sa toile.
- **Transfert** : piquage inox au bas du fût + vanne à boisseau, tuyau vers une **pompe de transfert** (pompe centrifuge inox ou à membrane, 10–20 L/min, compatible soude), puis tuyau qui entre par la trappe de R2. La liqueur ne remonte pas seule d'environ 1,3 m.

---

## 6. Appareil K — Four de calcination

**Four à moufle de laboratoire 1200 °C du commerce** (« box muffle furnace », chambre ≈ 230 × 230 × 300 mm, 12–15 L, 220 V, régulateur à rampes, porte à charnière, cheminée d'évacuation). Un four de potier électrique d'occasion convient aussi.

**Capacité : 3 creusets empilés.** L'hydrate pèse environ 1,05 à 1,7 kg par litre selon sa compacité. Les ≈ 1,7 kg d'hydrate d'un lot occupent donc 1 à 1,7 L. Un creuset de 160 × 160 × 45 mm (couche ≤ 40 mm) en contient environ 0,9 L : il en faut **2, plus 1 de réserve**. On les empile sur une plaque d'enfournement avec des cales réfractaires (4 par niveau), et l'ensemble entre et sort en une fois par la porte.

**Table de préparation** : à côté du four, plateau à la hauteur de la sole. On y remplit les creusets, puis on fait glisser la plaque à plat jusque dans le four (gants et pince : elle ressort chaude).

**Programme de cuisson (≈ 6 h + refroidissement) :**

1. Sécher l'hydrate à 110 °C (une nuit) : il doit arriver sec au four.
2. Montée à 5 °C/min jusqu'à 400 °C, **palier 2 h, cheminée ouverte** : c'est là que part l'essentiel de l'eau (≈ 0,6 kg de vapeur par lot). Ne pas pousser plus vite : la vapeur abîme l'isolation et les résistances.
3. Montée à 5–8 °C/min jusqu'à 1050 °C, palier 90 min.
4. Refroidissement porte fermée jusqu'à moins de 100 °C.

Contrôle : la masse doit avoir baissé d'environ 35 %. Une seconde cuisson d'un échantillon ne doit plus faire perdre que < 1 %.

---

## 7. Recyclage de la liqueur et de l'amorce

C'est ce qui rend la précipitation par amorçage économique.

- **Liqueur épuisée** (≈ 27 L après la filtration de l'hydrate) : elle contient toute la soude et ≈ 1,2 kg d'Al₂O₃ encore dissoute. On la garde dans le fût, puis on la renvoie dans R1 par la pompe de transfert.
- **Évaporation** : les eaux de lavage ajoutent ≈ 8–10 L par lot. On les évapore dans R1 ouverte, à ébullition douce, avant l'attaque suivante (≈ 6–7 kWh).
- **Appoint de soude** : ≈ 0,3–0,5 kg par lot, pour remplacer ce qui part avec les boues et les lavages.
- **Amorce** : après la filtration de l'hydrate, on remet ≈ 3,5 kg de gâteau dans le pot AMORCE ; seul le reste (≈ 1,7 kg) va au four. La première amorce est de l'hydroxyde d'aluminium du commerce (quelques kilos, peu cher).
- **Purge** : tous les 5 à 10 lots, remplacer une partie de la liqueur, qui se charge en impuretés (carbonate, silice, matière organique).

---

## 8. Mode opératoire

### Jour 1 — Attaque et filtration (≈ 7 h)

| # | Action | Repère |
|---|---|---|
| 1 | Verser **19 L d'eau** dans R1 par la trappe, agitation 150 tr/min (lots suivants : la liqueur recyclée, déjà évaporée) | |
| 2 | Ajouter **4,3 kg de NaOH** par portions de ~250 g en 20–30 min (lots suivants : l'appoint) | La dissolution chauffe seule jusqu'à ~60–70 °C. Toujours la soude dans l'eau, jamais l'inverse |
| 3 | Chauffer à 90 °C, puis verser la **poudre de bauxite** en 10 min par la trappe (5 kg au premier lot, ≈ 2,7 kg ensuite) | |
| 4 | Monter à **100 ± 3 °C**, tenir **2 h** à 200–250 tr/min, trappe fermée | Compléter l'eau évaporée jusqu'au repère |
| 5 | Ajouter 5 L d'eau chaude (eau de lavage du lot précédent) + 5–10 g d'amidon délayé, agiter 5 min, arrêter | L'amidon aide les boues à se déposer |
| 6 | Laisser décanter 1–2 h en maintenant **≥ 85 °C** | En dessous, l'alumine reprécipite dans les boues |
| 7 | Régler la pompe à vide sur **−0,2 bar**, ouvrir la **vanne haute** : la liqueur claire passe sur la toile « rouge » | Ne jamais dépasser −0,2 bar avec la liqueur chaude |
| 8 | Ouvrir la **vanne basse** : les boues vont sur le filtre | |
| 9 | Laver le gâteau avec 3 × 3 L d'eau à 80 °C | Le 1er lavage rejoint la liqueur ; les autres servent d'eau au lot suivant |
| 10 | Repasser la liqueur sur une toile fine propre, puis la pomper (≈ 27 L) dans R2 par la trappe | Elle doit être parfaitement limpide : chaque grain de boue rouge finit en fer et silicium dans l'aluminium |

### Jours 1 à 3 — Précipitation par amorçage (48 h)

| # | Action | Repère |
|---|---|---|
| 11 | Laisser R2 descendre à **60 °C**, agitation 100–150 tr/min | |
| 12 | Verser **≈ 3,5 kg d'amorce** (hydrate d'alumine) par la trappe | ≈ 130 g/L. Plus d'amorce = précipitation plus rapide |
| 13 | Agiter **48 h** en laissant descendre de 60 à **50 °C** (consigne du PID abaissée de 2 °C toutes les 10 h environ) | Plus froid précipite plus, mais donne des grains trop fins |
| 14 | Filtrer à −0,5 bar sur la toile « blanche » | Le filtrat est la liqueur épuisée : la garder (§7) |
| 15 | Laver le gâteau à l'eau chaude, au moins 3 × 5 L, jusqu'à pH du filtrat < 9 | Ce lavage fixe la teneur en sodium |
| 16 | Remettre ≈ 3,5 kg de gâteau dans le pot AMORCE ; le reste part au séchage | |

### Jours 3 et 4 — Séchage et calcination

17. Sécher une nuit à 110 °C, remplir 2 ou 3 creusets, cuire selon le programme du §6, peser l'alumine.

Un lot complet prend environ **4 jours**, dont 2 de précipitation. On peut attaquer le lot suivant dans R1 pendant que R2 précipite.

---

## 9. Mise à l'échelle

La capacité est fixée par le **volume de liqueur**, pas par la bauxite : chaque litre de liqueur dissout et rend ≈ 45 g d'Al₂O₃ par cycle.

| Cuves | Liqueur | Bauxite par lot (régime établi) | Alumine par lot |
|---|---|---|---|
| 50 L (ce plan) | ≈ 25 L | ≈ 2,7 kg | ≈ 1,1–1,2 kg |
| 100 L | ≈ 50 L | ≈ 5 kg | ≈ 2,2 kg |
| 200 L | ≈ 100 L | ≈ 10 kg | ≈ 4,5 kg |

Par litre de liqueur en circulation : ≈ 0,17 kg de NaOH, ≈ 130 g d'amorce. Au-delà de 200 L : chauffage par double enveloppe, filtre-presse, pompe pour tous les transferts.

---

## 10. Sécurité (à lire avant tout achat)

La soude à 270 g/L et 100 °C est le danger principal : une projection dans l'œil rend aveugle en quelques secondes.

- **Poste de sécurité** (dans le modèle 3D, entre R2 et le four) : **douche de sécurité + rince-œil** à moins de 10 secondes de chaque poste, raccordée à l'eau. En cas de contact : rinçage 15 min minimum, pas de vinaigre.
- **Protections obligatoires** (panneau près des cuves) : lunettes étanches **et** écran facial, gants longs nitrile ou néoprène, tablier chimique, bottes, manches longues.
- **Pas de pression** : l'évent des cuves n'est jamais bouché. Aucune cuve fermée n'est chauffée.
- **Vide limité à −0,2 bar** sur la liqueur chaude (§5).
- **Rétention** : bac sous les cuves et le filtre.
- **Aération** : extracteur d'air mural (brouillard de soude, vapeur du four).
- **Levage** : le fût du broyeur (≈ 18 kg) se lève au palan, jamais à bout de bras.
- **Aluminium interdit** dans tout le circuit caustique (hydrogène inflammable).
- **Électricité** : tableau avec **différentiel 30 mA** ; chaque appareil de 3 kW sur son propre circuit 16 A ; coffrets hors zone d'éclaboussures. Extincteur à proximité.
- **Boues rouges** : pH 11–14. Les laver, puis les neutraliser à pH 8–9 (acide dilué ajouté lentement), sécher, stocker en fût fermé, évacuer selon la réglementation locale. Certaines bauxites concentrent des métaux lourds dans les boues.
- **Poussières** : masque FFP3 pour le broyage, la soude en paillettes et l'alumine.
- **Étiquetage** : chaque seau, pot et bac porte le nom de son contenu (BAUXITE, POUDRE DE BAUXITE, SOUDE NaOH en rouge, AMORCE, BOUES ROUGES, EAU…).

---

## 11. Ordre de construction conseillé

1. **Essai de validation à 200 g** dans un récipient inox de 2 L sur plaque chauffante : 200 g de bauxite, 172 g de NaOH, 760 mL d'eau, 100 °C, 2 h, filtration à −0,2 bar (ou par gravité) en restant au-dessus de 85 °C, puis précipitation 48 h avec 140 g d'amorce, et cuisson au four. Cet essai vérifie :
   - le **taux d'extraction** (si on récupère moins de la moitié de l'alumine attendue dans la liqueur, voir §12) ;
   - que la liqueur **ne reprécipite pas** pendant la décantation ;
   - la **teneur en sodium** de l'alumine (analyse par un laboratoire, fluorescence X) ;
   - la quantité d'alumine réellement obtenue par litre de liqueur.
2. Cuve R1 + filtre F + pompe de transfert.
3. Cuve R2 (identique à R1).
4. Poste de sécurité (douche/rince-œil, protections, tableau électrique) : **avant** la première attaque.
5. Four K (achat).
6. Broyeur A0 + chariot à trémie + potence (au début on peut broyer à la main de petites quantités).

### Budget indicatif (matériel neuf ; à vérifier par devis)

| Poste | Ordre de grandeur |
|---|---|
| 2 cuves complètes (marmite, vannes, agitateur, plaque, PID, châssis) | 1000–1400 € |
| Filtre (cuve, fût, pompe à vide, toiles) + pompe de transfert | 350–550 € |
| Four à moufle 1200 °C + 3 creusets + plaque d'enfournement | 500–900 € |
| Broyeur (tube épais, rouleaux, motoréducteur) + chariot à trémie | 250–450 € |
| Potence + palan à chaîne + étrier | 150–300 € |
| Poste de sécurité (douche/rince-œil, protections, extincteur, extracteur) | 250–450 € |
| Amorce (hydroxyde d'aluminium), bacs, étiquettes, divers | 100–200 € |
| **Total** | **≈ 2600–4250 €** |

---

## 12. Si la bauxite n'est pas gibbsitique (plan B)

Les bauxites à boehmite ou diaspore demandent 200–250 °C sous 15–35 bar : un autoclave de ce type ne se bricole pas. On garde alors tout l'atelier et on remplace seulement l'attaque par un **frittage à la soude dans le four K** :

- mélanger bauxite broyée + carbonate de sodium (rapport molaire Na₂O/Al₂O₃ ≈ 1) + chaux (CaO/SiO₂ ≈ 2 en moles) ;
- cuire 1 h–1 h 30 à 1000–1200 °C ;
- broyer le fritté et le lessiver à l'eau chaude dans R1 → liqueur d'aluminate ;
- la suite (filtre, R2, four) est identique.

Les essais publiés donnent ~88 % d'extraction et une alumine à ~98 % par cette voie.

---

## 13. Variante — Précipitation au CO₂ (rapide, moins pure)

Pour une alumine destinée à autre chose que l'électrolyse (céramique, abrasif, démonstration) :

- ajouter à R2 une ligne CO₂ : bouteille 10 kg sur balance → détendeur → débitmètre 0–15 L/min → **clapet anti-retour** → tube plongeur inox terminé par un anneau percé sous la turbine ;
- carbonater **à 60–65 °C au plus** (au-dessus de 65 °C, risque de dawsonite), 5–8 L/min pendant 3–5 h, **arrêter à pH ≈ 11** ;
- toute l'alumine dissoute précipite en une fois : un lot de 5 kg de bauxite donne ≈ 2 kg d'alumine, sans cuves plus grandes ;
- mais l'alumine garde ≈ 0,6 % de Na₂O même après lavages répétés, et toute la soude devient du carbonate (≈ 5,7 kg par lot). On peut la régénérer à la chaux (Na₂CO₃ + Ca(OH)₂ → 2 NaOH + CaCO₃, 95 °C, ≈ 3,9 kg de chaux éteinte par lot), mais il faut ensuite évaporer beaucoup d'eau.

---

## 14. Adaptation à ton cas : Cameroun, achats en Chine, objectif aluminium

### Bauxite camerounaise

Les gisements connus (Minim-Martap et Ngaoundal dans l'Adamaoua, Fongo-Tongo à l'Ouest) sont **gibbsitiques**, vers 45 % d'Al₂O₃ avec peu de silice réactive (≈ 2–3 %). C'est le cas favorable. Comme tu ne connais pas l'origine exacte de ton minerai, l'essai à 200 g reste la première chose à faire.

### Contraintes locales

- **Électricité** : 220 V / 50 Hz monophasé. Ne pas faire chauffer deux appareils de 3 kW en même temps sur une installation domestique.
- **Coupures de courant** : l'attaque peut supporter une courte coupure (l'isolation garde la chaleur 1–2 h), mais R2 doit agiter **48 h sans arrêt**. Prévoir un groupe électrogène ou un onduleur qui tient les agitateurs (250 W chacun).
- **Soude** : en paillettes, sacs de 25 kg, chez les fournisseurs des savonneries. Ne s'importe pas par colis (matière dangereuse).
- **Hydroxyde d'aluminium (amorce)** : produit courant (traitement de l'eau, charges minérales), à acheter une seule fois.

### Fabriquer sur place ou acheter en Chine

| À souder / fabriquer localement | À commander en Chine (mots-clés de recherche) |
|---|---|
| Les châssis en cornière, la potence (colonne, flèche) | `50L 304 stainless steel stock pot` (×2) et `30L` (×1) |
| Le broyeur (tube Ø 273 × 6, releveurs, couvercle, rouleaux) et le chariot à trémie | `DN25 304 ball valve full bore PTFE` (×5) + `1 inch 304 weld half coupling` |
| Perçage des couvercles (trappes Ø 76) et du fond du filtre | `gear motor 200W 220V speed controller` (×2), `4 blade pitched impeller 304` |
| Soudure TIG des manchons et collerettes | `REX-C100 PID SSR-40DA kit`, `PT100 thermowell 304` |
| Bac de rétention, table de préparation | `3000W electric hot plate cast iron 220V` (×2) |
| | `polypropylene filter cloth 5 micron`, `30L stainless beer keg`, `oil free diaphragm vacuum pump 220V` |
| | `stainless centrifugal transfer pump 220V` |
| | **`1200C box muffle furnace 220V`**, `cordierite sagger 160mm` (×3), `kiln shelf` |
| | `manual chain hoist 100kg`, `grinding steel balls 20mm 30mm`, `60 mesh test sieve` |
| | `emergency shower eyewash station` |

Regrouper la commande chez un transitaire (groupage maritime). Je n'ai pas vérifié les prix : demander des devis.

### Ce que l'objectif « aluminium » change

L'alumine destinée à l'électrolyse doit être pauvre en **fer, silicium et sodium**. Repères de qualité métallurgique : Al₂O₃ ≥ 98,5 %, SiO₂ et Fe₂O₃ ≤ 0,02–0,03 %, Na₂O ≤ 0,5 %, perte au feu ≤ 1 %. Ce qui est fait pour cela :

- précipitation **par amorçage** plutôt qu'au CO₂ (moins de sodium, pas de dawsonite) ;
- liqueur filtrée deux fois avant précipitation (étape 10) ;
- 2 h d'attaque complètes, pour que la silice dissoute reprécipite dans les boues ;
- lavage abondant de l'hydrate (étape 15) ;
- calcination à 1050 °C maximum : au-delà, l'alumine devient « alpha » et se dissout mal dans le bain d'électrolyse.

Sans analyse, la pureté réelle ne peut pas être garantie : faire analyser le premier lot (fluorescence X).

**Attention à l'étape suivante.** Transformer l'alumine en aluminium (électrolyse Hall-Héroult) est un projet à part, nettement plus difficile que ce plan : bain de cryolithe fondue à 950–960 °C, courant continu de plusieurs centaines d'ampères sous 4–5 V, anodes en carbone consommées, fumées fluorées toxiques, environ 13–15 kWh par kg de métal. Il faut ≈ 1,9 kg d'alumine pour 1 kg d'aluminium : un lot de ce plan donne donc ≈ 0,6 kg de métal.

---

## 15. Modèle 3D et plans cotés

| Fichier | Contenu |
|---|---|
| `plans/planche-1-cuve.svg` | Cuve R : coupe cotée + perçages du couvercle |
| `plans/planche-2-chassis-cuve.svg` | Châssis de cuve et portique d'agitateur |
| `plans/planche-3-broyeur.svg` | Broyeur : tambour, châssis, rouleaux, chariot à trémie |
| `plans/planche-4-filtre.svg` | Filtre : cuve filtrante, fût récepteur, vannes, pompes |
| `plans_cotes.py` | Script qui regénère les 4 planches |
| `usine-bauxite-alumine-realiste.blend` | Modèle réaliste à l'échelle 1:1 (mètres), une collection par appareil, chaque pièce nommée |
| `usine-bauxite-alumine-animation.blend` | Animation du procédé (≈ 1 min 45) |
| `construire_usine.py`, `materiaux_realistes.py`, `animer_usine.py` | Scripts qui regénèrent le modèle, les matériaux et l'animation |
| `rendu-realiste-*.png` | Vues d'ensemble et de détail |
| `usine-bauxite-alumine.blend`, `rendu-vue-ensemble.png`, `rendu-cuves-filtre.png` | Première version (couleurs de schéma), gardée pour mémoire |

Implantation : le filtre est **entre** les deux cuves, dont les vannes se font face ; R1 puis R2 s'y vident par gravité. La pompe de transfert renvoie la liqueur du filtre vers R2 (puis la liqueur épuisée vers R1). La potence est derrière le broyeur, le poste de sécurité entre R2 et le four.

Les plans cotés donnent les cotes d'ensemble et les positions de perçage tirées du modèle. Avant découpe, vérifier chaque cote sur les pièces réellement achetées (diamètre exact de la marmite, entraxe des vannes, etc.).

---

## Sources

- [Digestion de la bauxite gibbsitique à basse température (brevet US 6555076)](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/6555076)
- [Procédé de production d'alumine, digestion et rapport A/C (brevet US 5122349)](https://patents.google.com/patent/US5122349)
- [Cinétique de dissolution de la bauxite gibbsitique sous pression atmosphérique, Yang et al. 2017](https://link.springer.com/article/10.1007/s11771-017-3451-7)
- [Lixiviation de bauxite à 95–105 °C, 200–250 g/L NaOH (E3S Conf. 2016)](https://www.e3s-conferences.org/articles/e3sconf/pdf/2016/03/e3sconf_mec2016_01021.pdf)
- [Dissolution de la gibbsite dans NaOH à pression ambiante, Grénman et al.](https://digital.library.adelaide.edu.au/items/ef7ff937-d40d-4e6a-ba0d-cbf077370ade/full)
- [Précipitation Bayer par amorçage : 55–75 °C, 24–72 h — fiche technologique](https://portfolio-pplus.com/TechnologyTypes/Details/169)
- [Facteurs influençant le taux de précipitation — ICSOBA 2023](https://icsoba.org/assets/files/publications/2023/Papers/AA16%20-%20Study%20on%20Influencing%20Factors%20of%20Precipitation%20ratio.pdf)
- [Récupération d'alumine par carbonatation, teneur en sodium — ICSOBA 2025](https://icsoba.org/assets/files/publications/2025/Papers/AA09%20-%20Alumina%20Recovery%20from%20Sodium%20Aluminate%20Solutions%20via%20Carbonation.pdf)
- [Procédé Pedersen : dawsonite au-dessus de 65 °C (Springer)](https://link.springer.com/content/pdf/10.1007/s40831-021-00403-w.pdf)
- [Carbonatation des solutions d'aluminate — Crystals 2021](https://mdpi.com/2073-4352/11/7/836)
- [Séparation des boues rouges chaudes sous pression (brevet)](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5607598)
- [Filtre sous pression contre la vaporisation — ICSOBA 2018](https://icsoba.org/assets/files/publications/2018/BX14.pdf)
- [Filtration des boues rouges — ANDRITZ](https://www.andritz.com/separation-en/insights/red-mud)
- [Hydrate d'alumine : densité, perte au feu — Digitalfire](https://digitalfire.com/material/alumina+hydrate)
- [Densité de la gibbsite (brevet alumine activée)](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/6962684)
- [Broyeurs à boulets de laboratoire : levage, grille de vidange — 911 Metallurgist](https://www.911metallurgist.com/equipment/lab-ball-mill)
- [Broyeur à jarres sur rouleaux](https://conductscience.com/lab/laboratory-roller-ball-mill)
- [Paramètres de calcination et qualité de l'alumine — ICSOBA 2024](https://icsoba.org/assets/files/publications/2024/Papers/AA29%20-%20Influence%20of%20Calcination%20Parameters%20on%20Alumina%20Quality%20in%20Gas%20Suspension%20Calciner.pdf)
- [Procédé de frittage chaux-soude sur bauxite pauvre](https://jme.shahroodut.ac.ir/article_2616_290a9fd6512f0f7cac173acdd5939afa.pdf)
- [Frittage chaux-soude pour bauxites siliceuses — RSC Advances 2023](https://pubs.rsc.org/en/content/articlepdf/2023/ra/d3ra03362g)
- [Corrosion en milieu soude caustique : acier et inox](https://hghouston.com/archive/special-corrosion-topics/caustic-corrosion)
- [Choix des inox pour la soude](https://tubingchina.com/Selection-of-stainless-steel-for-handling-sodium-hydroxide-NaOH.htm)
- [Neutralisation des lixiviats de boues rouges (Ajka) — Burke et al. 2013](https://homepages.see.leeds.ac.uk/~earitb/Burke%20et%20al%202013est.pdf)
- [Bauxite de Minim-Martap, Cameroun : composition](https://www.alcircle.com/news/canyon-resources-releases-resource-upgrade-for-its-minim-martap-bauxite-project-in-cameroon-48080)
