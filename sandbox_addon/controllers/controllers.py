# -*- coding: utf-8 -*-
# from odoo import http


# class SandboxAddon(http.Controller):
#     @http.route('/sandbox_addon/sandbox_addon', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sandbox_addon/sandbox_addon/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sandbox_addon.listing', {
#             'root': '/sandbox_addon/sandbox_addon',
#             'objects': http.request.env['sandbox_addon.sandbox_addon'].search([]),
#         })

#     @http.route('/sandbox_addon/sandbox_addon/objects/<model("sandbox_addon.sandbox_addon"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sandbox_addon.object', {
#             'object': obj
#         })

