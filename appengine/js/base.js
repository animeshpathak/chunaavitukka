/* base.js */
// updating this based on http://www.gajotres.net/document-onpageinit-vs-document-ready/
// $(document).ready(function() {
$(document).on('pageinit', function() {
	console.log("pageinit! Setting up hooks");
	$(".login").click( function() {
		window.location = $("#login_path").attr('href');
	});
	$(".vote").click( function() {
		var candidate_id = $(this).attr('data-candidate-id');
		// console.log('{ contest_slug:' + $("#contest_slug").val() + ', candidate_id:' + $(this).attr('data-candidate-id') + '}')
		$.ajax({
			type: 'POST',
			url: "/t/",
			data: { contest_slug: $("#contest_slug").val(), candidate_id: candidate_id },
			beforeSend: function() {
				$.mobile.loading('show');
			}

		}).done( function(data) {
			console.log (data);
			//not needed since it will be called in complete() 
			//$.mobile.loading('hide');
			$(this).parent().html("Voted!");
			$(".vote").removeClass("vote").parent().html("Done");
			var value = data['total'];
			//Show the new total
			$("#score_" + candidate_id).html(value);
			

			console.log('updated');
			$("#myPopup1-popup").html("Registered!").show().delay(1500).fadeOut('slow');

		}).complete( function(complete_object) {
			//the complete_object is not a direct map of the JSON
			//need to do a ['responseJSON']
			console.log( 'complete ');
			console.log( complete_object);
			var message = complete_object['responseJSON']['message'];
			console.log("message: " + message);
			if(complete_object.status != 200){
				//something went wrong
				$("#toast").html(message).show().delay(2500).fadeOut('slow');
			}
			//TODO post this message in the UI
			console.log('at end of complete');
			$.mobile.loading('hide');
		});
	});

});