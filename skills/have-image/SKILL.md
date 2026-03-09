---
name: have-image
description: Search and generate images. Use when user needs stock photos (Unsplash), AI-generated images (Pollinations/Gemini), or to find logos/people photos (Google).
---

# Have Image

Find or generate images for any purpose.

## When to use

- User needs an image for a project, presentation, or document
- User asks for a logo, photo of a person, or specific visual
- User wants to generate custom illustrations or AI art
- User needs stock photos or backgrounds

## Available tools

| Tool | Best for | Command |
|------|----------|---------|
| **unsplash** | Stock photos, backgrounds | `scripts/unsplash "query" [count]` |
| **pollinations** | AI generation (free) | `scripts/pollinations "prompt" [output.png]` |
| **google** | Logos, people photos | `scripts/google "query" [count]` |
| **gemini** | AI generation (quality) | `scripts/gemini "prompt" [output.png]` |

## Quick reference

```bash
# Stock photo
scripts/unsplash "modern office" 5

# AI generated
scripts/pollinations "happy team meeting, illustration style" team.png

# Find a logo
scripts/google "Stripe logo transparent png"

# Find person photo
scripts/google "Elon Musk headshot"

# High quality AI (requires GEMINI_API_KEY)
scripts/gemini "minimalist app icon, blue gradient" icon.png
```

## Workflow

1. **Understand need** → stock photo? AI generated? specific person/logo?
2. **Pick tool** → Unsplash for real photos, Pollinations/Gemini for custom, Google for specific
3. **Run script** → get URLs or generate file
4. **Show user** → present options, let them pick
5. **Download** → `curl -Lo image.jpg "URL"` if needed

## Examples

| User says | Tool | Why |
|-----------|------|-----|
| "find me a background for my slides" | unsplash | Generic stock photo |
| "create an illustration of a robot" | pollinations | Custom AI art |
| "get the Notion logo" | google | Specific brand asset |
| "photo of Sam Altman" | google | Specific person |
| "generate a professional app icon" | gemini | High quality AI |

## Upscaling / HD Recreation

Pour recréer une image basse résolution en haute qualité avec Gemini:

```bash
# Utiliser l'outil otomata avec --style-reference-file et --style-guidelines
cd /data/alexis/otomata && source app/venv/bin/activate && \
python3 app/tools/media/gemini-genai/generate_image.py \
  --prompt "Description courte de l'image" \
  --style-reference-file /chemin/vers/image_source.png \
  --style-guidelines "Match the pose, lighting, background and overall aesthetic of the reference image exactly. High resolution, sharp details, photorealistic." \
  --output-dir /chemin/output/
```

**Clés du succès:**
- `--prompt`: description factuelle courte (sujet, contexte)
- `--style-reference-file`: image source comme référence
- `--style-guidelines`: demander de matcher l'esthétique exacte + "high resolution, sharp details"

**Ce qui ne marche PAS:**
- Demander "upscale" directement (filtré par Gemini)
- Demander de reproduire "exactly this person" (filtré)
- Prompt trop long ou trop technique

**Alternative Real-ESRGAN** (upscaling pur, sans régénération):
```bash
# Télécharger si nécessaire
cd /tmp && wget -q https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-ubuntu.zip -O realesrgan.zip && unzip -qo realesrgan.zip -d realesrgan && chmod +x realesrgan/realesrgan-ncnn-vulkan

# Upscale x4
/tmp/realesrgan/realesrgan-ncnn-vulkan -i input.png -o output.png -n realesrgan-x4plus
```
⚠️ L'upscaling pur sur images trop petites (<300px) crée un effet "peinture" artificiel.

## Tips

- Unsplash returns direct URLs, ready to download
- Pollinations is free but lower quality than Gemini
- Google Images may require manual selection (JS rendering)
- Always show multiple options when possible
- Pour HD recreation: préférer Gemini avec référence plutôt que upscaling pur
