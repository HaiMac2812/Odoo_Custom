from odoo import api, fields, models

class SurveyV2(models.Model):
    _inherit = 'survey.survey'
    
    is_test = fields.Boolean(default = False)
    min_score = fields.Float(help='Min of the required range of test scores')
    max_score = fields.Float(help='Max of the required range of test scores')
    user_input_ids = fields.One2many('survey.user_input', 'survey_id', string='User responses', readonly=True, groups='survey.group_survey_user')
    message_advises = fields.Char(string="Advises", related="user_input_ids.message_advises")

    @api.onchange('is_test')
    def _onchange_is_test(self):
        self.scoring_success_min = 0.0
