/* base.js */
$( function() {

	$(".vote").click( function() {
		
		// console.log('{ contest_slug:' + $("#contest_slug").val() + ', candidate_id:' + $(this).attr('data-candidate-id') + '}')
		$.ajax({
			type: 'POST',
			url: "/t/",
			data: { contest_slug: $("#contest_slug").val(), candidate_id: $(this).attr('data-candidate-id') }
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

});