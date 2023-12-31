{
    'name': "Course Quizlet",
    'summary': 'Add Quizlet capabilities to your courses',
    'description': """This module lets you use the full power of quizlet within your courses.""",
    'category': 'Website/eLearning',
    'version': '1.0',
    'depends': ['website_slides_survey'],
    'installable': True,
    'auto_install': True,
    'data': [
        'security/ir.model.access.csv',
        'views/slide_slide_views.xml',
        'views/website_slides_menu_views.xml',
        'views/survey_survey_views.xml', 
        'views/website_slides_templates_course.xml',
        'views/website_slides_templates_lesson_fullscreen.xml',
        'views/website_slides_templates_lesson.xml',
        'views/website_slides_templates_utils.xml',
    ],
    # 'demo': [
    #     'data/survey_demo.xml',
    #     'data/slide_slide_demo.xml',
    #     'data/survey.user_input.line.csv',
    # ],
    'assets': {
        'web.assets_frontend': [
    #         'website_slides_survey/static/src/scss/website_slides_survey.scss',
            'website_slides_survey_quizlet/static/src/js/slides_upload.js',
            'website_slides_survey_quizlet/static/src/js/slides_course_fullscreen_player.js',
            'website_slides_survey_quizlet/static/src/xml/website_slide_upload.xml',
            'website_slides_survey_quizlet/static/src/xml/website_slides_fullscreen.xml',
            'website_slides_survey_quizlet/static/src/xml/config_view_certification_fullscreen.xml',
        ],
    #     'survey.survey_assets': [
    #         'website_slides_survey/static/src/scss/website_slides_survey_result.scss',
    #     ],
    },
    # 'uninstall_hook': 'uninstall_hook',
    'license': 'LGPL-3',
}
