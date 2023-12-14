// Function to update the profile
function updateProfile() {
  // Fetch updated data from modal inputs (you can add more fields as needed)
  var updatedName = $("#input-name").val();
  var updatedPic = $("#input-pic")[0].files[0];
  var updatednik = $("#input-nik").val();
  var updatedtlg_lahir = $("#input-tgl-lahir").val();
  var updatedtgender = $("input[name='input-gender']:checked").val();
  var updatedtagama = $("#input-agama").val();
  var updatedtstatus = $("#input-status").val();
  var updatedtalamat = $("#input-alamat").val();
  var updatedtno_tlp = $("#input-no-telp").val();
  // buat form data
  let form_data = new FormData();
  form_data.append("name", updatedName);
  form_data.append("profile_pic", updatedPic);
  form_data.append("nik", updatednik);
  form_data.append("tgl_lahir", formatDateString(updatedtlg_lahir));
  form_data.append("gender", updatedtgender);
  form_data.append("agama", updatedtagama);
  form_data.append("status", updatedtstatus);
  form_data.append("alamat", updatedtalamat);
  form_data.append("no_tlp", updatedtno_tlp);

  // Send the updated data to the server using AJAX
  $.ajax({
    url: "/api/profile/edit",
    type: "POST",
    data: form_data,
    cache: false,
    contentType: false,
    processData: false,
    success: function (response) {
      if (response.result === "success") {
        // reload page
        alert(response.message);
        window.location.reload();
      } else {
        alert(response.message);
      }
    },
    error: function (error) {
      alert("Failed to update profile");
    },
  });
}

// Function to format date from yyyy-mm-dd to dd-mm-yyyy
function formatDateString(dateString) {
  const [year, month, day] = dateString.split("-");
  return `${day}-${month}-${year}`;
}
