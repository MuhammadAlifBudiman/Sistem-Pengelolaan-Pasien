$(document).ready(function () {
    // Get today's date in the format YYYY-MM-DD
    let today = new Date().toISOString().split("T")[0];

    // Set the max attribute of the date input to today
    $("#tanggal").attr("min", today);
  // Fungsi untuk merender tabel berdasarkan data yang diberikan
  function renderTable(data) {
    console.log("Data for rendering table:", data);

    let tbody = $("#antrian-container tbody");
    tbody.empty();

    data.forEach(function (item, index) {
      let row = $("<tr>");
      let antrian = item.antrian || "-";
      row.append(`<td>${antrian}</td>`);
      row.append(`<td>${item.name}</td>`);
      row.append(`<td>${item.nik}</td>`);
      row.append(`<td>${item.tanggal}</td>`);
      row.append(`<td>${item.status}</td>`);

      tbody.append(row);
    });

    toggleFormAndAntrian(
      data.some(
        (item) => item.status === "pending" || item.status === "approved"
      )
    );
  }

  // Fungsi untuk menampilkan atau menyembunyikan formulir dan antrian berdasarkan data
  function toggleFormAndAntrian(hasPendingOrApproved) {
    $("#formulir-container").toggle(!hasPendingOrApproved);
    $("#antrian-container").toggle(hasPendingOrApproved);
    $("#formulir-container-done-rejected").toggle(
      sessionStorage.getItem("formStatus") === "rejected" ||
        sessionStorage.getItem("formStatus") === "done"
    );
  }

  // Periksa sessionStorage saat halaman dimuat
  let formStatus = sessionStorage.getItem("formStatus");
  console.log("formStatus:", formStatus);

  if (
    formStatus === "done" ||
    formStatus === "rejected" ||
    formStatus === null
  ) {
    toggleFormAndAntrian(false);
  } else {
    toggleFormAndAntrian(true);

    // Jika formulir sudah dikirim, ambil dan tampilkan data antrian
    if (formStatus === "pending" || formStatus === "approved") {
      $.ajax({
        type: "GET",
        url: "/get_antrian_data",
        success: function (data) {
          console.log("Response from the server:", data);
          renderTable(data.antrian_data);
        },
        error: function () {
          console.error("Failed to fetch queue data");
        },
      });
    }
  }

  // Perbarui peristiwa klik untuk tombol kirim
  $(".btn-submit-form").click(function (event) {
    event.preventDefault();

    if (formStatus === "done" || formStatus === "rejected") {
      alert(
        "Formulir telah terkirim. Anda tidak dapat mengirim formulir lagi."
      );
      return;
    }

    let poli = $("#poli").val();
    let tanggal = $("#tanggal").val();
    let keluhan = $("#keluhan").val();

    let formData = {
      poli: poli,
      tanggal: tanggal,
      keluhan: keluhan,
    };

    if (formData.poli === "") {
      alert("Harap pilih jenis poli sebelum mengirim formulir");
      return;
    }

    if (formData.tanggal === "") {
      alert("Harap pilih tanggal berobat sebelum mengirim formulir");
      return;
    }

    if (formData.keluhan === "") {
      alert("Harap isi keluhan Anda sebelum mengirim formulir");
      return;
    }

    // Permintaan Ajax untuk mengirim formulir
    $.ajax({
      type: "POST",
      url: "/api/pendaftaran",
      data: formData,
      success: function (data) {
        if (data.result === "fail"){
          alert("Gagal melakukan pendaftaran. Silakan coba lagi.");
          return;
        }
        console.log(
          "Response from the server after submitting the form:",
          data
        );
        let newStatus = "pending";
        showToast("Formulir telah diproses. Silakan tunggu.", "success", 3000);

        sessionStorage.setItem("formStatus", newStatus);
        toggleFormAndAntrian(
          newStatus === "pending" || newStatus === "approved"
        );
        renderTable(data.antrian_data);
      },
      error: function () {
        alert("Gagal melakukan pendaftaran. Silakan coba lagi.");
      },
    });
  });
});

