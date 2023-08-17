# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ChannelV2(models.Model):
    _inherit = 'slide.channel'

    nbr_quizlet = fields.Integer("Number of Quizlets", compute='_compute_slides_statistics', store=True)
