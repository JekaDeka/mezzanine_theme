$(document).ready(function() {
  $('.tmp').on('submit', function(event) {
    event.preventDefault();
    var form = $(this);
    $.ajax({
      method: "POST",
      url: $(form).attr('action'),
      data: $(form).serialize(),
      beforeSend: function() {
        $('.cart-btn').hide();
        $('.loader').show();
      },
      success: function(data) {
        if (data.error == true) {
          $('.cart-btn').show();
          $('.loader').hide();
        } else {
          $('.loader').hide();
          $('.cart-draw').html(data);
        }
      },
      error: function(data) {
        $('.cart-btn').show();
        $('.loader').hide();
      }
    });
  });
});
