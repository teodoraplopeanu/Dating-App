$('body').on('click', '#submit', function () {
	console.log("submit");

	$.ajax({
		url: "/api/token/",
		type: "POST",
		data: {
			username : document.getElementById("username").value,
			password : document.getElementById("password").value
		},
		success: function(json) {
			if (json['access'] != null) {
				setCookie("token", json['access'], 1);
				window.location = "/home?token=" + json['access'];
			} else {
				alert("MESSAGE ERRORS AGAIN");
				// TODO errors
			}
		},
		error: function(err) {
			alert("Please enter a valid username and password");
		},

	});
});
