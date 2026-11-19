import base64
import io
import json
import os
import re
from typing import List, Optional

import cv2
import numpy as np
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageDraw, ImageFilter
from pydantic import BaseModel

os.environ.setdefault("TORCH_HOME", "/tmp/torch_cache")

app = FastAPI(
    title="Articog Creative Operating Layer",
    description="AI Engineering Prototype: Brief Structuring, Multi-Channel Delivery & Automated Anti-Drift Review Gate",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Lazy-load lightweight pretrained MobileNetV3-Small for Brand Fidelity Scoring
# ---------------------------------------------------------------------------
_vision_model = None
_preprocess = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)


def get_vision_model():
    global _vision_model
    if _vision_model is None:
        weights = models.MobileNet_V3_Small_Weights.DEFAULT
        model = models.mobilenet_v3_small(weights=weights)
        model.classifier = torch.nn.Identity()
        model.eval()
        _vision_model = model
    return _vision_model


def extract_embedding(pil_img: Image.Image) -> np.ndarray:
    model = get_vision_model()
    tensor = _preprocess(pil_img.convert("RGB")).unsqueeze(0)
    with torch.no_grad():
        emb = model(tensor).squeeze(0).numpy()
    norm = np.linalg.norm(emb)
    return emb / (norm + 1e-8)


def compute_color_similarity(ref_pil: Image.Image, cand_pil: Image.Image) -> float:
    ref_bgr = cv2.cvtColor(np.array(ref_pil.convert("RGB")), cv2.COLOR_RGB2BGR)
    cand_bgr = cv2.cvtColor(np.array(cand_pil.convert("RGB")), cv2.COLOR_RGB2BGR)
    ref_hsv = cv2.cvtColor(ref_bgr, cv2.COLOR_BGR2HSV)
    cand_hsv = cv2.cvtColor(cand_bgr, cv2.COLOR_BGR2HSV)

    hist_ref = cv2.calcHist([ref_hsv], [0, 1], None, [32, 32], [0, 180, 0, 256])
    hist_cand = cv2.calcHist([cand_hsv], [0, 1], None, [32, 32], [0, 180, 0, 256])
    cv2.normalize(hist_ref, hist_ref, 0, 1, cv2.NORM_MINMAX)
    cv2.normalize(hist_cand, hist_cand, 0, 1, cv2.NORM_MINMAX)

    corr = cv2.compareHist(hist_ref, hist_cand, cv2.HISTCMP_CORREL)
    return float(np.clip((corr + 1.0) / 2.0 * 100.0, 0.0, 100.0))


def compute_sharpness_score(pil_img: Image.Image) -> float:
    gray = cv2.cvtColor(np.array(pil_img.convert("RGB")), cv2.COLOR_RGB2GRAY)
    lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    # Smooth saturation curve around typical sharp image variance (~250+)
    score = (lap_var / (lap_var + 120.0)) * 100.0
    return float(np.clip(score, 0.0, 100.0))


def evaluate_pair(ref_pil: Image.Image, cand_pil: Image.Image, label: str, preview_b64: Optional[str] = None) -> dict:
    ref_emb = extract_embedding(ref_pil)
    cand_emb = extract_embedding(cand_pil)

    raw_cos = float(np.dot(ref_emb, cand_emb))
    # Map real-world MobileNetV3 cosine similarity [0.15, 0.85] -> [0, 100]
    fidelity_score = float(np.clip(((raw_cos - 0.15) / 0.70) * 100.0, 0.0, 100.0))
    color_score = compute_color_similarity(ref_pil, cand_pil)
    sharpness_score = compute_sharpness_score(cand_pil)

    overall = round(0.45 * fidelity_score + 0.35 * color_score + 0.20 * sharpness_score, 1)

    issues = []
    if fidelity_score < 68:
        issues.append("Structural/silhouette drift from locked brand reference")
    if color_score < 65:
        issues.append("Color palette deviated from brand guidelines")
    if sharpness_score < 50:
        issues.append("Low sharpness / rendering blur detected")

    if overall >= 75.0:
        status = "APPROVED — Ready for Delivery"
        tier = "approved"
        diagnosis = "Matches locked product geometry, brand color language, and sharpness thresholds."
    elif overall >= 55.0:
        status = "REVIEW — Minor Drift"
        tier = "review"
        diagnosis = "; ".join(issues) if issues else "Minor variance detected; quick designer check advised."
    else:
        status = "REJECTED — Creative Drift Detected"
        tier = "rejected"
        diagnosis = "; ".join(issues) if issues else "Significant drift from locked reference; re-generate."

    return {
        "frame_name": label,
        "overall_score": overall,
        "fidelity_score": round(fidelity_score, 1),
        "color_score": round(color_score, 1),
        "sharpness_score": round(sharpness_score, 1),
        "status": status,
        "tier": tier,
        "diagnosis": diagnosis,
        "preview_b64": preview_b64,
    }


