import base64
import io
from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ItExportMixin(models.AbstractModel):
    """Méthodes utilitaires pour la génération de fichiers Excel."""
    _name = 'it.export.mixin'
    _description = 'Mixin exports Excel'

    @api.model
    def _get_workbook(self):
        try:
            import xlsxwriter
        except ImportError:
            raise UserError(_(
                "La bibliothèque xlsxwriter est requise.\n"
                "Installez-la avec : pip install xlsxwriter"
            ))
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        return workbook, output

    @staticmethod
    def _add_header_format(workbook):
        return workbook.add_format({
            'bold': True, 'bg_color': '#2E4057', 'font_color': 'white',
            'border': 1, 'align': 'center', 'valign': 'vcenter',
            'text_wrap': True,
        })

    @staticmethod
    def _add_title_format(workbook):
        return workbook.add_format({
            'bold': True, 'font_size': 14, 'font_color': '#2E4057',
        })

    @staticmethod
    def _add_money_format(workbook):
        return workbook.add_format({
            'num_format': '#,##0', 'align': 'right', 'border': 1,
        })

    @staticmethod
    def _add_cell_format(workbook, color=None):
        fmt = {'border': 1, 'valign': 'vcenter'}
        if color:
            fmt['bg_color'] = color
        return workbook.add_format(fmt)

    @staticmethod
    def _add_date_format(workbook):
        return workbook.add_format({
            'num_format': 'dd/mm/yyyy', 'border': 1,
        })

    @staticmethod
    def _finalize(workbook, output):
        workbook.close()
        output.seek(0)
        return base64.b64encode(output.read())


