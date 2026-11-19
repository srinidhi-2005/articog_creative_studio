let latestBriefData = null;

const PRESETS = {
  coffee: {
    brand: "Deccan Roast Cold Brew",
    track: "AI Video Production",
    audience: "Urban tech professionals & founders in Hyderabad, ages 24–38",
    offer: "18-hour single-origin Chikmagalur cold brew in matte-black amber glass",
    idea: "We want a sleek 15-second launch ad showing our matte-black coffee bottle condensation in morning sunlight, transitioning from a quiet minimalist desk to an energetic workday boost.",
  },
  ring: {
    brand: "Aether Chrono Smart Ring",
    track: "Ad Creative",
    audience: "Tech-savvy founders and athletes in Bengaluru & Hyderabad, ages 26–42",
    offer: "Grade-5 brushed titanium health ring with 7-day battery and zero monthly subscription",
    idea: "Show the brushed titanium ring floating above dark volcanic basalt stone with a subtle emerald biometric sensor glow, then cut to an early-morning runner checking recovery metrics before sunrise.",
  },
  serum: {
    brand: "Narmada Botanicals Kumkumadi Serum",
    track: "Social Creative",
    audience: "Skincare-conscious women in metro India, ages 22–35",
    offer: "Cold-pressed Kashmiri saffron & sandalwood night elixir in frosted terracotta dropper glass",
    idea: "Create a warm golden-hour Instagram Reel showing a single drop of saffron serum catching sunlight on a travertine marble tray next to raw saffron strands, ending with a clean packshot.",
  },
};

function toggleKeyBar() {
  document.getElementById("keyBar").classList.toggle("hidden");
}

function updateKeyIndicator() {
  const val = document.getElementById("apiKeyInput").value.trim();
  const ind = document.getElementById("keyStatusIndicator");
  if (val) {
    ind.textContent = "Custom Key Active";
    ind.className = "mono text-xs text-emerald-400 hidden sm:inline";
  } else {
    ind.textContent = "Default Engine";
    ind.className = "mono text-xs text-zinc-400 hidden sm:inline";
  }
}

function switchTab(num) {
  [1, 2, 3].forEach((i) => {
    document.getElementById(`tab${i}`).classList.toggle("hidden", i !== num);
    const btn = document.getElementById(`tabBtn${i}`);
    btn.className =
      i === num
        ? "tab-active px-5 py-2.5 rounded-xl text-sm sm:text-base transition flex items-center gap-2"
        : "tab-inactive px-5 py-2.5 rounded-xl text-sm sm:text-base transition flex items-center gap-2";
  });
}

function loadPreset(key) {
  const p = PRESETS[key];
  if (!p) return;
  document.getElementById("brandName").value = p.brand;
  document.getElementById("serviceTrack").value = p.track;
  document.getElementById("audience").value = p.audience;
  document.getElementById("offer").value = p.offer;
  document.getElementById("roughIdea").value = p.idea;
}

