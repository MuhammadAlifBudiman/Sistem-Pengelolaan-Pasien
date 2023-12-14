$(document).ready(function () {
  // Inisialisasi DataTables
  let myTable = $("#myTable").DataTable();

  // Ambil data riwayat pendaftaran
  $.ajax({
    url: "/api/riwayat_pendaftaran",
    type: "GET",
    success: function (data) {
      // Isi tabel riwayat pendaftaran
      myTable.clear().draw();
      data.riwayat.forEach(function (row, index) {
        myTable.row
          .add([
            index + 1,
            row.name,
            row.nik,
            row.poli,
            row.tanggal,
            row.status,
          ])
          .draw(false);
      });
    },
  });
});

function sign_out() {
  $.removeCookie("mytoken", { path: "/" });
  alert("Logged out!");
  window.location.href = "/";
}
