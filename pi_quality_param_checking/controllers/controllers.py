# -*- coding: utf-8 -*-
# from odoo import http


# class PiQualityParamChecking(http.Controller):
#     @http.route('/pi_quality_param_checking/pi_quality_param_checking', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pi_quality_param_checking/pi_quality_param_checking/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pi_quality_param_checking.listing', {
#             'root': '/pi_quality_param_checking/pi_quality_param_checking',
#             'objects': http.request.env['pi_quality_param_checking.pi_quality_param_checking'].search([]),
#         })

#     @http.route('/pi_quality_param_checking/pi_quality_param_checking/objects/<model("pi_quality_param_checking.pi_quality_param_checking"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pi_quality_param_checking.object', {
#             'object': obj
#         })

