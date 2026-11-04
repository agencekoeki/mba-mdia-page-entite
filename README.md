# Votre page d'entité · la mallette

Mallette du TP « Votre page d'entité », module SEO & GEO du MBA Marketing Digital et IA (De Vinci Executive Education, novembre 2026). Formateur : Sébastien Grillot.

**Vous êtes sur le modèle.** Suivez le guide ci-dessous : à l'étape 2, vous en ferez votre propre copie. Le même guide existe en PDF : [docs/guide-installation.pdf](docs/guide-installation.pdf). Les 4 Gems : [docs/gems.md](docs/gems.md) ([PDF](docs/gems.pdf)). Le résultat attendu, sur un exemple fictif : [exemple/](exemple/).

**Ce que vous allez obtenir** : une page pro publique à votre nom, `https://votre-identifiant.github.io/`, qui dit qui vous êtes aux humains et aux machines (Google, Gemini, ChatGPT…). Vous remplissez **un seul fichier**, votre fiche ; GitHub fabrique la page, son code pour les machines, sa version texte et son sommaire pour les robots IA. Tout dit la même chose, partout.

**Jour 2 (mercredi)** : la mallette passe en 2.1 et sait publier vos pages de contenu, afficher votre photo et entrer dans Google : [section Jour 2](#jour-2--mettre-à-jour-la-mallette-ajouter-une-page-une-photo-entrer-dans-google).

**Durée** : environ une heure, la première fois. **Matériel** : un ordinateur, votre adresse e-mail, votre compte Gemini (celui de l'école). **Aucun code à écrire.**

> **L'idée unique du module : les entités nommées sont le nouveau NAP.** En SEO local, le NAP (Name, Address, Phone) doit être identique partout, sinon Google hésite entre deux fiches. Pour vous, c'est pareil : même nom, même métier, même employeur, même ville, sur votre page, dans son code, sur LinkedIn. Cette mallette le garantit par construction : une seule source, tout le reste en découle.

## Le parcours en un coup d'œil

| Étape | Ce que vous faites | Durée |
|---|---|---|
| 1 | Créer votre compte GitHub | 10 min |
| 2 | Copier la mallette (« Use this template ») | 5 min |
| 3 | Régler la publication (Pages → GitHub Actions) | 3 min |
| 4 | Créer vos 4 Gems dans Gemini | 15 min |
| 5 | Écrire votre fiche avec le Gem « Ma fiche d'entité » | 10 min |
| 6 | Coller la fiche dans GitHub | 3 min |
| 7 | Regarder l'Action travailler | 2 min |
| 8 | Ouvrir votre page | 1 min |
| 9 | Valider le code sur validator.schema.org | 5 min |
| 10 | Tester ce que Gemini comprend de vous (A, B, C) | 10 min |

---

## Étape 1 · Créer votre compte GitHub (10 min)

GitHub est le site où vit le code de millions de projets. Votre page y sera rangée, puis publiée.

1. Ouvrez **github.com** et cliquez sur **Sign up**.
2. Saisissez votre e-mail, un mot de passe, puis un **identifiant** (*username*).
   - Choisissez-le avec soin : il fera partie de l'adresse de votre page, `https://identifiant.github.io/`.
   - Le plus simple : `prenom-nom` en minuscules, sans accent (par exemple `marie-exemple`). S'il est pris, ajoutez une initiale.
3. Résolvez la petite vérification (puzzle), puis **ouvrez votre boîte mail** : GitHub vous envoie un **code de vérification**. Recopiez-le dans GitHub (pensez aux spams s'il n'arrive pas).
4. GitHub pose quelques questions de bienvenue : vous pouvez cliquer sur **Skip personalization**. Choisissez le plan gratuit (**Free**) si on vous le demande.

**C'est bon quand** : vous voyez votre tableau de bord GitHub, avec votre photo (ou un avatar) en haut à droite.

> **Notez votre identifiant** (en haut à droite, en cliquant sur l'avatar). Vous en aurez besoin trois fois.

---

## Étape 2 · Copier la mallette (5 min)

1. Ouvrez la mallette : **github.com/agencekoeki/mba-mdia-page-entite**.
2. En haut à droite, cliquez sur le bouton vert **Use this template**, puis **Create a new repository**.
3. Remplissez :
   - **Owner** : votre identifiant (déjà sélectionné).
   - **Repository name** : **exactement** `identifiant.github.io`, avec votre identifiant à vous. Pour `marie-exemple`, c'est `marie-exemple.github.io`. Tout en minuscules.
   - **Public** (obligatoire avec un compte gratuit pour publier la page).
   - Laissez « Include all branches » décoché.
4. Cliquez sur **Create repository**.

**C'est bon quand** : vous êtes sur la page de *votre* dépôt, qui s'appelle `identifiant/identifiant.github.io`, avec la liste des fichiers de la mallette.

> Si le nom du dépôt n'est pas exactement `identifiant.github.io`, votre page sera quand même publiée, mais à une adresse plus longue : `https://identifiant.github.io/nom-du-depot/`. Pour corriger : **Settings → General → Repository name**, puis **Rename**.

---

## Étape 3 · Régler la publication (3 min)

C'est l'étape qu'on oublie, et la cause n° 1 des pages qui ne s'affichent pas.

1. Dans votre dépôt, cliquez sur **Settings** (l'onglet avec un engrenage, en haut).
2. Dans le menu de gauche, cliquez sur **Pages**.
3. Sous **Build and deployment**, à la ligne **Source**, choisissez **GitHub Actions** (et pas « Deploy from a branch »).
4. GitHub vous propose alors des modèles (« Jekyll », « Static HTML »…) : **n'en choisissez aucun**. La mallette a déjà le sien.
5. Allez dans l'onglet **Actions** (en haut). Dans la liste de gauche, cliquez sur **Publier ma page**, puis à droite sur **Run workflow**, et encore **Run workflow** (bouton vert).

**C'est bon quand** : une ligne « Publier ma page » apparaît avec un rond orange qui tourne. Vous pouvez passer à l'étape 4 pendant ce temps.

> Pourquoi relancer à la main ? Au moment où vous avez copié la mallette, la publication n'était pas encore réglée : rien n'a pu être publié. Ce premier lancement à la main publie la page modèle. Ensuite, tout est automatique. (Une première ligne verte ou rouge peut déjà figurer dans Actions, datée de la création du dépôt : ignorez-la.)

---

## Étape 4 · Créer vos 4 Gems dans Gemini (15 min)

Un Gem est un Gemini spécialisé, avec des instructions permanentes. Vous en créez quatre, une fois pour toutes. Leurs textes sont dans le dossier **gems/** de votre dépôt, et réunis dans **docs/gems.pdf** pour les avoir sous les yeux.

| Gem | Son rôle |
|---|---|
| SEO · SAVOIR ou PENSER | le garde-fou : sépare le prouvé du supposé, finit par une décision |
| Ma fiche d'entité | vous interroge une fois, puis rend votre fiche complète |
| Vérificateur de page | vérifie que le code de la page dit vrai et propose la correction |
| Designer de ma page | propose trois directions visuelles et recommande la sienne |

**Pour chaque Gem :**

1. Ouvrez **gemini.google.com** avec votre compte de l'école.
2. Dans le menu de gauche, cliquez sur **Gems** (le libellé peut être « Explorer les Gems » ou « Découvrir les Gems » ; si le menu est replié, cliquez d'abord sur les trois traits en haut à gauche).
3. Cliquez sur **Nouveau Gem** (ou **+ Nouveau Gem**).
4. Dans GitHub, ouvrez le fichier du Gem dans le dossier **gems/** (par exemple `1-savoir-ou-penser.md`). Chaque bloc gris a, en haut à droite, une icône **copier** (deux carrés) :
   - copiez le bloc **Nom** et collez-le dans le champ **Nom** du Gem ;
   - copiez le bloc **Description** et collez-le dans le champ **Description** (s'il n'existe pas dans votre interface, ignorez-le) ;
   - copiez le bloc **Instructions** et collez-le dans le grand champ **Instructions**.
5. Testez dans l'**aperçu** à droite avec la phrase indiquée en bas du fichier (« Tester tout de suite »).
6. Cliquez sur **Enregistrer** (en haut à droite). **Sans ce clic, le Gem est perdu** : l'aperçu n'enregistre rien.

**C'est bon quand** : vos quatre Gems apparaissent dans la liste **Mes Gems**, et dans le menu de gauche de Gemini.

> L'interface de Gemini change souvent. Si un libellé diffère, cherchez : un menu ou une icône « Gems » (un petit diamant), un bouton « Nouveau » ou « + », un champ pour le nom, un grand champ pour les instructions, et un bouton pour enregistrer. Si votre compte de l'école ne propose pas les Gems, utilisez votre compte Gemini personnel, ou collez les instructions au début d'une conversation Gemini ordinaire.

---

## Étape 5 · Écrire votre fiche avec le Gem « Ma fiche d'entité » (10 min)

1. Dans Gemini, ouvrez le Gem **Ma fiche d'entité** et écrivez « Bonjour ».
2. Il vous envoie **une seule liste de questions**. Répondez à tout en un message, en vrac. Le plus efficace : collez aussi votre résumé LinkedIn.
3. Il vous rend **votre fiche complète** dans un bloc de code, sans rien vous redemander.
4. Lisez les deux sections sous le bloc : **Ce que j'ai supposé (PENSER)** et **Invérifiable de mon côté**. Corrigez dans le bloc tout ce qui n'est pas exact : c'est votre identité publique.
5. Facultatif : ouvrez le Gem **Designer de ma page**, collez votre fiche, et remplacez les trois lignes `theme`, `couleur_accent` et `animations` par celles qu'il recommande.

**C'est bon quand** : vous avez un bloc qui commence par `{` et finit par `}`, et dont chaque information est vraie.

> **Rien de privé** : pas d'adresse, de téléphone, de date de naissance ni d'e-mail personnel. La page est publique, et elle le reste après la formation tant que vous ne supprimez pas le dépôt.

---

## Étape 6 · Coller la fiche dans GitHub (3 min)

1. Dans votre dépôt GitHub, cliquez sur le fichier **fiche.json**.
2. Cliquez sur le **crayon** (*Edit this file*), en haut à droite du fichier.
3. Sélectionnez tout le contenu (**Ctrl + A**, ou **Cmd + A** sur Mac) et supprimez-le.
4. Dans Gemini, cliquez sur l'icône **copier** du bloc de code (pas une sélection à la souris : vous risqueriez d'oublier une accolade), puis collez dans GitHub (**Ctrl + V**).
5. Cliquez sur le bouton vert **Commit changes…**, puis encore sur **Commit changes** dans la fenêtre qui s'ouvre.

**C'est bon quand** : GitHub affiche votre fiche, sans le texte du modèle.

> Chaque champ est expliqué, avec un exemple, dans le fichier **fiche.md** de votre dépôt. Un exemple complet et fictif : **fiche.exemple.json**.

---

## Étape 7 · Regarder l'Action travailler (2 min)

Votre commit a déclenché la fabrication de la page.

1. Cliquez sur l'onglet **Actions**.
2. La ligne du haut porte le titre de votre commit, avec :
   - un **rond orange** qui tourne : GitHub construit et publie (une à deux minutes) ;
   - une **coche verte** : la page est construite, vérifiée et publiée ;
   - une **croix rouge** : quelque chose est à corriger. Cliquez sur la ligne : le message en français dit **quoi corriger et où** (numéro de ligne de fiche.json). Corrigez avec le crayon, recommitez, et c'est reparti.
3. Cliquez sur la ligne verte : le **résumé** affiche l'adresse de votre page et la vérification « le code dit-il vrai ? », propriété par propriété.

**C'est bon quand** : la coche est verte.

---

## Étape 8 · Ouvrir votre page (1 min)

1. Ouvrez **https://identifiant.github.io/** (avec votre identifiant).
2. Vous y voyez votre nom en grand, votre phrase d'identité, la section « En bref », vos profils.
3. Ajoutez `moi.md` à la fin de l'adresse : c'est la même chose en texte brut, pour les robots IA. Puis `llms.txt` : leur sommaire.
4. Collez votre adresse dans le chat de la classe.

**C'est bon quand** : la page affiche **vos** informations. Si vous voyez encore la page modèle, attendez une minute et rechargez (**Ctrl + F5**, ou **Cmd + Maj + R** sur Mac).

---

## Étape 9 · Valider le code sur validator.schema.org (5 min)

1. Ouvrez **validator.schema.org**.
2. Choisissez **Fetch URL** (« Récupérer l'URL »), collez l'adresse de votre page, et lancez le test (**Run test**, « Exécuter le test »). Le site peut être en anglais ou en français selon votre navigateur.
3. À droite, vous devez voir **Person** avec 0 erreur. Cliquez dessus : chaque propriété s'affiche (name, jobTitle, worksFor…), avec ses valeurs.
4. Un avertissement ou une erreur que vous ne comprenez pas ? Copiez-le dans le Gem **Vérificateur de page** : il l'explique et vous donne la correction prête à coller dans fiche.json.

**C'est bon quand** : Person, 0 erreur. Et vous savez dire, pour chaque propriété, où elle se voit sur la page.

> Le validateur vérifie la forme, pas la vérité. Que chaque valeur du code se voie bien sur la page, c'est l'Action qui le prouve à chaque publication (étape 7, le résumé), et le Gem Vérificateur qui vous l'explique.

---

## Étape 10 · Tester ce que Gemini comprend de vous (10 min)

C'est le cœur du TP. Faites les trois tests dans une **conversation Gemini ordinaire** (pas dans un Gem), et notez les réponses : on les compare demain matin.

**Test A · Ce que Gemini sait de vous, sans votre page**

> Qui est [votre nom], [votre métier] à [votre ville] ? Dis ce que tu sais avec certitude, et ce que tu supposes.

**Test B · Ce qu'il comprend de votre page**

> Lis la page https://identifiant.github.io/ et dis-moi, en cinq lignes, qui est cette personne. Puis liste les informations que tu as trouvées dans ses données structurées schema.org.

**Test C · Ce qu'il comprend de la version texte**

> Lis https://identifiant.github.io/moi.md et résume qui est cette personne en trois lignes. Ce résumé est-il identique à celui de la page HTML ?

**À noter pour chaque test** : ce qui est juste, ce qui est faux, ce qui manque. Puis passez la réponse du test A au Gem **SEO · SAVOIR ou PENSER** : il sépare ce que Gemini savait vraiment de ce qu'il a deviné.

> Gemini ne relit pas forcément votre page au moment où vous le lui demandez, et peut répondre de mémoire. S'il dit qu'il ne peut pas ouvrir l'adresse, notez-le : c'est un résultat en soi. Les tests B et C se refont dans quelques jours, quand la page aura été explorée.

---

## Si ça bloque

**La page affiche « 404 · There isn't a GitHub Pages site here ».**
Dans l'ordre : (1) le nom du dépôt est-il exactement `identifiant.github.io` ? (2) **Settings → Pages → Source** est-il sur **GitHub Actions** ? (3) l'onglet **Actions** a-t-il une coche verte ? Si tout est bon, attendez deux minutes et rechargez : la toute première publication est parfois lente.

**L'Action est en rouge.**
Si le message est « Réglage de GitHub Pages à faire », c'est que l'étape 3 n'est pas faite (ou pas finie) : faites-la, puis **Actions → Publier ma page → Run workflow**. Sinon, cliquez sur la ligne rouge, puis sur le travail en rouge (« Construire et vérifier la page ») : le message en français dit quoi corriger. Les trois cas les plus fréquents :

- **« fiche.json n'est pas un JSON valide »** : une virgule manque ou est en trop, ou des guillemets typographiques `“ ”` se sont glissés. Le message donne le numéro de ligne. Le plus rapide : collez le message et votre fiche dans le Gem **Ma fiche d'entité**, il vous rend la fiche corrigée.
- **« ce champ obligatoire manque »** : ajoutez le champ indiqué (exemple donné dans le message, et dans fiche.md).
- **« Réglage de GitHub Pages à faire »** : refaites l'étape 3, puis **Actions → Publier ma page → Run workflow**.

**Le JSON est invalide et je ne trouve pas la faute.**
Ne cherchez pas à la main : recollez la fiche complète du Gem, en utilisant l'icône **copier** du bloc de code. Vérifiez que le fichier commence par `{` et finit par `}`.

**Pages n'est pas sur GitHub Actions.**
**Settings → Pages → Build and deployment → Source : GitHub Actions.** Si le menu ne propose que « Deploy from a branch », vérifiez que le dépôt est **Public** (**Settings → General**, tout en bas, *Danger Zone*, *Change visibility*).

**La page n'est pas à jour.**
Coche verte, mais l'ancienne version s'affiche ? C'est le cache : attendez une à deux minutes, puis rechargez en forçant (**Ctrl + F5**, ou **Cmd + Maj + R** sur Mac), ou ouvrez l'adresse dans une fenêtre de navigation privée.

**L'onglet Actions dit que les workflows sont désactivés.**
Cliquez sur le bouton vert **I understand my workflows, go ahead and enable them**, puis relancez **Publier ma page → Run workflow**.

**Je ne trouve pas les Gems dans Gemini.**
Repliez et dépliez le menu de gauche ; cherchez l'icône en forme de diamant. Si votre compte de l'école ne les propose pas, utilisez un compte Gemini personnel, ou collez les instructions du Gem au début d'une conversation normale.

---

## Plan B sans GitHub Actions

Si GitHub Actions ne marche pas pour vous (compte bloqué, réglage impossible), **la page ne peut pas être fabriquée dans le navigateur** : il faut l'Action, ou Python sur un ordinateur. Le plan B garde l'essentiel du TP, le code pour les machines :

1. Faites l'étape 5 : obtenez votre fiche avec le Gem **Ma fiche d'entité**.
2. Pour voir à quoi ressemble le résultat, ouvrez l'exemple de la mallette, `exemple/index.html` (bouton **Raw**) : le bloc `<script type="application/ld+json">…</script>` est en haut.
3. Collez votre fiche dans le Gem **Vérificateur de page** avec cette phrase : « Plan B : donne-moi le bloc JSON-LD de cette fiche. » Il vous rend le bloc complet, sur le modèle de celui de Marie Exemple, avec vos valeurs.
4. Ouvrez **validator.schema.org**, choisissez l'onglet **Code snippet** (« Extrait de code »), collez le bloc complet (de `<script` à `</script>`), et lancez le test (**Run test**).
5. Vérifiez : Person, 0 erreur, et chaque propriété correspond à votre fiche.

Vous aurez le code de votre entité, validé. La page en ligne suivra quand GitHub sera débloqué : il suffira de coller la fiche dans `fiche.json`.

---

## Ce que vous apprenez en faisant ça

Chaque étape illustre une seule idée : **les entités nommées sont le nouveau NAP**. Dire exactement la même chose de soi, partout.

| Étape | Ce que vous faites | Ce que ça vous apprend |
|---|---|---|
| Compte GitHub, identifiant | vous choisissez un nom stable | une entité commence par un identifiant qui ne change pas |
| La fiche, une seule source | vous écrivez chaque fait une seule fois | une seule source, donc aucune contradiction possible : c'est le NAP, appliqué à vous |
| Le Gem « Ma fiche » et ses PENSER | vous relisez ce que l'IA a supposé | une IA comble les trous ; à vous de séparer le vrai du deviné |
| L'Action qui construit | la page, le code, moi.md et llms.txt sortent de la même fiche | la cohérence n'est pas un effort, c'est une conséquence |
| La vérification « le code dit-il vrai ? » | chaque valeur du JSON-LD est retrouvée sur la page | Google demande que le balisage décrive ce qu'on voit ; rien de caché |
| L'@id `…/#moi` | votre entité a un numéro de dossier | c'est lui qui relie vos pages, vos projets, vos profils |
| Les sameAs | vos profils sont reliés à la page | c'est la preuve qu'il s'agit de la même personne : la fusion devient facile |
| validator.schema.org | la machine lit votre fiche normée | le JSON-LD, c'est le formulaire que les moteurs savent lire sans interpréter |
| Les tests A, B, C | vous comparez ce que Gemini sait, lit et comprend | une entité bien décrite est mieux comprise ; aucun balisage ne garantit une citation |

**À retenir** : vous n'avez pas fabriqué une page, vous avez fabriqué **une source**. Demain, on en fait le centre de votre présence en ligne.

---

## Jour 2 · Mettre à jour la mallette, ajouter une page, une photo, entrer dans Google

Mercredi, votre page d'entité devient le centre d'un petit site : des pages de contenu signées par vous, reliées à elle. Quatre gestes, dans l'ordre. Le premier est obligatoire : sans lui, les trois autres sont ignorés.

| Geste | Ce que vous faites | Durée |
|---|---|---|
| A | Mettre à jour la mallette (un seul fichier à remplacer) | 5 min |
| B | Ajouter une page de contenu | 15 min |
| C | Ajouter votre photo (facultatif) | 5 min |
| D | Faire entrer votre site dans Google (Search Console) | 15 min |

### Geste A · Mettre à jour la mallette (5 min)

Votre dépôt est une copie de la mallette du lundi : il ne reçoit pas les nouveautés tout seul. On remplace un seul fichier, `outils/construire.py`.

1. Ouvrez cette adresse : **https://raw.githubusercontent.com/agencekoeki/mba-mdia-page-entite/main/outils/construire.py**. C'est du code brut, en texte.
2. Sélectionnez tout (**Ctrl + A**, ou **Cmd + A** sur Mac), copiez (**Ctrl + C**).
3. Dans **votre** dépôt, ouvrez le dossier **outils**, puis le fichier **construire.py**, puis le **crayon** (*Edit this file*).
4. Sélectionnez tout (**Ctrl + A**), supprimez, collez (**Ctrl + V**).
5. **Commit changes…**, puis **Commit changes**.
6. Onglet **Actions** : attendez la coche verte, cliquez sur la ligne. Le résumé doit dire **« Page construite (mallette 2.1) »**.

**C'est bon quand** : le résumé dit « mallette 2.1 ». Votre page n'a pas changé : c'est normal, votre fiche est la même.

> Si l'Action dit plus tard « champ inconnu, ignoré : pages » (ou photo), c'est que ce geste A n'est pas fait.

### Geste B · Ajouter une page de contenu (15 min)

Une page de contenu prouve ce que vous savez faire : un cas réel, une date, un résultat, un lien pour le voir. Elle est écrite en **Markdown** (du texte presque normal) dans le dossier `pages/` ; la mallette en fait une page web signée par vous, avec son code pour les machines (un `Article` dont l'auteur est votre entité, `…/#moi`), et l'ajoute à votre page d'accueil sous « Mes pages ».

1. Dans votre dépôt : **Add file** (en haut, à côté du bouton vert **Code**) → **Create new file**.
2. Dans le champ du nom, tapez `pages/` puis le nom de votre page, en minuscules, avec des tirets et sans accents, par exemple `pages/relancer-la-newsletter.md`. Le `/` crée le dossier tout seul.
3. Collez votre texte, sur ce modèle :

   ```markdown
   # Le titre : la question à laquelle la page répond

   Date : 2026-11-04

   Prénom Nom a … (première phrase : la réponse, avec votre nom).

   ## Ce que j'ai fait

   - Première action, datée.
   - Deuxième action.

   ## Le résultat, et où le voir

   Le chiffre vrai, et [le lien qui le montre](https://…).
   ```

   Ce que la mallette comprend : `#` le titre (une seule fois, en première ligne), `Date :` (facultative), `##` et `###` les sous-titres, `-` les listes, `[texte](adresse)` les liens, `**gras**`, `>` une citation. Une ligne vide entre deux paragraphes.
4. **Commit changes…**, puis **Commit changes**. Attention : ce commit ne publie rien (seule la fiche déclenche la publication).
5. Ouvrez **fiche.json** (crayon) et ajoutez une ligne, par exemple juste après `"identifiant_github"` (virgule à la fin de la ligne précédente) :
   ```json
   "pages": ["pages/relancer-la-newsletter.md"],
   ```
   Plusieurs pages : `"pages": ["pages/premiere.md", "pages/deuxieme.md"],`
6. **Commit changes** : l'Action construit votre page. Elle sera à l'adresse `https://identifiant.github.io/relancer-la-newsletter.html`, avec sa version texte en `.md`.

**C'est bon quand** : votre page d'accueil a une section « Mes pages » avec le titre en lien, et la nouvelle page a un lien retour à votre nom.

> **Relier vos pages entre elles** : dans le texte d'une page, un lien vers une autre se note avec le nom de son fichier, `[ma page sur la newsletter](pages/relancer-la-newsletter.md)` ; la mallette le transforme en vrai lien.
>
> **Modifier une page plus tard** : corrigez le fichier `.md` (crayon, Commit), puis relancez la publication : **Actions → Publier ma page → Run workflow**. Sans ça, l'ancienne version reste en ligne.
>
> **Vous recollez une fiche écrite par le Gem ?** Il ne connaît pas les champs du jour 2 : recopiez vos lignes `"pages"`, `"photo"` et `"verification_google"` dans la nouvelle fiche avant de l'enregistrer.
>
> **Les conseils de l'Action** vous aident à écrire : votre nom absent du texte, un `[À SOURCER]` oublié, une page trop courte, un lien sans `https://`. Rien de bloquant, mais lisez-les.

Pour faire écrire le brouillon par Gemini, à partir de **vos** preuves (Gem « SEO · SAVOIR ou PENSER ») :

```text
Écris une page en Markdown pour ma mallette, à partir de MES PREUVES seulement : [vos preuves : ce que j'ai fait, quand, quel résultat, où le voir].
Première ligne : # puis le titre, sous forme de question. Puis « Date : AAAA-MM-JJ ».
Première phrase : la réponse, avec mon nom, [Prénom Nom]. Un paragraphe, une idée ; ## pour les sous-titres.
Écris [À SOURCER] là où une preuve manque. N'invente aucun chiffre. Puis liste ce que tu as supposé.
```

### Geste C · Ajouter votre photo (facultatif, 5 min)

Une photo pro, que vous acceptez de voir en public. Rien d'obligatoire : sans photo, la page garde ses initiales.

1. Préparez un fichier **JPG, PNG ou WebP**, de **moins de 2 Mo**, plutôt carré (les photos d'iPhone en HEIC ne marchent pas : faites une capture d'écran, ou exportez en JPG).
2. Dans votre dépôt : **Add file → Upload files**, glissez la photo, **Commit changes**. Elle arrive à la racine du dépôt, à côté de `fiche.json`.
3. Dans **fiche.json**, ajoutez la ligne avec le nom **exact** du fichier (majuscules et extension comprises) :
   ```json
   "photo": "photo.jpg",
   ```
4. **Commit changes**, coche verte : la photo s'affiche en haut de la page et sur vos pages de contenu. Dans le code, elle devient la propriété `image` de votre entité.

### Geste D · Faire entrer votre site dans Google (15 min)

Une page neuve n'existe pas pour Google tant qu'il ne l'a pas trouvée : aucun lien n'y mène encore. **Google Search Console** permet de lui dire « mon site existe, voici ses pages ». Il vous faut un compte Google (celui de l'école ou le vôtre).

1. Ouvrez **search.google.com/search-console** et connectez-vous.
2. Ouvrez le menu des propriétés (en haut à gauche), puis **Ajouter la propriété**. Une fenêtre « Sélectionnez un type de propriété » s'ouvre : cliquez sur **Ajouter un site Web** (pas Instagram, TikTok, X ou YouTube). Dans la fenêtre suivante, choisissez la colonne de droite, **Préfixe de l'URL** (pas « Domaine »), tapez `https://identifiant.github.io/`, puis **Continuer**. (Si vous n'avez encore aucune propriété, Search Console ouvre directement cette fenêtre.)
3. Parmi les méthodes de validation, ouvrez **Balise HTML**, puis **Copier** la balise `<meta name="google-site-verification" content="…">`.
4. Dans **fiche.json**, ajoutez une ligne et collez-y la balise, ou seulement le code entre les guillemets après `content=` :
   ```json
   "verification_google": "le-code-copié-dans-search-console",
   ```
   **Commit changes**, puis attendez la **coche verte** de l'Action (une à deux minutes).
5. Revenez dans Search Console et cliquez sur **Valider**. « Propriété validée » : c'est gagné. Ne retirez jamais ce champ : Google revérifie de temps en temps.
6. Menu **Sitemaps** : dans « Ajouter un sitemap », tapez `sitemap.xml`, puis **Envoyer**. Le sitemap liste votre page d'accueil et vos pages de contenu.
7. **Inspection de l'URL** (la barre tout en haut) : collez l'adresse de votre page d'accueil, puis **Demander une indexation** (à droite, sous « Cette URL est sur Google » ou « … n'est pas sur Google »). Recommencez avec chaque page de contenu.

**C'est bon quand** : la propriété est validée, le sitemap est envoyé, l'indexation est demandée.

> **Soyons honnêtes.** Demander une indexation, c'est demander, pas exiger : Google peut mettre quelques jours, parfois plus, et ne promet rien. En attendant, `site:identifiant.github.io` dans Google peut rester vide, et Gemini peut ne pas « voir » votre page s'il cherche par Google. Donner l'adresse exacte à Gemini marche souvent mieux, mais il n'ouvre pas toujours une page neuve : s'il répond sans l'avoir lue, il devine. C'est une photo, pas une mesure.
>
> Les noms de boutons de Search Console sont donnés tels qu'ils s'affichent en français à notre connaissance ; s'ils diffèrent un peu chez vous, cherchez le plus proche.

---

## Après la formation

- Pour modifier votre page : modifiez **fiche.json** (crayon, Commit changes). Jamais `index.html` : il est refabriqué à chaque fois.
- Pour modifier une page de contenu : modifiez son fichier dans `pages/`, puis **Actions → Publier ma page → Run workflow**.
- Pour supprimer la page et le dépôt : **Settings → General → Danger Zone → Delete this repository**.

---

## Ce que contient la mallette

| Fichier ou dossier | Rôle | Vous y touchez ? |
|---|---|---|
| `fiche.json` | **votre fiche d'identité, la seule source de la page** | oui, c'est le seul |
| `fiche.md` | l'aide de chaque champ, avec un exemple | à lire |
| `fiche.exemple.json` | une fiche complète, fictive (Marie Exemple, Lumen) | à lire |
| `pages/` | vos pages de contenu, en Markdown (jour 2 ; le dossier se crée avec la première page) | oui |
| `gems/` | les instructions des 4 Gems Gemini | à copier dans Gemini |
| `docs/` | ce guide et la page des Gems, en Markdown et en PDF | à lire |
| `outils/construire.py` | fabrique la page, `moi.md`, `llms.txt`, `robots.txt`, `sitemap.xml` (et, en 2.1, vos pages de contenu et votre photo) depuis la fiche | une fois, au geste A du jour 2 |
| `outils/verifier.py` | vérifie que chaque valeur du code se voit sur la page | non |
| `themes/` | les 3 thèmes (clair, sombre, editorial), le mouvement, les polices | non |
| `.github/workflows/publier.yml` | l'Action : construire, vérifier, publier, à chaque modification de la fiche | non |
| `exemple/` | le résultat, construit depuis `fiche.exemple.json`, avec une page de contenu et une photo dessinée (sources dans `exemple/sources/`) | à regarder |
| `index.html` | page d'attente, remplacée par la vôtre dès la première publication | non |

Les polices (Instrument Sans, Bricolage Grotesque, Newsreader) sont sous licence SIL Open Font License ; leurs licences sont dans `themes/polices/`.
