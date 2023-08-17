# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.osv import expression


class SurveyUserInputV2(models.Model):
    _inherit = 'survey.user_input'

    slide_id = fields.Many2one('slide.slide', 'Related course slide',
        help="The related course slide when there is no membership information")
    slide_partner_id = fields.Many2one('slide.slide.partner', 'Subscriber information',
        help="Slide membership information for the logged in user",
        index='btree_not_null') # index useful for deletions in comodel
    quizlet = fields.Boolean("Quizlet", related='survey_id.certification')

   