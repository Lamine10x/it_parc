from odoo import api, fields, models, _


class ItIntervention(models.Model):
    _name = 'it.intervention'
    _description = 'Intervention de maintenance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc'

    name = fields.Char(string='Référence', required=True, copy=False,
                       default=lambda self: _('Nouveau'))
    equipment_id = fields.Many2one('it.equipment', string='Équipement',
                                   required=True, tracking=True)
    technician_id = fields.Many2one('hr.employee', string='Technicien',
                                    tracking=True)
    type = fields.Selection([
        ('corrective', 'Corrective'),
        ('preventive', 'Préventive'),
    ], string='Type', default='corrective', required=True, tracking=True)

    date_start = fields.Datetime(string='Début', required=True, tracking=True)
    date_end = fields.Datetime(string='Fin', tracking=True)
    duration = fields.Float(string='Durée (h)', compute='_compute_duration',
                            store=True)
    cost = fields.Float(string='Coût (FCFA)', digits=(16, 0), tracking=True)
    description = fields.Text(string='Description du problème')
    report = fields.Text(string="Rapport d'intervention")

    state = fields.Selection([
        ('planned', 'Planifiée'),
        ('in_progress', 'En cours'),
        ('done', 'Terminée'),
        ('cancelled', 'Annulée'),
    ], string='État', default='planned', tracking=True)

    @api.depends('date_start', 'date_end')
    def _compute_duration(self):
        for rec in self:
            if rec.date_start and rec.date_end:
                delta = rec.date_end - rec.date_start
                rec.duration = delta.total_seconds() / 3600
            else:
                rec.duration = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouveau')) == _('Nouveau'):
                vals['name'] = self.env['ir.sequence'].next_by_code('it.intervention') or _('Nouveau')
        return super().create(vals_list)

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_done(self):
        if not self.date_end:
            self.date_end = fields.Datetime.now()
        self.write({'state': 'done'})
        self.equipment_id.write({'state': 'assigned'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})