def pil_to_b64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")


# ---------------------------------------------------------------------------
# Tab 1: Brief & Channel Delivery System
# ---------------------------------------------------------------------------
class BriefRequest(BaseModel):
    brand_name: str
    audience: str
    offer: str
    service_track: str
    rough_idea: str
    api_key: Optional[str] = None


def fallback_brief_generator(req: BriefRequest) -> dict:
    brand = req.brand_name.strip() or "Brand X"
    audience = req.audience.strip() or "modern urban consumers"
    offer = req.offer.strip() or "signature flagship release"
    track = req.service_track.strip() or "AI Video Production"
    idea = req.rough_idea.strip() or "Showcase the product in an atmospheric commercial setting."

    return {
        "source": "Deterministic Structured Pipeline (No External Key Required)",
        "brief_spec": {
            "campaign_objective": f"Convert {audience} for {brand} around '{offer}' via {track}.",
            "locked_visual_language": "High-contrast editorial studio lighting, tactile surface realism, clean negative space, consistent hero product silhouette across every frame.",
            "camera_and_motion": "Controlled macro dolly-in, 35mm anamorphic depth-of-field, subtle natural light sweep, zero erratic morphing.",
            "rejection_criteria": [
                "Do NOT alter hero product proportions, label typography, or signature brand color palette.",
                "Reject cluttered backgrounds, distorted hands/faces, or over-saturated neon artifacts.",
                "Reject inconsistent lighting direction between hook shot and product hero shot.",
            ],
        },
        "storyboard": [
            {
                "shot": "Shot 1 · Hook (0–3s)",
                "visual": f"Tight macro texture reveal transitioning into {brand} hero silhouette emerging from dramatic shadow.",
                "camera": "Slow 15% push-in, shallow f/1.8 depth of field",
            },
            {
                "shot": "Shot 2 · Product Hero (3–8s)",
                "visual": f"Full unobstructed hero framing of {brand} highlighting craftsmanship and '{offer}'.",
                "camera": "Smooth 45-degree orbital arc, crisp rim light",
            },
            {
                "shot": "Shot 3 · Lifestyle Proof (8–12s)",
                "visual": f"Authentic everyday moment tailored for {audience} interacting naturally with {brand}.",
                "camera": "Handheld editorial natural motion, warm key light",
            },
            {
                "shot": "Shot 4 · Brand Lockup & CTA (12–15s)",
                "visual": f"Clean studio packshot of {brand} centered with space for typography and '{offer}'.",
                "camera": "Locked static tripod frame, subtle specular gleam",
            },
        ],
        "voiceover_script": (
            f"[0:00 - Confident, warm pacing] Built for {audience} who notice every detail. "
            f"[0:05 - Crisp emphasis] Meet {brand} — crafted around {offer}. "
            f"[0:11 - Direct, clean close] Experience the difference today."
        ),
        "channel_prompts": {
            "social_vertical_9_16": (
                f"Vertical 9:16 commercial frame for {brand}, {idea}. Center-weighted hero composition with top/bottom safe zones for captions, "
                f"tactile studio rim lighting, photorealistic 8k product fidelity, consistent brand colors, shot on 35mm lens --ar 9:16"
            ),
            "ad_creative_1_1": (
                f"Square 1:1 high-converting paid ad creative featuring {brand} ({offer}) for {audience}. Minimalist architectural backdrop, "
                f"sharp product label accuracy, soft directional studio shadows, clean negative space for headline --ar 1:1"
            ),
            "ai_video_16_9": (
                f"Cinematic 16:9 brand film shot for {brand}: {idea}. Slow controlled dolly movement, anamorphic lens flare, "
                f"consistent lighting continuity, zero geometry warping, commercial color grade --ar 16:9"
            ),
        },
    }


