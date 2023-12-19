$(document).ready(function () {
  // Inisialisasi DataTables
  let myTable = $("#myTable").DataTable({
    serverSide: true,
    processing: true,
    scrollX: true,
    ajax: "/api/checkup/me",
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
      { data: "poli" },
      {
        data: null,
        render: function (data, type, row) {
          return row.dokter || "Belum ada dokter";
        },
      },
      { data: "keluhan" },
      {
        data: null,
        render: function (data, type, row) {
          return row.hasil_anamnesa || "Belum ada hasil anamnesa";
        },
      },
    ],
    columnDefs: [
      { width: "20%", targets: 0 }, // Adjust the width as needed
      { width: "20%", targets: 1 },
      { width: "20%", targets: 2 },
      { width: "20%", targets: 3 },
      { width: "20%", targets: 4 },
      { width: "20%", targets: 5 },
    ],
    order: [[1, "asc"]],
  });
});
