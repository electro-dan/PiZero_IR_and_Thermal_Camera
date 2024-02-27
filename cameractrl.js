function doCallback(jsonData) {
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        // Handle the response
        var json_response = JSON.parse(this.responseText);
        console.log(json_response);

        if (json_response.status == "OK") {
            // Set the status span elements
            document.getElementById("irState").innerHTML = json_response.ir_state;
            document.getElementById("thermalState").innerHTML = json_response.thermal_state;
        } else {
            // Popup with error
            alert("Error returned" + json_response.message);
        }
    }
    // Make the request
    xhttp.open("POST", "/action", true);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify(jsonData));
}

function readStatus() {
    // Request data
    const jsonData = {
        "action": "status"
    };
    doCallback(jsonData);
}

function triggerIR() {
    const jsonData = {
        "action": "ir"
    };
    doCallback(jsonData);
}

function triggerThermal() {
    const jsonData = {
        "action": "thermal"
    };
    doCallback(jsonData);
}

function doShutdown() {
    const jsonData = {
        "action": "shutdown"
    };
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        // Handle the response
        var json_response = JSON.parse(this.responseText);
        console.log(json_response);

        if (json_response.status == "OK") {
        // Set the status span elements
        alert('Will shutdown in 1 minute')
        } else {
        // Popup with error
        alert("Error returned" + json_response.message);
        }
    }
    // Make the request
    xhttp.open("POST", "/action", true);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify(jsonData));
}
