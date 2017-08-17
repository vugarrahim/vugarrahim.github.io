/**
 * Created by Labrin on 12/17/15.
 */
(function ($) {

    var vesselSelect;

//    $('#id_vessel').change(function () {
//        alert('works');
//    });

    window.onload = load;

    function load() {
        vesselSelect = document.getElementById('id_vessel');

        var path = window.location.pathname.split('/'),
            id = path[path.length - 2],
            url = '/booking/admin-help/';

        vesselSelect.onchange = function () {

            $.ajax({
                url: url,
                data: {
                    "booking": id,
                    "vessel": $('#id_vessel').val(),
                },
                cache: false,
                type: "GET",
                success: function (response) {
                    console.log(response);
                    $('#id_price').val(response.total);
                },
                error: function (xhr) {

                }
            });

            console.log(id, $('#id_vessel').val());
        };
    }


})(django.jQuery);
