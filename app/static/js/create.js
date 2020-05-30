$(document).ready(function() {

    $(function() {
        $("#autocomplete").autocomplete({
            source:function(request, response) {
                $.getJSON('/autocomplete',{
                    q: request.term, // in flask, "q" will be the argument to look for using request.args
                }, function(data) {
                    response([{label: "Rain On Me (with Ariana Grande) - Lady Gaga, Ariana Grande", value: "here"}])
                    // response(data.matching_results); // matching_results from jsonify
                });
            },
            minLength: 2,
            select: function(event, ui) {
                event.preventDefault();
                console.log(ui.item.label)
                console.log(ui.item.value); // not in your question, but might help later
            }
        });
    })

});