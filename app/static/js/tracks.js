$(document).ready(function() {

	function createPlaylist() {
		$.ajax({
	        url: '/createTopPlaylist',
	        type: 'POST',
	        data: $('#playlistForm').serialize(),          
	        success: function(data) {

	        }           
	    });
	};

	$('#createBtn').click(function() {
		console.log("here");
		createPlaylist();
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