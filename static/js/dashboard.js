// Jadwal Table
$(document).ready(function () {
  // Inisialisasi DataTables
  let myTable = $("#pendaftaranTable").DataTable({
    serverSide: true,
    processing: true,
    scrollX: true,
    ajax: "/api/pendaftaran",
    columns: [
      {
        data: null,
        render: function (data, type, row) {
          return row.antrian || "-";
        },
      },
      { data: "name" },
      { data: "poli" },
      { data: "tanggal" },
      {
        data: "status",
        orderable: false,
      },
    ],
    columnDefs: [
      { width: "20%", targets: 0 }, // Adjust the width as needed
      { width: "30%", targets: 1 },
      { width: "30%", targets: 2 },
      { width: "20%", targets: 3 },
      { width: "40%", targets: 4 },
    ],
    order: [[3, "asc"]],
  });
  let checkupTable = $("#checkupTable").DataTable({
    serverSide: true,
    processing: true,
    scrollX: true,
    ajax: "/api/checkup",
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
      { data: "nama" },
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
    ],
    columnDefs: [
      { width: "10%", targets: 0 }, // Adjust the width as needed
      { width: "10%", targets: 1 },
      { width: "10%", targets: 2 },
      { width: "10%", targets: 3 },
      { width: "10%", targets: 4 },
      { width: "10%", targets: 5 },
      { width: "40%", targets: 6 },
    ],
    order: [[1, "asc"]],
  });
  let rekamMedisTable = $("#rekamMedisTable").DataTable({
    serverSide: true,
    processing: true,
    scrollX: true,
    ajax: "/api/rekam_medis",
    columns: [
      {
        data: null,
        orderable: false,
        searchable: false,
        render: function (data, type, row, meta) {
          return meta.row + meta.settings._iDisplayStart + 1;
        },
      },
      { data: "nik" },
      { data: "nama" },
      {
        data: null,
        orderable: false,
        searchable: false,
        render: function (data, type, row) {
          return `<button class='btn text-light btn-lihat' data-bs-toggle='modal' data-bs-target='#lihatModal' data-rekammedis-nik='${row.nik}' style='background-color: #091e3e'>Lihat</button>`;
        },
      },
    ],
    columnDefs: [
      { width: "10%", targets: 0 }, // Adjust the width as needed
      { width: "10%", targets: 1 },
      { width: "10%", targets: 2 },
      { width: "10%", targets: 3 },
    ],
  });

  $("#rekamMedisTable").on("click", ".btn-lihat", function () {
    let rekamMedisNik = $(this).data("rekammedis-nik");

    // Destroy existing DataTable if it exists
    if ($.fn.DataTable.isDataTable("#list_checkup_user")) {
      $("#list_checkup_user").DataTable().destroy();
    }

    let list_checkup_user = $("#list_checkup_user").DataTable({
      serverSide: true,
      processing: true,
      scrollX: true,
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
      ],
      columnDefs: [
        { width: "10%", targets: 0 }, // Adjust the width as needed
        { width: "10%", targets: 1 },
        { width: "10%", targets: 2 },
        { width: "10%", targets: 3 },
        { width: "10%", targets: 4 },
        { width: "10%", targets: 5 },
      ],
      order: [[1, "asc"]],
    });

    $.ajax({
      url: `/api/rekam_medis/${rekamMedisNik}`,
      type: "GET",
      success: function (response) {
        console.log(response)
        $("#lihatModal").find("#no_kartu").text(response.data.no_kartu);
        $("#lihatModal").find("#nama").text(response.data.nama);
        $("#lihatModal").find("#nik").text(response.data.nik);
        $("#lihatModal").find("#umur").text(response.data.umur);
        $("#lihatModal").find("#alamat").text(response.data.alamat);
        $("#lihatModal").find("#no_telp").text(response.data.no_telp);
      },
      error: function (error) {
        showToast(error.responseJSON.message, "error", 3000)
      },
    })
  });
});
