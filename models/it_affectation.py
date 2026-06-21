from odoo import api, fields, models, _


class ItAffectation(models.Model):
    _name = 'it.affectation'
    _description = 'Historique des affectations'
    _order = 'date_start desc'

    equipment_id = fields.Many2one('it.equipment', string='Équipement',
                                   required=True, ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string='Employé',
                                  required=True)
    department_id = fields.Many2one('hr.department', string='Département')
    date_start = fields.Date(string='Date début', required=True,
                             default=fields.Date.today)
    date_end = fields.Date(string='Date fin')
    motif = fields.Text(string='Motif de la mutation')
    active = fields.Boolean(default=True)

    @api.onchange('employee_id')
    def _onchange_employee(self):
        if self.employee_id:
            self.department_id = self.employee_id.department_id
