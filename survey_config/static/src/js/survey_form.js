odoo.define("survey_config.form", function (require) {
  "use strict";
  var OriginalWidget = require("survey.form");
  var publicWidget = require("web.public.widget");

  OriginalWidget.include({
    // PREPARE SUBMIT TOOLS
    // -------------------------------------------------------------------------
    /**
     * For each type of question, extract the answer from inputs or textarea (comment or answer)
     *
     *
     * @private
     * @param {Event} event
     */
    _prepareSubmitValues: function (formData, params) {
    
      var self = this;
      formData.forEach(function (value, key) {
        switch (key) {
          case "csrf_token":
          case "token":
          case "page_id":
          case "question_id":
            params[key] = value;
            break;
        }
      });

      // Get all question answers by question type
      this.$("[data-question-type]").each(function () {
        console.log($(this).data("questionType"));
        switch ($(this).data("questionType")) {
          case "text_box":
          case "char_box":
          case "numerical_box":
          case "only_text":
            console.log(this.value);
            params[this.name] = this.value;
            break;
          case "date":
            params = self._prepareSubmitDates(
              params,
              this.name,
              this.value,
              false
            );
            break;
          case "datetime":
            params = self._prepareSubmitDates(
              params,
              this.name,
              this.value,
              true
            );
            break;
          case "simple_choice_radio":
          case "multiple_choice":
            params = self._prepareSubmitChoices(
              params,
              $(this),
              $(this).data("name")
            );
            break;
          case "matrix":
            params = self._prepareSubmitAnswersMatrix(params, $(this));
            break;
        }
      });
    },
  });
});
