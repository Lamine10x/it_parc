/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onWillStart } from "@odoo/owl";

class ItParcDashboard extends Component {
    static template = "it_parc.Dashboard";

    setup() {
        this.orm = useService("orm");
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

    formatNumber(value) {
        if (!value && value !== 0) return "0";
        return new Intl.NumberFormat("fr-FR").format(Math.round(value));
    }
}

registry.category("actions").add("it_parc.Dashboard", ItParcDashboard);
