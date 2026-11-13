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
  - **Moteur v2 (11/11)** : typo cinétique mot à mot, barre de progression segmentée, musique + effets générés (libres de droits), scènes `hook`, `clip`, `point`, `list`, `compare`, `phone`, `notif`, `counter`, `end`, thème clair par scène (`"theme": "light"`). Mode d'emploi complet en tête de `kit/tools/render_reel.py`, exemple dans `kit/exemples/reel_v2_demo.json`.
  - **Toujours lancer `--preview` d'abord** (planche d'images clés), la regarder, puis le rendu complet.
  - **Réel hybride (format à privilégier)** : scène `clip` en accroche (photo ou plan vidéo avec visage / avatar, fonds validés dans `kit/brand/story-bg/`, jamais d'hommes préhistoriques, étiquette IA à cocher), puis motion design. Les réels 100 % motion design touchent 5 à 7 personnes, ceux avec un visage 50 à 70.
  - **Accroche des réels hybrides (décision du 11/11)** : photo des fonds validés (`kit/brand/story-bg/`), pas de génération Higgsfield payante. Cocher `isAiGenerated: true` sur Instagram (avatar IA). Les réels v2 ont leur propre son : ne pas ajouter de musique Instagram (audioConfiguration) par-dessus.
  - Varier les scènes : pas plus de deux `point` d'affilée ; préférer `phone` / `notif` / `list` / `compare` pour montrer plutôt qu'écrire. `counter` uniquement avec un chiffre réel et sourcé.
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

## Règles tirées de l'état des lieux du 13/11 (à appliquer chaque semaine)
- **Appel à l'action « envoi »** : les demandes d'enregistrement n'obtiennent rien et le partage en message privé est le signal le plus fort. Réels : fin `"cta": "Envoie-le à …", "cta_icon": "send"`. Carrousels : alterner une semaine sur deux « Envoie ce post » (slide cta avec `"action": "Envoie ce post"`) et « Enregistre ce post » pour comparer. Toujours une seule action, identique dans le visuel et la légende Instagram.
- **Légendes Instagram** : première ligne avec les mots-clés du sujet (restaurant, hôtel, café + le problème), une ligne de fin « Direct Digital : IA et automatisation pour les restaurants, cafés et hôtels, à Toulouse et à distance. », 3 hashtags maximum.
- **Une story à sondage par semaine** (lundi) : rendue avec `"sticker_space": true`, sans options imprimées, programmée en `autoPublish: false` (notification) pour que Yohan ajoute l'autocollant Sondage. Indiquer les choix du sondage dans le récapitulatif.
- **Visage dans les 3 premières secondes** de chaque réel (scène `clip`). Si Yohan fournit de courtes vidéos de lui, les utiliser en priorité.
- Collaborations / mentions d'un établissement : uniquement avec un partenaire réel et son accord, jamais inventé.

## Stratégie d'acquisition (13/11) — à lire avant de choisir les sujets
`kit/strategie/STRATEGIE.md` fixe la cible (restaurants, cafés, bars et petits hôtels indépendants de Toulouse), le rôle du compte et **la répartition hebdomadaire des contenus (section 5), qui remplace l'ancienne règle « 1 post sur 3 ouvert aux TPE/PME »**. Le rythme et les horaires ne changent pas.
À chaque production hebdomadaire : appliquer la section 5, remplir la ligne de la semaine écoulée dans `kit/strategie/tableau-de-bord.md` avec les chiffres Metricool, et demander à Yohan dans le récapitulatif ses 3 chiffres (demandes GUIDE, conversations ouvertes, diagnostics réservés) ainsi que les problèmes entendus en prospection.
