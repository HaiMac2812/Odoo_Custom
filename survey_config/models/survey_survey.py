from odoo import api, fields, models


class SurveyV2(models.Model):
    _inherit = "survey.survey"

    is_test = fields.Boolean(default=False)
    min_score = fields.Float(help="Min of the required range of test scores")
    max_score = fields.Float(help="Max of the required range of test scores")

    @api.onchange("is_test")
    def _onchange_is_test(self):
        pass