class ItEquipmentExport(models.Model):
    _inherit = 'it.equipment'

    def action_export_inventaire_excel(self):
        """Export 1 : Inventaire complet (toutes colonnes)."""
        workbook, output = self.env['it.export.mixin']._get_workbook()
        ws = workbook.add_worksheet('Inventaire')
        mixin = self.env['it.export.mixin']

        hdr = mixin._add_header_format(workbook)
        cell = mixin._add_cell_format(workbook)
        money = mixin._add_money_format(workbook)
        dt = mixin._add_date_format(workbook)
        title_fmt = mixin._add_title_format(workbook)
        expired_fmt = mixin._add_cell_format(workbook, color='#FFD6D6')

        ws.write(0, 0, 'Inventaire du Parc Informatique — TECHPARK CI', title_fmt)
        ws.write(1, 0, f'Édité le {date.today().strftime("%d/%m/%Y")}')

        headers = [
            'Référence', 'Nom', 'Catégorie', 'Marque', 'Modèle',
            'N° série', 'Employé', 'Département', 'Localisation',
            "Date d'achat", "Valeur d'achat (FCFA)", 'Fin garantie', 'État',
        ]
        col_widths = [15, 25, 15, 12, 15, 18, 20, 20, 15, 12, 18, 12, 12]

        for col, (h, w) in enumerate(zip(headers, col_widths)):
            ws.write(3, col, h, hdr)
            ws.set_column(col, col, w)
        ws.set_row(3, 25)

        equipments = self.search([]) if not self else self
        state_labels = dict(self._fields['state'].selection)

        for row_idx, eq in enumerate(equipments, start=4):
            fmt = expired_fmt if eq.warranty_expired else cell
            ws.write(row_idx, 0, eq.reference or '', fmt)
            ws.write(row_idx, 1, eq.name, fmt)
            ws.write(row_idx, 2, eq.category_id.name or '', fmt)
            ws.write(row_idx, 3, eq.brand or '', fmt)
            ws.write(row_idx, 4, eq.model_name or '', fmt)
            ws.write(row_idx, 5, eq.serial_number or '', fmt)
            ws.write(row_idx, 6, eq.employee_id.name or '', fmt)
            ws.write(row_idx, 7, eq.department_id.name or '', fmt)
            ws.write(row_idx, 8, eq.location or '', fmt)
            if eq.purchase_date:
                ws.write_datetime(row_idx, 9,
                                  eq.purchase_date.strftime('%Y-%m-%d'), dt)
            else:
                ws.write(row_idx, 9, '', fmt)
            ws.write(row_idx, 10, eq.purchase_value or 0, money)
            if eq.warranty_date:
                ws.write_datetime(row_idx, 11,
                                  eq.warranty_date.strftime('%Y-%m-%d'), dt)
            else:
                ws.write(row_idx, 11, '', fmt)
            ws.write(row_idx, 12, state_labels.get(eq.state, ''), fmt)

        xlsx_data = mixin._finalize(workbook, output)
        attachment = self.env['ir.attachment'].create({
            'name': f'inventaire_parc_{date.today()}.xlsx',
            'type': 'binary',
            'datas': xlsx_data,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }


class ItInterventionExport(models.Model):
    _inherit = 'it.intervention'

    def action_export_couts_maintenance_excel(self):
        """Export 2 : Synthèse des coûts de maintenance par asset et par mois."""
        workbook, output = self.env['it.export.mixin']._get_workbook()
        ws = workbook.add_worksheet('Coûts maintenance')
        mixin = self.env['it.export.mixin']

        hdr = mixin._add_header_format(workbook)
        cell = mixin._add_cell_format(workbook)
        money = mixin._add_money_format(workbook)
        title_fmt = mixin._add_title_format(workbook)

        ws.write(0, 0, 'Synthèse des coûts de maintenance — TECHPARK CI', title_fmt)
        ws.write(1, 0, f'Édité le {date.today().strftime("%d/%m/%Y")}')

        headers = ['Équipement', 'Catégorie', 'Nb interventions',
                   'Durée totale (h)', 'Coût total (FCFA)',
                   'Coût moyen / intervention (FCFA)']
        col_widths = [25, 15, 18, 16, 20, 25]
        for col, (h, w) in enumerate(zip(headers, col_widths)):
            ws.write(3, col, h, hdr)
            ws.set_column(col, col, w)
        ws.set_row(3, 25)

        # Agréger par équipement
        interventions = self.search([('state', '=', 'done')])
        by_eq = {}
        for interv in interventions:
            eq_id = interv.equipment_id.id
            if eq_id not in by_eq:
                by_eq[eq_id] = {
                    'name': interv.equipment_id.name,
                    'category': interv.equipment_id.category_id.name or '',
                    'count': 0, 'duration': 0.0, 'cost': 0.0,
                }
            by_eq[eq_id]['count'] += 1
            by_eq[eq_id]['duration'] += interv.duration
            by_eq[eq_id]['cost'] += interv.cost

        for row_idx, data in enumerate(sorted(by_eq.values(),
                                              key=lambda x: x['cost'],
                                              reverse=True),
                                       start=4):
            avg = data['cost'] / data['count'] if data['count'] else 0
            ws.write(row_idx, 0, data['name'], cell)
            ws.write(row_idx, 1, data['category'], cell)
            ws.write(row_idx, 2, data['count'], cell)
            ws.write(row_idx, 3, round(data['duration'], 1), cell)
            ws.write(row_idx, 4, data['cost'], money)
            ws.write(row_idx, 5, round(avg, 0), money)

        xlsx_data = mixin._finalize(workbook, output)
        attachment = self.env['ir.attachment'].create({
            'name': f'couts_maintenance_{date.today()}.xlsx',
            'type': 'binary',
            'datas': xlsx_data,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }


class ItContratExport(models.Model):
    _inherit = 'it.contrat'

    def action_export_contrats_expiration_excel(self):
        """Export 3 : Contrats expirant dans les 60 jours (mise en couleur conditionnelle)."""
        workbook, output = self.env['it.export.mixin']._get_workbook()
        ws = workbook.add_worksheet('Contrats expirants')
        mixin = self.env['it.export.mixin']

        hdr = mixin._add_header_format(workbook)
        cell = mixin._add_cell_format(workbook)
        money = mixin._add_money_format(workbook)
        dt = mixin._add_date_format(workbook)
        title_fmt = mixin._add_title_format(workbook)
        danger_fmt = mixin._add_cell_format(workbook, color='#FFD6D6')
        warning_fmt = mixin._add_cell_format(workbook, color='#FFF3CD')

        ws.write(0, 0, 'Contrats expirant dans les 60 jours — TECHPARK CI', title_fmt)
        ws.write(1, 0, f'Édité le {date.today().strftime("%d/%m/%Y")}')

        headers = ['Intitulé', 'Type', 'Fournisseur', 'Date début',
                   'Date fin', 'Jours restants', 'Montant (FCFA)', 'État']
        col_widths = [25, 12, 20, 12, 12, 14, 18, 12]
        for col, (h, w) in enumerate(zip(headers, col_widths)):
            ws.write(3, col, h, hdr)
            ws.set_column(col, col, w)
        ws.set_row(3, 25)

        contrats = self.search([
            ('remaining_days', '<=', 60),
            ('state', '=', 'active'),
        ], order='remaining_days asc')

        type_labels = dict(self._fields['type'].selection)
        state_labels = dict(self._fields['state'].selection)

        for row_idx, ct in enumerate(contrats, start=4):
            if ct.remaining_days < 0:
                fmt, money_fmt = danger_fmt, danger_fmt
            elif ct.remaining_days < 15:
                fmt, money_fmt = danger_fmt, danger_fmt
            else:
                fmt, money_fmt = warning_fmt, warning_fmt

            ws.write(row_idx, 0, ct.name, fmt)
            ws.write(row_idx, 1, type_labels.get(ct.type, ''), fmt)
            ws.write(row_idx, 2, ct.partner_id.name or '', fmt)
            if ct.date_start:
                ws.write_datetime(row_idx, 3,
                                  ct.date_start.strftime('%Y-%m-%d'), dt)
            else:
                ws.write(row_idx, 3, '', fmt)
            if ct.date_end:
                ws.write_datetime(row_idx, 4,
                                  ct.date_end.strftime('%Y-%m-%d'), dt)
            else:
                ws.write(row_idx, 4, '', fmt)
            ws.write(row_idx, 5, ct.remaining_days, fmt)
            ws.write(row_idx, 6, ct.amount, money)
            ws.write(row_idx, 7, state_labels.get(ct.state, ''), fmt)

        xlsx_data = mixin._finalize(workbook, output)
        attachment = self.env['ir.attachment'].create({
            'name': f'contrats_expiration_{date.today()}.xlsx',
            'type': 'binary',
            'datas': xlsx_data,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
