// Jadwal Table
$(document).ready(function () {
  // Inisialisasi DataTables
  let myTable = $("#pendaftaranTable").DataTable({
    serverSide: true,
    processing: true,
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
    order: [[3, "asc"]],
  });
  let checkupTable = $("#checkupTable").DataTable({
    serverSide: true,
    processing: true,
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
    order: [[1, "asc"]],
  });
  let rekamMedisTable = $("#rekamMedisTable").DataTable({
    serverSide: true,
    processing: true,
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
          return `<button class='btn btn-primary btn-lihat' data-bs-toggle='modal' data-bs-target='#lihatModal' data-rekammedis-nik='${row.nik}'>Lihat</button>`;
        },
      },
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
      order: [[1, "asc"]],
    });
  });
});
