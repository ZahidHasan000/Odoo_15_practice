 odoo.define("meta_purchase_comparison_system.ComparisonData", function (require) {

     const FormRenderer = require("web.FormRenderer");
     const { Component } = owl;
     const { ComponentWrapper } = require("web.OwlCompatibility");

     const { useState } = owl.hooks;

     class PurchaseComparisonSummary extends Component {
         purchase = useState({});
         constructor(self, purchase){
            super();
            this.purchase = purchase;
         }
     };

     Object.assign(PurchaseComparisonSummary, {
         template: "meta_purchase_comparison_system.ComparisonData"
     });

     /**
      * Override the form renderer so that we can mount the component on render
      * to any div with the class o_partner_order_summary.
      */
     FormRenderer.include({
         async _render() {
             await this._super(...arguments);

             for(const element of this.el.querySelectorAll(".purchase_comparison_summary")) {
                this._rpc({
                    model: "purchase.requisition",
                    method: "comparison_chart",
                    args:[[this.state.data.requisition_id.res_id]]
                }).then(function (data)  {
                    console.log('joyanto',data);
                    (new ComponentWrapper(
                        this,
                        PurchaseComparisonSummary,
                        useState(data)
                    )).mount(element);
                });
             }
         }
     });

 });


// (new ComponentWrapper(this, PurchaseComparisonSummary))
//                     .mount(element)