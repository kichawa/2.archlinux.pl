;(function ($) {

    var pagination = function (a) {

        var pageNext = a.pageNext;
        var pagePrev = a.pagePrev;
        var $btnPrev = $(a.btnPrev);
        var $btnNext = $(a.btnNext);
        var $items = $(a.itemsBox);
        var scrollBot = a.scrollBot || 100;
        var scrollTop = a.scrollTop || 100;

        var isLoading = false;
        var paginationMarks = {};


        $btnPrev.click(function (e) {
            e.preventDefault();
            loadPrev();
        })

        var resourceUrl = function (page) {
            return '?page=' + page;
        };

        var loadPrev = function () {
            if (!pagePrev) {
                return;
            }
            if (isLoading) {
                return;
            }
            isLoading = true;
            $.getJSON(resourceUrl(pagePrev), {xhr: 1}, function (resp) {
                var midEl = parseInt(resp.objects.len / 2, 10);
                pagePrev = resp.meta.pagination.prev;
                var $d = $(document);
                var scrollBot = $d.height() - $d.scrollTop();
                $.each(resp.objects, function (i, o) {
                    var $el = $(o.html);
                    if (i === midEl) {
                        var id = 'pagination-page-' + pagePrev;
                        $el.attr('id', id);
                        paginationMarks[id] = $el;
                    }
                    $items.prepend($el);
                });
                window.scrollTo(0, $d.height() - scrollBot);
                activateScrollPrev();
                $btnPrev.attr('href', resourceUrl(pagePrev) || '#').hide();
                isLoading = false
            });
        };


        $btnNext.click(function (e) {
            e.preventDefault();
            loadNext();
        });

        var loadNext = function () {
            if (!pageNext) {
                return;
            }
            if (isLoading) {
                return;
            }
            isLoading = true;
            $.getJSON(resourceUrl(pageNext), {xhr: 1}, function (resp) {
                var midEl = parseInt(resp.objects.len / 2, 10);
                pageNext = resp.meta.pagination.next;
                $.each(resp.objects, function (i, o) {
                    var $el = $(o.html);
                    if (i === midEl) {
                        var id = 'pagination-page-' + pageNext;
                        $el.attr('id', id);
                        paginationMarks[id] = $el;
                    }
                    $items.append($el);
                });
                activateScrollNext();
                $btnNext.attr('href', resourceUrl(pageNext) || '#').hide();
                isLoading = false
            });
        };

        var activateScrollPrev = function () {
            var $d = $(document);

            var scrollPrev = function () {
                if ($d.scrollTop() < scrollTop) {
                    loadPrev();
                }
                if (!pagePrev) {
                    $d.unbind('scroll', scrollPrev);
                }
            }
            $d.scroll(scrollPrev);
        }

        var activateScrollNext = function () {
            var $d = $(document)

            var scrollNext = function () {
                var h = $d.height() - $(window).height();
                if (h - $d.scrollTop() < scrollBot) {
                    loadNext();
                }
                if (!pageNext) {
                    $d.unbind('scroll', scrollNext);
                }
            }
            $d.scroll(scrollNext);
        }


        if (pushStateAllowed) {
            $(document).scroll(function () {
                var s = $(document).scrollTop();
                var id;
                var scrollTop = 0;
                $.each(paginationMarks, function (name, $el) {
                    var elScroll = $el.position().top;
                    if (elScroll < s && elScroll > scrollTop) {
                        scrollTop = elScroll;
                        id = name;
                    }
                });
                if (id) {
                    var rx = id.match(/\d+/);
                    if (rx) {
                        pushPageState(rx[0]);
                    }
                }
            });
        }

    };




    var pushStateAllowed = !!(history && history.pushState);
    var pushPageState = function (page) {
        if (!pushState) {
            return;
        }
        var param = '?page=' + page;
        if (document.location.search === param) {
            return;
        }
        history.pushState(null, null, param);
    }



    window.Forum = typeof window.Forum === "undefined" ? {} : window.Forum;
    window.Forum.pagination = pagination;

})(jQuery);
