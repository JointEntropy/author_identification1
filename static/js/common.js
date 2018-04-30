$('.edit-img, .edit-span').hover(function () {
    $(this).closest('.field').addClass('highlight');
},
    function () {
    $(this).closest('.field').removeClass('highlight');
    }
);

$('.edit-img, .edit-span').click(function (t) {
    // получаем общее поле
    var field =$(this).closest(".field");
    var form = field.closest('.form');

    // получаем  элемент для редактируемых данных и копируем его
    var edit_form = field.find('.edit');
    var copy = edit_form.clone();

    // меняем элемент редаиктируемых данных на форму.
    var input = $("<input>", { val: $(this).text(), type: "text" });
    if (copy.is('img'))
        input.val(edit_form.attr('src'));
    else
        input.val(edit_form.text());
    edit_form.replaceWith(input);
    input.select();

    // вешаем слушатель на подтверждение ввода для формы.
    input.keypress(function(event) {
        if (event.keyCode == 13 || event.which == 13) {
            event.preventDefault();
            if (copy.is('img'))
                copy.attr('src', input.val());
            else
                copy.html(input.val());
            input.replaceWith(copy);
            // отправляем на сервер
            submit_field(form.attr('name'), form.attr('id'), field.attr('name'), input.val());
        }
    });
});
$(".field").hover(function (e) {
    $(this).find(".edit-span").attr('style', 'display:inline');

},function (e) {
    $(this).find(".edit-span").attr('style', 'display;none');
});




function get_author(id, callback){
    $.ajax({
        type: "GET",
        url: "/author/"+id,
    }).error(function (xhr, error_mess) {
        console.log('Произошла ошибка');
        console.log(xhr.responseText);
    }).done(function(data) {
        callback(data);
    });
}


function submit_field(entity_name, idx, field, value) {
    $.post(
        "/edit_field/"+entity_name+ "/"+idx,
        {
            'field': field,
            'value': value
        },
        function() {
            console.log('Post sended!');
            alert('Успешно изменено!');
        }
    );

}

function  delete_instance(entity_name, idx, callback)
{
    $.post(
        "/delete",
        {
            'entity_name': entity_name,
            'id': idx
        },
        function() {
            console.log('deleted!');
            alert('Запись удалена!');
            callback();
        }
    );
}