async function generateBrief() {
  const status = document.getElementById("briefStatus");
  const btn = document.getElementById("generateBriefBtn");
  const spinner = document.getElementById("briefBtnSpinner");
  const btnText = document.getElementById("briefBtnText");

  const brand = document.getElementById("brandName").value.trim();
  const idea = document.getElementById("roughIdea").value.trim();

  // Require at least a real brand name or rough idea (with letters/numbers, not pure symbols)
  const hasValidBrand = /[a-zA-Z0-9]{2,}/.test(brand);
  const hasValidIdea = /[a-zA-Z0-9]{3,}/.test(idea);

  if (!hasValidBrand && !hasValidIdea) {
    status.textContent = "⚠ Please enter a valid Brand Name or a brief campaign idea (or click a Quick Preset above).";
    status.className = "text-sm text-amber-400";
    return;
  }
  
  status.className = "text-sm text-zinc-300";
  status.textContent = "Structuring brief & multi-channel prompts...";
  btn.disabled = true;
  spinner.classList.remove("hidden");
  btnText.textContent = "Generating...";

  const payload = {
    brand_name: document.getElementById("brandName").value,
    service_track: document.getElementById("serviceTrack").value,
    audience: document.getElementById("audience").value,
    offer: document.getElementById("offer").value,
    rough_idea: document.getElementById("roughIdea").value,
    api_key: document.getElementById("apiKeyInput").value,
  };

  try {
    const res = await fetch("/api/generate-brief", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    latestBriefData = data;
    renderBrief(data);
    status.textContent = "";
  } catch (err) {
    status.textContent = "Error generating brief.";
  } finally {
    btn.disabled = false;
    spinner.classList.add("hidden");
    btnText.textContent = "Generate Production Pack →";
  }
}

function renderBrief(data) {
  document.getElementById("briefOutput").classList.remove("hidden");
  document.getElementById("briefSourceBadge").textContent =
    data.source || "Structured Engine";
  document.getElementById("outObjective").textContent =
    data.brief_spec.campaign_objective;
  document.getElementById("outVisualLang").textContent =
    data.brief_spec.locked_visual_language;
  document.getElementById("outCameraRules").textContent =
    data.brief_spec.camera_and_motion;

  const rejList = document.getElementById("outRejectionList");
  rejList.innerHTML = "";
  (data.brief_spec.rejection_criteria || []).forEach((item) => {
    const li = document.createElement("li");
    li.className = "flex items-start gap-2.5";
    li.innerHTML = `<span class="text-rose-400 mt-0.5">•</span><span>${item}</span>`;
    rejList.appendChild(li);
  });

  const sbGrid = document.getElementById("outStoryboardGrid");
  sbGrid.innerHTML = "";
  (data.storyboard || []).forEach((s) => {
    sbGrid.innerHTML += `
      <div class="sub-card p-4 sm:p-5 flex flex-col justify-between gap-3">
        <div class="space-y-2">
          <div class="mono text-xs sm:text-sm font-semibold text-white">${s.shot}</div>
          <p class="text-sm text-zinc-200 leading-relaxed">${s.visual}</p>
        </div>
        <div class="mono text-xs text-zinc-400 pt-2.5 border-t border-white/[0.08]">🎥 ${s.camera}</div>
      </div>
    `;
  });

  document.getElementById("outVoiceover").textContent = data.voiceover_script;
  document.getElementById("prompt916").textContent =
    data.channel_prompts.social_vertical_9_16;
  document.getElementById("prompt11").textContent =
    data.channel_prompts.ad_creative_1_1;
  document.getElementById("prompt169").textContent =
    data.channel_prompts.ai_video_16_9;
}

function showToast(msg = "✓ Copied to clipboard") {
  const toast = document.getElementById("toast");
  toast.textContent = msg;
  toast.classList.remove("hidden");
  clearTimeout(window._toastTimer);
  window._toastTimer = setTimeout(() => toast.classList.add("hidden"), 1800);
}

function copyText(elementId) {
  const text = document.getElementById(elementId).textContent;
  navigator.clipboard.writeText(text);
  showToast("✓ Copied to clipboard");
}

function downloadBriefJson() {
  if (!latestBriefData) return;
  const blob = new Blob([JSON.stringify(latestBriefData, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "articog_production_pack.json";
  a.click();
  URL.revokeObjectURL(url);
  showToast("↓ Downloaded JSON manifest");
}

function previewSelectedFiles(type) {
  if (type === "ref") {
    const file = document.getElementById("refImageInput").files[0];
    const container = document.getElementById("refSelectPreview");
    if (!file) return;
    const url = URL.createObjectURL(file);
    container.innerHTML = `
      <img src="${url}" class="w-14 h-14 rounded-lg object-cover border border-white/25" />
      <span class="text-sm text-zinc-100 truncate">${file.name}</span>
    `;
  } else {
    const files = document.getElementById("candImagesInput").files;
    const container = document.getElementById("candSelectPreview");
    if (!files || files.length === 0) return;
    container.innerHTML = "";
    Array.from(files).slice(0, 4).forEach((f) => {
      const url = URL.createObjectURL(f);
      container.innerHTML += `
        <div class="relative">
          <img src="${url}" title="${f.name}" class="w-14 h-14 rounded-lg object-cover border border-white/25" />
        </div>
      `;
    });
  }
}

async function runDemoDriftTest() {
  const status = document.getElementById("qcStatus");
  status.textContent = "Running PyTorch MobileNetV3 + OpenCV drift inspection...";
  try {
    const res = await fetch("/api/review-gate-demo", { method: "POST" });
    const data = await res.json();
    renderQcResults(data);
    status.textContent = "Demo inspection complete.";
  } catch (err) {
    status.textContent = "Error running demo inspection.";
  }
}

async function runCustomReviewGate() {
  const refFile = document.getElementById("refImageInput").files[0];
  const candFiles = document.getElementById("candImagesInput").files;
  const status = document.getElementById("qcStatus");

  if (!refFile || candFiles.length === 0) {
    status.textContent = "Select 1 reference image and at least 1 candidate image first.";
    return;
  }

  status.textContent = "Extracting MobileNetV3 embeddings & HSV color histograms...";
  const formData = new FormData();
  formData.append("reference_image", refFile);
  for (let i = 0; i < Math.min(candFiles.length, 4); i++) {
    formData.append("candidate_images", candFiles[i]);
  }

  try {
    const res = await fetch("/api/review-gate", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    renderQcResults(data);
    status.textContent = "Inspection complete.";
  } catch (err) {
    status.textContent = "Error evaluating images.";
  }
}

function renderQcResults(data) {
  document.getElementById("qcOutput").classList.remove("hidden");
  document.getElementById("refPreviewImg").src = data.reference_preview;

  const grid = document.getElementById("qcResultsGrid");
  grid.innerHTML = "";

  data.results.forEach((item) => {
    const badgeClass =
      item.tier === "approved"
        ? "badge-approved"
        : item.tier === "review"
        ? "badge-review"
        : "badge-rejected";

    const barColor =
      item.tier === "approved"
        ? "bg-emerald-400"
        : item.tier === "review"
        ? "bg-amber-400"
        : "bg-rose-400";

    grid.innerHTML += `
      <div class="sub-card p-5 sm:p-6 space-y-4">
        <div class="flex items-center gap-4">
          <img src="${item.preview_b64}" class="w-20 h-20 rounded-xl object-cover border border-white/20" />
          <div class="min-w-0 flex-1">
            <div class="mono text-xs sm:text-sm text-zinc-300 truncate">${item.frame_name}</div>
            <div class="text-2xl sm:text-3xl font-bold text-white mt-0.5">${item.overall_score}% <span class="text-xs sm:text-sm font-normal text-zinc-400">Overall Match</span></div>
            <span class="mono inline-block mt-1.5 text-xs px-3 py-0.5 rounded-full border ${badgeClass}">${item.status}</span>
          </div>
        </div>

        <div class="space-y-2.5 text-sm">
          <div class="flex justify-between text-zinc-300"><span>Brand Reference Fidelity (PyTorch)</span><span class="mono text-white font-medium">${item.fidelity_score}%</span></div>
          <div class="w-full bg-white/[0.08] h-2 rounded-full overflow-hidden"><div class="${barColor} h-full rounded-full" style="width:${item.fidelity_score}%"></div></div>

          <div class="flex justify-between text-zinc-300 pt-1"><span>Color Language Consistency (OpenCV)</span><span class="mono text-white font-medium">${item.color_score}%</span></div>
          <div class="w-full bg-white/[0.08] h-2 rounded-full overflow-hidden"><div class="${barColor} h-full rounded-full" style="width:${item.color_score}%"></div></div>

          <div class="flex justify-between text-zinc-300 pt-1"><span>Render Sharpness / Artifact Check</span><span class="mono text-white font-medium">${item.sharpness_score}%</span></div>
          <div class="w-full bg-white/[0.08] h-2 rounded-full overflow-hidden"><div class="${barColor} h-full rounded-full" style="width:${item.sharpness_score}%"></div></div>
        </div>

        <p class="text-sm text-zinc-300 pt-2.5 border-t border-white/[0.09] leading-relaxed">${item.diagnosis}</p>
      </div>
    `;
  });
}

