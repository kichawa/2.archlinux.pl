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

        var loadPage = function (resp) {
            if (resp.status !== 'ok') {
                throw "fail", resp
            }

            if (resp.code === 302) {
                $.getJSON(resp.location, {pjax: 1}, loadPage);
                return false;
            }

            history.pushState({pjax: true}, null, resp.location);
            $('body').html(resp.html.body);
        };

        // let the pjax happen!
        $.getJSON(href, {pjax: 1}, loadPage);

        return false;
    });


})(jQuery);
