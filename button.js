var buttonMO = $("#Motor_On");
buttonMO.click(function(){
	console.log(buttonMO.text());
	if(buttonMO.text() == "Motor On") {
		$.ajax({
		url: "/Motor_On",
		type: "post",
		success: function(response) {
			console.log(response);
			buttonMO.text("Motor On");
		}
	});
	}else {
		$.ajax({
			url: "/Motor_On",
			type: "post",
			success: function(response) {
				console.log(response);
				buttonMO.text("Motor On");
				}
			});
	}
});
var buttonMF = $("#Motor_Off");
buttonMF.click(function(){
        console.log(buttonMF.text());
        if(buttonMF.text() == "Motor Off") {
                $.ajax({
                url: "/Motor_Off",
                type: "post",
                success: function(response) {
                        console.log(response);
                        buttonMF.text("Motor Off");
                }
        });
        }else {
                $.ajax({
                        url: "/Motor_Off",
                        type: "post",
                        success: function(response) {
                                console.log(response);
                                buttonMF.text("Motor Off");
                                }
                        });
        }
});

var buttonDR = $("#Destination_Reached");
buttonDR.click(function(){
        console.log(buttonDR.text());
        if(buttonDR.text() == "Destination Reached") {
                $.ajax({
                url: "/Destination_Reached",
                type: "post",
                success: function(response) {
                        console.log(response);
                        buttonDR.text("Destination Reached");
                }
        });
        }else {
                $.ajax({
                        url: "/Destination_Reached",
                        type: "post",
                        success: function(response) {
                                console.log(response);
                                buttonDR.text("Destination Reached");
                                }
                        });
        }
});

