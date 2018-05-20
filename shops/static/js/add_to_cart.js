$(document).ready(function() {
  $(".add-to-cart").on('click touch', function() {
    if (!$(this).is('.added')) {
      event.preventDefault();
      var button = $(this);
      var form = $(this).parent('.add-to-cart-form');
      var data = $(form).serialize();
      // if ($("input#id_quantity").val() > 0) {
        $.ajax({
          method: "POST",
          url: $(form).attr('action'),
          data: data,
          success: function(data) {
            if (data.error == true) {
              console.log(data.error_message);
            } else {
              $(button).addClass("added");
              $(button).text('Добавлено');

              $('.cart-draw').html(data);
              $('.cart-btn>span').hide();
              $('.cart-btn>span').fadeIn(300);
            }
          },
          error: function(data) {
            console.log('error-level-2');
          }
        });
      // }
    }
  });
});
