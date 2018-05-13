(function($) {
  function dfs(node, depth, maxDepth, array) {
    if (depth == maxDepth) {
      array.push([node.parent, node.title, node.id]);
      return
    }
    if (node.children) {
      $.each(node.children, function(i, node) {
        {
          dfs(node, depth + 1, maxDepth, array);
        }
      });
    }
  }

  function make_selectors(data, selected_options) {
    var array = []
    maxDepth = 5;
    for (i = 1; i < maxDepth; i++) {
      var tmp = [];
      dfs(data, 0, i, tmp);
      if (tmp.length != 0) {
        array.push(tmp);
      }
    }
    // var html = '<div class="select-group">';
    $.each(array, function(i, val) {
      var html = '';
      html += render_select(val, i, selected_options);
      // $(".field-categories").before(html);
      $("#id_categories").before(html);
      if (i > 0) {
        $("#select" + (i + 1)).chained("#select" + i);
        // $("#select" + (i + 1)).css('display', 'none');
        make_selector_visible($("#select" + (i + 1)), 0);
      }
    })
    // html += '</div>';
    // $(".select-group").after('</div>');
  }

  function render_select(array, index, selected_options) {
    var html = '';
    html += '<div class="form-group margin-bottom-15"> \
        <select class="form-control" id="select' + (index + 1) + '" name="select' + (index + 1) + '"';
    var options = '';
    var show = false;
    $.each(array, function(i, val) {
      var val_id = "val_" + val[2];
      var chained = "val_" + val[0];
      var selected = "";
      if ($.inArray(val[2], selected_options) != '-1') {
        selected = 'selected="selected"';
        show = true;
      }
      options += '<option value=' + val_id + ' data-chained=' + chained  + ' ' + selected + '>';
      options += val[1];
      options += '</option>\n';
    });
    if (index > 0 && !show) {
      html += ' style="display: none"';
    }
    html += '>\n';
    html += options;
    html += '</select><span class="highlight"></span><span class="bar"></span></div>';
    return html;
  }

  function is_empty(element) {
    if (($(element).val()) != null) {
      return false
    } else {
      return true
    }
  }

  function make_selector_visible(select, animation) {
    var next = $(select).closest('div').nextAll('div').find('select');
    $.each(next, function(i, val) {
      if (is_empty(val) == true) {
        $(val).hide(animation);
      } else {
        $(val).show(animation);
      }
    })
  }

  function get_selected_values() {
    var selected_options = $(".form-group select option:selected").map(function() {
      return this.value.split('_')[1];
    }).get()
    selected_options.push('1');
    return selected_options;
  }

  function init_events() {
    $(".form-group select").on('click', function() {
      //append custom selected options to main select form
      var selected_options = get_selected_values();
      $("#id_categories").val(selected_options);
      make_selector_visible($(this), 250);
    }).trigger('click');
  }

  $.fn.get_categories = function(url) {
    $.ajax({
      type: "POST",
      url: url,
      dataType: 'json',
      success: function(data) {
        var selected_options = $('.datagroupselect option:selected').map(function() {
          return parseInt(this.value)
        }).get()
        make_selectors(data, selected_options);
        init_events();
      }
    });
  }
}(jQuery));
