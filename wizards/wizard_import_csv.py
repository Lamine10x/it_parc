import base64
import csv
import io
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class WizardImportCsv(models.TransientModel):
    _name = 'wizard.import.csv'
    _description = "Wizard d'import CSV d'équipements"

    csv_file = fields.Binary(string='Fichier CSV', required=True,
                              attachment=False)
    csv_filename = fields.Char(string='Nom du fichier')
    delimiter = fields.Selection([
        (',', 'Virgule (,)'),
        (';', 'Point-virgule (;)'),
        ('\t', 'Tabulation'),
    ], string='Séparateur', default=';', required=True)
    encoding = fields.Selection([
        ('utf-8', 'UTF-8'),
        ('latin-1', 'Latin-1 (ISO-8859-1)'),
    ], string='Encodage', default='utf-8', required=True)
    state = fields.Selection([
        ('draft', 'Prêt'),
        ('done', 'Terminé'),
    ], default='draft')
    result_line_ids = fields.One2many('wizard.import.csv.line', 'wizard_id',
                                      string='Résultats', readonly=True)
    count_created = fields.Integer(string='Créés', readonly=True)
    count_ignored = fields.Integer(string='Ignorés (doublons)', readonly=True)
    count_error = fields.Integer(string='Erreurs', readonly=True)

    def action_import(self):
        self.ensure_one()
        if not self.csv_file:
            raise UserError(_("Veuillez sélectionner un fichier CSV."))

        try:
            csv_data = base64.b64decode(self.csv_file)
            text = csv_data.decode(self.encoding)
        except Exception as e:
            raise UserError(_("Erreur de lecture du fichier : %s") % str(e))

        reader = csv.DictReader(io.StringIO(text), delimiter=self.delimiter)
        lines = []
        created = ignored = errors = 0

        required_fields = {'name', 'serial_number', 'category'}

        for row_num, row in enumerate(reader, start=2):
            row = {k.strip(): v.strip() for k, v in row.items() if k}
            missing = required_fields - set(row.keys())
            if missing:
                lines.append({
                    'wizard_id': self.id,
                    'row_number': row_num,
                    'status': 'error',
                    'name': row.get('name', ''),
                    'serial_number': row.get('serial_number', ''),
                    'message': _("Colonnes manquantes : %s") % ', '.join(missing),
                })
                errors += 1
                continue

            serial = row.get('serial_number', '').strip()
            name = row.get('name', '').strip()

            if not name or not serial:
                lines.append({
                    'wizard_id': self.id,
                    'row_number': row_num,
                    'status': 'error',
                    'name': name,
                    'serial_number': serial,
                    'message': _("Nom ou numéro de série vide."),
                })
                errors += 1
                continue

            # Vérification doublon
            existing = self.env['it.equipment'].search(
                [('serial_number', '=', serial)], limit=1)
            if existing:
                lines.append({
                    'wizard_id': self.id,
                    'row_number': row_num,
                    'status': 'ignored',
                    'name': name,
                    'serial_number': serial,
                    'message': _("Doublon — équipement existant : %s") % existing.name,
                })
                ignored += 1
                continue

            # Résolution de la catégorie
            cat_name = row.get('category', 'Autre').strip()
            category = self.env['it.equipment.category'].search(
                [('name', '=', cat_name)], limit=1)
            if not category:
                category = self.env['it.equipment.category'].create(
                    {'name': cat_name})

            try:
                vals = {
                    'name': name,
                    'serial_number': serial,
                    'category_id': category.id,
                    'brand': row.get('brand', ''),
                    'model_name': row.get('model', ''),
                    'location': row.get('location', ''),
                    'purchase_value': float(row['purchase_value']) if row.get('purchase_value') else 0.0,
                }
                self.env['it.equipment'].create(vals)
                lines.append({
                    'wizard_id': self.id,
                    'row_number': row_num,
                    'status': 'created',
                    'name': name,
                    'serial_number': serial,
                    'message': _("Créé avec succès."),
                })
                created += 1
            except Exception as e:
                lines.append({
                    'wizard_id': self.id,
                    'row_number': row_num,
                    'status': 'error',
                    'name': name,
                    'serial_number': serial,
                    'message': str(e),
                })
                errors += 1

        self.env['wizard.import.csv.line'].create(lines)
        self.write({
            'state': 'done',
            'count_created': created,
            'count_ignored': ignored,
            'count_error': errors,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.import.csv',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }


class WizardImportCsvLine(models.TransientModel):
    _name = 'wizard.import.csv.line'
    _description = "Ligne résultat import CSV"

    wizard_id = fields.Many2one('wizard.import.csv', ondelete='cascade')
    row_number = fields.Integer(string='Ligne')
    status = fields.Selection([
        ('created', 'Créé'),
        ('ignored', 'Ignoré'),
        ('error', 'Erreur'),
    ], string='Statut')
    name = fields.Char(string='Nom')
    serial_number = fields.Char(string='N° série')
    message = fields.Char(string='Message')
