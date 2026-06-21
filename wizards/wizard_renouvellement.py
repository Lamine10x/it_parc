from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta


class WizardRenouvellement(models.TransientModel):
    _name = 'wizard.renouvellement'
    _description = 'Wizard de renouvellement de contrat'

    contrat_id = fields.Many2one('it.contrat', string='Contrat', required=True,
                                 readonly=True)
    new_date_start = fields.Date(string='Nouvelle date début', required=True,
                                 default=fields.Date.today)
    new_date_end = fields.Date(string='Nouvelle date fin', required=True)
    new_amount = fields.Float(string='Nouveau montant (FCFA)', digits=(16, 0))
    note = fields.Text(string='Note de renouvellement')

    @api.onchange('contrat_id', 'new_date_start')
    def _onchange_compute_end(self):
        if self.contrat_id and self.new_date_start:
            # Propose la même durée que le contrat précédent
            if self.contrat_id.date_start and self.contrat_id.date_end:
                duration = relativedelta(self.contrat_id.date_end,
                                         self.contrat_id.date_start)
                self.new_date_end = self.new_date_start + duration
            if not self.new_amount:
                self.new_amount = self.contrat_id.amount

    def action_confirm(self):
        self.ensure_one()
        contrat = self.contrat_id
        contrat.write({
            'date_start': self.new_date_start,
            'date_end': self.new_date_end,
            'amount': self.new_amount,
            'state': 'renewed',
        })
        contrat.message_post(
            body=_("Contrat renouvelé jusqu'au %s. %s") % (
                self.new_date_end, self.note or '')
        )
        return {'type': 'ir.actions.act_window_close'}
