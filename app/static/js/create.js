$(document).ready(function() {
    $(function () {
      $('[data-toggle="tooltip"]').tooltip()
    })

    function createPlaylist() {
        $.ajax({
            url: '/create/playlist',
            type: 'POST',
            data: payload,          
            success: function(data) {
                window.location.href= data;
            }           
        });
    };

    $('#createBtn').click(function() {
        payload = $('#playlistForm').serialize();

        var counter = 0;
        $('.selected-search').each(function() {
            payload += '&' + counter.toString() + '=' + $(this).attr('data-id');
            counter += 1;
        });

        if (counter == 0) {
            alert('A minimum of one track or artist must be entered to create the playlist.');
        } else {
            createPlaylist(payload);
        }

    });

    $(function() {
        $("#autocomplete").autocomplete({
            source:function(request, response) {
                $.getJSON('/autocomplete',{
                    q: request.term,
                }, function(data) {
                    // response([{label: "Rain On Me (with Ariana Grande) - Lady Gaga, Ariana Grande", value: "here"}])
                    response(data.matching_results); // matching_results from jsonify
                });
            },
            minLength: 2,
            select: function(event, ui) {
                // event.preventDefault();
                $(this).val(''); 
                createSelected(ui.item.label, ui.item.value);
                return false;
            }
        });
    })

    $('input.form-check-input').change(function(){
        if ($(this).is(':checked')) {
            $(this).parent().next().find('.slider-range').prop('disabled', false);
        }
        else {
            $(this).parent().next().find('.slider-range').prop('disabled', true);
        }
    }).change();


    const $acousticVal = $('#sliderAcousticValue');
    const $acousticRange = $('#sliderAcousticRange');
    $acousticVal.html($acousticRange.val());
    $acousticRange.on('input change', () => {
        $acousticVal.html($acousticRange.val());
    });

    const $danceabilityVal = $('#sliderDanceabilityValue');
    const $danceabilityRange = $('#sliderDanceabilityRange');
    $danceabilityVal.html($danceabilityRange.val());
    $danceabilityRange.on('input change', () => {
        $danceabilityVal.html($danceabilityRange.val());
    });

    const $energyVal = $('#sliderEnergyValue');
    const $energyRange = $('#sliderEnergyRange');
    $energyVal.html($energyRange.val());
    $energyRange.on('input change', () => {
        $energyVal.html($energyRange.val());
    });

    const $popularityVal = $('#sliderPopularityValue');
    const $popularityRange = $('#sliderPopularityRange');
    $popularityVal.html($popularityRange.val());
    $popularityRange.on('input change', () => {
        $popularityVal.html($popularityRange.val());
    });

    const $valenceVal = $('#sliderValenceValue');
    const $valenceRange = $('#sliderValenceRange');
    $valenceVal.html($valenceRange.val());
    $valenceRange.on('input change', () => {
        $valenceVal.html($valenceRange.val());
    });

    function createSelected (label, value) {
        $('#selectedItems').append('<a class="list-group-item"><span class="float-left selected-search" data-id="' + value + '">' + label + '</span><span class="float-right"><span class="btn btn-xs btn-default" onclick="removeSelected(this);"><i class="far fa-times-circle"></i></span></span></a>');
    };

    removeSelected = function(span) {
        span.parentNode.parentNode.remove();
    };

    
});