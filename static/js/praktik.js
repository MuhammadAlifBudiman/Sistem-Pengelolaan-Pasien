// Jadwal Table
$(document).ready(function () {
  // Inisialisasi datatables
  let jadwalTable = $("#jadwalTable").DataTable({
    serverSide: true,
    processing: true,
    ajax: "/api/jadwal",
    columns: [
      { data: "nama" },
      { data: "poli" },
      { data: "hari" },
      {
        data: null,
        render: function (data, type, row) {
          return row.jam_buka + " - " + row.jam_tutup;
        },
      },
      {
        data: null,
        orderable: false,
        searchable: false,
        render: function (data, type, row) {
          return `<button class='btn btn-warning btn-sm btn-edit' data-bs-toggle='modal'        data-bs-target='#editModal' data-jadwal-id='${row._id}'>Edit</button> <button class='btn btn-danger btn-sm btn-delete' data-bs-toggle='modal' data-bs-target='#deleteModal' data-jadwal-id='${row._id}'>Delete</button>`;
        },
      },
    ],
  });

  // insert button tambah below h2 with id jadwal
  $("#jadwal").append(
    '<div class="d-grid gap-2 d-md-block col-2"> <button type="button" class="btn btn-primary text-light" data-bs-toggle="modal" data-bs-target="#exampleModal" style="background-color: #06a3da">Tambah</button></div>'
  );

  // Event listener for Add button
  $("#tambahJadwal").submit(function (e) {
    e.preventDefault();

    let formData = $(this).serializeArray();

    $.ajax({
      url: "/api/jadwal",
      type: "POST",
      data: formData,
      success: function (response) {
        if (response.result === "failed") {
          showToast(response.message, "error", 3000);
          return;
        }
        showToast(response.message, "success", 3000);
        jadwalTable.ajax.reload();
        // reset form
        $("#tambahJadwal")[0].reset();
        // close modal
        $("#exampleModal").modal("hide");
      },
      error: function (error) {
        showToast(error.responseJSON.message, "error", 3000);
      },
    });
  });

  // Event listener for Edit buttons
  $("#jadwalTable").on("click", ".btn-edit", function () {
    let jadwalId = $(this).data("jadwal-id");
    let editModal = $("#editModal");
    $.ajax({
      url: `/api/jadwal/${jadwalId}`,
      type: "GET",
      success: function (response) {
        let jadwal = response.data;

        // populate the edit modal
        editModal.find("#nama").val(jadwal.nama);
        editModal.find("#listPoli").val(jadwal.poli);
        editModal.find("#jamBuka").val(jadwal.jam_buka);
        editModal.find("#jamTutup").val(jadwal.jam_tutup);
        // Clear all checkboxes first
        editModal.find("input[name='hari']").prop("checked", false);
        // Check the checkboxes based on the received values
        for (let i = 0; i < jadwal.hari.length; i++) {
          editModal
            .find(
              "input[name='hari'][value='" + jadwal.hari[i].toLowerCase() + "']"
            )
            .prop("checked", true);
        }
      },
      error: function (error) {
        showToast(error.responseJSON.message, "error", 3000);
        alert(error.responseJSON.message);
      },
    });

    // Event listener for Edit form submission
    editModal
      .find("#editJadwal")
      .off("submit")
      .submit(function (e) {
        e.preventDefault();

        let formData = $(this).serializeArray();

        $.ajax({
          url: `/api/jadwal/${jadwalId}`,
          type: "POST",
          data: formData,
          success: function (response) {
            if (response.result === "failed") {
              showToast(response.message, "error", 3000);
              return;
            }

            showToast(response.message, "success", 3000);
            jadwalTable.ajax.reload();

            // Reset the form
            editModal.find("#editJadwal")[0].reset();

            // Close the modal
            editModal.modal("hide");
          },
          error: function (error) {
            showToast(error.responseJSON.message, "error", 3000);
          },
        });
      });
  });

  // Event listener for Delete buttons
  $("#jadwalTable").on("click", ".btn-delete", function () {
    let jadwalId = $(this).data("jadwal-id");
    $.ajax({
      url: `/api/jadwal/${jadwalId}`,
      type: "GET",
      success: function (response) {
        let jadwal = response.data;
        $("#deleteModal").find("#deleteTitle").text(`Yakin hapus data ${jadwal.nama}?`);
      },
      error: function (error) {
        showToast(error.responseJSON.message, "error", 3000);
      },
    })
    
    $("#hapusJadwal")
      .off("submit")
      .submit(function (e) {
        e.preventDefault();

        $.ajax({
          url: `/api/jadwal/${jadwalId}`,
          type: "DELETE",
          success: function (response) {
            if (response.result === "failed") {
              showToast(response.message, "error", 3000);
              return;
            }
            showToast(response.message, "success", 3000);
            jadwalTable.ajax.reload();
            // Close the modal
            $("#deleteModal").modal("hide");
          },
          error: function (error) {
            showToast(error.responseJSON.message, "error", 3000);
          },
        });
      });
  });
});
