# -*- coding: utf-8 -*-
# from odoo import http


# class BiometricIntegration(http.Controller):
#     @http.route('/biometric_integration/biometric_integration', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/biometric_integration/biometric_integration/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('biometric_integration.listing', {
#             'root': '/biometric_integration/biometric_integration',
#             'objects': http.request.env['biometric_integration.biometric_integration'].search([]),
#         })

#     @http.route('/biometric_integration/biometric_integration/objects/<model("biometric_integration.biometric_integration"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('biometric_integration.object', {
#             'object': obj
#         })

