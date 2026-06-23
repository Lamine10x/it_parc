from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    equipment_ids = fields.One2many('it.equipment', 'employee_id', string='Équipements IT')
    equipment_count = fields.Integer(compute='_compute_equipment_count', string="Nombre d'équipements IT")

    @api.depends('equipment_ids')
    def _compute_equipment_count(self):
        for rec in self:
            rec.equipment_count = len(rec.equipment_ids)

    def action_view_it_equipments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Équipements IT',
            'res_model': 'it.equipment',
            'view_mode': 'list,kanban,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id},
        }
