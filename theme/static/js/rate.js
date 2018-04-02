$(document).ready(function() {
    $('.rating-star>input').change(function() {
        event.preventDefault();
        var form = $('.rate-form');
        $.ajax({
            type: 'POST',
            url: $(form).attr('action'),
            data: $(form).serialize(),
            cache: false,
            processData: false,
            success: function(data) {
                var rate = $.parseJSON(data);
                $("#rate-number").text(rate.rating_average/2);
            },
            error: function(response) {
                console.log(response);
            }
        });
    });

    $('.rate-form').submit(function(event) {
        event.preventDefault();
        var form = $(this);
        $.ajax({
            type: 'POST',
            url: $(this).attr('action'),
            data: form.serialize(),
            cache: false,
            processData: false,
            success: function(data) {
                var rate = $.parseJSON(data);
                $("#rate-number").text(rate.rating_average);
            },
            error: function(response) {
                console.log(response);
            }
        });
    });
});