# Votre fiche, champ par champ

`fiche.json` est la **seule source** de votre page. Vous la remplissez une fois ; la page, son code pour les machines (le JSON-LD), sa version texte (`moi.md`) et son sommaire pour les robots IA (`llms.txt`) en découlent. Tout dit la même chose, partout : c'est l'idée du module, **les entités nommées sont le nouveau NAP**.

Le plus simple : demandez votre fiche au Gem « Ma fiche d'entité » (voir le guide), collez-la dans `fiche.json`, enregistrez. Cette page vous sert à comprendre ou à corriger un champ.

## Trois règles d'écriture du JSON

Le JSON est un format strict : une seule faute et la page ne se construit pas (l'onglet Actions vous dit alors où est la faute, en français).

1. **Guillemets droits** `"` autour des noms de champs et des textes. Jamais `“ ”` ni `« »`.
2. **Une virgule entre deux champs**, et pas de virgule après le dernier, juste avant `}` ou `]`.
3. **Pas de commentaire** : le JSON n'en accepte pas. C'est pour ça que cette aide est dans un fichier à part. Un champ dont le nom commence par `_` (comme `_aide`) est ignoré : vous pouvez le garder ou le supprimer.

Exemple complet et fictif : [`fiche.exemple.json`](fiche.exemple.json) (Marie Exemple, Lumen et La Fournée n'existent pas).

## Les champs obligatoires

### `nom`
Votre nom tel que vous voulez qu'on vous trouve. Le même partout : sur LinkedIn, sur votre CV, ici.
```json
"nom": "Marie Exemple",
```

### `phrase_identite`
Une phrase, une ou deux lignes : qui vous êtes, ce que vous faites, où. Commencez par votre nom, citez votre employeur et votre ville. C'est elle qu'on lit en premier sur la page, et c'est la `description` du JSON-LD.
```json
"phrase_identite": "Marie Exemple est chargée de marketing digital chez Lumen, éditeur de logiciels pour boulangeries, à Lyon.",
```

### `metier`
Votre intitulé de poste, sans fioriture. Devient `jobTitle`.
```json
"metier": "Chargée de marketing digital",
```

### `ville`
La ville où vous travaillez. Pas d'adresse : la page est publique. Devient `address.addressLocality`.
```json
"ville": "Lyon",
```

### `domaines`
Trois à six domaines de compétence, entre crochets, chacun entre guillemets. Soyez précise : « SEO local » dit plus que « digital ». Devient `knowsAbout`.
```json
"domaines": ["Marketing digital", "SEO", "Emailing", "Marketing des artisans"],
```

### `identifiant_github`
Votre identifiant GitHub, sans @ (il est en haut à droite de GitHub, sous votre photo). Il sert à fabriquer l'adresse de votre page, `https://identifiant.github.io/`, et l'identifiant unique de votre entité, `https://identifiant.github.io/#moi`. Dans GitHub Actions, c'est le nom du dépôt qui fait foi.
```json
"identifiant_github": "marie-exemple-fictive",
```

## Les champs recommandés

### `employeur`
Votre employeur, votre école ou votre projet principal. `url` est facultative ; `description` (facultative) dit en quelques mots ce que fait l'organisation ; `libelle` (facultatif) change l'étiquette affichée, « Employeur » par défaut (par exemple « Alternance » ou « École »). Devient `worksFor`, avec son propre identifiant `https://identifiant.github.io/#employeur`.
```json
"employeur": {
  "nom": "Lumen",
  "url": "https://lumen.example/",
  "description": "éditeur de logiciels pour boulangeries"
},
```

### `ce_que_je_fais`
Deux ou trois phrases, à la première personne : ce que vous faites, pour qui, avec quoi. Pour un nouveau paragraphe, écrivez `\n` dans le texte.
```json
"ce_que_je_fais": "Chez Lumen, je prépare les campagnes d'emailing et les pages du site qui présentent nos logiciels aux boulangers.",
```

### `parcours`
Une ou deux phrases : d'où vous venez, ce que vous préparez.
```json
"parcours": "Après une licence de communication, je suis le MBA Marketing Digital et Intelligence Artificielle de De Vinci Executive Education, en alternance chez Lumen.",
```

### `profils`
Vos profils ailleurs : LinkedIn d'abord, puis tout profil public qui parle de vous (Malt, Medium, GitHub, YouTube…). Chaque adresse complète, en `https://`. Devient `sameAs` : la preuve que la page et ces profils parlent de la même personne. C'est le lien le plus utile de tout le TP.
```json
"profils": [
  { "nom": "LinkedIn", "url": "https://www.linkedin.com/in/marie-exemple-fictive" },
  { "nom": "Malt", "url": "https://www.malt.fr/profile/marieexemple" }
],
```

## L'apparence (le Gem « Designer de ma page » vous la propose)

### `theme`
`"clair"` (net et lumineux), `"sombre"` (fond bleu nuit, titre expressif) ou `"editorial"` (comme un portrait de magazine, avec empattements).
```json
"theme": "editorial",
```

### `couleur_accent`
Une couleur au format `#RRVVBB`. Elle colore le monogramme, le trait sous le nom et les liens. Si elle n'est pas assez contrastée sur le thème choisi, la page l'ajuste toute seule pour rester lisible (niveau AA) et vous le dit dans l'onglet Actions.
```json
"couleur_accent": "#8E2B6E",
```

### `animations`
`true` : une seule apparition sobre au chargement (le nom monte, le trait se trace, le reste arrive), environ une seconde. `false` : rien ne bouge. Sans guillemets. Si votre visiteur a demandé « moins de mouvement » à son ordinateur, rien ne bouge non plus.
```json
"animations": true,
```

## Le bonus : une seconde entité reliée

### `entite_liee`
Un projet, une association, un podcast, une lettre, un livre : une seconde entité, reliée à vous par son identifiant (`https://identifiant.github.io/#projet`). À ne remplir que si elle existe vraiment.

- `type` : `"Organization"` (association, entreprise, collectif) ou `"CreativeWork"` (podcast, blog, lettre, livre, œuvre).
- `nom` : son nom exact.
- `description` (facultatif) : ce que c'est, en quelques mots.
- `url` (facultatif) : son adresse.
- `relation` : votre place. Pour une Organization : `fondatrice`, `cofondatrice` (devient `founder`), `membre`, `bénévole`, `présidente` (devient `memberOf`). Pour une CreativeWork : `autrice` (devient `author`), `créatrice` (`creator`), `contributrice` (`contributor`). Le masculin marche aussi.
- `titre_section` (facultatif) : le titre de la section sur la page, « Mon projet » par défaut.

```json
"entite_liee": {
  "type": "CreativeWork",
  "nom": "La Fournée",
  "description": "une lettre mensuelle sur le marketing des artisans boulangers",
  "relation": "autrice",
  "titre_section": "Ma lettre"
},
```

## Les champs techniques

### `type`
Toujours `"Person"` : l'entité principale, c'est vous. Vous pouvez l'omettre.

### `fictif`
`true` seulement pour un exemple (il ajoute un bandeau « Exemple fictif » et demande aux moteurs de ne pas indexer la page). Ne le mettez pas dans votre fiche.

## Ce qui n'a pas sa place ici

Rien de privé : pas d'adresse, de téléphone, de date de naissance ni d'e-mail personnel. La page est publique, et la construction vous prévient si elle repère un e-mail ou un numéro.

## Tester sur son ordinateur (facultatif)

Si Python 3 est installé :

```
python3 outils/construire.py
python3 outils/verifier.py
```

La page est dans `_site/index.html`. Pour voir l'exemple : `python3 outils/construire.py --fiche fiche.exemple.json --sortie exemple --url-base https://agencekoeki.github.io/mba-mdia-page-entite/exemple/`.
