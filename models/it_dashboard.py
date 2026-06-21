from odoo import api, models, fields


class ItDashboard(models.Model):
    _name = 'it.dashboard'
    _description = 'Dashboard IT Parc — données RPC'

    @api.model
    def get_dashboard_data(self):
        """Retourne toutes les données nécessaires au dashboard OWL."""
        Equipment = self.env['it.equipment']
        Intervention = self.env['it.intervention']
        Contrat = self.env['it.contrat']
        Alerte = self.env['it.alerte']

        total = Equipment.search_count([])
        assigned = Equipment.search_count([('state', '=', 'assigned')])
        in_maintenance = Equipment.search_count([('state', '=', 'maintenance')])
        retired = Equipment.search_count([('state', '=', 'retired')])
        warranty_expired = Equipment.search_count([('warranty_expired', '=', True)])
        open_alerts = Alerte.search_count([('state', '=', 'open')])
        active_contrats = Contrat.search_count([('state', '=', 'active')])
        expiring_contrats = Contrat.search_count([
            ('remaining_days', '<=', 60),
            ('remaining_days', '>=', 0),
            ('state', '=', 'active'),
        ])

        done_interventions = Intervention.search([('state', '=', 'done')])
        total_maintenance_cost = sum(done_interventions.mapped('cost'))
        total_maintenance_hours = sum(done_interventions.mapped('duration'))

        # Distribution par état (pour le graphique en donut)
        state_data = [
            {'label': 'Brouillon', 'value': Equipment.search_count([('state', '=', 'draft')]), 'color': '#6c757d'},
            {'label': 'Affecté', 'value': assigned, 'color': '#28a745'},
            {'label': 'Maintenance', 'value': in_maintenance, 'color': '#ffc107'},
            {'label': 'Retiré', 'value': retired, 'color': '#dc3545'},
        ]

        # Interventions par mois (6 derniers mois)
        from datetime import date, timedelta
        today = date.today()
        months_data = []
        for i in range(5, -1, -1):
            month_start = (today.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1, day=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1, day=1)
            count = Intervention.search_count([
                ('date_start', '>=', fields.Datetime.to_string(month_start)),
                ('date_start', '<', fields.Datetime.to_string(month_end)),
            ])
            months_data.append({
                'label': month_start.strftime('%b %Y'),
                'count': count,
            })

        # Top 5 équipements par coût de maintenance
        eq_costs = {}
        for interv in done_interventions:
            eq_id = interv.equipment_id.id
            eq_name = interv.equipment_id.name
            eq_costs[eq_id] = eq_costs.get(eq_id, {'name': eq_name, 'cost': 0})
            eq_costs[eq_id]['cost'] += interv.cost
        top5 = sorted(eq_costs.values(), key=lambda x: x['cost'], reverse=True)[:5]

        return {
            'kpis': {
                'total_equipments': total,
                'assigned': assigned,
                'in_maintenance': in_maintenance,
                'warranty_expired': warranty_expired,
                'open_alerts': open_alerts,
                'active_contrats': active_contrats,
                'expiring_contrats': expiring_contrats,
                'total_maintenance_cost': total_maintenance_cost,
                'total_maintenance_hours': round(total_maintenance_hours, 1),
            },
            'state_chart': state_data,
            'monthly_interventions': months_data,
            'top5_costs': top5,
        }
