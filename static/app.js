const modeSelect = document.getElementById("mode");
const modeHint = document.getElementById("modeHint");
const ivField = document.getElementById("ivField");
const keyInput = document.getElementById("key");
const ivInput = document.getElementById("iv");
const generateKeyButton = document.getElementById("generateKey");
const generateIvButton = document.getElementById("generateIv");

const fileForm = document.getElementById("fileForm");
const fileMessage = document.getElementById("fileMessage");
const downloadLink = document.getElementById("downloadLink");
const fileIv = document.getElementById("fileIv");
const fileDuration = document.getElementById("fileDuration");

const textForm = document.getElementById("textForm");
const textOutput = document.getElementById("textOutput");
const textIv = document.getElementById("textIv");
const textDuration = document.getElementById("textDuration");

const modeTips = {
  CBC: "CBC được khuyến nghị cho hầu hết trường hợp, cần IV ngẫu nhiên.",
  CFB: "CFB phù hợp dữ liệu luồng, cũng cần IV.",
  ECB: "ECB không khuyến nghị vì lộ mẫu dữ liệu.",
};

const updateModeUI = () => {
  const mode = modeSelect.value;
  modeHint.textContent = modeTips[mode] || "";
  ivField.style.display = mode === "ECB" ? "none" : "block";
};

const randomHex = (length) => {
  const bytes = new Uint8Array(length / 2);
  crypto.getRandomValues(bytes);
  return Array.from(bytes)
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
};

if (modeSelect) {
  updateModeUI();
  modeSelect.addEventListener("change", updateModeUI);
}

if (generateKeyButton) {
  generateKeyButton.addEventListener("click", async () => {
    const response = await fetch("/api/generate-key", { method: "POST" });
    if (!response.ok) {
      return;
    }
    const data = await response.json();
    keyInput.value = data.key_hex;
  });
}

if (generateIvButton) {
  generateIvButton.addEventListener("click", () => {
    ivInput.value = randomHex(16);
  });
}

const gatherSharedFields = () => {
  return {
    mode: modeSelect.value,
    key: keyInput.value,
    iv: ivInput.value,
  };
};

if (textForm) {
  textForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    textOutput.textContent = "Đang xử lý...";
    textIv.textContent = "";
    textDuration.textContent = "";

    const formData = new FormData(textForm);
    const shared = gatherSharedFields();
    formData.set("mode", shared.mode);
    formData.set("key", shared.key);
    formData.set("iv", shared.iv);

    const response = await fetch("/process-text", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    if (!response.ok) {
      textOutput.textContent = data.error || "Có lỗi xảy ra.";
      return;
    }

    textOutput.textContent = data.result;
    if (data.iv_used) {
      textIv.textContent = `IV sử dụng: ${data.iv_used}`;
    }
    textDuration.textContent = `Thời gian: ${data.duration_ms} ms`;
  });
}

if (fileForm) {
  fileForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    fileMessage.textContent = "Đang xử lý...";
    fileIv.textContent = "";
    fileDuration.textContent = "";
    downloadLink.hidden = true;

    const formData = new FormData(fileForm);
    const shared = gatherSharedFields();
    formData.set("mode", shared.mode);
    formData.set("key", shared.key);
    formData.set("iv", shared.iv);

    const response = await fetch("/process-file", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const data = await response.json();
      fileMessage.textContent = data.error || "Có lỗi xảy ra.";
      return;
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const disposition = response.headers.get("Content-Disposition") || "";
    const match = disposition.match(/filename="?([^";]+)"?/);
    const filename = match ? match[1] : "output.bin";

    downloadLink.href = url;
    downloadLink.download = filename;
    downloadLink.hidden = false;
    downloadLink.textContent = `Tải về ${filename}`;
    fileMessage.textContent = "Xử lý thành công.";

    const ivUsed = response.headers.get("X-IV-Used");
    const duration = response.headers.get("X-Duration-Ms");
    if (ivUsed) {
      fileIv.textContent = `IV sử dụng: ${ivUsed}`;
    }
    if (duration) {
      fileDuration.textContent = `Thời gian: ${duration} ms`;
    }
  });
}
