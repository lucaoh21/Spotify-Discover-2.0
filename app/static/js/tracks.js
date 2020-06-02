$(document).ready(function() {

	function createPlaylist() {
		$.ajax({
	        url: '/tracks/topplaylist',
	        type: 'POST',
	        data: $('#playlistForm').serialize(),          
	        success: function(data) {
	        	window.location.href= data;
	        }           
	    });
	};

	$('#createBtn').click(function() {
		if ($('#shortTerm:checked').val() || $('#mediumTerm:checked').val() || $('#longTerm:checked').val()) {
			createPlaylist();
		} else {
			alert('A minimum of one playlist type must be selected.');
		}

	});

	$('input.form-check-input').change(function(){
		if ($(this).is(':checked')) {
	    	$(this).parent().next().find('div.form-text').show();
		}
		else {
	    	$(this).parent().next().find('div.form-text').hide();
		}
	
	}).change();

});