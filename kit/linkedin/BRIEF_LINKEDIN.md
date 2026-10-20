# Brief LinkedIn — Direct Digital

État au 20/10/2026 (13 h 30). Ce fichier sert de point de départ à toute conversation dédiée à LinkedIn.
Instagram et Facebook sont gérés ailleurs (tâche hebdomadaire « Production hebdo Direct Digital » + Metricool) et ne sont pas concernés ici.

## Comptes
| Compte | URL | Outil de publication | État |
|---|---|---|---|
| Page **Direct Digital** | linkedin.com/company/directdigital-ai | Typefully — social set `348317` (« Direct Digital ») | Connectée |
| Profil perso **Yohan Soubrat** (Fondateur & Gérant) | linkedin.com/in/yohan-soubrat | Typefully (à connecter) | **Pas encore connecté** |

- Typefully, offre gratuite : **10 publications / mois** (quota vu sur la page, remis à zéro le 1er de chaque mois). À vérifier : quota commun ou par compte, et possibilité d'un 2e compte en gratuit.
- Créneaux de la page dans Typefully : mardi, mercredi, jeudi à 8 h 30 (Europe/Paris). **Décision en attente** : passer à 2 posts / semaine (mardi + jeudi) pour tenir dans le quota.
- LinkedIn n'est pas relié à Metricool.

## Ligne éditoriale
- **Page** : contenu pédagogique et utile — listes, carrousels, conseils actionnables. Ton **« vous »**, voix « nous ». 2 posts / semaine (cible).
- **Profil perso** : 1 post / semaine (mardi ou mercredi, 8 h–9 h, en décalé de la page), au **« je »**, mention @Direct Digital environ 1 post sur 3. Rotation sur 4 semaines :
  1. L'histoire (pourquoi Direct Digital, parcours commerce + communication + IA)
  2. Observation terrain (gérants, dirigeants, problèmes vécus)
  3. Coulisses (une automatisation testée : ce qui a marché / raté)
  4. Prise de position sur l'IA
- Cibles : dirigeants de TPE/PME, restaurateurs, hôteliers, indépendants (France, Belgique, Suisse).
- Fiabilité : aucun client, résultat chiffré ou témoignage inventé ; ne pas écrire « je travaille avec des agences » tant que ce n'est pas vrai ; aucun prix.
- Interactions (commentaires, invitations, messages privés) : **toujours manuelles**. L'automatisation est réservée à la programmation des posts.

## Charte graphique
- Charte officielle (voir `kit/README.md`, `kit/templates/carousel.css`) : bleu électrique `#2563FF`, bleu nuit `#10172A`, blanc ; violet en accent discret ; Poppins + Inter ; logo `kit/brand/mark.png` ; pas de robots ni de néons.
- Rendu : `python3 kit/tools/render_carousel.py spec.json sortie/`. Pour LinkedIn, textes au « vous » (surcharger `swipe` et `action`). Le carrousel du 22/10 a été rendu avec une typographie agrandie pour les slides `task` (surcharge CSS locale, kit non modifié).
- Format LinkedIn conseillé : carrousel **PDF** (document) 1080×1350.

## Publications
| Date | Compte | Sujet | Visuel | Statut Typefully | ID |
|---|---|---|---|---|---|
| Mar. 20/10, 17 h 30 | Page | 4 idées reçues sur l'automatisation | 6 PNG (`/home/claude/li/mythes`, ancien style violet, pas dans le dépôt) | Programmé | 11363400 |
| Jeu. 22/10, 8 h 30 | Page | 5 tâches à automatiser dès cette semaine | `2026-10/linkedin/2026-10-22_linkedin_5taches.pdf` (charte officielle) | Programmé, PDF joint | 11363406 |
| Mar. 27/10, 8 h 30 | Page | Assistant vocal restaurants & hôtels (« Écrivez APPEL en commentaire ») | Aucun | **Planifié, à confirmer** | 11363408 |
| Jeu. 29/10, 8 h 30 | Page | 3 signes qu'il est temps d'automatiser | Aucun | **Planifié, à confirmer** | 11363410 |

Déjà publiés ou existants hors Typefully :
- Réel avatar « L'IA vous rend des heures » : publié par Yohan (ne pas le republier sur la page).
- Carrousel perso « Arrêtez de faire à la main ce que l'IA peut faire pour vous » (6 slides, photo de Yohan retouchée, chemise marine) : préparé pour le profil perso, texte du post fourni.
- Section Expérience du profil : « Fondateur & Gérant · Direct Digital » rédigée ; descriptions proposées pour Scheppach, Peugeot, Le Bon Mot.
- Slogan de la page proposé : « L'IA et l'automatisation au service des PME, restaurants et hôtels : gagnez du temps, ne ratez plus un client. »

## Prospection
- Outil : **Engage Fast** (offre gratuite, 3 leads visibles). Pas de connecteur Claude actif. Recommandation : affiner les mots-clés (automatisation, IA, réservation, restaurant, hôtel…) et les postes (Gérant, Fondateur, Directeur d'hôtel, Restaurateur).
- Leads :
  - **Prospect A** (dirigeant d'une agence immobilière, Suisse, message gratuit ouvert) — plan : suivre + commenter son dernier post, puis message sur les demandes de visite hors heures de bureau. Brouillons fournis.
  - **Prospect B** (agence immobilière, Suisse) — commentaire politique hors sujet : ne pas y répondre ; demande de connexion basée sur son métier (brouillon fourni).
  - **Prospect C** (comptable salariée) — réponse publique proposée sous un post viral ; cible secondaire.
- Invitations à suivre la page : 50 envoyées le 20/10 (crédits mensuels).
- Connecteurs disponibles mais non utilisés pour LinkedIn : HubSpot (CRM), Vibe Prospecting (données d'entreprises).

## Contraintes techniques
- L'environnement de Claude ne peut pas téléverser de fichiers vers Typefully (`typefully-user-uploads.s3.amazonaws.com` bloqué) : les visuels sont joints à la main par Yohan, ou le domaine doit être autorisé dans claude.ai → Paramètres → Capacités.
- Les brouillons « planifiés » ne partent pas tant qu'ils ne sont pas confirmés.
- Changement d'heure le 25/10 : écrire les dates de novembre en `+01:00`.

## À faire
1. Décider : page à 2 posts / semaine (recommandé) ou offre Typefully payante.
2. Connecter le profil perso dans Typefully, puis préparer le 1er post perso (l'histoire de Direct Digital, à partir du texte retravaillé).
3. Confirmer (et illustrer) les posts des 27 et 29/10.
4. Option : refaire le carrousel « 4 idées reçues » dans la charte officielle.
5. Mettre en place une tâche hebdomadaire LinkedIn (brouillons « planifiés » dans Typefully, validation par Yohan).
