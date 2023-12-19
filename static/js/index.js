$(document).ready(function () {
  if (typeof globalMessage !== "undefined") {
    showToast(globalMessage, "success", 3000);
  }

  function isSmallDevice() {
    return window.innerWidth <= 531; // Adjust the threshold as needed
  }

  let jadwalTable = $("#jadwalTable").DataTable({
    serverSide: true,
    processing: true,
    scrollX: true,
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
    ],
    columnDefs: [
      { width: "20%", targets: 0 }, // Adjust the width as needed
      { width: "20%", targets: 1 },
      { width: "20%", targets: 2 },
      { width: "40%", targets: 3 },
    ],
    initComplete: function () {
      // Add AOS attributes dynamically after DataTable is populated
      $("#jadwalTable tbody tr").each(function (index) {
        $(this).attr("data-aos", "fade-up");
        $(this).attr("data-aos-delay", index * 100);
      });
    },
  });

  let antrianTable = $("#antrianTable").DataTable({});

  // Ambil data antrian hari ini
  $.ajax({
    url: "/api/antrian/today",
    type: "GET",
    success: function (data) {
      // Isi tabel antrian hari ini
      antrianTable.clear().draw();
      data.data.forEach(function (row, index) {
        antrianTable.row
          .add([row.poli, row.jumlah_pendaftar, row.dalam_antrian])
          .draw(false);
        // Add AOS attributes dynamically after adding data to the DataTable
        $("#antrianTable tbody tr:last").attr("data-aos", "fade-up");
        $("#antrianTable tbody tr:last").attr(
          "data-aos-delay",
          (index + jadwalTable.rows().count()) * 100
        );
      });
    },
  });

  // Check screen size on window resize
  $(window).resize(function () {
    // Update DataTable settings based on screen size
    jadwalTable.settings()[0].scrollX = isSmallDevice();
    jadwalTable.draw();
  });

  // Initial check for screen size on page load
  jadwalTable.settings()[0].scrollX = isSmallDevice();
  jadwalTable.draw();
});
