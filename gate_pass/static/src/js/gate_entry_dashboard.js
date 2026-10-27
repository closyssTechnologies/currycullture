/** @odoo-module **/

import { Component, xml } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class GateEntryDashboard extends Component {
    static template = xml`
        <div class="o_gate_entry_dashboard">
            <div class="container-fluid">
                <div class="row justify-content-center" style="margin-top: 100px;">
                    <div class="col-md-4 mb-4 mx-3">
                        <div class="card h-100" style="border: 3px solid #5cb3a8; cursor: pointer; background-color: #b8ddd9;" t-on-click="openInwardGateEntry">
                            <div class="card-body d-flex flex-column align-items-center justify-content-center" style="min-height: 150px; padding: 30px;">
                                <div style="font-size: 40px; margin-bottom: 15px; color: black; font-weight: bold;">→</div>
                                <h5 class="text-center mb-2" style="color: black; font-weight: bold;">Inward Gate Entry</h5>
                                <small style="color: black; font-weight: bold;">Enter</small>
                            </div>
                        </div>
                    </div>

                    <div class="col-md-4 mb-4 mx-3">
                        <div class="card h-100" style="border: 3px solid #d4a574; cursor: pointer; background-color: #f5e6d3;" t-on-click="openOutwardGateEntry">
                            <div class="card-body d-flex flex-column align-items-center justify-content-center" style="min-height: 150px; padding: 30px;">
                                <div style="font-size: 40px; margin-bottom: 15px; color: black; font-weight: bold;">←</div>
                                <h5 class="text-center mb-2" style="color: black; font-weight: bold;">Outward Gate Entry</h5>
                                <small style="color: black; font-weight: bold;">Exit</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    setup() {
        this.action = useService("action");
    }

    openInwardGateEntry() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Inward Operation',
            res_model: 'inward.operation',
            view_mode: 'tree,form',
            views: [[false, 'list'], [false, 'form']],
            target: 'current',
        });
    }

    openOutwardGateEntry() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Outward Gate Entry',
            res_model: 'outward.gate.entry',
            view_mode: 'tree,form',
            views: [[false, 'list'], [false, 'form']],
            target: 'current',
        });
    }
}

registry.category("actions").add("gate_entry_dashboard", GateEntryDashboard);