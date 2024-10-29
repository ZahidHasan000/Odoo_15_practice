odoo.define('hide_action_menu_buttons.ListView', function (require) {
"use strict";
 var ListView = require('web.ListView');
    var rpc = require('web.rpc');


ListView.include({

        init: function(viewInfo, params) {
            var self = this;
            this._super.apply(this, arguments);

            var domain = [];
            var fields = [];
            rpc.query({
                model: 'hide.action.buttons',
                method: 'check_if_group_view',
                args: [domain, fields],
            }).then(function(data) {
                const model = data.models;
                console.log(model)
                console.log(data)

                if (model.includes(self.controllerParams.modelName) && data.group_hide_action_menu_button_view_list)
                {
                console.log((model.includes(self.controllerParams.modelName) && data.group_hide_action_menu_button_view_list))
                    self.controllerParams.hasActionMenus = false;

                }
            });

        },

    });
});