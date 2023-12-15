
$(document).ready(function () {
  if(typeof globalMessage !== 'undefined'){
    showToast(globalMessage, "success", 3000)
  }
  // if ({{msg}}){
  //   showToast({{msg}}, "success", 3000);
  // }
  // Inisialisasi DataTables
  let jadwalTable = $("#jadwalTable").DataTable();
  let antrianTable = $("#antrianTable").DataTable();

  // Ambil data jadwal praktek
  $.ajax({
    url: "/api/get_jadwal",
    type: "GET",
    success: function (data) {
      // Isi tabel jadwal praktek
      jadwalTable.clear().draw();
      data.jadwal.forEach(function (row) {
        jadwalTable.row
          .add([
            row.nama,
            row.poli,
            row.hari,
            row.jam_buka + " - " + row.jam_tutup,
          ])
          .draw();
      });
    },
  });

  // Ambil data antrian hari ini
  $.ajax({
    url: "/api/antrian/today",
    type: "GET",
    success: function (data) {
      // Isi tabel antrian hari ini
      antrianTable.clear().draw();
      data.data.forEach(function (row) {
        antrianTable.row
          .add([row.poli, row.jumlah_pendaftar, row.dalam_antrian])
          .draw(false);
      });
    },
  });

  $(".navbar-toggler").on("click", function () {
    $(".navbar-collapse").toggleClass("show");
  });
});


