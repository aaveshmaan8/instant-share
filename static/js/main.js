// ================= TAB SWITCH =================
function switchTab(tabName) {

    const uploadTab = document.getElementById("uploadTab");
    const downloadTab = document.getElementById("downloadTab");
    const uploadSection = document.getElementById("upload");
    const downloadSection = document.getElementById("download");

    if (!uploadTab || !downloadTab) return;

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

const uploadForm = document.getElementById("uploadForm");
const progressContainer = document.getElementById("progressContainer");
const progressBar = document.getElementById("progressBar");
const resultBox = document.getElementById("resultBox");
const generatedCode = document.getElementById("generatedCode");
const qrImage = document.getElementById("qrImage");
const countdownElement = document.getElementById("countdown");


// ================= FORMAT SIZE =================
function formatSize(bytes) {
    if (bytes === 0) return "0 Bytes";
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return (bytes / Math.pow(1024, i)).toFixed(2) + " " + sizes[i];
}


// ================= FILE PREVIEW =================
function showPreview(files) {

    dropDefault.classList.add("hidden");
    dropPreview.classList.remove("hidden");
    fileNameEl.innerHTML = "";

    Array.from(files).forEach(file => {
        const div = document.createElement("div");
        div.textContent = `${file.name} (${formatSize(file.size)})`;
        fileNameEl.appendChild(div);
    });
}


// ================= DRAG & DROP =================
if (dropArea && fileInput) {

    dropArea.addEventListener("click", (e) => {
        if (e.target.tagName !== "LABEL") fileInput.click();
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
            showPreview(e.dataTransfer.files);
        }
    });

    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            showPreview(fileInput.files);
        }
    });
}


// ================= AJAX UPLOAD =================
if (uploadForm && fileInput) {

    uploadForm.addEventListener("submit", function (e) {

        e.preventDefault();

        if (!fileInput.files.length) {
            showToast("Please upload at least one file.", "error");
            return;
        }

        const formData = new FormData();
        Array.from(fileInput.files).forEach(file => {
            formData.append("file", file);
        });

        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/upload_ajax", true);

        progressContainer.classList.remove("hidden");
        progressBar.style.width = "0%";

        xhr.upload.onprogress = function (e) {
            if (e.lengthComputable) {
                progressBar.style.width =
                    ((e.loaded / e.total) * 100) + "%";
            }
        };

        xhr.onload = function () {

            if (xhr.status !== 200) {
                showToast("Upload failed.", "error");
                return;
            }

            const response = JSON.parse(xhr.responseText);

            if (!response.success) {
                showToast(response.error || "Upload failed.", "error");
                return;
            }

            const code = response.code;

            generatedCode.innerHTML = `
                <div class="code-display">
                    <span class="main-code">${code}</span>
                    <button class="copy-btn" onclick="copyCode('${code}')">
                        Copy
                    </button>
                </div>
                <div class="file-count">
                    ${fileInput.files.length} file(s) uploaded
                </div>
            `;

            qrImage.src = `/static/${code}.png?${Date.now()}`;
            resultBox.classList.remove("hidden");

            startCountdown(300);
            showToast("Files uploaded successfully!", "success");
        };

        xhr.onerror = () => showToast("Network error.", "error");

        xhr.send(formData);
    });
}


// ================= COUNTDOWN =================
let countdownInterval = null;

function startCountdown(duration) {

    if (countdownInterval) clearInterval(countdownInterval);

    let timer = duration;

    countdownInterval = setInterval(() => {

        const minutes = Math.floor(timer / 60);
        const seconds = timer % 60;

        countdownElement.textContent =
            `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;

        timer--;

        if (timer < 0) {
            clearInterval(countdownInterval);
            countdownElement.textContent = "Expired";
            showToast("File expired!", "error");
        }

    }, 1000);
}


// ================= COPY =================
function copyCode(code) {
    navigator.clipboard.writeText(code);
    showToast("Code copied!", "success");
}


// ================= DOWNLOAD HANDLER =================
const downloadForm = document.querySelector("#download form");

if (downloadForm) {

    downloadForm.addEventListener("submit", function (e) {

        e.preventDefault();

        const codeInput = downloadForm.querySelector("input[name='code']");
        const code = codeInput.value.trim().toUpperCase();

        if (!code || code.length !== 6) {
            showToast("Invalid download code.", "error");
            return;
        }

        fetch(`/download_direct/${code}`)
            .then(res => {

                const contentType = res.headers.get("content-type") || "";

                if (contentType.includes("application/json")) {
                    return res.json().then(data => {
                        throw new Error(data.error || "Invalid code");
                    });
                }

                return res.blob();
            })
            .then(blob => {

                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = "";
                document.body.appendChild(a);
                a.click();
                a.remove();

            })
            .catch(err => {
                showToast(err.message || "Download failed", "error");
            });

    });
}


// ================= TOAST =================
function showToast(message, type = "success") {

    const toast = document.getElementById("toast");
    if (!toast) return;

    toast.textContent = message;
    toast.className = `toast show ${type}`;

    setTimeout(() => {
        toast.classList.remove("show");
    }, 3000);
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
