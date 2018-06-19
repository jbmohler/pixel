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

	var obj = jQuery.parseJSON(rect);

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
							set_data(JSON.stringify(data));
						}
	});
}

function auto_update() {
	if ( $('#auto_update').is(":checked") ) {
		update_full_image();
	}
}

$(document).ready(function() {
	setInterval(auto_update, 1000);
});
