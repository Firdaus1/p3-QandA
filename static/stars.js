$(window).on('load', function() {
    console.log('the page is loaded');
});

$('.widget.upvote').on('click', function() {
    console.log('upvote was clicked');
    var state = $(this).attr('data-state');
    if (state == 'pending') {
        console.log('request in progress, dropping second click');
        return;
    }
    var checked  = state === 'checked';
    var nextState = checked ? 'unchecked' : 'checked';
    var elt = $(this);
    elt.attr('data-state', 'pending');
    $.ajax('/api/upvote', {
        method: 'POST',
        data: {
            answer_id: $('.answer.content').attr('data-answer-id'),
            want_star: !checked,
            _csrf_token: csrfToken,
        },
        success: function(data) {
            /* called when post succeeds */
            console.log('post succeeded with result %s', data.result);
            elt.attr('data-state', nextState);
        },
        error: function() {
            /* called when post fails */
            console.error('post failed');
            elt.attr('data-state', state);
        }
    });
});

$('.widget.downvote').on('click', function() {
    console.log('downvote was clicked');
    var state = $(this).attr('data-state');
    if (state == 'pending') {
        console.log('request in progress, dropping second click');
        return;
    }
    var checked  = state === 'checked';
    var nextState = checked ? 'unchecked' : 'checked';
    var elt = $(this);
    elt.attr('data-state', 'pending');
    $.ajax('/api/downvote', {
        method: 'POST',
        data: {
            answer_id: $('.answer.content').attr('data-answer-id'),
            want_star: !checked,
            _csrf_token: csrfToken,
        },
        success: function(data) {
            /* called when post succeeds */
            console.log('post succeeded with result %s', data.result);
            elt.attr('data-state', nextState);
        },
        error: function() {
            /* called when post fails */
            console.error('post failed');
            elt.attr('data-state', state);
        }
    });
});