@app.post("/api/generate-brief")
async def generate_brief(req: BriefRequest):
    combined_text = f"{req.brand_name} {req.audience} {req.offer} {req.rough_idea}".strip()
    if len(re.findall(r"[a-zA-Z0-9]{2,}", combined_text)) < 2:
        raise HTTPException(
            status_code=422,
            detail="Please provide a recognizable Brand Name and a short campaign description.",
        )
    
    try:
        api_key = (req.api_key or "").strip() or os.environ.get("GEMINI_API_KEY", "").strip()

        if api_key:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            prompt = f"""
                You are a Senior Creative AI Systems Engineer at Articog (an AI-native film and ad production studio).
                Convert this rough client input into a zero-ambiguity production specification that prevents creative drift and prepares multi-channel delivery prompts.

                Brand/Product: {req.brand_name}
                Target Audience: {req.audience}
                Core Offer/Message: {req.offer}
                Service Track: {req.service_track}
                Rough Client Idea: {req.rough_idea}

                Return strictly valid JSON matching this exact schema:
                {{
                "source": "Live LLM Engine",
                "brief_spec": {{
                    "campaign_objective": "string",
                    "locked_visual_language": "string",
                    "camera_and_motion": "string",
                    "rejection_criteria": ["string", "string", "string"]
                }},
                "storyboard": [
                    {{"shot": "Shot 1 · Hook (0–3s)", "visual": "string", "camera": "string"}},
                    {{"shot": "Shot 2 · Product Hero (3–8s)", "visual": "string", "camera": "string"}},
                    {{"shot": "Shot 3 · Lifestyle Proof (8–12s)", "visual": "string", "camera": "string"}},
                    {{"shot": "Shot 4 · Brand Lockup & CTA (12–15s)", "visual": "string", "camera": "string"}}
                ],
                "voiceover_script": "string (15-second timed script with pacing cues)",
                "channel_prompts": {{
                    "social_vertical_9_16": "string",
                    "ad_creative_1_1": "string",
                    "ai_video_16_9": "string"
                }}
                }}
            """

            excluded_keywords = ("tts", "image", "audio", "embedding", "aqa", "vision")
            available = []
            try:
                for m in client.models.list():
                    name = m.name.replace("models/", "")
                    low = name.lower()
                    if ("gemini" in low or "gemma" in low) and not any(k in low for k in excluded_keywords):
                        available.append(name)
            except Exception:
                pass

            preferred = [m for m in available if "3." in m and "flash" in m]
            others = [m for m in available if m not in preferred]
            candidate_models = preferred + others + ["gemini-3.8-flash", "gemini-2.5-pro", "gemini-flash-latest"]

            last_err = ""
            for model_name in candidate_models[:8]:
                for attempt in range(2):
                    try:
                        config_kwargs = {"temperature": 0.4}
                        if "gemma" not in model_name.lower():
                            config_kwargs["response_mime_type"] = "application/json"

                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                            config=types.GenerateContentConfig(**config_kwargs),
                        )
                        raw_text = response.text.strip()
                        if raw_text.startswith("```"):
                            raw_text = raw_text.split("```")[1]
                            if raw_text.startswith("json"):
                                raw_text = raw_text[4:]
                        parsed = json.loads(raw_text.strip())
                        parsed["source"] = f"Live LLM Engine ({model_name})"
                        return JSONResponse(content=parsed)
                    except Exception as e:
                        last_err = str(e)
                        if "503" not in last_err:
                            break

            fallback = fallback_brief_generator(req)
            fallback["source"] = f"Deterministic Structured Pipeline (API fallback: {last_err[:50]})"
            return JSONResponse(content=fallback)

        # No API key provided -> directly use built-in deterministic generator
        return JSONResponse(content=fallback_brief_generator(req))

    except Exception as outer_err:
        print(f"[Unexpected route error]: {outer_err}")
        return JSONResponse(content=fallback_brief_generator(req))


