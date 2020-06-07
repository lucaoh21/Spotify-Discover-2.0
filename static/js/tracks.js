$(document).ready(function() {
	
	// AJAX call to create a playlist
	function createPlaylist() {
		$.ajax({
	        url: '/tracks/topplaylist',
	        type: 'POST',
	        data: $('#playlistForm').serialize(),          
	        success: function(data) {
	        	// redirect user to Spotify application
	        	window.location.href= data;
	        }           
	    });
	};

	// User attempts to create a new playlist
	$('#createBtn').click(function() {

		// At least one time frame must be selected
		if ($('#shortTerm:checked').val() || $('#mediumTerm:checked').val() || $('#longTerm:checked').val()) {
			createPlaylist();
		} else {
			alert('A minimum of one playlist type must be selected.');
		}

	});

	// Whether or not to show Playlist Name fields depends on whether user is attempting
	// to create a playlist for that time frame
	$('input.form-check-input').change(function(){
		if ($(this).is(':checked')) {
	    	$(this).parent().next().find('div.form-text').show();
		}
		else {
	    	$(this).parent().next().find('div.form-text').hide();
		}
	
	}).change();

});