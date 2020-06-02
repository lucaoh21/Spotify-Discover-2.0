$(document).ready(function() {

	const $valIT = $('#sliderITValue');
	const $slideIT = $('#sliderIT');
	$valIT.html($slideIT.val());
	$slideIT.on('input change', () => {
		$valIT.html($slideIT.val());
	});

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

	function timeInterval () {
		time_interval = setInterval(function() {

			if (time_counter <= 0) {
				$.ajax({
			        url: '/playback/skip',
			        type: 'GET',
			        // success: function(msg) {
			        //     console.log("success");
			        // }    
			        success: function(data) {
			            $('#currentName').html(data['name']);
	        			$('.clock').css('background-image', 'url(' + data['img'] + ')');
			        }              
			    });
			    time_counter = time;
				$('#secCount').css('color', '#ffffff');
				$('#minCount').css('color', '#ffffff');
			}

			time_counter = time_counter - 1;
		    
			var minutes = Math.floor(time_counter / 60);
			var seconds = Math.floor(time_counter % 60);

			document.getElementById("minCount").innerHTML = minutes;
			document.getElementById("secCount").innerHTML = seconds;

			if (time_counter == 5) {
				$('#secCount').css('color', '#ff0000');
				$('#minCount').css('color', '#ff0000');
			}

		}, 1000);
	};

	function lengthInterval() {
		length_interval = setInterval(function() {
			length_counter = length_counter - 1;
		    
			var hours = Math.floor(length_counter / 3600);
			var minutes = Math.floor(length_counter % 3600 / 60);
			var seconds = Math.floor(length_counter % 60);

			document.getElementById("totalHourCount").innerHTML = hours;
			document.getElementById("totalMinCount").innerHTML = minutes;
			document.getElementById("totalSecCount").innerHTML = seconds;

			if (length_counter <= 0) {
				document.getElementById("minCount").innerHTML = 0;
				document.getElementById("secCount").innerHTML = 0;
				clearInterval(time_interval);
				clearInterval(length_interval);
			}
		}, 1000);
	};

	function startPlayback() {
		$.ajax({
	        url: '/timer/start',
	        type: 'POST',
	        data: $('#intervalTimer').serialize(),          
	        success: function(data) {
	        	$('#currentName').html(data['name']);
	        	$('.clock').css('background-image', 'url(' + data['img'] + ')');
	        }           
	    });
	};

	function pausePlayback() {
		$.ajax({
	        url: '/playback/pause',
	        type: 'GET',            
  			success: function(msg) {
	        }      
	    });
	};

	function resumePlayback() {
		$.ajax({
	        url: '/playback/resume',
	        type: 'GET',            
  			success: function(data) {
	        	$('#currentName').html(data['name']);
	        	$('.clock').css('background-image', 'url(' + data['img'] + ')');
	        } 
	    });
	};

	

	$('#startBtn').click(function() {
		if (typeof time_interval !== 'undefined') {
			clearInterval(time_interval);
			clearInterval(length_interval);
		}

		time = document.getElementById("sliderITValue").innerHTML;
		time_counter = time;
		length = document.getElementById("sliderTLValue").innerHTML * 60; //html is in minutes
		length_counter = length;

		startPlayback();
		timeInterval();
		lengthInterval();
	});

	$('#restartBtn').click(function() {
		if (typeof time_interval !== 'undefined') {
			clearInterval(time_interval);
			clearInterval(length_interval);

			startPlayback();
			time_counter = time;
			length_counter = length;

			timeInterval();
			lengthInterval();
		}
	});

	$('#pauseBtn').click(function() {
		if (typeof time_interval !== 'undefined') {
			clearInterval(time_interval);
			clearInterval(length_interval);
			pausePlayback();
		}
	});

	$('#resumeBtn').click(function() {
		if (typeof time_interval !== 'undefined') {
			resumePlayback();
			timeInterval();
			lengthInterval();
		}
	});

});