// odoo.define('website_slides_survey_quizlet.upload_modal', function (require) {
//     "use strict";
    
//     var core = require('web.core');
//     var _t = core._t;
//     var SlidesUploads = require('@website_slides/js/slides_upload')[Symbol.for("default")];
    
//     /**
//      * Management of the new 'quizlet' slide_category
//      */
//     SlidesUploads.SlideUploadDialog.include({
//         events: _.extend({}, SlidesUploads.SlideUploadDialog.prototype.events || {}, {
//             'change input#quizlet_id': '_onChangeQuizlet'
//         }),
    
//         //--------------------------------------------------------------------------
//         // Handlers
//         //--------------------------------------------------------------------------
    
//        /**
//         * Will automatically set the title of the slide to the title of the chosen quizlet
//         */
//     //    fill tiêu để title trong phần tạo 1 course mới theo survey đã chọn
//         _onChangeQuizlet: function (ev) {
//             const $inputElement = this.$("input#name");
//             if (ev.added) {
//                 this.$('.o_error_no_quizlet').addClass('d-none');
//                 this.$('#quizlet_id').parent().find('.select2-container').removeClass('is-invalid');
//                 if (ev.added.text && !$inputElement.val().trim()) {
//                     $inputElement.val(ev.added.text);
//                 }
//             }
//         },
    
//         //--------------------------------------------------------------------------
//         // Private
//         //--------------------------------------------------------------------------
    
//         /**
//          * Overridden to add the "quizlet" slide category
//          *
//          * @override
//          * @private
//          */
//         _setup: function () {
//             console.log("In custom setup");
//             this._super.apply(this, arguments);
//             this.slide_category_data['quizlet'] = {
//                 icon: 'fa-question-circle',
//                 label: _t('Quizlet'),
//                 template: 'website.slide.upload.modal.quizlet',
//             };
//         },
//         /**
//          * Overridden to add quizlets management in select2
//          *
//          * @override
//          * @private
//          */
//         _bindSelect2Dropdown: function () {
//             this._super.apply(this, arguments);
    
//             var self = this;
//             this.$('#quizlet_id').select2(this._select2Wrapper(_t('Quizlet'), false,
//                 function () {
//                     return self._rpc({
//                         route: '/slides_survey/quizlet/search_read',
//                         params: {
//                             fields: ['title'],
//                         }
//                     });
//                 }, 'title')
//             );
//         },
//         /**
//          * The select2 field makes the "required" input hidden on the interface.
//          * We need to make the "quizlet" field required so we override this method
//          * to handle validation in a fully custom way.
//          *
//          * @override
//          * @private
//          */
//         _formValidate: function () {
//             var result = this._super.apply(this, arguments);
    
//             var $quizletInput = this.$('#quizlet_id');
//             if ($quizletInput.length !== 0) {
//                 var $select2Container = $quizletInput
//                     .parent()
//                     .find('.select2-container');
//                 var $errorContainer = $('.o_error_no_quizlet');
//                 $select2Container.removeClass('is-invalid is-valid');
//                 if ($quizletInput.is(':invalid')) {
//                     $select2Container.addClass('is-invalid');
//                     $errorContainer.removeClass('d-none');
//                 } else if ($quizletInput.is(':valid')) {
//                     $select2Container.addClass('is-valid');
//                     $errorContainer.addClass('d-none');
//                 }
//             }
    
//             return result;
//         },
//         /**
//          * Overridden to add the 'quizlet' field into the submitted values
//          *
//          * @override
//          * @private
//          */
//         _getSelect2DropdownValues: function () {
//             var result = this._super.apply(this, arguments);
    
//             var quizletValue = this.$('#quizlet_id').select2('data');
//             var survey = {};
//             if (quizletValue) {
//                 if (quizletValue.create) {
//                     survey.id = false;
//                     survey.title = quizletValue.text;
//                 } else {
//                     survey.id = quizletValue.id;
//                 }
//             }
//             result['survey'] = survey;
//             return result;
//         },
//     });
    
//     });
    