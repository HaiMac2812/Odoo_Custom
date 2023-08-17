# # -*- coding: utf-8 -*-
# # Part of Odoo. See LICENSE file for full copyright and licensing details.

# import werkzeug
# import werkzeug.utils
# import werkzeug.exceptions

# from odoo import _
# from odoo import http
# from odoo.addons.http_routing.models.ir_http import slug
# from odoo.exceptions import AccessError
# from odoo.http import request
# from odoo.osv import expression

# from odoo.addons.website_slides.controllers.main import WebsiteSlides


# class WebsiteSlidesSurvey(WebsiteSlides):

#     @http.route(['/slides_survey/slide/get_quizlet_url'], type='http', auth='user', website=True)
#     def slide_get_quizlet_url(self, slide_id, **kw):
#         fetch_res = self._fetch_slide(slide_id)
#         if fetch_res.get('error'):
#             raise werkzeug.exceptions.NotFound()
#         slide = fetch_res['slide']
#         if slide.channel_id.is_member:
#             slide.action_set_viewed()
#         quizlet_url = slide._generate_quizlet_url().get(slide.id)
#         if not quizlet_url:
#             raise werkzeug.exceptions.NotFound()
#         return request.redirect(quizlet_url)

#     @http.route(['/slides_survey/quizlet/search_read'], type='json', auth='user', methods=['POST'], website=True)
#     def slides_quizlet_search_read(self, fields):
#         can_create = request.env['survey.survey'].check_access_rights('create', raise_exception=False)
#         return {
#             'read_results': request.env['survey.survey'].search_read([('certification', '=', False)], fields),
#             'can_create': can_create,
#         }

#     @http.route(['/slides/add_slide'], type='json', auth='user', methods=['POST'], website=True)
#     def create_slide(self, *args, **post):
#         create_new_survey = post['slide_category'] == "certification" and post.get('survey') and not post['survey']['id']
#         linked_survey_id = int(post.get('survey', {}).get('id') or 0)

#         if create_new_survey:
#             # If user cannot create a new survey, no need to create the slide either.
#             if not request.env['survey.survey'].check_access_rights('create', raise_exception=False):
#                 return {'error': _('You are not allowed to create a survey.')}

#             # Create survey first as certification slide needs a survey_id (constraint)
#             post['survey_id'] = request.env['survey.survey'].create({
#                 'title': post['survey']['title'],
#                 'questions_layout': 'page_per_question',
#                 'is_attempts_limited': True,
#                 'attempts_limit': 1,
#                 'is_time_limited': False,
#                 'scoring_type': 'scoring_without_answers',
#                 'certification': True,
#                 'scoring_success_min': 70.0,
#                 'certification_mail_template_id': request.env.ref('survey.mail_template_certification').id,
#             }).id
#         elif linked_survey_id:
#             try:
#                 request.env['survey.survey'].browse([linked_survey_id]).read(['title'])
#             except AccessError:
#                 return {'error': _('You are not allowed to link a certification.')}

#             post['survey_id'] = post['survey']['id']


#         create_new_survey_quizlet = post['slide_category'] == "quizlet" and post.get('survey') and not post['survey']['id']
#         linked_survey_id_quizlet = int(post.get('survey', {}).get('id') or 0)

#         if create_new_survey_quizlet:
#             # If user cannot create a new survey, no need to create the slide either.
#             if not request.env['survey.survey'].check_access_rights('create', raise_exception=False):
#                 return {'error': _('You are not allowed to create a survey.')}

#             # Create survey first as certification slide needs a survey_id (constraint)
#             post['survey_idd'] = request.env['survey.survey'].create({
#                 'title': post['survey']['title'],
#                 'questions_layout': 'page_per_question',
#                 'is_attempts_limited': True,
#                 'attempts_limit': 1,
#                 'is_time_limited': False,
#                 'scoring_type': 'scoring_without_answers',
#                 'certification': False,
#                 'scoring_success_min': 70.0,
#             }).id
#         elif linked_survey_id_quizlet:
#             try:
#                 request.env['survey.survey'].browse([linked_survey_id_quizlet]).read(['title'])
#             except AccessError:
#                 return {'error': _('You are not allowed to link a certification.')}

#             post['survey_idd'] = post['survey']['id']
#         # Then create the slide
#         result = super(WebsiteSlidesSurvey, self).create_slide(*args, **post)

#         if post['slide_category'] == "certification":
#             # Set the url to redirect the user to the survey
#             result['url'] = '/slides/slide/%s?fullscreen=1' % (slug(request.env['slide.slide'].browse(result['slide_id']))),
#         if post['slide_category'] == "quizlet":
#             result['url'] = 'slides/slides/%s?fullscreen=1' % (slug(request.env['slide.slide'].browse(result['slide_idd']))),
        
        
#         return result


# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import werkzeug
import werkzeug.utils
import werkzeug.exceptions

from odoo import _
from odoo import http
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.osv import expression

from odoo.addons.website_slides.controllers.main import WebsiteSlides

from odoo.addons.website_slides_survey.controllers.slides import WebsiteSlidesSurvey


class WebsiteSlideCustom(WebsiteSlides):
    def _get_valid_slide_post_values(self):
        print("Get valid data")
        return [
            "name",
            "url",
            "video_url",
            "document_google_url",
            "image_google_url",
            "tag_ids",
            "slide_category",
            "channel_id",
            "is_preview",
            "binary_content",
            "description",
            "image_1920",
            "is_published",
            "source_type",
            "survey_idd",
            "survey_id",
        ]


class WebsiteSlidesSurvey(WebsiteSlidesSurvey):
    @http.route(
        ["/slides_survey/slide/get_quizlet_url"], type="http", auth="user", website=True
    )
    def slide_get_quizlet_url(self, slide_id, **kw):
        fetch_res = self._fetch_slide(slide_id)
        if fetch_res.get("error"):
            raise werkzeug.exceptions.NotFound()
        slide = fetch_res["slide"]
        if slide.channel_id.is_member:
            slide.action_set_viewed()
        quizlet_url = slide._generate_quizlet_url().get(slide.id)
        if not quizlet_url:
            raise werkzeug.exceptions.NotFound()
        return request.redirect(quizlet_url)

    @http.route(
        ["/slides_survey/quizlet/search_read"],
        type="json",
        auth="user",
        methods=["POST"],
        website=True,
    )
    def slides_quizlet_search_read(self, fields):
        can_create = request.env["survey.survey"].check_access_rights(
            "create", raise_exception=False
        )
        return {
            "read_results": request.env["survey.survey"].search_read(
                [("certification", "=", False)], fields
            ),
            "can_create": can_create,
        }

    # ------------------------------------------------------------
    # Overrides
    # ------------------------------------------------------------

    @http.route(
        ["/slides/add_slide"], type="json", auth="user", methods=["POST"], website=True
    )
    def create_slide(self, *args, **post):
        print("CREATE IN CUSTOM")
        print(post)
        create_new_survey = (
            post["slide_category"] == "quizlet"
            and post.get("survey")
            and not post["survey"]["id"]
        )
        linked_survey_id = int(post.get("survey", {}).get("id") or 0)

        if create_new_survey:
            print("CREATE new survey")
            # If user cannot create a new survey, no need to create the slide either.
            if not request.env["survey.survey"].check_access_rights(
                "create", raise_exception=False
            ):
                return {"error": _("You are not allowed to create a survey.")}

            # Create survey first as quizlet slide needs a survey_idd (constraint)
            post["survey_idd"] = (
                request.env["survey.survey"]
                .create(
                    {
                        "title": post["survey"]["title"],
                        "questions_layout": "page_per_question",
                        "is_attempts_limited": True,
                        "attempts_limit": 1,
                        "is_time_limited": False,
                        "scoring_type": "scoring_without_answers",
                        "certification": False,
                        "scoring_success_min": 70.0,
                    }
                )
                .id
            )
        elif linked_survey_id:
            try:
                print("Link to a survey")
                request.env["survey.survey"].browse([linked_survey_id]).read(["title"])

            except AccessError:
                return {"error": _("You are not allowed to link a quizlet.")}

        post["survey_idd"] = post["survey"]["id"]
        post["survey_id"] = post["survey_idd"]
        # Then create the slide
        print(post)
        webslide = WebsiteSlideCustom()
        result = webslide.create_slide(*args, **post)
        print(result)

        if post["slide_category"] == "quizlet":
            # Set the url to redirect the user to the survey
            result["url"] = (
                "/slides/slide/%s?fullscreen=1"
                % (slug(request.env["slide.slide"].browse(result["slide_id"]))),
            )

        return result

    # Utils
    # ---------------------------------------------------
    def _slide_mark_completed(self, slide):
        if slide.slide_category == "quizlet":
            raise werkzeug.exceptions.Forbidden(
                _("Quizlet slides are completed when the survey is succeeded.")
            )
        return super(WebsiteSlidesSurvey, self)._slide_mark_completed(slide)

    def _get_valid_slide_post_values(self):
        result = super(WebsiteSlidesSurvey, self)._get_valid_slide_post_values()
        result.append("survey_idd")
        return result

     
