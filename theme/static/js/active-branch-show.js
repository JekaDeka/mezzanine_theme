$(function() {
    var ul = $('.active-branch').parent(); //curent active ul
    var parent_li = $(ul).parent();
    var a_parent_li = ul.parent().children()[0]; //anchor tag inside parent list
    var parent_ul = $(parent_li).parent();
    var a_parent_ul = parent_ul.parent().children()[0];
    var main_ul = $(ul).parents('ul').last();
    if (ul.attr('class') == "parent-1") { //either it's 2 or more ul
        ul.css('display', 'block');
        if (parent_ul.attr('class') == "parent-2") {
            $(a_parent_li).addClass('active');
            parent_ul.css('display', 'block');
            $(a_parent_ul).addClass('active');

            //find top level ul
            var top_li = $(parent_ul).parent();
            $(top_li).addClass('active-li');
            var a_top_li = top_li.children()[0];
            $(a_top_li).addClass('active');
        } else {
            $(parent_li).addClass('active-li');
            $(a_parent_li).addClass('active');
        }
    } else {
        //we are on the top level
        var active_li = ul.children('.active-branch');
        $(active_li).addClass('active-li');
    }

    //expand active li elements in top nav menu on mobile
    if ($(window).width() < 960) {
        $("#jPanelMenu-menu li.top_active_branch").parentsUntil($("ul#jPanelMenu-menu")).css("display", "block");
        $.each($("#jPanelMenu-menu .top_nav.caret"), function(i, val) {
            var text = $(this).prev('a').text().trim();
            $(this).text('▼');
            var offset = 42
            if (text.length > 25 ) {
                offset = 60;
            }
            $(val).css('top', -1 * offset);
            $(val).css('height', offset - 12);
        });

    }
});