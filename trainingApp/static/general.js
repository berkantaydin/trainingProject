$(function () {

    $("a.comment_add").click(function (e) {
        e.preventDefault();
        //Every comment area hide!
        $('div.comment_form').hide();
        //Show me lucky one ;)
        $(this).parent().next().next().show();
    });
});