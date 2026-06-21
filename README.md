# Module IT Parc — Gestion de parc informatique

**Auteur :** Touré Lamine  
**Niveau :** Licence 2  
**Projet :** Projet de fin de module — Initiation à l'informatique de gestion  
**Entreprise fictive :** TECHPARK CI — Abidjan, Côte d'Ivoire  
**Version Odoo :** 18.0  

---

## Présentation du projet

Dans le cadre de mon projet de fin de module, j'ai développé un module Odoo 18 qui permet à une entreprise informatique de gérer son parc de matériel. L'idée de base c'est que beaucoup d'entreprises ont du mal à savoir exactement quel équipement elles ont, qui l'utilise, et quand est-ce qu'il faut faire une maintenance ou renouveler un contrat. Ce module essaie de répondre à ces problèmes.

L'entreprise choisie s'appelle **TECHPARK CI**, une société informatique basée à Abidjan. Elle possède des dizaines d'équipements (ordinateurs, serveurs, imprimantes, téléphones IP, équipements réseau) répartis dans plusieurs bureaux.

---

## Ce que fait le module

### 1. Gestion des équipements
On peut enregistrer tous les équipements de l'entreprise avec leurs informations : marque, modèle, numéro de série, date d'achat, valeur, localisation, et date de fin de garantie. Chaque équipement a un état (Brouillon, Affecté, En maintenance, Retiré).

### 2. Affectation aux employés
Le module permet d'affecter un équipement à un employé ou un département. On garde un historique complet de toutes les affectations. Il y a aussi un assistant (wizard) pour faire une réaffectation facilement.

### 3. Suivi des interventions de maintenance
Quand un équipement tombe en panne ou qu'on fait une maintenance préventive, on crée une intervention. On y renseigne la date, le technicien, la description du problème, le rapport et le coût.

### 4. Contrats fournisseurs
On peut enregistrer les contrats de maintenance, de licence ou de support avec les fournisseurs. Le module calcule automatiquement le nombre de jours restants avant l'expiration et affiche une alerte visuelle si le contrat expire bientôt.

### 5. Alertes automatiques
Une tâche planifiée tourne chaque jour et génère des alertes automatiquement quand une garantie ou un contrat est sur le point d'expirer (30 jours par défaut, paramétrable). Il y a aussi un assistant pour lancer le scan manuellement.

### 6. Import CSV
On peut importer des équipements en masse depuis un fichier CSV. C'est utile quand on a beaucoup d'équipements à enregistrer d'un coup.

### 7. Rapports PDF
Trois rapports sont disponibles :
- Fiche détaillée d'un équipement
- Inventaire complet du parc
- Historique des interventions

### 8. Exports Excel
Trois exports Excel sont disponibles :
- Inventaire complet
- Coûts de maintenance
- Contrats expirant bientôt

### 9. Tableau de bord (Dashboard)
Un tableau de bord avec 8 indicateurs clés (KPIs) et des graphiques pour voir en un coup d'œil l'état du parc : nombre d'équipements, interventions du mois, coûts, alertes ouvertes, etc.

---

## Structure du module

```
it_parc/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── it_equipment.py       # Modèle équipement + catégorie
│   ├── it_affectation.py     # Modèle affectation
│   ├── it_intervention.py    # Modèle intervention
│   ├── it_contrat.py         # Modèle contrat fournisseur
│   ├── it_alerte.py          # Modèle alerte + cron
│   ├── it_export.py          # Exports Excel (xlsxwriter)
│   └── it_dashboard.py       # Données pour le dashboard OWL
├── views/
│   ├── it_equipment_views.xml
│   ├── it_affectation_views.xml
│   ├── it_intervention_views.xml
│   ├── it_contrat_views.xml
│   ├── it_alerte_views.xml
│   └── menus.xml
├── wizards/
│   ├── wizard_reaffectation.py / _views.xml
│   ├── wizard_renouvellement.py / _views.xml
│   ├── wizard_scan_alertes.py / _views.xml
│   └── wizard_import_csv.py / _views.xml
├── report/
│   ├── report_equipment_fiche.xml
│   ├── report_inventaire.xml
│   ├── report_interventions.xml
│   └── report_actions.xml
├── security/
│   ├── it_parc_security.xml
│   └── ir.model.access.csv
├── data/
│   ├── it_parc_cron.xml
│   └── it_parc_demo.xml
└── static/
    ├── description/icon.png
    └── src/
        ├── js/dashboard.js
        ├── xml/dashboard.xml
        └── css/dashboard.css
```

---

## Prérequis

- Odoo 18.0 (Community ou Enterprise)
- Python 3.10+
- PostgreSQL 14+
- Bibliothèque Python `xlsxwriter` (pour les exports Excel)
- `wkhtmltopdf` (pour les rapports PDF)

### Installer xlsxwriter si nécessaire

```bash
pip install xlsxwriter
```

---

## Installation du module

### Étape 1 — Copier le module

Copier le dossier `it_parc` dans le répertoire `addons` de votre installation Odoo :

```
/chemin/vers/odoo/addons/it_parc/
```

### Étape 2 — Créer une base de données

Si vous utilisez la ligne de commande, créez une base vide :

```bash
python odoo-bin -c odoo.conf -d it_parc_db --without-demo=all
```

### Étape 3 — Installer le module

```bash
python odoo-bin -c odoo.conf -d it_parc_db -i it_parc
```

### Étape 4 — Lancer le serveur

```bash
python odoo-bin -c odoo.conf -d it_parc_db
```

Puis ouvrir le navigateur à l'adresse : `http://localhost:8069`

---

## Données de démonstration

Le module contient des données de démonstration dans `data/it_parc_demo.xml` :

- 5 catégories d'équipements
- 10 équipements (laptops, serveurs, réseau, imprimante, téléphone)
- 3 contrats fournisseurs (Dell ProSupport, Cisco SmartNet, Licence Odoo)
- 5 interventions (correctives et préventives)
- 2 alertes

Pour charger les données de démo, installer le module sur une base avec démo activée (sans `--without-demo=all`).

---

## Groupes d'accès

| Groupe | Accès |
|---|---|
| IT Technicien | Lecture des équipements, création d'interventions |
| IT Manager | Accès complet (équipements, contrats, alertes, rapports, exports) |

Pour configurer les accès : **Paramètres → Utilisateurs → Sélectionner un utilisateur → onglet IT Parc**

---

## Technologies utilisées

- **Odoo 18.0** — framework ERP
- **Python 3** — modèles, logique métier
- **XML / QWeb** — vues et rapports PDF
- **OWL 2** (Odoo Web Library) — dashboard interactif en JavaScript
- **xlsxwriter** — génération des fichiers Excel
- **PostgreSQL** — base de données

---

*Projet réalisé dans le cadre du module Initiation à l'informatique de gestion — Licence 2*
