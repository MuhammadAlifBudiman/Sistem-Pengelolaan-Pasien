// Jadwal Table
$(document).ready(function () {
  // Inisialisasi DataTables
  let myTable = $("#pendaftaranTable").DataTable();
  let checkupTable = $("#checkupTable").DataTable();
  let rekamMedisTable = $("#rekamMedisTable").DataTable();
  let list_checkup_user = $("#list_checkup_user").DataTable();

  // Ambil data riwayat pendaftaran
  $.ajax({
    url: "/api/dashboard_pendaftaran",
    type: "GET",
    success: function (data) {
      // Isi tabel riwayat pendaftaran
      myTable.clear().draw();
      data.data_list_pendaftaran.forEach(function (row, index) {
        let antrian = row.antrian || "-";
        myTable.row
          .add([antrian, row.name, row.poli, row.tanggal, row.status])
          .draw(false);
      });
    },
  });

  // Ambil data riwayat pendaftaran
  $.ajax({
    url: "/api/dashboard_checkup",
    type: "GET",
    success: function (data) {
      console.log(data);
      // Isi tabel riwayat pendaftaran
      checkupTable.clear().draw();
      data.data_list_checkup.forEach(function (row, index) {
        let dokter = row.dokter || "-";
        let hasil_anamnesa = row.hasil_anamnesa || "-";
        checkupTable.row
          .add([
            index + 1,
            row.tgl_periksa,
            row.nama,
            dokter,
            row.poli,
            row.keluhan,
            hasil_anamnesa,
          ])
          .draw(false);
      });
    },
  });

  // Ambil data riwayat pendaftaran
  $.ajax({
    url: "/api/dashboard_rekam_medis",
    type: "GET",
    success: function (data) {
      console.log(data);
      // Isi tabel riwayat pendaftaran
      rekamMedisTable.clear().draw();
      data.data_list_rekam_medis.forEach(function (row, index) {
        rekamMedisTable.row
          .add([
            index + 1,
            row.nik,
            row.nama,
            "<button class='btn btn-primary btn-lihat' data-bs-toggle='modal' data-bs-target='#lihatModal'>Lihat</button>",
          ])
          .draw(false);
      });
    },
  });

  $("#rekamMedisTable").on("click", ".btn-lihat", function (e) {
    e.preventDefault();
    console.log("lihat");
    let row = rekamMedisTable.row($(this).parents("tr"));
    let rowData = row.data();
    console.log(rowData);
    let nik = rowData[1];

    $.ajax({
      url: `/lihat_rekam_medis/${nik}`,
      type: "GET",
      success: function (response) {
        // Update tabel
        console.log(response.list_checkup_user);
        list_checkup_user.clear().draw();
        for (let i = 0; i < response.list_checkup_user.length; i++) {
          let dokter = response.list_checkup_user[i].dokter || "Belum ada dokter";
          let hasil_anamnesa = response.list_checkup_user[i].hasil_anamnesa || "Belum ada hasil anamnesa";
          let newRow = [
            i + 1,
            response.list_checkup_user[i].tgl_periksa,
            dokter,
            response.list_checkup_user[i].poli,
            response.list_checkup_user[i].keluhan,
            hasil_anamnesa,
          ];
          let rowNode = list_checkup_user.row.add(newRow).draw().node();
          $(rowNode).attr("id", response.list_checkup_user[i]._id);
        }
      },
      error: function (error) {
        console.log("Error:", error);
      },
    });
  });
});


