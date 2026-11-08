# Kit de production Direct Digital

Outils et gabarits utilisés chaque semaine pour produire les publications Instagram et Facebook de Direct Digital.

## Rendu
- Carrousels, visuels uniques et stories : `python3 kit/tools/render_carousel.py spec.json sortie/`
  (types de slides et format de la spec documentés en tête du script ; `"format": "story"` pour du 1080x1920).
- **Stories : DA native** (depuis le 03/11) : `python3 kit/tools/render_story_native.py spec.json sortie/` — format et règles en tête du script.
  Les stories ne reprennent PAS la DA des publications : elles doivent avoir l'air postées depuis le téléphone de Yohan.
  Vraie photo ou image de vie en fond : piocher dans `kit/brand/story-bg/` (voir INDEX.md, images Higgsfield, étiquette IA à cocher ; jamais la série « hommes préhistoriques ») ou une photo fournie par Yohan, texte façon Instagram (étiquette blanche + texte surligné noir, un mot en bleu au maximum),
  pas de logo, pas de bouton, pas de capitales, « je » plutôt que « nous », 25 mots maximum, texte placé sous les visages, rien sous 1620 px.
  Le ton : une vraie question ou une confidence (« Question du soir 👀 », « Petit cadeau ☕ »), jamais une annonce.
- Reels en motion design + couverture : `python3 kit/tools/render_reel.py spec.json sortie/`
- Après chaque rendu, regarder les images produites (planche contact) avant de publier. Le script signale les slides qui débordent.

## Rangement
- Visuels publiés : `AAAA-MM/semaine-NN/…`
- `kit/historique.json` : tout ce qui a été programmé (date, réseau, sujet, uuid Metricool). À lire avant de choisir les sujets, à compléter après chaque programmation.
- `kit/sujets.md` : réserve de sujets, à piocher dans l'ordre et à cocher.

## Liens publics
Les fichiers de ce dépôt sont publics : Metricool les télécharge par leur lien `raw.githubusercontent.com/directdigital-visuels/directdigital-visuels/main/<chemin>`.

## Horaires de publication Instagram / Facebook (validés le 08/11, prioritaires sur toute autre consigne)
Cible CHR : ne jamais publier pendant les services (11 h 30-14 h 30 et 19 h-22 h 30).
- Carrousels, visuels question et posts du fil : **16 h 00** (coupure de l'après-midi), plus 12 h 30.
- Reels : **15 h 30**.
- Stories : **18 h 00** (elles restent 24 h ; texte au ton « du soir »).
- Le dimanche est le jour où l'audience est la plus active (Metricool) : un créneau possible à 17 h 00.
- LinkedIn est géré par une autre conversation : ne pas toucher à ses horaires.
