// Jadwal Table
$(document).ready(function () {
  // Inisialisasi datatables
  let jadwalTable = $("#jadwalTable").DataTable();

  // insert button tambah below h2 with id jadwal
  $("#jadwal").append(
    '<div class="d-grid gap-2 d-md-block col-2"> <button type="button" class="btn btn-primary text-light" data-bs-toggle="modal" data-bs-target="#exampleModal" style="background-color: #06a3da">Tambah</button></div>'
  );

  // Ambil data jadwal praktek
  $.ajax({
    url: "/api/get_jadwal",
    type: "GET",
    success: function (data) {
      console.log()
      // Isi tabel jadwal praktek
      jadwalTable.clear().draw();
      data.jadwal.forEach(function (row) {
        console.log(row._id)
        // Update tabel
        let newRow = [
          row.nama,
          row.poli,
          row.hari,
          row.jam_buka + " - " + row.jam_tutup,
          "<button class='btn btn-warning btn-sm btn-edit' data-bs-toggle='modal'        data-bs-target='#editModal'>Edit</button> <button class='btn btn-danger btn-sm btn-delete' data-bs-toggle='modal' data-bs-target='#deleteModal'>Delete</button>",
        ];
        let rowNode = jadwalTable.row.add(newRow).draw().node();
        $(rowNode).attr("id", row._id);
      });
    },
    error: function (error) {
      alert(error.responseJSON.message);
    },
  });

  // Event listener for Add button
  $("#tambahJadwal").submit(function (e) {
    e.preventDefault();

    // Ambil nilai input
    let nama = $("#nama").val();
    let poli = $("#listPoli").val();
    let hari = $("input[name='hari']:checked").val();
    let jamBuka = $("#jamBuka").val();
    let jamTutup = $("#jamTutup").val();

    // Lakukan validasi
    if (!nama || !poli || !hari || !jamBuka || !jamTutup) {
      alert("Semua field harus diisi!");
      return;
    }

    if (jamBuka >= jamTutup) {
      alert("Jam buka harus lebih kecil dari jam tutup!");
      return;
    }

    let formData = $(this).serializeArray();

    $.ajax({
      url: "/api/tambah_jadwal",
      type: "POST",
      data: formData,
      success: function (response) {
        if (response.result == "success") {
          let jadwal = response.jadwal;
          // Update tabel
          let newRow = [
            jadwal.nama,
            jadwal.poli,
            jadwal.hari,
            jadwal.jam_buka + " - " + jadwal.jam_tutup,
            "<button class='btn btn-warning btn-sm btn-edit' data-bs-toggle='modal'        data-bs-target='#editModal'>Edit</button> <button class='btn btn-danger btn-sm btn-delete' data-bs-toggle='modal' data-bs-target='#deleteModal'>Delete</button>",
          ];
          let rowNode = jadwalTable.row.add(newRow).draw().node();
          $(rowNode).attr("id", jadwal._id); // Set ID for the new row

          alert(response.message);
          // Reset the form
          $("#tambahJadwal")[0].reset();

          // Close the modal
          $("#exampleModal").modal("hide");
        } else {
          alert(response.message);
        }
      },
      error: function (error) {
        alert(error.responseJSON.message);
      },
    });
  });

  // Event listener for Edit buttons
  $("#jadwalTable").on("click", ".btn-edit", function () {
    let action = $(this).text();
    let row = jadwalTable.row($(this).parents("tr"));
    let rowData = row.data();
    let rowId = $(this).parents("tr").attr("id");
    let editModal = $("#editModal");
    $.ajax({
      url: "/api/get_jadwal/" + rowId,
      type: "GET",
      success: function (response) {
        let jadwal = response.jadwal;

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
            .find("input[name='hari'][value='" + jadwal.hari[i].toLowerCase() + "']")
            .prop("checked", true);
        }
      },
      error: function (error) {
        alert(error.responseJSON.message);
      },
    });

    // Event listener for Edit form submission
    editModal
      .find("#editJadwal")
      .off("submit")
      .submit(function (e) {
        e.preventDefault();

        // Ambil nilai input
        let nama = editModal.find("#nama").val();
        let poli = editModal.find("#listPoli").val();
        let hari = editModal.find("input[name='hari']:checked").val();
        let jamBuka = editModal.find("#jamBuka").val();
        let jamTutup = editModal.find("#jamTutup").val();

        // Lakukan validasi
        if (!nama || !poli || !hari || !jamBuka || !jamTutup) {
          alert("Semua field harus diisi!");
          return;
        }

        if (jamBuka >= jamTutup) {
          alert("Jam buka harus lebih kecil dari jam tutup!");
          return;
        }

        let formData = $(this).serializeArray();

        $.ajax({
          url: "/api/edit_jadwal/" + rowId,
          type: "POST",
          data: formData,
          success: function (response) {
            if (response.result == "success") {
              let jadwal = response.jadwal;
              // Update the row
              row
                .data([
                  jadwal.nama,
                  jadwal.poli,
                  jadwal.hari,
                  jadwal.jam_buka + " - " + jadwal.jam_tutup,
                  "<button class='btn btn-warning btn-sm btn-edit' data-bs-toggle='modal'        data-bs-target='#editModal'>Edit</button> <button class='btn btn-danger btn-sm btn-delete' data-bs-toggle='modal' data-bs-target='#deleteModal'>Delete</button>",
                ])
                .draw();

              alert(response.message);

              // Reset the form
              editModal.find("#editJadwal")[0].reset();

              // Close the modal
              editModal.modal("hide");
            } else {
              alert(response.message);
            }
          },
          error: function (error) {
            alert(error.responseJSON.message);
          },
        });
      });
  });

  // Event listener for Delete buttons
  $("#jadwalTable").on("click", ".btn-delete", function () {
    let rowId = $(this).parents("tr").attr("id");
    $("#hapusJadwal")
      .off("submit")
      .submit(function (e) {
        e.preventDefault();

        $.ajax({
          url: "/api/hapus_jadwal/" + rowId,
          type: "POST",
          success: function (response) {
            if (response.result == "success") {
              // Delete the row
              jadwalTable
                .row("#" + rowId)
                .remove()
                .draw();

              alert(response.message);
              // Close the modal
              $("#deleteModal").modal("hide");
            } else {
              alert(response.message);
            }
          },
          error: function (error) {
            alert(error.responseJSON.message);
          },
        });
      });
  });
});

function sign_out() {
  $.removeCookie("mytoken", { path: "/" });
  alert("Logged out!");
  window.location.href = "/";
}
