from odoo import api, fields, models, _


class ItAlerte(models.Model):
    _name = 'it.alerte'
    _description = 'Alerte de garantie ou contrat'
    _order = 'date_echeance asc'

    name = fields.Char(string='Description', required=True)
    type = fields.Selection([
        ('warranty', 'Garantie'),
        ('contrat', 'Contrat'),
    ], string='Type', required=True)
    equipment_id = fields.Many2one('it.equipment', string='Équipement',
                                   ondelete='cascade')
    contrat_id = fields.Many2one('it.contrat', string='Contrat',
                                 ondelete='cascade')
    date_echeance = fields.Date(string='Date échéance', required=True)
    remaining_days = fields.Integer(compute='_compute_remaining',
                                    string='Jours restants', store=False)
    state = fields.Selection([
        ('open', 'Ouverte'),
        ('acknowledged', 'Prise en compte'),
        ('closed', 'Fermée'),
    ], string='État', default='open')

    @api.depends('date_echeance')
    def _compute_remaining(self):
        today = fields.Date.today()
        for rec in self:
            if rec.date_echeance:
                rec.remaining_days = (rec.date_echeance - today).days
            else:
                rec.remaining_days = 0

    def action_acknowledge(self):
        self.write({'state': 'acknowledged'})

    def action_close(self):
        self.write({'state': 'closed'})

    @api.model
    def _cron_generate_alertes(self):
        """Tâche planifiée : génère les alertes pour garanties et contrats expirant bientôt."""
        config = self.env['ir.config_parameter'].sudo()
        delay = int(config.get_param('it_parc.alerte_delay_days', default=30))
        self._scan_alertes(delay)

    @api.model
    def _scan_alertes(self, delay_days=30):
        today = fields.Date.today()
        from datetime import timedelta
        limit_date = today + timedelta(days=delay_days)

        # Alertes garantie
        equipments = self.env['it.equipment'].search([
            ('warranty_date', '!=', False),
            ('warranty_date', '<=', limit_date),
            ('state', 'not in', ['retired']),
        ])
        for eq in equipments:
            existing = self.search([
                ('type', '=', 'warranty'),
                ('equipment_id', '=', eq.id),
                ('state', '=', 'open'),
            ])
            if not existing:
                self.create({
                    'name': _("Garantie expirante : %s") % eq.name,
                    'type': 'warranty',
                    'equipment_id': eq.id,
                    'date_echeance': eq.warranty_date,
                })

        # Alertes contrat
        contrats = self.env['it.contrat'].search([
            ('date_end', '!=', False),
            ('date_end', '<=', limit_date),
            ('state', '=', 'active'),
        ])
        for ct in contrats:
            existing = self.search([
                ('type', '=', 'contrat'),
                ('contrat_id', '=', ct.id),
                ('state', '=', 'open'),
            ])
            if not existing:
                self.create({
                    'name': _("Contrat expirant : %s") % ct.name,
                    'type': 'contrat',
                    'contrat_id': ct.id,
                    'date_echeance': ct.date_end,
                })
