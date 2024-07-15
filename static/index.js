// Function to send selected data to Flask route
function callRoute(route) {
    var selectedMedia = [];

    // Collect selected image paths
    var imageCheckboxes = document.querySelectorAll('input[name="selectedMedia[]"]:checked');
    imageCheckboxes.forEach(function(checkbox) {
        selectedMedia.push(checkbox.value);
    });

    // Send selected data to Flask route
    fetch(`/${route}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            selectedMedia: selectedMedia
        })
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;  // Redirect to the new URL
        } else {
            return response.text();  // Get the text response from the server
        }
    })
    .then(text => {
        if (text && text.trim() === "reload") {  // Check if the response is "reload"
            location.reload();  // Reload the page
        } else if (text) {
            console.log(text);  // Log the response if it's not "reload" (for debugging)
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Function to handle class checkbox check/uncheck
function toggleClass(className) {
    var classCheckbox = document.getElementById(className);
    var mediaImagesCheckboxes = document.querySelectorAll('.mediaImages .' + className);
    mediaImagesCheckboxes.forEach(function(checkbox) {
        checkbox.checked = classCheckbox.checked;
    });
    console.log(document.querySelectorAll('input[name="selectedMedia[]"]:checked'));
}
