/**
 * Created by Labrin
 */
$(function () {

    // Datepicker
    if ($('.datepicker').length) {

        $('.datepicker').each(function () {
            var datePicker = $(this),
                calendarIcon = datePicker.parent().find('.pico-calendar');

            datePicker.datepicker({
                dateFormat: 'yy-mm-dd',
                minDate: 0
            });

            calendarIcon.on('click', function () {

                datePicker.focus();

            });
        });


        if ($('#id_departure_date').length) { // return date can not be before departure date
            $('#id_departure_date').on('change', function (e) {
                var ths = $(this);
                $('#id_return_date').datepicker('option', 'minDate', ths.val()).val('');
            });
        }
    }

    $('.birthpicker').datepicker({
        dateFormat: 'yy-mm-dd',
        changeYear: true,
        changeMonth: true,
        yearRange: "1930:c"
    });

    if ($('#id_type').length) {
        $('input[name=type]').on('change', function (e) {
            var ths = $(this);
            console.log(ths.val());
            if (ths.val() === '1') {
                $('#return_date').addClass('hide');
            } else {
                $('#return_date').removeClass('hide');
            }

        });
    }

    // Nav content box
    if ($('.nav-content-box').length) {

        $('.nav-content-box').each(function () {
            var navContentBody = $(this),
                navTr = navContentBody.find('.table tbody tr'),
                radios = navTr.find('input[type="radio"]');

            navTr.on('click', function (e) {

                navTr.find('>td').removeClass('bg-success');
                $(this).find('>td').addClass('bg-success');
                radios.removeAttr('checked');
                $(this).find('input[type="radio"]').prop('checked', true);
            });
        });
    }


    // Booking choose box
    if ($('.booking-choose-list').length) {
        var bookingChooseList = $('.booking-choose-list'),
            radioInputs = bookingChooseList.find('input[name="navs"]'),
            returnInput = $('#return');

        radioInputs.on('change', function (e) {

            if ($(this).val() == 'return') {
                returnInput.removeAttr('disabled');
            }
            else if ($(this).val() == 'oneWay') {
                returnInput.attr('disabled', 'disabled');
            }
        });
    }

    // Choosen select dev
    if ($('.chosen-select').length) {

        $('.chosen-select').each(function () {
            var chosenSelect = $(this);

            chosenSelect.chosen();
        });
    }

    // From to change
    if ($('#id_dir_from').length) {
        var movement_class = $('.movement_class');

        movement_class.on('change', function () {
            var changed_obj = $(this);

            movement_class.each(function () {

                if (!changed_obj.is($(this))) {
                    chosenSelectFn(changed_obj, $(this));
                }
            });
        });
    }

    // Calculate TIR
    if ($('.select-cargo-count').length) {
        var select_cargo_count = $('.select-cargo-count');

        select_cargo_count.on('change', function () {
            var changed_obj = $(this);

            calculateSelectTir(changed_obj, select_cargo_count, CARGO_LIMIT);

            select_cargo_count.find('option[value="0"]').removeAttr('disabled');
        });
    }

    // Select to plaintext
    if ($('.select-plain').length) {
        $('.select-plain').each(function (idx, elm) {
            var plaintext = $('<div class="form-control nb">{data}</div>'.replace('{data}', $(elm).find(":selected").text()));

            $(elm).after(plaintext);
//            console.log(elm);
        });
    }

    // get passanger spots
    if ($('#passenger_spots').length) {
        var $pas_spot = $('#passenger_spots'),
            trns_spot = $pas_spot.data('spot');

        $.get(CALC_PRICE_URL, function (data) {
            var spots = data.passenger_spots,
                away_spots = spots.away,
                trns_spot = $pas_spot.data('spot'),
                away_list = createLi(away_spots, $pas_spot.data('away'), trns_spot);

            $pas_spot.html(away_list.join(' '));

            console.log(spots);

            // away spots
            if (spots.hasOwnProperty("return")) {
                var return_spots = spots.return,
                    return_list = createLi(return_spots, $pas_spot.data('back'), trns_spot);
                $pas_spot.append(return_list.join(' '));
            }


        });
    }
    function createLi(arr, trns_title, trns_spot) {
        var list = ['<li class="title">' + trns_title + '</li>'];

        for (var i = 0, j = arr.length; i < j; i++) {

            var li = '<li class="small">' +
                arr[i].obj.fields.name + ': <em>' +
                arr[i].spot + ' ' + trns_spot +
                '</em></li>';

            list.push(li);
        }
        return list;
    }

    if ($('#passenger_forms').length) {
        $('#passenger_forms input[type=radio]').on('change', function (e) {
            getBookingPrices();
        });
        if ($('#passenger_forms input[type=radio]').is(':checked')) {
            getBookingPrices();
        }
    }

    function getBookingPrices() {
        var form = $('#booking-step-3');
        $.get(CALC_PRICE_URL, form.serialize(), function (data) {
            var prices = data.prices;

            console.log(prices);

            // passenger
            $('#price-passenger-away').text(prices.passenger.away);
            $('#price-passenger-back').text(prices.passenger.back);

            // transit
            if (prices.transit_fee) {
                $('#price-transit').text(prices.transit_fee.total + ' usd (+' + $('#price-transit').data('percentage') + '%)');
            }


            // total
            $('#price-total').text(prices.grand_total);
            $('.total-price').removeClass('hide');
        });
    }

    if ($('#price-block').length) {
        var price_block = $('#price-block');
        price_block.stick_in_parent({
            parent: $('.nav-content-side')
        });
    }


    // Google map dev
    if ($('#map-canvas').length) {

        initialize();
        google.maps.event.addDomListener(window, 'load', initialize);

    }


    // For map initialize
    function initialize() {
        var myLatlng = new google.maps.LatLng(41.5009623, 51.1853849, 14);
        var mapOptions = {
            zoom: 5,
            center: myLatlng,
            disableDefaultUI: true
        };
        var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
    }

    // chosen select checker
    function chosenSelectFn(this_obj, sibling_obj) {

        sibling_obj.find('option').removeAttr('disabled');

        if (!this_obj) {

            this_obj.find('option[value="' + sibling_obj.val() + '"]').attr('disabled', 'disabled');
        }
        else {

            sibling_obj.find('option[value="' + this_obj.val() + '"]').attr('disabled', 'disabled');
        }

        sibling_obj.find('option[value=""]').removeAttr('disabled');
        sibling_obj.trigger("chosen:updated");

    }

    // calc select
    function calculateSelectTir(this_obj, all_selects, result_number) {

        all_selects.find('option').attr('disabled', 'disabled');

        var calcResult = 0;

        // Each for calculate all selects value
        all_selects.each(function (idx, elm) {

            calcResult += parseFloat(elm.value);
        });

        // Each for calculate
        all_selects.each(function (idx, elm) {

            calc_remote_elms($(elm), all_selects, result_number);

        });

        // Check if only one select changed
        if (calcResult === parseFloat(this_obj[0].value)) {

            this_obj.find('option').removeAttr('disabled');

        }

    }

    // calculate remote elms
    function calc_remote_elms(remote_this, all_selects, result_number) {

        var detail_count = 0;

        for (var i = 0, iLen = all_selects.length; i < iLen; i++) {

            if (!remote_this.is($(all_selects[i])))
                detail_count += parseFloat(all_selects[i].value);

        }

        remote_this.find('option').each(function (index, elm) {

            if (elm.value <= (result_number - detail_count))
                $(elm).removeAttr('disabled', 'disabled');

        });

    }


});