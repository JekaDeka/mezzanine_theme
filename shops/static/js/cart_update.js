$(function() {
  $("td.delete>a.cart-remove").on("click", function() {
    var checkbox = $(this).next();
    $(checkbox).prop('checked', true);
    var row = $(this).closest('tr');
    // console.log(row);
    $(row).hide('200');
    // $('.cart-form').submit();
  });
});
