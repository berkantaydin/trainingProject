$(function () {
    $("[id$='parent_id']").parent().parent().hide();
    $("[id$='parent_type']").parent().parent().hide();
    $(".add_comment").click(function (e) {
        e.preventDefault();
//        console.log($(this).closest("tr").parent().append(""));

        $('.comment_form').modal({
            keyboard: true,
            backdrop: false
        });
    });
    $("#comment_tree").treetable();
});