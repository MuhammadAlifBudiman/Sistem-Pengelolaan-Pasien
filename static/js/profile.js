// Function to update the profile
/**
 * Updates the user profile by collecting data from modal inputs and sending it to the server.
 * Uses AJAX to submit a multipart/form-data POST request to /api/profile/edit.
 */
function updateProfile() {
  // Fetch updated data from modal input fields
  /**
   * @type {string} updatedName - The updated name from the input field
   */
  let updatedName = $("#input-name").val();
  /**
   * @type {File} updatedPic - The updated profile picture file from the input field
   */
  let updatedPic = $("#input-pic")[0].files[0];
  /**
   * @type {string} updatednik - The updated NIK (identity number)
   */
  let updatednik = $("#input-nik").val();
  /**
   * @type {string} updatedtlg_lahir - The updated date of birth
   */
  let updatedtlg_lahir = $("#input-tgl-lahir").val();
  /**
   * @type {string} updatedtgender - The updated gender (radio input)
   */
  let updatedtgender = $("input[name='input-gender']:checked").val();
  /**
   * @type {string} updatedtagama - The updated religion
   */
  let updatedtagama = $("#input-agama").val();
  /**
   * @type {string} updatedtstatus - The updated marital status
   */
  let updatedtstatus = $("#input-status").val();
  /**
   * @type {string} updatedtalamat - The updated address
   */
  let updatedtalamat = $("#input-alamat").val();
  /**
   * @type {string} updatedtno_tlp - The updated phone number
   */
  let updatedtno_tlp = $("#input-no-telp").val();

  // Create a FormData object to hold the updated profile data
  let form_data = new FormData();
  form_data.append("name", updatedName); // Add name
  form_data.append("profile_pic", updatedPic); // Add profile picture file
  form_data.append("nik", updatednik); // Add NIK
  form_data.append("tgl_lahir", formatDateString(updatedtlg_lahir)); // Add formatted date of birth
  form_data.append("gender", updatedtgender); // Add gender
  form_data.append("agama", updatedtagama); // Add religion
  form_data.append("status", updatedtstatus); // Add marital status
  form_data.append("alamat", updatedtalamat); // Add address
  form_data.append("no_tlp", updatedtno_tlp); // Add phone number

  // Send the updated data to the server using AJAX
  $.ajax({
    url: "/api/profile/edit", // API endpoint for profile update
    type: "POST", // HTTP method
    data: form_data, // Data to send (FormData)
    cache: false, // Disable cache
    contentType: false, // Let jQuery set the content type
    processData: false, // Prevent jQuery from processing the data
    success: function (response) {
      // Handle success response from server
      if (response.result === "failed") {
        showToast(response.message, "error", 3000); // Show error toast
        return;
      }
      showToast(response.message, "success", 3000); // Show success toast
      window.location.reload(); // Reload the page to reflect changes
    },
    error: function (error) {
      // Handle AJAX error
      showToast("Gagal memperbarui profil", "error", 3000);
    },
  });
}
