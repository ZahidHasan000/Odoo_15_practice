odoo.define("jb_hide_edit_in_view.hideedit", function(require) {
    "use strict";

    var FormRenderer = require('web.FormRenderer');
    var Domain = require("web.Domain");
    var rpc = require('web.rpc');

    FormRenderer.include({

        autofocus: function () {
            this.show_hide_edit_button();
            return this._super();
        },

        show_hide_edit_button : function () {
            if( 'disable_edit_mode' in this.arch.attrs && this.arch.attrs.disable_edit_mode) {
                var domain = Domain.prototype.stringToArray(this.arch.attrs.disable_edit_mode)
                var button = $(".o_form_button_edit");
                if (button) {
                    var hide_edit = new Domain(domain).compute(this.state.data);
                    // If you just need to disable edit button
                    // button.prop('disabled', hide_edit);

                    // button is shown if the parameter is true and hidden if it is false
                    button.toggle(!hide_edit);
                }
            }
        },

    });

});

//disable_edit_mode="[('state', '=', 'approved')]"
//request_state