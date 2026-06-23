/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onWillStart } from "@odoo/owl";

class ItParcDashboard extends Component {
    static template = "it_parc.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            loading: true,
            data: {
                kpis: {},
                state_chart: [],
                monthly_interventions: [],
                top5_costs: [],
            },
        });
        onWillStart(async () => {
            await this._loadData();
        });
    }

    async _loadData() {
        try {
            const data = await this.orm.call(
                "it.dashboard",
                "get_dashboard_data",
                [],
                {}
            );
            this.state.data = data;
        } catch (e) {
            console.error("Erreur chargement dashboard IT Parc:", e);
        } finally {
            this.state.loading = false;
        }
    }

    onKpiClick(type) {
        let domain = [];
        let resModel = "it.equipment";
        let name = "Équipements";
        let context = {};
        
        const todayStr = new Date().toISOString().split('T')[0];

        switch (type) {
            case 'total_equipments':
                name = "Tous les équipements";
                break;
            case 'assigned':
                name = "Équipements affectés";
                domain = [["state", "=", "assigned"]];
                break;
            case 'in_maintenance':
                name = "Équipements en maintenance";
                domain = [["state", "=", "maintenance"]];
                break;
            case 'warranty_expired':
                name = "Garanties expirées";
                domain = [["warranty_date", "<", todayStr]];
                break;
            case 'open_alerts':
                resModel = "it.alerte";
                name = "Alertes ouvertes";
                domain = [["state", "=", "open"]];
                break;
            case 'expiring_contrats':
                resModel = "it.contrat";
                name = "Contrats expirant sous 60 jours";
                const limitDate = new Date();
                limitDate.setDate(limitDate.getDate() + 60);
                const limitStr = limitDate.toISOString().split('T')[0];
                domain = [
                    ["date_end", ">=", todayStr],
                    ["date_end", "<=", limitStr],
                    ["state", "=", "active"]
                ];
                break;
            case 'total_maintenance_cost':
            case 'total_maintenance_hours':
                resModel = "it.intervention";
                name = "Interventions terminées";
                domain = [["state", "=", "done"]];
                break;
            default:
                return;
        }

        this.action.doAction({
            type: "ir.actions.act_window",
            name: name,
            res_model: resModel,
            views: [[false, "list"], [false, "form"]],
            domain: domain,
            context: context,
        });
    }

    formatNumber(value) {
        if (!value && value !== 0) return "0";
        return new Intl.NumberFormat("fr-FR").format(Math.round(value));
    }
}

registry.category("actions").add("it_parc.Dashboard", ItParcDashboard);
