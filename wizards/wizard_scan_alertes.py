from odoo import api, fields, models, _


class WizardScanAlertes(models.TransientModel):
    _name = 'wizard.scan.alertes'
    _description = "Wizard de scan manuel des alertes"

    delay_days = fields.Integer(
        string='Délai d\'alerte (jours)', default=30, required=True,
        help="Générer des alertes pour les échéances dans ce délai.")
    result_line_ids = fields.One2many('wizard.scan.alertes.line', 'wizard_id',
                                      string='Alertes générées', readonly=True)
    state = fields.Selection([
        ('draft', 'Prêt'),
        ('done', 'Terminé'),
    ], default='draft')

    def action_scan(self):
        self.ensure_one()
        self.env['it.alerte']._scan_alertes(self.delay_days)

        # Collecter les alertes ouvertes
        alertes = self.env['it.alerte'].search([('state', '=', 'open')])
        lines = [(5, 0, 0)]
        for a in alertes:
            lines.append((0, 0, {
                'wizard_id': self.id,
                'alerte_name': a.name,
                'alerte_type': a.type,
                'date_echeance': a.date_echeance,
                'remaining_days': a.remaining_days,
            }))
        self.write({'result_line_ids': lines, 'state': 'done'})

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.scan.alertes',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }


class WizardScanAlertesLine(models.TransientModel):
    _name = 'wizard.scan.alertes.line'
    _description = 'Ligne résultat scan alertes'

    wizard_id = fields.Many2one('wizard.scan.alertes', ondelete='cascade')
    alerte_name = fields.Char(string='Description')
    alerte_type = fields.Selection([('warranty', 'Garantie'), ('contrat', 'Contrat')],
                                   string='Type')
    date_echeance = fields.Date(string='Échéance')
    remaining_days = fields.Integer(string='Jours restants')
