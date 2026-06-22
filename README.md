Module IT Parc — Gestion de parc informatique
Auteur : Touré Lamine | Licence 2 | Odoo 18.0 | TECHPARK CI (Abidjan)


Ceci est un module Odoo pour gérer son parc informatique. Il permet de suivre chaque équipement, savoir qui l'utilise, quand il a été acheté, et quand sa garantie expire. Il gère aussi les maintenances et les contrats fournisseurs. Tout est centralisé avec des alertes automatiques pour ne rien oublier.

Ce qu'on peut faire avec :

On peut Enregistrer les équipements (marque, modèle, série, date d'achat, prix, localisation, garantie)

Affecter un équipement à un employé (avec historique)

Suivre les interventions de maintenance

Gérer les contrats fournisseurs (expiration calculée automatiquement)

Recevoir des alertes quand une garantie ou un contrat expire bientôt

Importer des équipements depuis un fichier CSV

Exporter en Excel (inventaire, coûts, contrats à échéance)

Imprimer des rapports PDF (fiche équipement, inventaire, interventions)

Visualiser un tableau de bord avec les indicateurs clés

Installation rapide

commmandes bash :
pip install xlsxwriter
python odoo-bin -c odoo.conf -d it_parc_db -i it_parc
Puis ouvrez http://localhost:8069

Accès
IT Technicien : consulter les équipements et créer des interventions

IT Manager : accès complet

Projet de fin de module — Initiation à l'informatique de gestion
