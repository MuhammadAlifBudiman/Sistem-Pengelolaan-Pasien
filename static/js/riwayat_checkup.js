$(document).ready(function () {
  // Inisialisasi DataTables
  let myTable = $("#myTable").DataTable();

  // Ambil data riwayat pendaftaran
  $.ajax({
    url: "/api/riwayat_checkup",
    type: "GET",
    success: function (data) {
      console.log(data);
      // Isi tabel riwayat pendaftaran
      myTable.clear().draw();
      data.data_list_checkup_user.forEach(function (row, index) {
        let dokter = row.dokter || "Belum ada dokter";
        let hasil_anamnesa = row.hasil_anamnesa || "Belum ada hasil anamnesa";
        myTable.row
          .add([
            index + 1,
            row.tgl_periksa,
            row.poli,
            dokter,
            row.keluhan,
            hasil_anamnesa,
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
