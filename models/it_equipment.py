from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ItEquipment(models.Model):
    _name = 'it.equipment'
    _description = 'Équipement informatique'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'name'

    name = fields.Char(string='Nom', required=True, tracking=True)
    reference = fields.Char(string='Référence interne', copy=False,
                            default=lambda self: _('Nouveau'))
    category_id = fields.Many2one('it.equipment.category', string='Catégorie',
                                  required=True, tracking=True)
    serial_number = fields.Char(string='Numéro de série', tracking=True, copy=False)
    brand = fields.Char(string='Marque')
    model_name = fields.Char(string='Modèle')
    purchase_date = fields.Date(string="Date d'achat", tracking=True)
    purchase_value = fields.Float(string="Valeur d'achat (FCFA)", digits=(16, 0))
    warranty_date = fields.Date(string='Fin de garantie', tracking=True)
    location = fields.Char(string='Localisation', tracking=True)
    description = fields.Text(string='Description technique')
    image = fields.Image(string='Photo', max_width=1024, max_height=1024)

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('assigned', 'Affecté'),
        ('maintenance', 'En maintenance'),
        ('retired', 'Retiré'),
    ], string='État', default='draft', tracking=True, required=True)

    employee_id = fields.Many2one('hr.employee', string='Employé affecté',
                                  tracking=True)
    department_id = fields.Many2one('hr.department', string='Département',
                                    tracking=True)

    affectation_ids = fields.One2many('it.affectation', 'equipment_id',
                                      string='Historique affectations')
    intervention_ids = fields.One2many('it.intervention', 'equipment_id',
                                       string='Interventions')
    contrat_ids = fields.Many2many('it.contrat', string='Contrats')

    affectation_count = fields.Integer(compute='_compute_counts')
    intervention_count = fields.Integer(compute='_compute_counts')
    contrat_count = fields.Integer(compute='_compute_counts')
    warranty_remaining_days = fields.Integer(compute='_compute_warranty_days',
                                             string='Jours garantie restants',
                                             store=False)
    warranty_expired = fields.Boolean(compute='_compute_warranty_days',
                                      string='Garantie expirée')

    @api.depends('affectation_ids', 'intervention_ids', 'contrat_ids')
    def _compute_counts(self):
        for rec in self:
            rec.affectation_count = len(rec.affectation_ids)
            rec.intervention_count = len(rec.intervention_ids)
            rec.contrat_count = len(rec.contrat_ids)

    @api.depends('warranty_date')
    def _compute_warranty_days(self):
        today = fields.Date.today()
        for rec in self:
            if rec.warranty_date:
                delta = (rec.warranty_date - today).days
                rec.warranty_remaining_days = delta
                rec.warranty_expired = delta < 0
            else:
                rec.warranty_remaining_days = 0
                rec.warranty_expired = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', _('Nouveau')) == _('Nouveau'):
                vals['reference'] = self.env['ir.sequence'].next_by_code('it.equipment') or _('Nouveau')
        return super().create(vals_list)

    @api.constrains('serial_number')
    def _check_serial_unique(self):
        for rec in self:
            if rec.serial_number:
                domain = [('serial_number', '=', rec.serial_number),
                          ('id', '!=', rec.id)]
                if self.search_count(domain):
                    raise ValidationError(
                        _("Le numéro de série '%s' existe déjà.") % rec.serial_number)

    def action_assign(self):
        self.write({'state': 'assigned'})

    def action_maintenance(self):
        self.write({'state': 'maintenance'})

    def action_retire(self):
        self.write({'state': 'retired'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_view_affectations(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Historique affectations',
            'res_model': 'it.affectation',
            'view_mode': 'list,form',
            'domain': [('equipment_id', '=', self.id)],
            'context': {'default_equipment_id': self.id},
        }

    def action_view_interventions(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Interventions',
            'res_model': 'it.intervention',
            'view_mode': 'list,form',
            'domain': [('equipment_id', '=', self.id)],
            'context': {'default_equipment_id': self.id},
        }

    def action_view_contrats(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contrats',
            'res_model': 'it.contrat',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.contrat_ids.ids)],
            'context': {'default_equipment_ids': [(4, self.id)]},
        }

    def action_open_reaffectation_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Réaffecter',
            'res_model': 'wizard.reaffectation',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_equipment_id': self.id},
        }


class ItEquipmentCategory(models.Model):
    _name = 'it.equipment.category'
    _description = "Catégorie d'équipement"
    _order = 'name'

    name = fields.Char(string='Catégorie', required=True)
    description = fields.Char(string='Description')
    equipment_count = fields.Integer(compute='_compute_count')

    @api.depends()
    def _compute_count(self):
        for rec in self:
            rec.equipment_count = self.env['it.equipment'].search_count(
                [('category_id', '=', rec.id)])
