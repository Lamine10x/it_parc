from odoo import api, fields, models, _
from odoo.exceptions import UserError


class WizardReaffectation(models.TransientModel):
    _name = 'wizard.reaffectation'
    _description = "Wizard de réaffectation d'équipement"

    equipment_id = fields.Many2one('it.equipment', string='Équipement',
                                   required=True, readonly=True)
    current_employee_id = fields.Many2one(related='equipment_id.employee_id',
                                          string='Employé actuel', readonly=True)
    new_employee_id = fields.Many2one('hr.employee', string='Nouvel employé',
                                      required=True)
    new_department_id = fields.Many2one('hr.department', string='Nouveau département')
    motif = fields.Text(string='Motif de la réaffectation', required=True)
    date_reaffectation = fields.Date(string='Date', required=True,
                                     default=fields.Date.today)

    @api.onchange('new_employee_id')
    def _onchange_new_employee(self):
        if self.new_employee_id:
            self.new_department_id = self.new_employee_id.department_id

    def action_confirm(self):
        self.ensure_one()
        equipment = self.equipment_id

        # Clore l'affectation précédente
        prev = self.env['it.affectation'].search([
            ('equipment_id', '=', equipment.id),
            ('date_end', '=', False),
        ], limit=1)
        if prev:
            prev.date_end = self.date_reaffectation

        # Créer nouvelle affectation
        self.env['it.affectation'].create({
            'equipment_id': equipment.id,
            'employee_id': self.new_employee_id.id,
            'department_id': self.new_department_id.id if self.new_department_id else False,
            'date_start': self.date_reaffectation,
            'motif': self.motif,
        })

        # Mettre à jour l'équipement
        equipment.write({
            'employee_id': self.new_employee_id.id,
            'department_id': self.new_department_id.id if self.new_department_id else False,
            'state': 'assigned',
        })

        equipment.message_post(
            body=_("Réaffecté à %s — Motif : %s") % (self.new_employee_id.name, self.motif)
        )
        return {'type': 'ir.actions.act_window_close'}
