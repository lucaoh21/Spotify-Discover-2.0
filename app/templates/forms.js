
$(document).ready(function() {

	$("#intervalTime").slider();
	$("#intervalTime").on("slide", function(slideEvt) {
	  $("#intervalTimeSliderVal").text(slideEvt.value);
	});

});