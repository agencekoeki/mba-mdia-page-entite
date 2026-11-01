# Modèle · page d'entité

Modèle du TP « Votre page d'entité » du module SEO & GEO (MBA MDIA, De Vinci Executive Education, novembre 2026). Formateur : Sébastien Grillot (Kōeki).

## Ce que contient ce dépôt

| Fichier | Rôle |
|---|---|
| `index.html` | votre page, pour les humains, avec son bloc JSON-LD (schema.org) pour les machines |
| `moi.md` | le jumeau Markdown de la page : les mêmes faits, en texte brut |
| `llms.txt` | un sommaire pour les robots IA, qui pointe vers `moi.md` |
| `exemple/` | un TP terminé, fictif (Marie Exemple), pour voir le résultat attendu |
| `.nojekyll` | dit à GitHub Pages de publier les fichiers tels quels (ne le supprimez pas) |

## Démarrer en 3 gestes

1. En haut de cette page : **Use this template → Create a new repository**.
2. Nom du dépôt : **`votre-identifiant.github.io`** (exactement votre identifiant GitHub, puis `.github.io`), visibilité **Public**, puis **Create repository**.
3. Dans votre nouveau dépôt : **Settings → Pages → Build and deployment → Source : Deploy from a branch → Branch : `main` · `/ (root)` → Save**.

Après une à cinq minutes, votre page s'affiche à l'adresse `https://votre-identifiant.github.io/`.

## Modifier un fichier sans rien installer

Cliquez sur le fichier, puis sur le crayon (**Edit this file**), modifiez, puis **Commit changes…** et encore **Commit changes**. La page se met à jour en une à deux minutes.

Partout, remplacez `IDENTIFIANT` par votre identifiant GitHub.

## Règles

- Rien de privé : la page est publique. Pas d'adresse personnelle, de téléphone ni de date de naissance.
- Rien d'inventé : chaque propriété du JSON-LD correspond à quelque chose de visible sur la page.
- Vous pourrez supprimer le dépôt après la formation : **Settings → General → Danger Zone → Delete this repository**.
