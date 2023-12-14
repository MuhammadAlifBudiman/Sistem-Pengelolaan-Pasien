$(document).ready(function () {
  // Get today's date in the format YYYY-MM-DD
  var today = new Date().toISOString().split("T")[0];

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
    alert(validationMessage);
    return;
  }

  // Update the tglLahir property in the formData
  formData.tglLahir = formatDateString(formData.tglLahir);

  try {
    // Perform registration
    const registrationResponse = await registerUser(formData);

    if (registrationResponse.result === "success") {
      alert(registrationResponse.message);
      window.location.replace("/login");
    } else {
      alert(registrationResponse.message);
    }
  } catch (error) {
    alert(error.message);
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

  // Password regex validation
  const passwordRegex =
    /^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
  if (!passwordRegex.test(formData.password)) {
    return "Password harus memenuhi persyaratan: minimal 8 karakter, setidaknya 1 huruf kapital, 1 angka, dan 1 simbol";
  }

  // Confirm password match validation
  if (formData.password !== formData.confirmPassword) {
    return "Password dan konfirmasi password tidak cocok";
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

  if (!response.ok) {
    throw new Error("Failed to register user");
  }

  return response.json();
}

// Function to format date from yyyy-mm-dd to dd-mm-yyyy
function formatDateString(dateString) {
  const [year, month, day] = dateString.split("-");
  return `${day}-${month}-${year}`;
}
