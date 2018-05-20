$(function() {
  $("a.cart-remove").on('click touch', function(e) {
    e.preventDefault();
    var checkbox = $(this).next().next();
    $(checkbox).prop('checked', true);
    var row = $(this).parent().parent();
    $(row).hide('200');

    var table = $(row).closest('.table');
    var all_table_is_hidden = true;
    setTimeout(function() { //calls click event after a certain time
      if ($(table).children(':visible').length == 1) {
         $("#cart-form").submit();
      }
    }, 500);

  });

});
