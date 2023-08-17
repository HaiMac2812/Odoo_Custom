# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import collections
import contextlib
import json
import itertools
import operator

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class SurveyQuestion(models.Model):
    _inherit = "survey.question"

    # question generic data
    title = fields.Html('Title', required=True, translate=True)
    question_already = fields.Many2one(
        "survey.question", string="Question Already", ondelete="set null"
    )

    in_question_bank = fields.Boolean(string="Question is added to question bank.")

    question_type = fields.Selection(
        selection_add=[("only_text", "Input answer and get score."),
                       ("drop_down", "Multiple choice: only one answer (render as a Dropdown)"),
                       ("title", "Title")]
    )

    answer_only_text = fields.Char(
        "Correct text box answer", help="Correct text box answer for this question."
    )
    
    triggering_question_id = fields.Many2one(
    'survey.question', string="Triggering Question", copy=False, compute="_compute_triggering_question_id",
    store=True, readonly=False, help="Question containing the triggering answer to display the current question.",
    domain="[('survey_id', '=', survey_id), \
                '&', ('question_type', 'in', ['simple_choice', 'multiple_choice', 'drop_down']), \
                '|', \
                    ('sequence', '<', sequence), \
                    '&', ('sequence', '=', sequence), ('id', '<', id)]")
    
    
    
    def validate_question(self, answer, comment=None):
        """ Validate question, depending on question type and parameters
         for simple choice, text, date and number, answer is simply the answer of the question.
         For other multiple choices questions, answer is a list of answers (the selected choices
         or a list of selected answers per question -for matrix type-):
            - Simple answer : answer = 'example' or 2 or question_answer_id or 2019/10/10
            - Multiple choice : answer = [question_answer_id1, question_answer_id2, question_answer_id3]
            - Matrix: answer = { 'rowId1' : [colId1, colId2,...], 'rowId2' : [colId1, colId3, ...] }

         return dict {question.id (int): error (str)} -> empty dict if no validation error.
         """
        self.ensure_one()
        if isinstance(answer, str):
            answer = answer.strip()
        # Empty answer to mandatory question
        if self.constr_mandatory and not answer and self.question_type not in ['simple_choice', 'multiple_choice','drop_down']:
            return {self.id: self.constr_error_msg or _('This question requires an answer.')}

        # because in choices question types, comment can count as answer
        if answer or self.question_type in ['simple_choice', 'multiple_choice','drop_down']:
            if self.question_type == 'char_box':
                return self._validate_char_box(answer)
            elif self.question_type == 'numerical_box':
                return self._validate_numerical_box(answer)
            elif self.question_type in ['date', 'datetime']:
                return self._validate_date(answer)
            elif self.question_type in ['simple_choice', 'multiple_choice','drop_down']:
                return self._validate_choice(answer, comment)
            elif self.question_type == 'matrix':
                return self._validate_matrix(answer)
        return {}
    def _prepare_statistics(self, user_input_lines):
        """ Compute statistical data for questions by counting number of vote per choice on basis of filter """
        all_questions_data = []
        for question in self:
            question_data = {'question': question, 'is_page': question.is_page}

            if question.is_page:
                all_questions_data.append(question_data)
                continue

            # fetch answer lines, separate comments from real answers
            all_lines = user_input_lines.filtered(lambda line: line.question_id == question)
            if question.question_type in ['simple_choice', 'multiple_choice', 'matrix','drop_down']:
                answer_lines = all_lines.filtered(
                    lambda line: line.answer_type == 'suggestion' or (
                        line.skipped and not line.answer_type) or (
                        line.answer_type == 'char_box' and question.comment_count_as_answer)
                    )
                comment_line_ids = all_lines.filtered(lambda line: line.answer_type == 'char_box')
            else:
                answer_lines = all_lines
                comment_line_ids = self.env['survey.user_input.line']
            skipped_lines = answer_lines.filtered(lambda line: line.skipped)
            done_lines = answer_lines - skipped_lines
            question_data.update(
                answer_line_ids=answer_lines,
                answer_line_done_ids=done_lines,
                answer_input_done_ids=done_lines.mapped('user_input_id'),
                answer_input_skipped_ids=skipped_lines.mapped('user_input_id'),
                comment_line_ids=comment_line_ids)
            question_data.update(question._get_stats_summary_data(answer_lines))

            # prepare table and graph data
            table_data, graph_data = question._get_stats_data(answer_lines)
            question_data['table_data'] = table_data
            question_data['graph_data'] = json.dumps(graph_data)

            all_questions_data.append(question_data)
        return all_questions_data
    
    
    def _get_stats_data(self, user_input_lines):
        if self.question_type == 'simple_choice':
            return self._get_stats_data_answers(user_input_lines)
        elif self.question_type == 'drop_down':
            return self._get_stats_data_answers(user_input_lines)
        elif self.question_type == 'multiple_choice':
            table_data, graph_data = self._get_stats_data_answers(user_input_lines)
            return table_data, [{'key': self.title, 'values': graph_data}]
        elif self.question_type == 'matrix':
            return self._get_stats_graph_data_matrix(user_input_lines)
        return [line for line in user_input_lines], []
    def _get_stats_summary_data(self, user_input_lines):
        stats = {}
        if self.question_type in ['simple_choice', 'multiple_choice','drop_down']:
            stats.update(self._get_stats_summary_data_choice(user_input_lines))
        elif self.question_type == 'numerical_box':
            stats.update(self._get_stats_summary_data_numerical(user_input_lines))

        if self.question_type in ['numerical_box', 'date', 'datetime']:
            stats.update(self._get_stats_summary_data_scored(user_input_lines))
        return stats



    @api.depends(
        "question_type",
        "scoring_type",
        "answer_date",
        "answer_datetime",
        "answer_numerical_box",
        "answer_only_text",
    )
    def _compute_is_scored_question(self):
        """Computes whether a question "is scored" or not. Handles following cases:
        - inconsistent Boolean=None edge case that breaks tests => False
        - survey is not scored => False
        - 'date'/'datetime'/'numerical_box'/only_text question types w/correct answer => True
          (implied without user having to activate, except for numerical whose correct value is 0.0)
        - 'simple_choice / multiple_choice': set to True even if logic is a bit different (coming from answers)
        - question_type isn't scoreable (note: choice questions scoring logic handled separately) => False
        """
        for question in self:
            if (
                question.is_scored_question is None
                or question.scoring_type == "no_scoring"
            ):
                question.is_scored_question = False
            elif question.question_type == "date":
                question.is_scored_question = bool(question.answer_date)
            elif question.question_type == "datetime":
                question.is_scored_question = bool(question.answer_datetime)
            elif (
                question.question_type == "numerical_box"
                and question.answer_numerical_box
            ):
                question.is_scored_question = True
            elif question.question_type in [
                "simple_choice",
                "multiple_choice",
                "only_text",
                "drop_dowwn"
            ]:  # config
                question.is_scored_question = True
            else:
                question.is_scored_question = False

    @api.onchange('question_already')
    def _onchange_question_already(self):
        if self.question_already:
            self.write({
                'title': self.question_already.title})
        if self.question_already and self.question_already.question_type:
            self.question_type = self.question_already.question_type
        if self.question_already and self.question_already.suggested_answer_ids:
            self.suggested_answer_ids = self.question_already.suggested_answer_ids
        if self.question_already and self.question_already.description:
            self.description = self.question_already.description
        if self.question_already and self.question_already.validation_required:
            self.validation_required = self.question_already.validation_required
        if self.question_already and self.question_already.validation_length_min:
            self.validation_length_min = self.question_already.validation_length_min
        if self.question_already and self.question_already.validation_length_max:
            self.validation_length_max = self.question_already.validation_length_max
        if self.question_already and self.question_already.validation_min_float_value:
            self.validation_min_float_value = self.question_already.validation_min_float_value
        if self.question_already and self.question_already.validation_max_float_value:
            self.validation_max_float_value = self.question_already.validation_max_float_value
        if self.question_already and self.question_already.validation_min_date:
            self.validation_min_date = self.question_already.validation_min_date  
        if self.question_already and self.question_already.validation_max_date:
            self.validation_max_date = self.question_already.validation_max_date 
        if self.question_already and self.question_already.validation_min_datetime:
            self.validation_min_datetime = self.question_already.validation_min_datetime   
        if self.question_already and self.question_already.validation_max_datetime:
            self.validation_max_datetime = self.question_already.validation_max_datetime   
        if self.question_already and self.question_already.validation_error_msg:
            self.validation_error_msg = self.question_already.validation_error_msg   
        if self.question_already and self.question_already.matrix_subtype:
            self.matrix_subtype = self.question_already.matrix_subtype
        if self.question_already and self.question_already.question_placeholder:
            self.question_placeholder = self.question_already.question_placeholder
        if self.question_already and self.question_already.comments_allowed:
            self.comments_allowed = self.question_already.comments_allowed
        if self.question_already and self.question_already.comments_message:
            self.comments_message = self.question_already.comments_message
        if self.question_already and self.question_already.comment_count_as_answer:
            self.comment_count_as_answer = self.question_already.comment_count_as_answer
        if self.question_already and self.question_already.is_conditional:
            self.is_conditional = self.question_already.is_conditional
        if self.question_already and self.question_already.triggering_answer_id:
            self.triggering_answer_id = self.question_already.triggering_answer_id
        if self.question_already and self.question_already.constr_mandatory:
            self.constr_mandatory = self.question_already.constr_mandatory
        if self.question_already and self.question_already.constr_error_msg:
            self.constr_error_msg = self.question_already.constr_error_msg
        if self.question_already and self.question_already.is_time_limited:
            self.is_time_limited = self.question_already.is_time_limited
        if self.question_already and self.question_already.time_limit:
            self.time_limit = self.question_already.time_limit
        


            

    # ------------------------------------------------------------
    # STATISTICS / REPORTING
    # ------------------------------------------------------------
    @api.depends('question_type')
    def _compute_question_placeholder(self):
        for question in self:
            if question.question_type in ('simple_choice', 'multiple_choice', 'matrix','drop_down') \
                    or not question.question_placeholder:  # avoid CacheMiss errors
                question.question_placeholder = False
    


    def _prepare_statistics(self, user_input_lines):
        """Compute statistical data for questions by counting number of vote per choice on basis of filter"""
        all_questions_data = []
        for question in self:
            question_data = {"question": question, "is_page": question.is_page}

            if question.is_page:
                all_questions_data.append(question_data)
                continue

            # fetch answer lines, separate comments from real answers
            all_lines = user_input_lines.filtered(
                lambda line: line.question_id == question
            )
            if question.question_type in ["simple_choice", "multiple_choice", "matrix"]:
                answer_lines = all_lines.filtered(
                    lambda line: line.answer_type == "suggestion"
                    or (line.skipped and not line.answer_type)
                    or (
                        line.answer_type == "char_box"
                        and question.comment_count_as_answer
                    )
                )
                comment_line_ids = all_lines.filtered(
                    lambda line: line.answer_type == "char_box"
                )
            else:
                answer_lines = all_lines
                comment_line_ids = self.env["survey.user_input.line"]
            skipped_lines = answer_lines.filtered(lambda line: line.skipped)
            done_lines = answer_lines - skipped_lines
            question_data.update(
                answer_line_ids=answer_lines,
                answer_line_done_ids=done_lines,
                answer_input_done_ids=done_lines.mapped("user_input_id"),
                answer_input_skipped_ids=skipped_lines.mapped("user_input_id"),
                comment_line_ids=comment_line_ids,
            )
            question_data.update(question._get_stats_summary_data(answer_lines))

            # prepare table and graph data
            table_data, graph_data = question._get_stats_data(answer_lines)
            question_data["table_data"] = table_data
            question_data["graph_data"] = json.dumps(graph_data)

            all_questions_data.append(question_data)
        return all_questions_data

    def _get_stats_data(self, user_input_lines):
        if self.question_type == "simple_choice":
            return self._get_stats_data_answers(user_input_lines)
        elif self.question_type == "multiple_choice":
            table_data, graph_data = self._get_stats_data_answers(user_input_lines)
            return table_data, [{"key": self.title, "values": graph_data}]
        elif self.question_type == "matrix":
            return self._get_stats_graph_data_matrix(user_input_lines)
        return [line for line in user_input_lines], []

    def _get_stats_data_answers(self, user_input_lines):
        """Statistics for question.answer based questions (simple choice, multiple
        choice.). A corner case with a void record survey.question.answer is added
        to count comments that should be considered as valid answers. This small hack
        allow to have everything available in the same standard structure."""
        suggested_answers = [answer for answer in self.mapped("suggested_answer_ids")]
        if self.comment_count_as_answer:
            suggested_answers += [self.env["survey.question.answer"]]

        count_data = dict.fromkeys(suggested_answers, 0)
        for line in user_input_lines:
            if line.suggested_answer_id in count_data or (
                line.value_char_box and self.comment_count_as_answer
            ):
                count_data[line.suggested_answer_id] += 1

        table_data = [
            {
                "value": _("Other (see comments)")
                if not sug_answer
                else sug_answer.value,
                "suggested_answer": sug_answer,
                "count": count_data[sug_answer],
            }
            for sug_answer in suggested_answers
        ]
        graph_data = [
            {
                "text": _("Other (see comments)")
                if not sug_answer
                else sug_answer.value,
                "count": count_data[sug_answer],
            }
            for sug_answer in suggested_answers
        ]

        return table_data, graph_data

    def _get_stats_graph_data_matrix(self, user_input_lines):
        suggested_answers = self.mapped("suggested_answer_ids")
        matrix_rows = self.mapped("matrix_row_ids")

        count_data = dict.fromkeys(itertools.product(matrix_rows, suggested_answers), 0)
        for line in user_input_lines:
            if line.matrix_row_id and line.suggested_answer_id:
                count_data[(line.matrix_row_id, line.suggested_answer_id)] += 1

        table_data = [
            {
                "row": row,
                "columns": [
                    {
                        "suggested_answer": sug_answer,
                        "count": count_data[(row, sug_answer)],
                    }
                    for sug_answer in suggested_answers
                ],
            }
            for row in matrix_rows
        ]
        graph_data = [
            {
                "key": sug_answer.value,
                "values": [
                    {"text": row.value, "count": count_data[(row, sug_answer)]}
                    for row in matrix_rows
                ],
            }
            for sug_answer in suggested_answers
        ]

        return table_data, graph_data

    def _get_stats_summary_data(self, user_input_lines):
        stats = {}
        if self.question_type in ["simple_choice", "multiple_choice"]:
            stats.update(self._get_stats_summary_data_choice(user_input_lines))
        elif self.question_type == "numerical_box":
            stats.update(self._get_stats_summary_data_numerical(user_input_lines))

        if self.question_type in ["numerical_box", "date", "datetime"]:
            stats.update(self._get_stats_summary_data_scored(user_input_lines))
        return stats

    def _get_stats_summary_data_choice(self, user_input_lines):
        right_inputs, partial_inputs = (
            self.env["survey.user_input"],
            self.env["survey.user_input"],
        )
        right_answers = self.suggested_answer_ids.filtered(
            lambda label: label.is_correct
        )
        if self.question_type == "multiple_choice":
            for user_input, lines in tools.groupby(
                user_input_lines, operator.itemgetter("user_input_id")
            ):
                user_input_answers = (
                    self.env["survey.user_input.line"]
                    .concat(*lines)
                    .filtered(lambda l: l.answer_is_correct)
                    .mapped("suggested_answer_id")
                )
                if user_input_answers and user_input_answers < right_answers:
                    partial_inputs += user_input
                elif user_input_answers:
                    right_inputs += user_input
        else:
            right_inputs = user_input_lines.filtered(
                lambda line: line.answer_is_correct
            ).mapped("user_input_id")
        return {
            "right_answers": right_answers,
            "right_inputs_count": len(right_inputs),
            "partial_inputs_count": len(partial_inputs),
        }

    def _get_stats_summary_data_numerical(self, user_input_lines):
        all_values = user_input_lines.filtered(lambda line: not line.skipped).mapped(
            "value_numerical_box"
        )
        lines_sum = sum(all_values)
        return {
            "numerical_max": max(all_values, default=0),
            "numerical_min": min(all_values, default=0),
            "numerical_average": round(lines_sum / (len(all_values) or 1), 2),
        }

    def _get_stats_summary_data_scored(self, user_input_lines):
        return {
            "common_lines": collections.Counter(
                user_input_lines.filtered(lambda line: not line.skipped).mapped(
                    "value_%s" % self.question_type
                )
            ).most_common(5),
            "right_inputs_count": len(
                user_input_lines.filtered(lambda line: line.answer_is_correct).mapped(
                    "user_input_id"
                )
            ),
        }

    

    

        
        