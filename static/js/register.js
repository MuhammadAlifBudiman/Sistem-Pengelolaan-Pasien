$(document).ready(function () {
  // Get today's date in the format YYYY-MM-DD
  let today = new Date().toISOString().split("T")[0];
  let passwordInput = $("#password");
  let confirmPasswordInput = $("#confirm");

  $("#password-addon1").click(function () {
    if (passwordInput.attr("type") === "password") {
      passwordInput.attr("type", "text");
      $(this).html('<i class="fa-solid fa-eye-slash"></i>');
    } else {
      passwordInput.attr("type", "password");
      $(this).html('<i class="fa-solid fa-eye"></i>');
    }
  })
  
  $("#password-addon2").click(function () {
    if (confirmPasswordInput.attr("type") === "password") {
      confirmPasswordInput.attr("type", "text");
      $(this).html('<i class="fa-solid fa-eye-slash"></i>');
    } else {
      confirmPasswordInput.attr("type", "password");
      $(this).html('<i class="fa-solid fa-eye"></i>');
    }
  })

  // Set the max attribute of the date input to today
  $("#tgl-lahir").attr("max", today);

  // Event listener for form submission
  $("#registrationForm").submit(function (event) {
    event.preventDefault();
    signUp();
  });

});

async function signUp() {
  // Retrieve form data
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

  // Validate form data
  const validationMessage = validateForm(formData);
  if (validationMessage) {
    showToast(validationMessage, "error", 3000)
    return;
  }

  // Update the tglLahir property in the formData
  formData.tglLahir = formatDateString(formData.tglLahir);

  try {
    // Perform registration
    const registrationResponse = await registerUser(formData);

    if (registrationResponse.result === "success") {
      // alert(registrationResponse.message);
      window.location.replace(`/login?msg=${registrationResponse.message}`);
    } else {
      showToast(registrationResponse.message, "error", 3000);
    }
  } catch (error) {
    showToast(error.message, "error", 3000);
  }
}

function validateForm(formData) {
  // Define validation rules
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

  // Perform validation
  for (const field in validationRules) {
    const value = formData[field];

    if (!value) {
      if (field === "nik") {
        return validationRules[field][0];
      }
      return validationRules[field];
    }

    if (Array.isArray(validationRules[field])) {
      const regex = /^\d+$/;

      if (field === "nik" && (value.length !== 16 || !regex.test(value))) {
        return validationRules[field][1];
      }
    }
  }

  return null; // No validation issues
}

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


