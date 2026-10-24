const API = window.location.origin;

const btnIndex = document.getElementById("btnIndex");
const idxStatus = document.getElementById("idxStatus");
const formSearch = document.getElementById("formSearch");
const queryInput = document.getElementById("queryInput");
const topK = document.getElementById("topK");
const btnSearch = document.getElementById("btnSearch");
const errorBox = document.getElementById("errorBox");
const resultsBox = document.getElementById("resultsBox");
const resultsInfo = document.getElementById("resultsInfo");
const resultsList = document.getElementById("resultsList");

function tampilkanError(pesan) {
    errorBox.textContent = pesan;
    errorBox.classList.remove("hidden");
    resultsBox.classList.add("hidden");
}

function sembunyikanError() {
    errorBox.classList.add("hidden");
}

function aturStatusIndex(teks, tipe) {
    idxStatus.textContent = teks;
    idxStatus.className = "status " + (tipe || "ok");
}

async function indexkanData() {
    sembunyikanError();
    resultsBox.classList.add("hidden");
    btnIndex.disabled = true;
    aturStatusIndex("Mengindex dataset...", "ok");

    try {
        const respon = await fetch(API + "/index", { method: "POST" });
        if (!respon.ok) {
            throw new Error("Gagal mengindex: HTTP " + respon.status);
        }
        const data = await respon.json();
        aturStatusIndex("Selesai: " + data.indexed + " dokumen diindex", "ok");
    } catch (kesalahan) {
        aturStatusIndex(kesalahan.message, "err");
        tampilkanError(kesalahan.message);
    } finally {
        btnIndex.disabled = false;
    }
}

async function cariData(peristiwa) {
    peristiwa.preventDefault();
    sembunyikanError();
    resultsBox.classList.add("hidden");
    resultsList.innerHTML = "";
    resultsInfo.textContent = "";

    const kueri = queryInput.value.trim();
    if (!kueri) {
        tampilkanError("Masukkan kueri pencarian terlebih dahulu.");
        return;
    }

    btnSearch.disabled = true;
    btnSearch.textContent = "Mencari...";

    try {
        const respon = await fetch(API + "/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query: kueri,
                top_k: parseInt(topK.value, 10),
            }),
        });

        if (!respon.ok) {
            throw new Error("Gagal mencari: HTTP " + respon.status);
        }

        const data = await respon.json();
        tampilkanHasil(data);
    } catch (kesalahan) {
        tampilkanError(kesalahan.message);
    } finally {
        btnSearch.disabled = false;
        btnSearch.textContent = "Cari";
    }
}

function tampilkanHasil(data) {
    resultsInfo.textContent =
        'Kueri: "' + data.query + '" | top_k: ' + data.top_k + " | ditemukan: " + data.results.length;

    if (data.results.length === 0) {
        resultsList.innerHTML =
            '<div class="result-card"><div class="result-text">Tidak ada hasil. Pastikan dataset sudah diindex terlebih dahulu.</div></div>';
    } else {
        data.results.forEach(function (item, indeks) {
            const kartu = document.createElement("div");
            kartu.className = "result-card";
            kartu.innerHTML =
                '<div class="result-header">' +
                '<span class="result-title">' + escapeHtml(item.title ?? "(tanpa judul)") + "</span>" +
                '<span class="result-score">Skor: ' + (item.score ?? 0).toFixed(4) + "</span>" +
                "</div>" +
                '<div class="result-meta">Kategori: ' + escapeHtml(item.category) + "</div>" +
                '<div class="result-text">' + escapeHtml(item.text) + "</div>";
            resultsList.appendChild(kartu);
        });
    }

    resultsBox.classList.remove("hidden");
}

function escapeHtml(teks) {
    if (teks == null) return "";
    const elemen = document.createElement("div");
    elemen.textContent = teks;
    return elemen.innerHTML;
}

btnIndex.addEventListener("click", indexkanData);
formSearch.addEventListener("submit", cariData);
queryInput.addEventListener("keypress", function (peristiwa) {
    if (peristiwa.key === "Enter" && peristiwa.target === queryInput) {
        peristiwa.preventDefault();
        cariData(peristiwa);
    }
});
