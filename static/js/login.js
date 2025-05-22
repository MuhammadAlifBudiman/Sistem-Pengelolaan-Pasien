// login.js - Handles login form submission and user authentication

// Wait for the DOM to be fully loaded
$(document).ready(function () {
  // If a global message exists, show it as a success toast
  if (typeof globalMessage !== "undefined") {
    showToast(globalMessage, "success", 3000);
  }
  // Attach submit event handler to the login form
  $("#loginForm").on("submit", function (e) {
    e.preventDefault(); // Prevent default form submission
    sign_in(); // Call sign_in to handle login
  });
});

/**
 * sign_in - Collects username and password from the form,
 * sends an AJAX POST request to the login API,
 * and handles the response for login success or failure.
 */
function sign_in() {
  // Get username and password values from input fields
  const username = $("#username").val();
  const password = $("#password").val();

  // Send AJAX POST request to /api/login with credentials
  $.ajax({
    type: "POST", // HTTP method
    url: "/api/login", // API endpoint
    data: {
      username, // Username from form
      password, // Password from form
    },
    // Handle response from server
    success: function (response) {
      if (response.success) {
        // On success, redirect to home with message
        window.location.replace(`/?msg=${response.message}`);
      } else {
        // On failure, show error toast
        showToast(response.message, "error", 3000);
      }
    },
  });
}
// End of login.js
