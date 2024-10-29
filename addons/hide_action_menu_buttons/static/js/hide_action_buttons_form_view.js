odoo.define('hide_action_menu_buttons.FromView', function(require) {
    "use strict";
    var FormView = require('web.FormView');
    var rpc = require('web.rpc');


    FormView.include({

        init: function(viewInfo, params) {
            var self = this;
            this._super.apply(this, arguments);
            console.log('backend_result')
            var domain = [];
            var fields = [];
            rpc.query({
                model: 'hide.action.buttons',
                method: 'check_if_group_view',
                args: [domain, fields],
            }).then(function(data) {

                const model = data.models;

                if (model.includes(self.controllerParams.modelName) && data.group_hide_action_menu_button_view_form)
                {
                    self.controllerParams.hasActionMenus = false;

                }
            });

        },

    });
});