# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Website Slides Custom',
    'version': '2.0',
    'category': 'Marketing/Surveys',
    'description': """
    Config Web Slides
    """,
    'summary': 'Config some function',
    'depends': [
        'website_slides'],
    'installable': True,
    'auto_install': True,
    'data': [
        'views/slide_slide_views.xml',
        ],
    'assets': {
        'web.assets_backend': [
            
            'website_slides_config/static/src/css/main.css'
        ],
    },  
    'license': 'LGPL-3',
}