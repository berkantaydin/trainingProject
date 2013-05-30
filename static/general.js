$(function () {
    $("[id$='parent_id']").parent().parent().hide();
    $("[id$='parent_type']").parent().parent().hide();
    $(".add_comment").click(function (e) {
        e.preventDefault();

        $("[id$='parent_id']").val($(this).attr('relid'));
        $("[id$='parent_type']  > option").removeAttr("selected");
        $("[id$='parent_type']  > option:contains('" + $(this).attr('reltype') + "')").attr('selected', 'selected');
        console.log($(this).attr('reltype'));
        $('.comment_form').modal({
            keyboard: true,
            backdrop: false
        });
    });

    $(".close").click(function (e) {
        e.preventDefault();

        $('.comment_form').modal("hide");
    });

    $("#comment_tree").treetable();
});