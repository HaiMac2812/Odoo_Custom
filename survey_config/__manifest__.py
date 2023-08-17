# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Surveys Custom',
    'version': '2.0',
    'category': 'Marketing/Surveys',
    'description': """
Create beautiful surveys and visualize answers
==============================================

It depends on the answers or reviews of some questions by different users. A
survey may have multiple pages. Each page may contain multiple questions and
each question may have multiple answers. Different users may give different
answers of question and according to that survey is done. Partners are also
sent mails with personal token for the invitation of the survey.
    """,
    'summary': 'Send your surveys or share them live.',
    'website': 'https://www.odoo.com/app/surveys',
    'depends': [
        'survey'],
    'installable': True,
    'auto_install': True,
    'data': [
        'view/survey_already.xml',
        'view/survey_survey_views.xml',
        'view/survey_templates.xml',
        "view/survey_question_views.xml",
        ],
    "assets": {
        "survey.survey_assets": [
            "survey_config/static/src/js/survey_form.js",
        ],
    },
    'license': 'LGPL-3',
}