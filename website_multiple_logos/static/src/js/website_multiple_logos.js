odoo.define('website_multiple_logos.sticky_header', function (require) {
'use strict';

var publicWidget = require('web.public.widget');

publicWidget.registry.stickyHeader = publicWidget.Widget.extend({
    selector: 'header#top',
    disabled: false,

    /**
     * @override
     */
    start: function () {
        if (this.editableMode) {
            this.disabled = true;
            return this._super.apply(this, arguments);
        }

        this.header = this.$el;
        this.headerHeight = this.header.outerHeight();
        this.stickyPoint = this.header.offset().top;
        this.scrollFunction = _.throttle(this._updateHeader.bind(this), 100);
        $(window).on('scroll.sticky_header', this.scrollFunction);

        this._updateHeader();

        return this._super.apply(this, arguments);
    },

    /**
     * @override
     */
    destroy: function () {
        if (!this.disabled) {
            $(window).off('.sticky_header');
            $('body').removeClass('o_header_is_sticky').css('padding-top', '');
        }
        this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _updateHeader: function () {
        var scrollTop = $(window).scrollTop();
        var isSticky = this.header.hasClass('o_header_sticky');

        if (scrollTop > this.stickyPoint && !isSticky) {
            // Header sabitlenmeden önce body'e padding ekleyerek sayfa içeriğinin zıplamasını önle
            $('body').css('padding-top', this.headerHeight);
            this.header.addClass('o_header_sticky');
            $('body').addClass('o_header_is_sticky');
        } else if (scrollTop <= this.stickyPoint && isSticky) {
            this.header.removeClass('o_header_sticky');
            $('body').removeClass('o_header_is_sticky').css('padding-top', '');
        }
    },
});
});
