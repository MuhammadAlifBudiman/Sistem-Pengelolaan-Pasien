// rekam medis
$(document).ready(function () {
  // Inisialisasi datatables
  let rekam_medisTable = $("#rekam_medisTable").DataTable();
  let list_checkup_user = $("#list_checkup_user").DataTable();

  // Ambil data riwayat pendaftaran
  $.ajax({
    url: "/api/rekam_medis",
    type: "GET",
    success: function (data) {
      // Isi tabel riwayat pendaftaran
      rekam_medisTable.clear().draw();
      data.data_rekam_medis.forEach((row)=> {
        let action = ``
        if (row.action == 'lihat') {
          action = `<button class='btn btn-danger btn-sm btn-lihat' data-bs-toggle='modal' data-bs-target='#lihatModal'>Lihat</button>`
        } else {
          action = `<button class='btn btn-warning btn-sm btn-buat' data-bs-toggle='modal' data-bs-target='#buatModal'>Buat</button>`
        }
        rekam_medisTable.row
          .add([
            row.name,
            row.nik,
            action
          ])
          .draw(false);
      });
    },
  });

  // Event listener for Submit button
  $("#rekam_medisTable").on("click", ".btn-buat", function (e) {
    let row = rekam_medisTable.row($(this).parents("tr"));
    let rowData = row.data();
    let nik = rowData[1];
    $("#buatrekam_medis")
      .off("submit")
      .submit(function (e) {
        e.preventDefault();

        // Ambil nilai input
        let no_kartu = $("#no_kartu").val();
        let dokter = $("#dokter").val();
        let hasil_anamnesa = $("#hasil_anamnesa").val();

        // Lakukan validasi
        // if (!no_kartu || !dokter || !hasil_anamnesa || !nik) {
        //   alert("Semua field harus diisi!");
        //   return;
        // }

        let formData = $(this).serializeArray();
        console.log("save");

        $.ajax({
          url: `/buat_rekam_medis/${nik}`,
          type: "POST",
          data: formData,
          success: function (response) {
            // // Update tabel
            // let newRow = [
            //   response.no_kartu,
            //   response.dokter,
            //   response.hasil_anamnesa,
            //   response.nik,
            //   "<button class='btn btn-warning btn-sm btn-edit' data-bs-toggle='modal'        data-bs-target='#editModal'>Edit</button> <button class='btn btn-danger btn-sm btn-delete' data-bs-toggle='modal' data-bs-target='#deleteModal'>Delete</button>",
            // ];
            // let rowNode = rekam_medisTable.row.add(newRow).draw().node();
            // $(rowNode).attr("id", response._id); // Set ID for the new row

            // // Reset the form
            // $("#buatrekam_medis")[0].reset();

            // // Close the modal
            // $("#buatModal").modal("hide");

            alert("Jadwal berhasil ditambahkan!");
            window.location.reload();
          },
          error: function (error) {
            console.log("Error:", error);
          },
        });
      });
  });

  // Event listener for Add button
  $("#rekam_medisTable").on("click", ".btn-lihat", function (e) {
    e.preventDefault();
    console.log("lihat");
    let row = rekam_medisTable.row($(this).parents("tr"));
    let rowData = row.data();
    console.log(rowData);
    let nik = rowData[1];

    $.ajax({
      url: `/lihat_rekam_medis/${nik}`,
      type: "GET",
      success: function (response) {
        // Update tabel
        console.log(response.list_checkup_user.length);
        list_checkup_user.clear().draw();
        for (let i = 0; i < response.list_checkup_user.length; i++) {
          let dokter =
            response.list_checkup_user[i].dokter || "Belum ada dokter";
          let hasil_anamnesa =
            response.list_checkup_user[i].hasil_anamnesa ||
            "Belum ada hasil anamnesa";
          let newRow = [
            i + 1,
            response.list_checkup_user[i].tgl_periksa,
            dokter,
            response.list_checkup_user[i].poli,
            response.list_checkup_user[i].keluhan,
            hasil_anamnesa,
            "<button class='btn btn-warning btn-sm btn-edit' data-bs-toggle='modal'        data-bs-target='#editModal'>Edit</button>",
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

  // Event listener for Edit buttons
  $("#list_checkup_user").on("click", ".btn-edit", function () {
    let action = $(this).text();
    let row = list_checkup_user.row($(this).parents("tr"));
    let rowData = row.data();
    let rowId = $(this).parents("tr").attr("id");
    let editModal = $("#editModal");
    console.log(rowData, row.id());
    $.ajax({
      url: "/api/get-edit_rekam_medis/" + rowId,
      type: "GET",
      success: function (response) {
        console.log(response);
        editModal.find("#dokter").val(response.dokter);
        editModal.find("#hasil_anamnesa").val(response.hasil_anamnesa);
      },
      error: function (error) {
        console.log("Error:", error);
      },
    });

    // Event listener for Edit form submission
    editModal
      .find("#edit")
      .off("submit")
      .submit(function (e) {
        e.preventDefault();

        // Ambil nilai input
        let dokter = editModal.find("#dokter").val();
        let hasil_anamnesa = editModal.find("#hasil_anamnesa").val();

        let formData = $(this).serializeArray();

        $.ajax({
          url: "/api/edit-rekam_medis/" + rowId,
          type: "POST",
          data: formData,
          success: function (response) {
            console.log(response);
            // // Update the row
            // row
            //   .data([
            //     rowData[0],
            //     response.tgl_periksa,
            //     response.dokter,
            //     response.poli,
            //     response.keluhan,
            //     response.hasil_anamnesa,
            //     "<button class='btn btn-warning btn-sm btn-edit' data-bs-toggle='modal'        data-bs-target='#editModal'>Edit</button>"
            //   ])
            //   .draw();

            // Reset the form
            editModal.find("#edit")[0].reset();

            // Close the modal
            editModal.modal("hide");

            alert("Jadwal berhasil diubah!");
          },
          error: function (error) {
            console.log("Error:", error);
          },
        });
      });
  });
}),
  function sign_out() {
    $.removeCookie("mytoken", { path: "/" });
    alert("Logged out!");
    window.location.href = "/";
  };
