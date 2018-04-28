$('.edit, .edit-span').click(function (t) {
        var field_name = this.id;
        alert(field_name);
    });
    $(".field").hover(function (e) {
        $(this).find(".edit-span").attr('style', 'display:inline');
    },function (e) {
        $(this).find(".edit-span").attr('style', 'display;none');
});

