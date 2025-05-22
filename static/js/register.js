// register.js - Handles user registration form logic

// Wait for the DOM to be fully loaded before executing scripts
$(document).ready(function () {
  // Get today's date in the format YYYY-MM-DD for date input max attribute
  let today = new Date().toISOString().split("T")[0];
  // Cache password and confirm password input fields
  let passwordInput = $("#password");
  let confirmPasswordInput = $("#confirm");

  // Toggle password visibility for the main password field
  $("#password-addon1").click(function () {
    // If password is hidden, show it; otherwise, hide it
    if (passwordInput.attr("type") === "password") {
      passwordInput.attr("type", "text");
      // Change icon to indicate visibility
      $(this).html('<i class="fa-solid fa-eye-slash"></i>');
    } else {
      passwordInput.attr("type", "password");
      // Change icon to indicate hidden
      $(this).html('<i class="fa-solid fa-eye"></i>');
    }
  });

  // Toggle password visibility for the confirm password field
  $("#password-addon2").click(function () {
    if (confirmPasswordInput.attr("type") === "password") {
      confirmPasswordInput.attr("type", "text");
      $(this).html('<i class="fa-solid fa-eye-slash"></i>');
    } else {
      confirmPasswordInput.attr("type", "password");
      $(this).html('<i class="fa-solid fa-eye"></i>');
    }
  });

  // Set the maximum selectable date for date of birth to today
  $("#tgl-lahir").attr("max", today);

  // Intercept form submission to handle with custom logic
  $("#registrationForm").submit(function (event) {
    event.preventDefault(); // Prevent default form submission
    signUp(); // Call signUp function to process registration
  });
});

/**
 * signUp - Collects form data, validates, and submits registration
 * Handles async registration process and error display
 */
async function signUp() {
  // Retrieve form data from input fields
  const formData = {
    username: $("#username").val(),
    name: $("#name").val(),
    nik: $("#nik").val(),
    tglLahir: $("#tgl-lahir").val(),
    gender: $("input[name='gender']:checked").val(),
    agama: $("#agama").val(),
    status: $("#status").val(),
    alamat: $("#alamat").val(),
    noTelp: $("#no-telp").val(),
    password: $("#password").val(),
    confirmPassword: $("#confirm").val(),
  };

  // Validate form data and show error if invalid
  const validationMessage = validateForm(formData);
  if (validationMessage) {
    showToast(validationMessage, "error", 3000);
    return;
  }

  // Format date of birth before sending
  formData.tglLahir = formatDateString(formData.tglLahir);

  try {
    // Send registration data to server
    const registrationResponse = await registerUser(formData);

    if (registrationResponse.result === "success") {
      // On success, redirect to login with message
      window.location.replace(`/login?msg=${registrationResponse.message}`);
    } else {
      // Show error message from server
      showToast(registrationResponse.message, "error", 3000);
    }
  } catch (error) {
    // Show error if request fails
    showToast(error.message, "error", 3000);
  }
}

/**
 * validateForm - Validates registration form data
 * @param {Object} formData - The form data to validate
 * @returns {string|null} - Error message if invalid, otherwise null
 */
function validateForm(formData) {
  // Validation rules for each field
  const validationRules = {
    username: "Username tidak boleh kosong",
    name: "Nama tidak boleh kosong",
    nik: ["NIK tidak boleh kosong", "NIK harus terdiri dari 16 digit angka"],
    tglLahir: "Tanggal lahir tidak boleh kosong",
    gender: "Jenis kelamin harus dipilih",
    agama: "Agama tidak boleh kosong",
    status: "Status tidak boleh kosong",
    alamat: "Alamat tidak boleh kosong",
    noTelp: "Nomor telepon tidak boleh kosong",
    password: "Password tidak boleh kosong",
    confirmPassword: "Konfirmasi password tidak boleh kosong",
  };

  // Loop through each field and validate
  for (const field in validationRules) {
    const value = formData[field];

    // Check for empty fields
    if (!value) {
      if (field === "nik") {
        return validationRules[field][0];
      }
      return validationRules[field];
    }

    // Additional validation for NIK (must be 16 digits)
    if (Array.isArray(validationRules[field])) {
      const regex = /^\d+$/;

      if (field === "nik" && (value.length !== 16 || !regex.test(value))) {
        return validationRules[field][1];
      }
    }
  }

  return null; // No validation issues
}

/**
 * registerUser - Sends registration data to the server
 * @param {Object} data - Registration data
 * @returns {Promise<Object>} - Server response as JSON
 */
async function registerUser(data) {
  const response = await fetch("/api/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  return response.json();
}
