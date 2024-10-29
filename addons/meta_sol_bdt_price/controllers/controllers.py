# -*- coding: utf-8 -*-
# from odoo import http


# class MetaSolBdtPrice(http.Controller):
#     @http.route('/meta_sol_bdt_price/meta_sol_bdt_price', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/meta_sol_bdt_price/meta_sol_bdt_price/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('meta_sol_bdt_price.listing', {
#             'root': '/meta_sol_bdt_price/meta_sol_bdt_price',
#             'objects': http.request.env['meta_sol_bdt_price.meta_sol_bdt_price'].search([]),
#         })

#     @http.route('/meta_sol_bdt_price/meta_sol_bdt_price/objects/<model("meta_sol_bdt_price.meta_sol_bdt_price"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('meta_sol_bdt_price.object', {
#             'object': obj
#         })
