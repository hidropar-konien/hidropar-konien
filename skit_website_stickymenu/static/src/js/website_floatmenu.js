odoo.define('skit_website_stickymenu.website_floatmenu', function (require) {
	$(document).ready(function () {
        var menu = $('.fixed-homemenu');
        var origOffsetY = menu.offset().top;
    if ($(".o_connected_user").length > 0){
    	function scroll() {
            if ($(window).scrollTop() >= origOffsetY) {
                $('.fixed-homemenu').addClass('sticky_homemenu_afterlogin');
            } else {
                $('.fixed-homemenu').removeClass('sticky_homemenu_afterlogin');
            }
        }
    	document.onscroll = scroll;
    }
    else{
    	function scroll() {
            if ($(window).scrollTop() >= origOffsetY) {
                $('.fixed-homemenu').addClass('sticky_homemenu_beforelogin');
            } else {
                $('.fixed-homemenu').removeClass('sticky_homemenu_beforelogin');
            }
        }
    	document.onscroll = scroll;
    }
    });
});