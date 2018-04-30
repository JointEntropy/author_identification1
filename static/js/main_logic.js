
$("#load_btn").click(function(e) {

    var file = document.getElementById("inputfile").files[0];
    var reader = new FileReader();
    reader.onload = function (e) {
        var textArea = document.getElementById("textar");
        textArea.value = e.target.result;
    };
    reader.readAsText(file);
});

$("#analyze_form").on( "submit", function( event ) {
    event.preventDefault();
    //var request_data = $('#textar').val();
    var request_data =  JSON.stringify({"text": $('#textar').val()});
    $("#predict_box").hide();
    $.ajax({
        type: "POST",
        url: "/submit",
        data: request_data,
       contentType:"application/json; charset=utf-8",
       dataType:"json",
    }).error(function (xhr, error_mess) {
        console.log('Произошла ошибка');
        alert('Ошибка ввода');
        console.log(xhr.responseText);
    }).done(function(data) {
        var c = data;
        $.each(data, function (i, item) {
            $.ajax({
                type: "GET",
                url: "/author/"+c[i]['id'],
            }).error(function (xhr, error_mess) {
                console.log(xhr.responseText);
            }).done(function(inner_data) {
                    var prefix = "#a"+(i+1);
                    $(prefix+"_text").html(inner_data["name"]);
                    $(prefix+"_prob").html(item['prob']);
                    var img_url = inner_data['img_url'];
                    if ( img_url == null)
                        img_url = "{{ url_for('static',filename='img/author_placeholder.jpg') }}";
                    $(prefix+"_img").attr("src", img_url);

            });
        });
        $("#predict_box").css({
            opacity: 0,
            display: 'inline-block'
        }).animate({opacity:1},2000);
    });
});

$("#add_comp_btn").click(function(e) {
    var request_data =  JSON.stringify({"text": $('#textar').val(),
                                        "title": $('#title_input').val(),
                                        "author_name": $("#author_input").val()});
    $.ajax({
        type: "POST",
        url: "/add_comp",
        data: request_data,
       contentType:"application/json; charset=utf-8",
       dataType:"json"
    }).error(function (xhr, error_mess) {
        console.log('Произошла ошибка');
        alert('Ошибка ввода');
        console.log(xhr.responseText);
    }).done(function(data) {
        alert('Успешно!');
    });
});




