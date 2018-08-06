// Convert a hex string to a byte array
function hexToBytes(hex) {
	var bytes = [];
	for (var c = 0; c < hex.length; c += 2)
		bytes.push(parseInt(hex.substr(c, 2), 16));
	return bytes;
}

function set_data(rect){
	var canvas = document.getElementById("myCanvas");
	var ctx = canvas.getContext("2d");

	var obj = rect;

	var bytes = hexToBytes(obj.imdata);

	var imageData = new ImageData(obj.width, obj.height);//ctx.getImageData(obj.x, obj.y, obj.width, obj.height);
	for (var c = 0; c < bytes.length; c+= 1) {
		imageData.data[c] = bytes[c];
	}
	ctx.putImageData(imageData, obj.x, obj.y);      
}

function update_full_image() {
	var canvas = document.getElementById("myCanvas");
	$.ajax({
			type: "GET",
			url: "api/rectangle-binary",
			data: "x=0&y=0&height="+canvas.height+"&width="+canvas.width,
			error: function(xhr, ajaxOptions, thrownError) {
							$('#info').html('<p>An error has occurred</p>');
						},
			success: function(data) {
							$('#info').html('');
							// window.last = data.histnode;
							set_data(data);
						}
	});
}

function update_incremental(changes) {
	var canvas = document.getElementById("myCanvas");
	$.ajax({
			type: "GET",
			url: "api/rectangle-binary",
			data: "x="+changes.x+"&y="+changes.y+"&height="+changes.height+"&width="+changes.width,
			error: function(xhr, ajaxOptions, thrownError) {
							$('#info').html('<p>An error has occurred</p>');
						},
			success: function(data) {
							$('#info').html('');
							set_data(data);
							read_updates();
						}
	});
}

function read_updates() {
	$.ajax({
			type: "GET",
			url: "api/change-poll",
			data: "last="+window.last,
			error: function(xhr, ajaxOptions, thrownError) {
							//$('#info').html('<p>An error has occurred</p>');
						},
			success: function(data) {
							//$('#info').html('');
							if (data.x === undefined) {
								$('#info').html('no update')
							}else{
								window.last = data.histnode;
								set_data(data);
							}
							read_updates();
						}
	});
}

function auto_update() {
	if ( $('#auto_update').is(":checked") ) {
		update_full_image();
	}
}

function canvas_click(event) {
	var canvas = document.getElementById("myCanvas");
	var elemLeft = canvas.offsetLeft,
			elemTop = canvas.offsetTop;	
	var x = event.pageX - elemLeft,
			y = event.pageY - elemTop;
	$.ajax({
			type: "PUT",
			url: "api/pixel",
			data: "x="+x+"&y="+y,
			success: function(data) {
							$('#info').html('clicked');
						}
	});
}

function canvas_move(event) {
	var canvas = document.getElementById("myCanvas");
	var elemLeft = canvas.offsetLeft,
			elemTop = canvas.offsetTop;	
	var x = event.pageX - elemLeft,
			y = event.pageY - elemTop;
	if( event.buttons == 1 ) {
		$.ajax({
				type: "PUT",
				url: "api/ellipse",
				data: "xcenter="+x+"&ycenter="+y+"&xradius=2&yradius=2",
				success: function(data) {
								$('#info').html('clicked');
							}
		});
	}
}

$(document).ready(function() {
	//setInterval(auto_update, 1000);
	window.last = 0;
	update_full_image();
	read_updates();

	var canvas = document.getElementById("myCanvas");
	canvas.addEventListener('click', canvas_click, false);
	canvas.addEventListener('mousemove', canvas_move, false);
});
