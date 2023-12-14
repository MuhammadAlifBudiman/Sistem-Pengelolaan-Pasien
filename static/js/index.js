$(document).ready(function () {
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
    url: "/api/get_antrian",
    type: "GET",
    success: function (data) {
      // Isi tabel antrian hari ini
      antrianTable.clear().draw();
      data.antrian.forEach(function (row) {
        antrianTable.row
          .add([row.poli, row.jumlah_pendaftar, row.dalam_antrian])
          .draw(false);
      });
    },
  });

  // $(".navbar-toggler").on("click", function () {
  //   $(".navbar-collapse").toggleClass("show");
  // });
});

function sign_out() {
  $.removeCookie("mytoken", { path: "/" });
  alert("Logged out!");
  window.location.href = "/";
}
