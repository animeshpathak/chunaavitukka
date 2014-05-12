/* base.js */
$( function() {
	$.ajax({
		url: "/t/",
		data: { contest_slug: 'slug', candidate_id: 'cid' }
	}).done( function(data) {
		console.log (data);
		if (data.indexOf("200") > 1) {
			//success, show alert
			console.log('successfully updated');
		} else {
			// {'message': message }

			var obj = JSON && JSON.parse(data) || $.parseJSON(data);
			console.log(obj.message);
		}
	});
});