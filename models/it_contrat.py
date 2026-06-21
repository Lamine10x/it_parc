from odoo import api, fields, models, _


class ItContrat(models.Model):
    _name = 'it.contrat'
    _description = 'Contrat fournisseur'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_end asc'

    name = fields.Char(string='Intitulé du contrat', required=True, tracking=True)
    reference = fields.Char(string='Référence contrat', copy=False)
    type = fields.Selection([
        ('maintenance', 'Maintenance'),
        ('license', 'Licence logicielle'),
        ('support', 'Support'),
        ('other', 'Autre'),
    ], string='Type', default='maintenance', required=True)
    partner_id = fields.Many2one('res.partner', string='Fournisseur',
                                 required=True, tracking=True)
    date_start = fields.Date(string='Date début', required=True, tracking=True)
    date_end = fields.Date(string='Date fin', required=True, tracking=True)
    amount = fields.Float(string='Montant (FCFA)', digits=(16, 0))
    description = fields.Text(string='Description')
    equipment_ids = fields.Many2many('it.equipment', string='Équipements couverts')

    remaining_days = fields.Integer(compute='_compute_remaining',
                                    string='Jours restants', store=False)
    is_expired = fields.Boolean(compute='_compute_remaining',
                                string='Expiré', store=False)
    state = fields.Selection([
        ('active', 'Actif'),
        ('expired', 'Expiré'),
        ('renewed', 'Renouvelé'),
        ('cancelled', 'Annulé'),
    ], string='État', default='active', tracking=True)

    @api.depends('date_end')
    def _compute_remaining(self):
        today = fields.Date.today()
        for rec in self:
            if rec.date_end:
                delta = (rec.date_end - today).days
                rec.remaining_days = delta
                rec.is_expired = delta < 0
            else:
                rec.remaining_days = 0
                rec.is_expired = False

    def action_open_renouvellement_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Renouveler le contrat',
            'res_model': 'wizard.renouvellement',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_contrat_id': self.id},
        }
