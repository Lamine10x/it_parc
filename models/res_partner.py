from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    contrat_ids = fields.One2many('it.contrat', 'partner_id', string='Contrats IT')
    contrat_count = fields.Integer(compute='_compute_contrat_count', string="Nombre de contrats IT")

    @api.depends('contrat_ids')
    def _compute_contrat_count(self):
        for rec in self:
            rec.contrat_count = len(rec.contrat_ids)

    def action_view_it_contrats(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contrats IT',
            'res_model': 'it.contrat',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }
