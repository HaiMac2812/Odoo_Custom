# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SlidePartnerRelationV2(models.Model):
    _inherit = 'slide.slide.partner'

    user_input_ids = fields.One2many('survey.user_input', 'slide_partner_id', 'Quizlet attempts')
    survey_scoring_success = fields.Boolean('Quizlet Succeeded', compute='_compute_survey_scoring_success', store=True)

    @api.depends('partner_id', 'user_input_ids.scoring_success')
    def _compute_survey_scoring_success(self):
        succeeded_user_inputs = self.env['survey.user_input'].sudo().search([
            ('slide_partner_id', 'in', self.ids),
            ('scoring_success', '=', True)
        ])
        succeeded_slide_partners = succeeded_user_inputs.mapped('slide_partner_id')
        for record in self:
            record.survey_scoring_success = record in succeeded_slide_partners

    def _compute_field_value(self, field):
        super()._compute_field_value(field)
        if field.name == 'survey_scoring_success':
            self.filtered('survey_scoring_success').write({
                'completed': True
            })

class SlideV2(models.Model):
    _inherit = 'slide.slide'

    name = fields.Char(compute='_compute_name', readonly=False, store=True)
    slide_category = fields.Selection(selection_add=[
        ('quizlet', 'Quizlet')
    ], ondelete={'quizlet': 'set default'})

    slide_type = fields.Selection(selection_add=[
        ('quizlet', 'Quizlet')
    ], ondelete={'quizlet': 'set null'})
    survey_idd = fields.Many2one('survey.survey', 'Quizlet')
    nbr_quizlet = fields.Integer("Number of Quizlet", compute='_compute_slides_statistics', store=True)
    # small override of 'is_preview' to uncheck it automatically for slides of type 'quizlet'
    is_preview = fields.Boolean(compute='_compute_is_preview', readonly=False, store=True)

    _sql_constraints = [
        ('check_survey_id', "CHECK(slide_category != 'quizlet' OR survey_idd IS NOT NULL)", "A slide of type 'quizlet' requires a quizlet."),
    ]



    @api.depends('survey_idd')
    def _compute_name(self):
        for slide in self:
            if not slide.name and slide.survey_idd:
                slide.name = slide.survey_idd.title

    def _compute_mark_complete_actions(self):
        slides_quizlet = self.filtered(lambda slide: slide.slide_category == 'quizlet' or slide.slide_category == 'certification')
        slides_quizlet.can_self_mark_uncompleted = False
        slides_quizlet.can_self_mark_completed = False
        super(SlideV2, self - slides_quizlet)._compute_mark_complete_actions()

    @api.depends('slide_category')
    def _compute_is_preview(self):
        for slide in self:
            if slide.slide_category == 'quizlet':
                slide.is_preview = True

    @api.depends('slide_category', 'source_type')
    def _compute_slide_type(self):
        super(SlideV2, self)._compute_slide_type()
        for slide in self:
            if slide.slide_category == 'quizlet':
                slide.slide_type = 'quizlet'
            if slide.slide_category == 'certification':
                slide.slide_type = 'certification'

   

    def _generate_quizlet_url(self):
        """ get a map of quizlet url for quizlet slide from `self`. The url will come from the survey user input:
                1/ existing and not done user_input for member of the course
                2/ create a new user_input for member
                3/ for no member, a test user_input is created and the url is returned
            Note: the slide.slides.partner should already exist

            We have to generate a new invite_token to differentiate pools of attempts since the
            course can be enrolled multiple times.
        """
        quizlet_urls = {}
        for slide in self.filtered(lambda slide: slide.slide_category == 'quizlet' and slide.survey_idd):
            if slide.channel_id.is_member:
                user_membership_id_sudo = slide.user_membership_id.sudo()
                if user_membership_id_sudo.user_input_ids:
                    last_user_input = next(user_input for user_input in user_membership_id_sudo.user_input_ids.sorted(
                        lambda user_input: user_input.create_date, reverse=True
                    ))
                    quizlet_urls[slide.id] = last_user_input.get_start_url()
                else:
                    user_input = slide.survey_idd.sudo()._create_answer(
                        partner=self.env.user.partner_id,
                        check_attempts=False,
                        **{
                            'slide_id': slide.id,
                            'slide_partner_id': user_membership_id_sudo.id
                        },
                        invite_token=self.env['survey.user_input']._generate_invite_token()
                    )
                    quizlet_urls[slide.id] = user_input.get_start_url()
            else:
                user_input = slide.survey_idd.sudo()._create_answer(
                    partner=self.env.user.partner_id,
                    check_attempts=False,
                    test_entry=True, **{
                        'slide_id': slide.id
                    }
                )
                quizlet_urls[slide.id] = user_input.get_start_url()
        return quizlet_urls


    def _generate_certification_url(self):
        """ get a map of certification url for certification slide from `self`. The url will come from the survey user input:
                1/ existing and not done user_input for member of the course
                2/ create a new user_input for member
                3/ for no member, a test user_input is created and the url is returned
            Note: the slide.slides.partner should already exist

            We have to generate a new invite_token to differentiate pools of attempts since the
            course can be enrolled multiple times.
        """
        certification_urls = {}
        for slide in self.filtered(lambda slide: slide.slide_category == 'certification' and slide.survey_id):
            if slide.channel_id.is_member:
                user_membership_id_sudo = slide.user_membership_id.sudo()
                if user_membership_id_sudo.user_input_ids:
                    last_user_input = next(user_input for user_input in user_membership_id_sudo.user_input_ids.sorted(
                        lambda user_input: user_input.create_date, reverse=True
                    ))
                    certification_urls[slide.id] = last_user_input.get_start_url()
                else:
                    user_input = slide.survey_id.sudo()._create_answer(
                        partner=self.env.user.partner_id,
                        check_attempts=False,
                        **{
                            'slide_id': slide.id,
                            'slide_partner_id': user_membership_id_sudo.id
                        },
                        invite_token=self.env['survey.user_input']._generate_invite_token()
                    )
                    certification_urls[slide.id] = user_input.get_start_url()
            else:
                user_input = slide.survey_id.sudo()._create_answer(
                    partner=self.env.user.partner_id,
                    check_attempts=False,
                    test_entry=True, **{
                        'slide_id': slide.id
                    }
                )
                certification_urls[slide.id] = user_input.get_start_url()
        return certification_urls

