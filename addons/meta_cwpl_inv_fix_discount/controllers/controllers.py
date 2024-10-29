# -*- coding: utf-8 -*-
# from odoo import http


# class MetaCwplInvFixDiscount(http.Controller):
#     @http.route('/meta_cwpl_inv_fix_discount/meta_cwpl_inv_fix_discount', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/meta_cwpl_inv_fix_discount/meta_cwpl_inv_fix_discount/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('meta_cwpl_inv_fix_discount.listing', {
#             'root': '/meta_cwpl_inv_fix_discount/meta_cwpl_inv_fix_discount',
#             'objects': http.request.env['meta_cwpl_inv_fix_discount.meta_cwpl_inv_fix_discount'].search([]),
#         })

#     @http.route('/meta_cwpl_inv_fix_discount/meta_cwpl_inv_fix_discount/objects/<model("meta_cwpl_inv_fix_discount.meta_cwpl_inv_fix_discount"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('meta_cwpl_inv_fix_discount.object', {
#             'object': obj
#         })
