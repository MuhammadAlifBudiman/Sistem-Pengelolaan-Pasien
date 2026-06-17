// login.js - Handles login form submission and user authentication

// Guard against duplicate in-flight submissions
let _loginSubmitting = false;

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
  if (_loginSubmitting) return; // Prevent duplicate submission

  const username = $("#username").val();
  const password = $("#password").val();
  const $btn = $("#loginForm button[type='submit']");

  $.ajax({
    type: "POST",
    url: "/api/login",
    data: {
      username,
      password,
    },
    beforeSend: function () {
      _loginSubmitting = true;
      $btn.prop("disabled", true).text("Memuat...");
    },
    success: function (response) {
      // Redirect on successful authentication
      window.location.replace("/?msg=" + encodeURIComponent(response.message));
    },
    error: function (xhr) {
      // Show backend message or safe generic fallback; never exposes server internals
      var message =
        (xhr.responseJSON && xhr.responseJSON.message) ||
        "Login gagal. Silakan periksa data Anda dan coba lagi.";
      showToast(message, "error", 3000);
    },
    complete: function () {
      // Restore button regardless of outcome
      _loginSubmitting = false;
      $btn.prop("disabled", false).text("Login");
    },
  });
}
// End of login.js
