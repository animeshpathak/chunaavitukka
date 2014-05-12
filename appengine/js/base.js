/* base.js */
$( function() {

	$(".login").click( function() {
		window.location = $("#login_path").attr('href');
	});
	$(".vote").click( function() {
		
		// console.log('{ contest_slug:' + $("#contest_slug").val() + ', candidate_id:' + $(this).attr('data-candidate-id') + '}')
		$.ajax({
			type: 'POST',
			url: "/t/",
			data: { contest_slug: $("#contest_slug").val(), candidate_id: $(this).attr('data-candidate-id') },
			beforeSend: function() {
				$.mobile.loading('show');
			}

		}).done( function(data) {
			console.log ('done ' +data);
			$.mobile.loading('hide');
			$(this).parent().html("Voted!");
			$(".vote").removeClass("vote").parent().html("Done");

			console.log('updated');
			// $("#myPopup1-popup").html("Registered!").show().delay(1500).fadeOut('slow');

		}).complete( function(data) {
			console.log( 'complete ' + data);

			// var obj = JSON && JSON.parse(data) || $.parseJSON(data);
			// $(this).parent().html("Voted!");
			// $(".vote").removeClass("vote").parent().html("Done");

			if (is_JSON(data)) {
				// {'message': message }
				console.log ('jsonn');

				// $("#myPopup1-popup").html("Unsuccess").show().delay(1500).fadeOut('slow');
				var obj = JSON && JSON.parse(data) || $.parseJSON(data);
				console.log(obj.message);
			}
			console.log('whatever');
			$.mobile.loading('hide');
		});
	});

});

function is_JSON(str) {
    try {
        var c = $.parseJSON(str);
    } catch (e) {
        return false;
    }
    return true;
}