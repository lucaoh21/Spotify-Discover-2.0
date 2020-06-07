$(document).ready(function() {

	// Updates slider value when user moves slider
	const $valIT = $('#sliderITValue');
	const $slideIT = $('#sliderIT');
	$valIT.html($slideIT.val());
	$slideIT.on('input change', () => {
		$valIT.html($slideIT.val());
	});

	// Updates slider value when user moves slider
	const $valTL = $('#sliderTLValue');
	const $slideTL = $('#sliderTL');
	$valTL.html($slideTL.val());
	$slideTL.on('input change', () => {
		$valTL.html($slideTL.val());
	});

	var time;
	var length;
	var time_counter;
	var length_counter;
	var time_interval;
	var length_interval;
	var spotify_error = false;
	var is_active = false;

	// The timer for one interval
	function timeInterval () {
		time_interval = setInterval(function() {

			// When an interval is over, skip to next track
			if (time_counter <= 0) {
				$.ajax({
			        url: '/playback/skip',
			        type: 'GET', 
			        success: function(data) {
			        	// Show the album cover and name of current song
			            $('#currentName').html(data['name']);
	        			$('.clock').css('background-image', 'url(' + data['img'] + ')');
			        },
			        statusCode: {
		            	403: function () { 	
		                	alert("You must have a Premium Spotify account to use this feature.")
		                	clearInterval(time_interval);
							clearInterval(length_interval);
		                },
		                404: function () { 	
		                	alert("No devices were found. Head to the Spotify app and start playback to create an active device to use this feature.")
		                	clearInterval(time_interval);
							clearInterval(length_interval);
		                }
		            }                 
			    });
			    time_counter = time;
				$('#secCount').css('color', '#ffffff');
				$('#minCount').css('color', '#ffffff');
			}

			time_counter = time_counter - 1;
		    
		    // Update the countdown timer shown to user
			var minutes = Math.floor(time_counter / 60);
			var seconds = Math.floor(time_counter % 60);
			document.getElementById("minCount").innerHTML = minutes;
			document.getElementById("secCount").innerHTML = seconds;

			// Alert user if time is almost out by making countdown red
			if (time_counter == 5) {
				$('#secCount').css('color', '#ff0000');
				$('#minCount').css('color', '#ff0000');
			}

		}, 1000);
	};

	// The timer for the total length
	function lengthInterval() {
		length_interval = setInterval(function() {
			length_counter = length_counter - 1;
		    
		    // Update the countdown timer shown to user
			var hours = Math.floor(length_counter / 3600);
			var minutes = Math.floor(length_counter % 3600 / 60);
			var seconds = Math.floor(length_counter % 60);
			document.getElementById("totalHourCount").innerHTML = hours;
			document.getElementById("totalMinCount").innerHTML = minutes;
			document.getElementById("totalSecCount").innerHTML = seconds;

			// If countdown gets below 0, then stop both the interval and length intervals
			if (length_counter <= 0) {
				document.getElementById("minCount").innerHTML = 0;
				document.getElementById("secCount").innerHTML = 0;
				clearInterval(time_interval);
				clearInterval(length_interval);
			}
		}, 1000);
	};

	// AJAX call to start playback
	function startPlayback() {
		$.ajax({
	        url: '/timer/start',
	        type: 'POST',
	        data: $('#intervalTimer').serialize(),          
	        success: function(data) {
	        	// Show the album cover and name of current song
	        	$('#currentName').html(data['name']);
	        	$('.clock').css('background-image', 'url(' + data['img'] + ')');
	        	spotify_error = false;
	        },
	        statusCode: {
            	403: function () { 	
                	alert("You must have a Premium Spotify account to use this feature.")
                	spotify_error = true;
                	if (typeof time_interval !== 'undefined') {
						clearInterval(time_interval);
						clearInterval(length_interval);
					}
                },
                404: function () { 	
                	alert("No devices were found. Head to the Spotify app and start playback to create an active device to use this feature.")
                	spotify_error = true;
                	if (typeof time_interval !== 'undefined') {
						clearInterval(time_interval);
						clearInterval(length_interval);
					}
                }
            }           
	    });
	};

	// AJAX call to pause playback
	function pausePlayback() {
		$.ajax({
	        url: '/playback/pause',
	        type: 'GET',            
  			success: function(msg) {
  				spotify_error = false;
	        },
	        statusCode: {
            	403: function () { 	
                	alert("You must have a Premium Spotify account to use this feature.")
                	spotify_error = true;
                },
                404: function () { 	
                	alert("No devices were found. Head to the Spotify app and start playback to create an active device to use this feature.")
                	spotify_error = true;
                }
            }            
	    });
	};

	// AJAX call to resume playback
	function resumePlayback() {
		$.ajax({
	        url: '/playback/resume',
	        type: 'GET',            
  			success: function(data) {
  				// Show the album cover and name of current song
	        	$('#currentName').html(data['name']);
	        	$('.clock').css('background-image', 'url(' + data['img'] + ')');
	        	spotify_error = false;
	        },
	        statusCode: {
            	403: function () { 	
                	alert("You must have a Premium Spotify account to use this feature.")
                	spotify_error = true;
                },
                404: function () { 	
                	alert("No devices were found. Head to the Spotify app and start playback to create an active device to use this feature.")
                	spotify_error = true;
                }
            }    
	    });
	};

	
	// Activated when user starts the interval timer
	$('#startBtn').click(function() {
		// If timer was previously started, reset it
		if (typeof time_interval !== 'undefined') {
			clearInterval(time_interval);
			clearInterval(length_interval);
		}

		// Get user specified interval and lenght times
		time = document.getElementById("sliderITValue").innerHTML;
		time_counter = time;
		length = document.getElementById("sliderTLValue").innerHTML * 60; //html is in minutes
		length_counter = length;

		startPlayback()
		if (!spotify_error) {
			is_active = true;
			timeInterval();
			lengthInterval();
		}
	});

	// Activated when user restarts the interval timer
	$('#restartBtn').click(function() {
		// If timer was previously started, reset it
		if (typeof time_interval !== 'undefined') {
			clearInterval(time_interval);
			clearInterval(length_interval);

			startPlayback()
			if (!spotify_error) {
				is_active = true;
				time_counter = time;
				length_counter = length;

				timeInterval();
				lengthInterval();
			}
		}
	});


	// Activated when user pauses the interval timer
	$('#pauseBtn').click(function() {
		// Only pause if interval timer is actually active
		if (typeof time_interval !== 'undefined' && is_active == true) {
			is_active = false;
			clearInterval(time_interval);
			clearInterval(length_interval);
			pausePlayback();
		}
	});

	// Activated when user resumes the interval timer
	$('#resumeBtn').click(function() {
		// Only pause if interval timer is not active
		if (typeof time_interval !== 'undefined' && is_active == false) {
			is_active = true;
			resumePlayback()
			if (!spotify_error) {
				timeInterval();
				lengthInterval();
			}
		}
	});

});