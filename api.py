# TODO: utiliser hug https://www.hug.rest/website/quickstart
# pour implémenter une API permettant d'obtenir :

# - les parties d'un joueur donné / avec ou sans les coups ?
#   (contre un joueur précis, qu'il a gagnées/perdues, à la date D...)
# - des joueurs par identifiant(s), ou par motifs sur le nom.

# L'idée étant, par exemple, de pouvoir créer un site sur lequel
# s'afficherait un "leaderboard" (comme sur fishrandom.io), et où
# on pourrait rejouer des parties, etc.

# => Requêtes plus complexes à construire ensuite ; exemples :
# - nombre maximal de parties gagnées d'affilée ?
# - pourcentage de victoires ?

# On peut aussi imaginer écrire dans la base depuis l'API :
# par exemple pour permettre de jouer des tournois.
# --> création d'une table "Tournaments",
#     ajout d'un champ "tid" dans la table Games (NULL par défaut),
#     ajout d'un paramètre optionnel après #!/play : ID de partie
#     (permet de récupérer l'adversaire ID + nom via XHR ...etc)
#     (si adversaire absent à la connexion, le signaler et attendre)

RPSLS_PATH = './' #edit if launched from elsewhere
DB_PATH = RPSLS_PATH + 'db/rpsls.sqlite'
# ...

# Extension : on peut aussi permettre de choisir le nombre de rounds.
