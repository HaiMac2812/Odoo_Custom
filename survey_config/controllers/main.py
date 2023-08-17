# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import logging
import werkzeug

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import fields, http, SUPERUSER_ID, _
from odoo.exceptions import UserError
from odoo.http import request, content_disposition
from odoo.osv import expression
from odoo.tools import format_datetime, format_date, is_html_empty
from odoo.addons.base.models.ir_qweb import keep_query
from addons.survey.controllers import main
_logger = logging.getLogger(__name__)


class Survey(main.Survey):
    
    def _prepare_survey_data(self, survey_sudo, answer_sudo, **post):
            data = super._prepare_survey_data(survey_sudo, answer_sudo, **post)
            for row in data["breadcrumb_pages"]:
                if row["title"].startswith("<p>"):
                    row["title"] = row["title"][3:]
                if row["title"].endswith("</p>"):
                    row["title"] = row["title"][:-4]
            return data
    

     