# Mini-usine bauxite → alumine : plan de construction (version 1)

Atelier discontinu (« batch ») composé de 4 appareils séparés. On charge un appareil, on regarde ce qui en sort, on passe au suivant.

**Taille de référence : 5 kg de bauxite par lot → environ 1,7 à 2,0 kg d'alumine.**
Toutes les quantités se mettent à l'échelle avec le tableau du §9.

---

## 1. Les choix de procédé (et pourquoi)

L'industrie utilise le procédé Bayer : attaque à la soude en autoclave (140–250 °C sous pression), décantation, précipitation par amorçage pendant 24–72 h, calcination en lit fluidisé. C'est trop lourd pour une petite quantité. Voici ce que j'ai simplifié :

| Étape | Industrie | Ici | Ce qu'on y gagne |
|---|---|---|---|
| Attaque | Autoclave 140–250 °C, 5–35 bar | Cuve **ouverte** à 100 °C, soude à ~220 g/L, 2 h | Aucun appareil sous pression. Fonctionne pour la bauxite **gibbsitique** (Guinée, Cameroun, Ghana, Brésil, Jamaïque…) |
| Séparation des boues | Décanteurs + laveurs en cascade | Décantation dans la cuve + un filtre sous vide | 1 seul appareil de filtration pour tout |
| Précipitation | Amorçage, 24–72 h, ~50 % de rendement par passe | **Carbonatation au CO₂**, 3–5 h, ~95 % de rendement | Rapide, visible, pas de stock d'amorce à gérer |
| Calcination | Lit fluidisé / four rotatif | Four électrique à chambre, 1050 °C | Un four de potier suffit |

Astuce de construction : l'attaque et la précipitation se font dans **le même modèle de cuve agitée chauffée**. On construit donc un seul design, en deux exemplaires.

Le prix à payer pour la carbonatation : la soude est transformée en carbonate de sodium et n'est pas réutilisable directement (voir §7 pour la régénérer à la chaux, en option).

### Chimie

```
Attaque        Al(OH)3 + NaOH            →  NaAl(OH)4            (100 °C)
Précipitation  2 NaAl(OH)4 + CO2         →  2 Al(OH)3 ↓ + Na2CO3 + H2O
               2 NaOH (excès) + CO2      →  Na2CO3 + H2O
Calcination    2 Al(OH)3                 →  Al2O3 + 3 H2O ↑      (1050 °C)
```

Le fer, le titane et la silice ne se dissolvent pas (ou reprécipitent) : ils partent dans les **boues rouges**.

---

## 2. Vue d'ensemble

```
 Bauxite 5 kg
     │
 ┌───▼────────────┐
 │ A0 PRÉPARATION │  sécher → concasser → broyer → tamiser < 250 µm
 └───┬────────────┘
     │ poudre 5 kg            NaOH 3,5 kg + eau 15,5 L
 ┌───▼────────────┐◄──────────────┘
 │ R1 ATTAQUE     │  100 °C, 2 h, agitation
 └───┬────────────┘
     │ pulpe chaude
 ┌───▼────────────┐
 │ F  FILTRE      │──► boues rouges ≈ 4 kg humides (≈ 2 kg sec) → lavage → neutralisation
 └───┬────────────┘
     │ liqueur claire d'aluminate ≈ 28 L     CO2 ≈ 2 kg
 ┌───▼────────────┐◄──────────────────────────┘
 │ R2 PRÉCIPITAT. │  75 °C, 3–5 h, jusqu'à pH ≈ 11
 └───┬────────────┘
     │ suspension blanche
 ┌───▼────────────┐
 │ F  FILTRE      │──► solution de Na2CO3 ≈ 4,6 kg dissous (→ §7)
 └───┬────────────┘
     │ hydrate Al(OH)3 ≈ 2,9 kg sec
 ┌───▼────────────┐
 │ K  FOUR        │  1050 °C, 1 h 30  (–35 % de masse : vapeur d'eau)
 └───┬────────────┘
     ▼
 ALUMINE ≈ 1,7–2,0 kg (poudre blanche)
```

### Bilan matière pour 5 kg de bauxite

Hypothèse : bauxite gibbsitique à ~50 % Al₂O₃ total, dont ~45 % extractible, ~2,5 % de silice réactive, ~20 % Fe₂O₃. **À recalculer avec ton analyse réelle.**