# ---------------------------------------------------------------------------
# Tab 2: Automated Review & Anti-Drift Gate
# ---------------------------------------------------------------------------
@app.post("/api/review-gate")
async def review_gate(
    reference_image: UploadFile = File(...),
    candidate_images: List[UploadFile] = File(...),
):
    if not candidate_images:
        raise HTTPException(status_code=400, detail="Upload at least one candidate image.")

    ref_bytes = await reference_image.read()
    ref_pil = Image.open(io.BytesIO(ref_bytes)).convert("RGB")
    ref_preview = pil_to_b64(ref_pil.resize((240, 240)))

    results = []
    for idx, cand_file in enumerate(candidate_images[:4]):
        cand_bytes = await cand_file.read()
        cand_pil = Image.open(io.BytesIO(cand_bytes)).convert("RGB")
        cand_preview = pil_to_b64(cand_pil.resize((240, 240)))
        name = cand_file.filename or f"Candidate_Frame_{idx + 1}.png"
        results.append(evaluate_pair(ref_pil, cand_pil, name, cand_preview))

    return {"reference_preview": ref_preview, "results": results}


@app.post("/api/review-gate-demo")
async def review_gate_demo():
    """Generates a locked brand product image + 2 realistic AI candidates (1 aligned, 1 drifted)."""
    # 1. Locked Brand Reference: Matte-black & amber minimalist bottle label card
    ref = Image.new("RGB", (320, 320), (18, 18, 22))
    draw_r = ImageDraw.Draw(ref)
    draw_r.rounded_rectangle([95, 45, 225, 275], radius=24, fill=(32, 34, 40), outline=(217, 155, 67), width=4)
    draw_r.rectangle([110, 115, 210, 195], fill=(217, 155, 67))
    draw_r.rectangle([125, 135, 195, 150], fill=(18, 18, 22))
    draw_r.ellipse([142, 62, 178, 98], fill=(217, 155, 67))

    # 2. Candidate A: Brand-aligned studio render (slight lighting shift, preserves silhouette & amber palette)
    cand_good = Image.new("RGB", (320, 320), (26, 24, 28))
    draw_g = ImageDraw.Draw(cand_good)
    draw_g.rounded_rectangle([98, 48, 222, 272], radius=24, fill=(38, 40, 46), outline=(224, 165, 75), width=4)
    draw_g.rectangle([112, 118, 208, 194], fill=(224, 165, 75))
    draw_g.rectangle([127, 137, 193, 151], fill=(22, 22, 26))
    draw_g.ellipse([144, 65, 176, 97], fill=(224, 165, 75))

    # 3. Candidate B: Creative Drift (wrong geometry, off-brand teal/pink colors, blurred render)
    cand_drift = Image.new("RGB", (320, 320), (45, 110, 125))
    draw_d = ImageDraw.Draw(cand_drift)
    draw_d.ellipse([60, 70, 260, 260], fill=(215, 75, 140), outline=(255, 255, 255), width=3)
    draw_d.polygon([(160, 90), (220, 210), (100, 210)], fill=(90, 220, 190))
    cand_drift = cand_drift.filter(ImageFilter.GaussianBlur(radius=4.5))

    results = [
        evaluate_pair(ref, cand_good, "Candidate_01_StudioHero.png", pil_to_b64(cand_good)),
        evaluate_pair(ref, cand_drift, "Candidate_02_DriftedConcept.png", pil_to_b64(cand_drift)),
    ]
    return {"reference_preview": pil_to_b64(ref), "results": results}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "articog-creative-operating-layer"}


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    return FileResponse("static/index.html")

