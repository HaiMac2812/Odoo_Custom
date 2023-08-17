odoo.define('website_slides_survey_quizlet.fullscreen', function (require) {
    "use strict";
    var core = require('web.core');
    var QWeb = core.qweb;
    var Fullscreens = require('@website_slides/js/slides_course_fullscreen_player')[Symbol.for("default")];

    Fullscreens.include({
        /**
         * Extend the _renderSlide method so that slides of category "quizlet"
         * are also taken into account and rendered correctly
         *
         * @private
         * @override
         */
        
        _renderSlide: function (){
            var def = this._super.apply(this, arguments);
            var $content = this.$('.o_wslides_fs_content');
            if (this.get('slide').category === "quizlet"){
                $content.html(QWeb.render('website.slides.fullscreen.quizlet',{widget: this}));
            }
            return Promise.all([def]);
        },
    });
    });
    
    
    