| Entrées | | Sorties | |
|---|---|---|---|
| Bauxite sèche | 5,0 kg | Alumine | 1,7–2,0 kg |
| Soude NaOH (perles/paillettes) | 3,5 kg | Boues rouges (sec) | 1,7–2,2 kg |
| Eau (attaque + lavages) | ≈ 40 L | Carbonate de sodium (en solution) | ≈ 4,6 kg |
| CO₂ | ≈ 2 kg (prévoir 2,5) | Vapeur d'eau (four) | ≈ 1 kg |
| Électricité | ≈ 25–35 kWh | | |

---

## 3. Appareil A0 — Préparation de la bauxite

But : poudre sèche passant au tamis de 250 µm. Plus c'est fin, plus l'attaque est complète (les essais publiés donnent ~80 % d'extraction en 1 h sur la fraction fine contre 43–58 % sur les fractions grossières).

1. **Séchage** : 105 °C quelques heures (four de cuisine dédié, ou soleil).
2. **Concassage** à < 10 mm : masse sur plaque d'acier dans un sac de toile, ou petit concasseur à mâchoires.
3. **Broyage — broyeur à boulets à construire :**
   - Tambour : fût acier 20 L à couvercle cerclé (Ø ≈ 280 mm), 3 cornières soudées à l'intérieur comme releveurs.
   - Charge : 10–12 kg de billes d'acier Ø 20–40 mm + 5 kg de bauxite (≈ 40 % du volume).
   - Vitesse : 55–60 tr/min (≈ 70 % de la vitesse critique 42,3/√D).
   - Entraînement : tambour posé sur 2 arbres Ø 20 mm gainés de caoutchouc, montés sur 4 paliers ; un arbre entraîné par motoréducteur 180–250 W avec courroie.
   - Durée : 1–2 h.
   - **Couvercle à charnière** : le couvercle cerclé du fût est monté sur une charnière verticale (côté arrière), il s'ouvre comme une porte sans être posé au sol.
   - **Chargement : chariot à trémie** : trémie carrée inox (300 × 300 mm en haut) + goulotte en U inclinée à 44°, longueur 450 mm, sur un poteau à base roulante. On l'avance jusqu'à ce que le bout de la goulotte entre dans l'ouverture du fût, on verse la bauxite puis les billes dans la trémie, on recule le chariot et on referme.
   - **Vidange : grille + bac** : on pose une grille (barreaux tous les 35 mm) dans l'ouverture pour retenir les billes, on soulève le fût et on l'incline au-dessus d'un bac de récupération inox (≈ 10 L) ; la poudre tombe, les billes restent dans le fût.
4. **Tamisage** à 250 µm (tamis 60 mesh) ; le refus retourne au broyeur.

Masque FFP3 pendant le broyage et le tamisage.

---

## 4. Appareil R — Cuve agitée chauffée (à construire en 2 exemplaires : R1 et R2)

```
              moteur-réducteur 150–250 W, 100–300 tr/min
                    ┌───┐
   portique acier ══╪═══╪══════════════
                    │   │        évent Ø25 → extérieur (JAMAIS fermé)
   trappe Ø100 ┐    │   │   ┌─ doigt de gant + sonde
          ╔════╧════╪═══╪═══╧════╗  couvercle inox
          ║         │arbre Ø14   ║
   laine  ║         │            ║  marmite inox 304/316, 50 L
   de     ║ chicane │            ║  Ø 400 × H 400 mm, fond épais
   roche  ║  │      │            ║
   50 mm  ║  │   ╱──┴──╲ turbine ║
          ║  │   4 pales 45°     ╠═► vanne HAUTE DN25 (axe à 70 mm du fond)
          ║      Ø 130 mm        ║     = soutirage du liquide clair
          ╚══════════════════════╩═► vanne BASSE DN25 (au ras du fond)
          ▓▓▓▓ plaque électrique 3 kW ▓▓▓▓     = vidange des boues / solides
          ───── châssis acier, fond de cuve à 90 cm du sol ─────
          ═════ bac de rétention ≥ 50 L sous l'ensemble ═════
```

### Liste des pièces (par cuve)

| Pièce | Spécification | Remarque |
|---|---|---|
| Cuve | Marmite inox 304 ou 316, 50 L, fond sandwich | Volume utile 18–30 L, le reste est de la garde contre les débordements |
| Vannes (×2) | Robinet à boisseau sphérique inox DN25 **passage intégral**, sièges PTFE | Montage par manchon soudé TIG, ou traversée de paroi vissée avec joints PTFE/EPDM |
| Couvercle | Inox, percé : arbre (Ø 20 avec bague PTFE), trappe de chargement Ø 76, doigt de gant, évent Ø 25 | L'évent part vers l'extérieur ; la cuve reste toujours à pression atmosphérique |
| Trappe de chargement | Collerette inox Ø 76 × 30 mm soudée sur le trou + couvercle Ø 100 à charnière (côté extérieur) et bouton | Tout entre par là : l'eau (tuyau), la soude, la poudre de bauxite ; sur R2, le tuyau de la liqueur |
| Agitateur | Motoréducteur 150–250 W à vitesse variable ; arbre inox Ø 14 × 450 mm ; turbine 4 pales inclinées Ø 130 mm, à 60 mm du fond | Sens : pousse vers le bas |
| Chicanes | 3 plats inox 35 × 300 mm accrochés au bord | Facultatif mais empêche le vortex et les dépôts |
| Chauffage | Plaque électrique résistive 2,5–3 kW | Résistive (pas induction) pour pouvoir la piloter par relais |
| Régulation | Régulateur PID + relais statique 40 A sur dissipateur + sonde PT100 ou thermocouple K dans un doigt de gant inox | Ajouter un thermostat de sécurité indépendant réglé à 115 °C |
| Isolation | Laine de roche 50 mm + tôle autour de la paroi | Divise le temps de chauffe et protège des brûlures |
| Châssis | Cornière acier 40 × 40, peinte époxy | Hauteur telle que la vanne basse soit au-dessus du filtre |

**Supplément pour R2 (précipitation) :**
bouteille de CO₂ 10 kg (alimentaire ou soudage) posée sur une balance → détendeur → débitmètre à bille 0–15 L/min → **clapet anti-retour** → tube plongeur inox Ø 10 terminé par un anneau percé de trous de 1 mm, placé sous la turbine.

### Matériaux : ce qui est permis et interdit avec la soude chaude

- **Oui** : inox 304/316 (jusqu'à ~100 °C à cette concentration), PTFE, EPDM, polypropylène (jusqu'à ~80 °C).
- **Jamais** : aluminium (dégage de l'hydrogène, se perce), zinc / acier galvanisé, laiton, étain, verre ordinaire, joints Viton (FKM), silicone en contact prolongé.
- Acier ordinaire : acceptable à froid, à éviter au-dessus de ~65 °C (fissuration caustique).

---

## 5. Appareil F — Filtre sous vide (1 exemplaire, 2 toiles)

```
        pulpe
          ▼
   ┌──────────────┐  cuve supérieure inox 30 L
   │              │
   │▒▒▒▒▒▒▒▒▒▒▒▒▒▒│  toile filtrante polypropylène, serrée par un cerclage
   │● ● ● ● ● ● ● │  fond percé Ø 5 mm, entraxe 15 mm (ou tôle perforée)
   └──────┬───────┘
     joint EPDM
   ┌──────┴───────┐
   │  fût inox    │──► vacuomètre + vanne de mise à l'air
   │  30–50 L     │──► piège à liquide 5 L ──► pompe à vide
   │  (filtrat)   │        (trompe à eau ou pompe à membrane, –0,3 à –0,6 bar)
   └──────────────┘
```

- **Récepteur** : fût à bière inox (conçu pour la pression, il tient le vide). Ne pas utiliser de seau plastique ni de marmite à paroi mince sous vide avec du liquide chaud.
- **Toiles** : une toile PP ~5–10 µm réservée aux boues rouges, une toile PP ~10–25 µm réservée à l'hydrate blanc. Ne jamais les mélanger, sinon l'alumine sera rose.
- **Version économique sans vide** : poche filtrante PP 5 µm suspendue dans un seau inox. Ça marche, mais les boues rouges mettent plusieurs heures à s'égoutter.
- **Sortie des gâteaux** : la galette (boue rouge, puis hydrate) sort par le haut de la cuve filtrante, avec sa toile.
- **Vidange du récepteur et transfert vers R2** : piquage inox au bas du fût + petite vanne à boisseau, tuyau vers une petite pompe de transfert (pompe centrifuge inox ou pompe à membrane, ≈ 10–20 L/min, compatible soude), puis tuyau qui entre dans R2 par sa trappe de chargement. La liqueur ne remonte pas toute seule d'environ 1,3 m : il faut cette pompe (ou la transvaser au seau).

---

## 6. Appareil K — Four de calcination

**Option recommandée : four à moufle de laboratoire 1200 °C du commerce** (« box muffle furnace », chambre ≈ 230 × 230 × 300 mm, 12–15 L, 220 V, régulateur à rampes intégré, porte à charnière). C'est le four représenté dans le modèle 3D et la solution la plus simple depuis le Cameroun (voir §14). Un four de potier électrique d'occasion (40–60 L, 1200–1300 °C) convient aussi. C'est la pièce la plus difficile à fabriquer soi-même.

**Table de préparation** : à côté du four, une petite table dont le plateau est à la hauteur de la sole de la chambre. On y remplit le creuset d'hydrate, puis on le fait glisser à plat jusque dans le four par la porte, et on l'y ressort de la même façon (gants et pince à creuset : il ressort chaud).

**Option à construire** (ordre de grandeur, à détailler avant fabrication) :

| Élément | Spécification |
|---|---|
| Chambre | ≈ 230 × 230 × 230 mm (12 L), en briques réfractaires isolantes classe 26 (230 × 114 × 64 mm), ≈ 30 briques |
| Isolation extérieure | Panneau de fibre biosoluble 25 mm + carcasse en cornière et tôle |
| Résistance | Fil Kanthal A1 Ø 1,6 mm, ≈ 24 m bobiné (≈ 17,5 Ω → 3 kW sous 230 V), logé dans des rainures fraisées dans les briques |
| Régulation | Régulateur PID à rampes/paliers + relais statique 40 A + thermocouple K (ou S) |
| Sécurité | Contact de porte coupant la puissance, châssis relié à la terre, différentiel 30 mA |

**Récipients** : gazettes en cordiérite-mullite ou creusets en alumine, couche de poudre ≤ 40–50 mm.

**Programme de cuisson :**

1. Sécher l'hydrate à 110 °C (une nuit).
2. Montée à 5 °C/min jusqu'à 400 °C, palier 60 min, évent ouvert (c'est là que part l'essentiel de l'eau).
3. Montée à 5–8 °C/min jusqu'à 1050 °C, palier 90 min.
4. Refroidissement naturel porte fermée.

Contrôle : la masse doit avoir baissé de ~35 %. Une seconde cuisson d'un échantillon ne doit plus faire perdre que < 1 %.

---

## 7. Option — Régénérer la soude à la chaux

Le filtrat de R2 est une solution de carbonate de sodium. Dans R1 (libre à ce moment-là) :

```
Na2CO3 + Ca(OH)2  →  2 NaOH + CaCO3 ↓      (95 °C, 1–2 h, agitation)
```

- Diluer à ≈ 100 g/L de Na₂CO₃ (≈ 45 L pour un lot), ajouter ≈ 3,2 kg de chaux éteinte, filtrer le calcaire.
- On récupère ≈ 85–90 % de la soude, mais diluée (~70 g/L) : il faut évaporer environ les deux tiers de l'eau pour la réutiliser. C'est rentable seulement si la soude est chère ou si on enchaîne beaucoup de lots.
- Sans cette option : évaporer et cristalliser le carbonate (cristaux de soude), ou le faire reprendre par une filière de déchets. Pas de rejet au sol ni à l'égout.

---

## 8. Mode opératoire d'un lot de 5 kg

### Jour 1 — Attaque et filtration (≈ 7 h)

| # | Action | Repère |
|---|---|---|
| 1 | Verser **15,5 L d'eau froide** dans R1, agitation à 150 tr/min | |
| 2 | Ajouter **3,5 kg de NaOH** par portions de ~250 g en 20–30 min | La dissolution chauffe seule jusqu'à ~60–70 °C. Toujours la soude dans l'eau, jamais l'inverse |
| 3 | Chauffer à 90 °C, puis ajouter les **5 kg de bauxite** en 10 min par la trappe | |
| 4 | Monter à **100 ± 3 °C**, tenir **2 h** à 200–250 tr/min, couvercle posé | Compléter l'eau évaporée jusqu'au repère de niveau |
| 5 | Ajouter 8 L d'eau chaude + 5–10 g d'amidon (ou farine) délayé, agiter 5 min, arrêter l'agitation | L'amidon est le floculant historique des boues rouges |
| 6 | Laisser décanter 1–2 h en maintenant **≥ 85 °C** | En dessous, l'alumine reprécipite dans les boues et elle est perdue |
| 7 | Ouvrir la **vanne haute** : la liqueur claire passe par le filtre (toile « rouge ») | Liquide jaune-brun limpide |
| 8 | Ouvrir la **vanne basse** : les boues épaisses vont sur le filtre | |
| 9 | Laver le gâteau avec 3 × 3 L d'eau à 80 °C | Le 1er lavage rejoint la liqueur ; les suivants servent d'eau pour le lot suivant |
| 10 | Repasser toute la liqueur une 2e fois sur une toile fine propre (filtration de sécurité), puis la transférer (≈ 28 L) dans R2 | Elle doit être parfaitement limpide : chaque grain de boue rouge qui passe finit en fer et silicium dans l'aluminium |

### Jour 1 ou 2 — Précipitation (≈ 6 h)

| # | Action | Repère |
|---|---|---|
| 11 | Porter R2 à **75 °C**, agitation 150 tr/min. Si disponible, ajouter 0,5–1 kg d'hydrate d'un lot précédent comme amorce | L'amorce donne des grains plus gros, plus faciles à filtrer |
| 12 | Injecter le CO₂ à **5–8 L/min** pendant 3–5 h | La réaction chauffe : la plaque ne travaille presque pas. Injection trop rapide → gel infiltrable |
| 13 | Toutes les 30 min : prélever 20 mL, refroidir, mesurer le pH | Les sondes pH ne survivent pas en continu dans ce milieu |
| 14 | **Arrêter le CO₂ à pH ≈ 11** (≈ 1,8–1,9 kg consommés à la balance) | Plus bas, la silice dissoute et la dawsonite (aluminium + sodium + carbonate) précipitent et polluent le produit. Pour faire de l'aluminium, mieux vaut perdre 5 % de rendement que pousser la carbonatation |
| 15 | Laisser mûrir 1 h sous agitation, puis filtrer (toile « blanche ») | |
| 16 | Laver le gâteau à l'eau à 80 °C, au moins 3 × 5 L, jusqu'à pH du filtrat < 9 | C'est ce lavage qui fixe la pureté (sodium résiduel) |

### Jour 2–3 — Calcination

17. Sécher, puis cuire selon le programme du §6. Peser l'alumine.

---

## 9. Mise à l'échelle

| Par kg de bauxite | Quantité |
|---|---|
| NaOH | 0,70 kg |
| Eau d'attaque | 3,1 L |
| Volume de cuve conseillé | 10 L |
| CO₂ | 0,4–0,5 kg |
| Chaux éteinte (option §7) | 0,65 kg |
| Alumine obtenue | 0,35–0,40 kg |
| Boues rouges sèches | 0,35–0,45 kg |

Le design reste valable tel quel de ~1 kg à ~25 kg par lot (cuves de 10 à 250 L). Au-delà, il faut passer au chauffage par double enveloppe et à un filtre-presse.

---

## 10. Sécurité (à lire avant tout achat)

La soude à 220 g/L et 100 °C est le danger principal : une projection dans l'œil rend aveugle en quelques secondes.

- **Équipement** : lunettes étanches **et** écran facial, gants longs nitrile ou néoprène, tablier chimique, bottes, manches longues.
- **Eau** : tuyau d'arrosage ouvert ou douche/rince-œil à moins de 10 secondes du poste. En cas de contact : eau courante 15 min minimum, pas de vinaigre sur la peau ou les yeux.
- **Pas de pression** : l'évent des cuves n'est jamais bouché. Aucune cuve fermée n'est chauffée.
- **Rétention** : bac sous chaque cuve et sous le filtre.
- **CO₂** : travailler dehors ou atelier largement ventilé ; le CO₂ s'accumule au sol. Bouteille attachée.
- **Aluminium interdit** dans tout le circuit caustique (hydrogène inflammable).
- **Électricité** : chaque appareil de 3 kW sur son propre circuit 16 A avec différentiel 30 mA ; coffrets hors zone d'éclaboussures.
- **Boues rouges** : pH 11–14 à la sortie. Les laver, puis les neutraliser à pH 8–9 (barbotage de CO₂ dans la boue délayée, ou acide dilué ajouté lentement), sécher, stocker en fût fermé, évacuer selon la réglementation locale. Certaines bauxites concentrent des métaux lourds dans les boues.
- **Poussières** : masque FFP3 pour le broyage, le chargement de la soude en perles et la manipulation de l'alumine.
- **Étiquetage** : chaque seau, pot et bac porte le nom de son contenu (BAUXITE, POUDRE DE BAUXITE, SOUDE NaOH en rouge, BOUES ROUGES, EAU…). Une confusion entre un seau de soude et un seau d'eau est un accident grave.

---

## 11. Ordre de construction conseillé

1. **Essai de validation à 200 g** dans un récipient inox de 2 L sur plaque chauffante (mêmes proportions : 140 g NaOH, 620 mL d'eau, 100 °C, 2 h, filtration sur papier/toile, précipitation au CO₂, cuisson). Cet essai dit si ta bauxite convient **avant** de dépenser pour le reste : si on récupère moins de la moitié de l'alumine attendue, voir §12.
2. Cuve R1 + filtre F.
3. Cuve R2 + ligne CO₂.
4. Four K (achat ou construction).
5. Broyeur A0 (au début on peut broyer à la main de petites quantités).

### Budget indicatif (Europe, matériel neuf sauf four ; à vérifier)

| Poste | Ordre de grandeur |
|---|---|
| 2 cuves complètes (marmite, vannes, agitateur, plaque, PID, châssis) | 1000–1400 € |
| Filtre sous vide (cuve, fût, pompe, toiles) | 250–400 € |
| Ligne CO₂ (bouteille, détendeur, débitmètre, balance) | 150–250 € |
| Four (occasion) ou construction | 400–900 € |
| Broyeur à boulets | 150–300 € |
| Protection, pH-mètre, bacs, divers | 250–350 € |
| **Total** | **≈ 2200–3600 €** |

---

## 12. Si la bauxite n'est pas gibbsitique (plan B)

Les bauxites à boehmite ou diaspore (Europe du Sud, Chine, une partie de l'Inde…) demandent 200–250 °C sous 15–35 bar : un autoclave de ce type ne se bricole pas. On garde alors tout l'atelier et on remplace seulement l'attaque par un **frittage à la soude dans le four K** :

- mélanger bauxite broyée + carbonate de sodium (rapport molaire Na₂O/Al₂O₃ ≈ 1) + chaux (CaO/SiO₂ ≈ 2 en moles) ;
- cuire 1 h–1 h 30 à 1000–1200 °C ;
- broyer le fritté et le lessiver à l'eau chaude dans R1 → liqueur d'aluminate ;
- la suite (filtre, R2, four) est identique.

Les essais publiés donnent ~88 % d'extraction et une alumine à ~98 % par cette voie.

---

## 13. Variante — Précipitation par amorçage (Bayer classique)

À la place du CO₂ : refroidir la liqueur à 60 °C dans R2, ajouter 100–300 g/L d'hydrate d'amorce, agiter 48 h en laissant descendre vers 50 °C. Environ la moitié de l'alumine précipite ; la liqueur restante contient toujours sa soude et retourne à l'attaque après évaporation. Produit plus pur en sodium, pas de CO₂ ni de chaux, mais 2 jours d'agitation par lot et un stock d'amorce à entretenir. À envisager une fois l'atelier rodé.

---

## 14. Adaptation à ton cas : Cameroun, achats en Chine, objectif aluminium

### Bauxite camerounaise

Les gisements connus (Minim-Martap et Ngaoundal dans l'Adamaoua, Fongo-Tongo à l'Ouest) sont **gibbsitiques**, vers 45 % d'Al₂O₃ avec peu de silice réactive (≈ 2–3 %). C'est le cas favorable : l'attaque à 100 °C en cuve ouverte est la bonne voie. Comme tu ne connais pas l'origine exacte de ton minerai, l'essai à 200 g du §11 reste la première chose à faire.

### Contraintes locales

- **Électricité** : 220 V / 50 Hz monophasé. Commander tout le matériel dans cette tension. Ne pas faire chauffer deux appareils de 3 kW en même temps sur une installation domestique.
- **Coupures de courant** : pendant l'attaque ce n'est pas dangereux, mais si la pulpe refroidit sans agitation, l'alumine reprécipite dans les boues et le lot est perdu. Prévoir un petit groupe électrogène ou un onduleur qui tient au moins les deux agitateurs (250 W chacun) ; l'isolation de la cuve garde la chaleur 1–2 h.
- **Soude** : la soude en paillettes en sacs de 25 kg est celle des savonneries, elle s'achète localement.
- **CO₂** : bouteilles chez les distributeurs de gaz industriels (Douala, Yaoundé). Si l'approvisionnement est difficile, utiliser la variante sans gaz du §13.
- **Soude et CO₂ ne s'importent pas** par colis : matières dangereuses, à acheter sur place.

### Fabriquer sur place ou acheter en Chine

| À souder / fabriquer localement | À commander en Chine (mots-clés de recherche) |
|---|---|
| Les 3 châssis en cornière acier | `50L 304 stainless steel stock pot` (×2) et `30L` (×1) |
| Le broyeur à boulets (fût, rouleaux, paliers) | `DN25 304 ball valve full bore PTFE` (×4) + `1 inch 304 weld half coupling` |
| Perçage des couvercles et du fond du filtre | `gear motor 200W 220V speed controller` (×2), `4 blade pitched impeller 304` |
| Soudure TIG (argon) des manchons de vanne sur les marmites | `REX-C100 PID SSR-40DA kit`, `PT100 thermowell 304` |
| Bac de rétention | `3000W electric hot plate cast iron 220V` (×2) |
| | `polypropylene filter cloth 5 micron`, `30L stainless beer keg`, `oil free diaphragm vacuum pump 220V` |
| | `CO2 regulator with flowmeter`, `stainless check valve 1/4` |
| | **`1200C box muffle furnace 220V`** (chambre 5–12 L) |
| | `grinding steel balls 20mm 30mm`, `60 mesh test sieve` |

Le four à moufle chinois 1200 °C tout fait revient en général moins cher et plus sûr que de le construire brique par brique : c'est la pièce que je recommande d'acheter complète. Regrouper la commande chez un transitaire (groupage maritime) plutôt qu'en colis séparés. Je n'ai pas vérifié les prix : demander des devis avant de fixer le budget.

### Ce que l'objectif « aluminium » change

L'alumine destinée à l'électrolyse doit surtout être pauvre en **fer et silicium**, car ils passent directement dans le métal. Repères de qualité métallurgique : Al₂O₃ ≥ 98,5 %, SiO₂ et Fe₂O₃ ≤ 0,02–0,03 %, Na₂O ≤ 0,5 %, perte au feu ≤ 1 %. Conséquences déjà intégrées au mode opératoire :

- liqueur filtrée deux fois avant précipitation (étape 10) ;
- 2 h d'attaque complètes, pour que la silice dissoute reprécipite dans les boues ;
- carbonatation arrêtée à pH ≈ 11 (étape 14) ;
- lavage abondant de l'hydrate (étape 16) ;
- calcination à 1050 °C maximum : au-delà l'alumine devient « alpha » et se dissout mal dans le bain d'électrolyse.

Sans laboratoire d'analyse, la pureté réelle ne peut pas être garantie ; un contrôle par un labo (fluorescence X) sur le premier lot est conseillé.

**Attention à l'étape suivante.** Transformer l'alumine en aluminium (électrolyse Hall-Héroult) est un projet à part, nettement plus difficile que tout ce plan : bain de cryolithe fondue à 950–960 °C, courant continu de plusieurs centaines d'ampères sous 4–5 V, anodes en carbone consommées, fumées fluorées toxiques, environ 13–15 kWh par kg de métal. Il faut ≈ 1,9 kg d'alumine pour 1 kg d'aluminium : un lot de 5 kg de bauxite donne donc au mieux ≈ 1 kg de métal.

---

## 15. Modèle 3D

| Fichier | Contenu |
|---|---|
| `usine-bauxite-alumine-realiste.blend` | Modèle réaliste à l'échelle 1:1 (mètres), une collection par appareil, chaque pièce nommée, matériaux réels |
| `usine-bauxite-alumine-animation.blend` | Animation du procédé (≈ 1 min 45) : chaque produit entre et sort par une vraie ouverture |
| `construire_usine.py` | Script qui régénère toute la scène ; les cotes sont en tête de chaque fonction, modifiables |
| `materiaux_realistes.py` | Matériaux réels (inox brossé, acier brut, fonte, fibre céramique…), lumière, caméras |
| `animer_usine.py` | Script qui reconstruit la scène et crée l'animation |
| `rendu-realiste-*.png` | Vues d'ensemble et de détail (broyeur, cuves + filtre, pompe à vide, four) |
| `usine-bauxite-alumine.blend`, `rendu-vue-ensemble.png`, `rendu-cuves-filtre.png` | Première version (couleurs de schéma), gardée pour mémoire |

Implantation retenue : le filtre est placé **entre** les deux cuves, dont les vannes se font face. R1 puis R2 s'y vident par gravité dans le filtre. Seul le retour de la liqueur du filtre vers R2 demande une petite pompe de transfert.

Équipements ajoutés pour que les transferts se fassent proprement : chariot à trémie du broyeur, couvercle de fût à charnière, grille de vidange, bac de récupération, trappes de chargement à charnière sur R1 et R2, arrivée d'eau avec robinet, vanne de vidange et pompe de transfert sur le filtre, table de préparation à côté du four, étiquettes sur tous les récipients.

---

## Sources

- [Digestion de la bauxite gibbsitique à basse température (brevet US 6555076)](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/6555076)
- [Procédé de production d'alumine, digestion atmosphérique (brevet US 5122349)](https://patents.google.com/patent/US5122349)
- [Cinétique de dissolution de la bauxite gibbsitique sous pression atmosphérique, Yang et al. 2017](https://link.springer.com/article/10.1007/s11771-017-3451-7)
- [Lixiviation de bauxite à 95–105 °C, 200–250 g/L NaOH (E3S Conf. 2016)](https://www.e3s-conferences.org/articles/e3sconf/pdf/2016/03/e3sconf_mec2016_01021.pdf)
- [Dissolution de la gibbsite dans NaOH à pression ambiante, Grénman et al.](https://digital.library.adelaide.edu.au/items/ef7ff937-d40d-4e6a-ba0d-cbf077370ade/full)
- [Extraction de l'aluminium à partir de la bauxite — 911 Metallurgist](https://911metallurgist.com/extraction-process-of-aluminium-from-bauxite-ore)
- [Récupération d'alumine par carbonatation des solutions d'aluminate — ICSOBA 2025](https://icsoba.org/assets/files/publications/2025/Papers/AA09%20-%20Alumina%20Recovery%20from%20Sodium%20Aluminate%20Solutions%20via%20Carbonation.pdf)
- [Carbonatation des solutions d'aluminate : température, pH, durée — Crystals 2021](https://mdpi.com/2073-4352/11/7/836)
- [Précipitation Bayer par amorçage : 55–75 °C, 24–72 h — fiche technologique](https://portfolio-pplus.com/TechnologyTypes/Details/169)
- [Facteurs influençant le taux de précipitation — ICSOBA 2023](https://icsoba.org/assets/files/publications/2023/Papers/AA16%20-%20Study%20on%20Influencing%20Factors%20of%20Precipitation%20ratio.pdf)
- [Paramètres de calcination et qualité de l'alumine — ICSOBA 2024](https://icsoba.org/assets/files/publications/2024/Papers/AA29%20-%20Influence%20of%20Calcination%20Parameters%20on%20Alumina%20Quality%20in%20Gas%20Suspension%20Calciner.pdf)
- [Procédé de frittage chaux-soude sur bauxite pauvre, 88 % d'extraction, alumine 98 %](https://jme.shahroodut.ac.ir/article_2616_290a9fd6512f0f7cac173acdd5939afa.pdf)
- [Frittage chaux-soude pour bauxites siliceuses — RSC Advances 2023](https://pubs.rsc.org/en/content/articlepdf/2023/ra/d3ra03362g)
- [Corrosion en milieu soude caustique : acier et inox](https://hghouston.com/archive/special-corrosion-topics/caustic-corrosion)
- [Choix des inox pour la soude](https://tubingchina.com/Selection-of-stainless-steel-for-handling-sodium-hydroxide-NaOH.htm)
- [Neutralisation des lixiviats de boues rouges (Ajka) — Burke et al. 2013](https://homepages.see.leeds.ac.uk/~earitb/Burke%20et%20al%202013est.pdf)
- [Bauxite de Minim-Martap, Cameroun : composition](https://www.alcircle.com/news/canyon-resources-releases-resource-upgrade-for-its-minim-martap-bauxite-project-in-cameroon-48080)
