// rekam medis
$(document).ready(function () {
  // Inisialisasi datatables
  let rekam_medisTable = $("#rekam_medisTable").DataTable({
    serverSide: true,
    processing: true,
    ajax: "/api/users/pasien",
    columns: [
      {
        data: null,
        orderable: false,
        searchable: false,
        render: function (data, type, row, meta) {
          return meta.row + meta.settings._iDisplayStart + 1;
        },
      },
      { data: "name" },
      { data: "nik" },
      {
        data: null,
        render: function (data, type, row) {
          if (row.has_rekam_medis){
            return `<button class='btn btn-danger btn-sm btn-lihat' data-bs-toggle='modal' data-bs-target='#lihatModal' data-rekammedis-nik='${row.nik}'>Lihat</button>`;
          }
          else{
            return `<button class='btn btn-warning btn-sm btn-buat' data-bs-toggle='modal' data-bs-target='#buatModal' data-rekammedis-nik='${row.nik}'>Buat</button>`;
          }
        },
      },
    ],
  });

  // Event listener for Submit button
  $("#rekam_medisTable").on("click", ".btn-buat", function (e) {
    let rekamMedisNik = $(this).data("rekammedis-nik");
    
    $("#buatrekam_medis")
      .off("submit")
      .submit(function (e) {
        e.preventDefault();

        // Ambil nilai input
        let no_kartu = $("#no_kartu").val();
        let dokter = $("#dokter").val();
        let hasil_anamnesa = $("#hasil_anamnesa").val();

        let formData = $(this).serializeArray();
        formData.push({ name: "nik", value: rekamMedisNik });

        $.ajax({
          url: `/api/rekam_medis`,
          type: "POST",
          data: formData,
          success: function (response) {
            console.log(response)
            if(response.result === "failed"){
              showToast(response.message, "error", 3000)
              return;
            }
            showToast(response.message, "success", 3000)
            $("#buatrekam_medis")[0].reset();
            $("#buatModal").modal("hide");
            rekam_medisTable.ajax.reload();
          },
          error: function (error) {
            console.log("Error:", error);
          },
        });
      });
  });

  // Event listener for Lihat button
  $("#rekam_medisTable").on("click", ".btn-lihat", function () {
    let rekamMedisNik = $(this).data("rekammedis-nik");

    // Destroy existing DataTable if it exists
    if ($.fn.DataTable.isDataTable("#list_checkup_user")) {
      $("#list_checkup_user").DataTable().destroy();
    }

    let list_checkup_user = $("#list_checkup_user").DataTable({
      serverSide: true,
      processing: true,
      ajax: `/api/checkup/${rekamMedisNik}`,
      columns: [
        {
          data: null,
          orderable: false,
          searchable: false,
          render: function (data, type, row, meta) {
            return meta.row + meta.settings._iDisplayStart + 1;
          },
        },
        { data: "tgl_periksa" },
        {
          data: null,
          render: function (data, type, row) {
            return row.dokter || "Belum ada dokter";
          },
        },
        { data: "poli" },
        { data: "keluhan" },
        {
          data: null,
          render: function (data, type, row) {
            return row.hasil_anamnesa || "Belum ada hasil anamnesa";
          },
        },
        {
          data: null,
          orderable: false,
          searchable: false,
          render: function (data, type, row) {
            return `<button class='btn btn-warning btn-sm btn-edit' data-bs-toggle='modal'        data-bs-target='#editModal' data-checkup-id='${row._id}' data-rekammedis-nik='${rekamMedisNik}'>Edit</button>`;
          },
        }
      ],
      order: [[1, "asc"]],
    });
  });

  // Event listener for Edit buttons
  $("#list_checkup_user").on("click", ".btn-edit", function () {
    let checkupId = $(this).data("checkup-id");
    let rekamMedisNik = $(this).data("rekammedis-nik");
    let editModal = $("#editModal");
    $.ajax({
      url: `/api/checkup/${rekamMedisNik}/${checkupId}`,
      type: "GET",
      success: function (response) {
        editModal.find("#dokter").val(response.data.dokter);
        editModal.find("#hasil_anamnesa").val(response.data.hasil_anamnesa);
      },
      error: function (error) {
        showToast(error.responseJSON.message, "error", 3000)
      },
    });

    // Event listener for Edit form submission
    editModal
      .find("#edit")
      .off("submit")
      .submit(function (e) {
        e.preventDefault();

        let formData = $(this).serializeArray();

        $.ajax({
          url: `/api/checkup/${rekamMedisNik}/${checkupId}`,
          type: "POST",
          data: formData,
          success: function (response) {
            if (response.result === "failed") {
              showToast(response.message, "error", 3000)
              return;
            }
            showToast(response.message, "success", 3000)
            $("#list_checkup_user").DataTable().ajax.reload();

            // Reset the form
            editModal.find("#edit")[0].reset();

            // Close the modal
            editModal.modal("hide");
          },
          error: function (error) {
            showToast(error.responseJSON.message, "error", 3000)
          },
        });
      });
  });
});
