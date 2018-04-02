$(document).ready(function() {
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

    function make_selectors(data) {
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
            html += render_select(val, i);
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

    function render_select(array, index) {
        var html = '';
        html += '<div class="form-group"> \
        <select class="required form-control" id="select' + (index + 1) + '" name="select' + (index + 1) + '">\n'
        $.each(array, function(i, val) {
            var val_id = "val_" + val[2];
            var chained = "val_" + val[0];
            html += '<option value=' + val_id + ' data-chained=' + chained + '>';
            html += val[1];
            html += '</option>\n';
        });
        html += '</select></div>';
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

    function init_events() {
        $(".widget_type__datagroupselect .form-group select").on('click', function() {
            //append custom selected options to main select form
            var selected_options = $(".widget_type__datagroupselect .form-group select option:selected").map(function() {
                return this.value.split('_')[1];
            }).get()
            $("#id_categories").val(selected_options);
            make_selector_visible($(this), 350);
        });
        //make visible selected
        var selected_options = $("#id_categories option:selected").map(function() {
            return this.text;
        }).get()
        $.each(selected_options, function(i, val) {
            var opt_name = val.split(" / ");
            var leveles = opt_name.length - 1;
            var value = $('#select' + leveles + ' option').filter(function() { return $(this).html() == opt_name[leveles]; }).val();
            $('#select' + leveles).val(value);
            $('#select' + leveles).trigger("change");
            make_selector_visible($('#select' + leveles));
        })

    }


    $.ajax({
        type: "POST",
        url: '/init/ajax/get_categories/',
        dataType: 'json',
        success: function(data) {
            make_selectors(data);
            init_events();

        }
    });

});