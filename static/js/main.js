// ================= TAB SWITCH =================
function switchTab(tabName) {

    const uploadTab = document.getElementById("uploadTab");
    const downloadTab = document.getElementById("downloadTab");
    const uploadSection = document.getElementById("upload");
    const downloadSection = document.getElementById("download");

    if (!uploadTab || !downloadTab || !uploadSection || !downloadSection) return;

    uploadTab.classList.remove("active");
    downloadTab.classList.remove("active");

    uploadSection.classList.remove("active");
    downloadSection.classList.remove("active");

    document.getElementById(tabName + "Tab").classList.add("active");
    document.getElementById(tabName).classList.add("active");
}



// ================= ELEMENTS =================
const dropArea = document.getElementById("dropArea");
const fileInput = document.getElementById("fileInput");
const dropDefault = document.getElementById("dropDefault");
const dropPreview = document.getElementById("dropPreview");
const fileNameEl = document.getElementById("fileName");
const fileInfoEl = document.getElementById("fileInfo");

const uploadForm = document.getElementById("uploadForm");
const progressContainer = document.getElementById("progressContainer");
const progressBar = document.getElementById("progressBar");
const resultBox = document.getElementById("resultBox");
const generatedCode = document.getElementById("generatedCode");
const qrImage = document.getElementById("qrImage");
const copyCodeBtn = document.getElementById("copyCodeBtn");
const copyLinkBtn = document.getElementById("copyLinkBtn");



// ================= FILE PREVIEW =================
function showPreview(file) {

    if (!fileNameEl || !fileInfoEl) return;

    fileNameEl.textContent = file.name;

    const extension = file.name.includes(".")
        ? file.name.split(".").pop().toUpperCase()
        : "FILE";

    fileInfoEl.textContent =
        `${extension} • ${formatSize(file.size)}`;

    dropDefault.classList.add("hidden");
    dropPreview.classList.remove("hidden");
}



// ================= FORMAT SIZE =================
function formatSize(bytes) {
    if (bytes === 0) return "0 Bytes";
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return (bytes / Math.pow(1024, i)).toFixed(2) + " " + sizes[i];
}



// ================= DRAG & DROP =================
if (dropArea && fileInput) {

    dropArea.addEventListener("click", (e) => {
        if (e.target.tagName !== "LABEL") {
            fileInput.click();
        }
    });

    dropArea.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropArea.classList.add("dragover");
    });

    dropArea.addEventListener("dragleave", () => {
        dropArea.classList.remove("dragover");
    });

    dropArea.addEventListener("drop", (e) => {
        e.preventDefault();
        dropArea.classList.remove("dragover");

        if (e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
            showPreview(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            showPreview(fileInput.files[0]);
        }
    });
}



// ================= AJAX UPLOAD =================
if (uploadForm && fileInput) {

    uploadForm.addEventListener("submit", function (e) {

        e.preventDefault();

        if (!fileInput.files.length) {
            showToast("Please select a file.", "error");
            return;
        }

        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/upload_ajax", true);

        if (progressContainer && progressBar) {
            progressContainer.classList.remove("hidden");
            progressBar.style.width = "0%";
        }

        xhr.upload.onprogress = function (e) {
            if (e.lengthComputable && progressBar) {
                const percent = (e.loaded / e.total) * 100;
                progressBar.style.width = percent + "%";
            }
        };

        xhr.onload = function () {

            if (xhr.status === 200) {

                const response = JSON.parse(xhr.responseText);

                if (response.success && response.codes.length > 0) {

                    const code = response.codes[0];

                    generatedCode.textContent = code;
                    qrImage.src = `/static/${code}.png`;
                    resultBox.classList.remove("hidden");
                    progressBar.style.width = "100%";

                    showToast("Upload successful!", "success");
                    startCountdown(300);

                } else {
                    showToast("Upload failed.", "error");
                }

            } else {
                showToast("Upload failed.", "error");
            }
        };

        xhr.onerror = function () {
            showToast("Network error!", "error");
        };

        xhr.send(formData);
    });
}



// ================= TOAST =================
function showToast(message, type = "success") {

    const toast = document.getElementById("toast");
    if (!toast) return;

    toast.textContent = message;
    toast.className = "toast show " + type;

    setTimeout(() => {
        toast.classList.remove("show");
    }, 3000);
}



// ================= COUNTDOWN =================
let countdownInterval;

function startCountdown(duration) {

    clearInterval(countdownInterval);

    let timer = duration;
    const countdownElement = document.getElementById("countdown");

    countdownInterval = setInterval(() => {

        const minutes = String(Math.floor(timer / 60)).padStart(2, "0");
        const seconds = String(timer % 60).padStart(2, "0");

        countdownElement.textContent = `${minutes}:${seconds}`;

        if (--timer < 0) {
            clearInterval(countdownInterval);
            countdownElement.textContent = "Expired";
            showToast("File expired!", "error");
        }

    }, 1000);
}



// ================= COPY =================
if (copyCodeBtn) {
    copyCodeBtn.addEventListener("click", () => {
        navigator.clipboard.writeText(generatedCode.textContent);
        showToast("Code copied!", "success");
    });
}

if (copyLinkBtn) {
    copyLinkBtn.addEventListener("click", () => {
        const fullLink =
            `${window.location.origin}/download_direct/${generatedCode.textContent}`;
        navigator.clipboard.writeText(fullLink);
        showToast("Download link copied!", "success");
    });
}



// ================= THEME TOGGLE =================
document.addEventListener("DOMContentLoaded", function () {

    const themeToggle = document.getElementById("themeToggle");
    if (!themeToggle) return;

    if (localStorage.getItem("theme") === "light") {
        document.body.classList.add("light");
        themeToggle.textContent = "☀️";
    }

    themeToggle.addEventListener("click", function () {

        document.body.classList.toggle("light");

        if (document.body.classList.contains("light")) {
            localStorage.setItem("theme", "light");
            themeToggle.textContent = "☀️";
        } else {
            localStorage.setItem("theme", "dark");
            themeToggle.textContent = "🌙";
        }
    });
});
