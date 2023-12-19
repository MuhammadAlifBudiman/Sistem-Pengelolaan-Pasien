
// Function to update the profile
function updateProfile() {
  // Fetch updated data from modal inputs (you can add more fields as needed)
  let updatedName = $("#input-name").val();
  let updatedPic = $("#input-pic")[0].files[0];
  let updatednik = $("#input-nik").val();
  let updatedtlg_lahir = $("#input-tgl-lahir").val();
  let updatedtgender = $("input[name='input-gender']:checked").val();
  let updatedtagama = $("#input-agama").val();
  let updatedtstatus = $("#input-status").val();
  let updatedtalamat = $("#input-alamat").val();
  let updatedtno_tlp = $("#input-no-telp").val();
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
      if (response.result === "failed") {
        showToast(response.message, "error", 3000);
        return;
      }
      showToast(response.message, "success", 3000);
      window.location.reload();
    },
    error: function (error) {
      showToast("Gagal memperbarui profil", "error", 3000)
    },
  });
}


