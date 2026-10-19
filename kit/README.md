# Kit de production Direct Digital

Outils et gabarits utilisés chaque semaine pour produire les publications Instagram et Facebook de Direct Digital.

## Rendu
- Carrousels, visuels uniques et stories : `python3 kit/tools/render_carousel.py spec.json sortie/`
  (types de slides et format de la spec documentés en tête du script ; `"format": "story"` pour du 1080x1920).
- Reels en motion design + couverture : `python3 kit/tools/render_reel.py spec.json sortie/`
- Après chaque rendu, regarder les images produites (planche contact) avant de publier. Le script signale les slides qui débordent.

## Rangement
- Visuels publiés : `AAAA-MM/semaine-NN/…`
- `kit/historique.json` : tout ce qui a été programmé (date, réseau, sujet, uuid Metricool). À lire avant de choisir les sujets, à compléter après chaque programmation.
- `kit/sujets.md` : réserve de sujets, à piocher dans l'ordre et à cocher.

## Liens publics
Les fichiers de ce dépôt sont publics : Metricool les télécharge par leur lien `raw.githubusercontent.com/directdigital-visuels/directdigital-visuels/main/<chemin>`.
