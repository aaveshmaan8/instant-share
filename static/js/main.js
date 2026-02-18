document.addEventListener("DOMContentLoaded", function () {

    /* ================= TAB SWITCH ================= */
    window.switchTab = function (tabName) {
        document.querySelectorAll(".tab").forEach(btn =>
            btn.classList.remove("active")
        );

        document.querySelectorAll(".tab-content").forEach(content =>
            content.classList.remove("active")
        );

        const activeBtn = document.querySelector(
            `button[onclick="switchTab('${tabName}')"]`
        );

        if (activeBtn) activeBtn.classList.add("active");

        const activeContent = document.getElementById(tabName);
        if (activeContent) activeContent.classList.add("active");
    };


    /* ================= ELEMENTS ================= */
    const dropArea = document.getElementById("dropArea");
    const fileInput = document.getElementById("fileInput");
    const filePreview = document.getElementById("filePreview");
    const removeFile = document.getElementById("removeFile");
    const uploadForm = document.getElementById("uploadForm");
    const progressContainer = document.getElementById("progressContainer");
    const progressBar = document.getElementById("progressBar");
    const resultBox = document.getElementById("resultBox");
    const generatedCode = document.getElementById("generatedCode");
    const qrImage = document.getElementById("qrImage");
    const downloadCodeInput = document.getElementById("downloadCodeInput");
    const copyCodeBtn = document.getElementById("copyCodeBtn");
    const copyLinkBtn = document.getElementById("copyLinkBtn");
    const themeToggle = document.getElementById("themeToggle");


    /* ================= DRAG & DROP ================= */
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

            const files = e.dataTransfer.files;
            fileInput.files = files;

            if (files.length > 0) {
                showPreview(files[0]);
            }
        });
    }


    /* ================= FILE PREVIEW ================= */
    if (fileInput) {
        fileInput.addEventListener("change", () => {
            if (fileInput.files.length > 0) {
                showPreview(fileInput.files[0]);
            }
        });
    }

    if (removeFile) {
        removeFile.addEventListener("click", () => {
            fileInput.value = "";
            filePreview.classList.add("hidden");
        });
    }

    function showPreview(file) {
        const fileNameEl = document.getElementById("fileName");
        const fileInfoEl = document.getElementById("fileInfo");

        if (!fileNameEl || !fileInfoEl) return;

        fileNameEl.textContent = file.name;

        const extension = file.name.includes(".")
            ? file.name.split(".").pop().toUpperCase()
            : "FILE";

        const size = formatSize(file.size);

        fileInfoEl.textContent = `${extension} • ${size}`;

        filePreview.classList.remove("hidden");
    }

    function formatSize(bytes) {
        const sizes = ["Bytes", "KB", "MB", "GB"];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return (bytes / Math.pow(1024, i)).toFixed(2) + " " + sizes[i];
    }


    /* ================= AJAX UPLOAD ================= */
    if (uploadForm && fileInput) {

        uploadForm.addEventListener("submit", function (e) {

            e.preventDefault();

            if (!fileInput.files.length) {
                showToast("Please select a file.", "error");
                return;
            }

            const formData = new FormData();
            for (let i = 0; i < fileInput.files.length; i++) {
                formData.append("file", fileInput.files[i]);
            }

            const xhr = new XMLHttpRequest();
            xhr.open("POST", "/upload_ajax", true);

            progressContainer.classList.remove("hidden");
            progressBar.style.width = "0%";

            xhr.upload.onprogress = function (e) {
                if (e.lengthComputable) {
                    const percent = (e.loaded / e.total) * 100;
                    progressBar.style.width = percent + "%";
                }
            };

            xhr.onload = function () {

                if (xhr.status === 200) {

                    const response = JSON.parse(xhr.responseText);

                    if (response.codes && response.codes.length > 0) {

                        const firstCode = response.codes[0];

                        resultBox.classList.remove("hidden");
                        progressBar.style.width = "100%";

                        generatedCode.textContent = firstCode;
                        qrImage.src = "/static/" + firstCode + ".png";

                        switchTab("download");
                        downloadCodeInput.value = firstCode;

                        showToast(response.codes.length + " file(s) uploaded!", "success");

                        startCountdown(300);
                    }

                } else {
                    showToast("Upload failed!", "error");
                }
            };

            xhr.send(formData);
        });
    }


    /* ================= TOAST ================= */
    function showToast(message, type = "success") {
        const toast = document.getElementById("toast");
        if (!toast) return;

        toast.textContent = message;
        toast.className = "toast show " + type;

        setTimeout(() => {
            toast.classList.remove("show");
        }, 3000);
    }


    /* ================= COUNTDOWN ================= */
    let countdownInterval;

    function startCountdown(durationInSeconds) {

        clearInterval(countdownInterval);

        let timer = durationInSeconds;
        const countdownElement = document.getElementById("countdown");

        countdownInterval = setInterval(() => {

            let minutes = Math.floor(timer / 60);
            let seconds = timer % 60;

            minutes = minutes < 10 ? "0" + minutes : minutes;
            seconds = seconds < 10 ? "0" + seconds : seconds;

            countdownElement.textContent = minutes + ":" + seconds;

            if (--timer < 0) {
                clearInterval(countdownInterval);
                countdownElement.textContent = "Expired";

                showToast("File expired!", "error");

                setTimeout(() => {
                    resultBox.classList.add("hidden");
                    filePreview.classList.add("hidden");
                    fileInput.value = "";
                    progressContainer.classList.add("hidden");
                }, 2000);
            }

        }, 1000);
    }


    /* ================= COPY BUTTONS ================= */
    if (copyCodeBtn) {
        copyCodeBtn.addEventListener("click", () => {
            const code = generatedCode.textContent;
            navigator.clipboard.writeText(code);
            showToast("Code copied!", "success");
        });
    }

    if (copyLinkBtn) {
        copyLinkBtn.addEventListener("click", () => {
            const code = generatedCode.textContent;
            const fullLink = window.location.origin + "/download_direct/" + code;

            navigator.clipboard.writeText(fullLink);
            showToast("Download link copied!", "success");
        });
    }


    /* ================= THEME TOGGLE ================= */
    if (themeToggle) {

        // Load saved theme
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
    }

});
