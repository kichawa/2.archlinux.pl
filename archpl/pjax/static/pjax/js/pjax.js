;(function ($) {

    if (!window.history || !window.history.pushState) {
        return;
    }

    $('a').live('click', function (e) {
        var $t = $(e.target);

        if ($t.hasClass('no-pjax')) {
            return true;
        }

        var href = $t.attr('href');
        if (!href  || !href.match(/^\/[^/]*/)) {
            return true;
        }

        e.preventDefault();

        // let the pjax happen!
        $.getJSON(href, {pjax: 1}, function (resp) {
            if (resp.status !== 'ok') {
                throw "fail", resp
            }
            history.pushState(null, null, href);
            $('body').html(resp.html);
        });
        return false;
    });


})(jQuery);
