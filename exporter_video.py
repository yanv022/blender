# Calcule les images de l'animation dans un dossier temporaire.
# Reprise possible : les images deja calculees ne sont pas refaites.
# Lance par exporter_video.cmd, qui assemble ensuite la video avec ffmpeg.

import bpy, os, tempfile

sc = bpy.context.scene
r = sc.render
out = os.path.join(tempfile.gettempdir(), "usine-bauxite-images")
os.makedirs(out, exist_ok=True)

ims = r.image_settings
if hasattr(ims, "media_type"):
    ims.media_type = 'IMAGE'
ims.file_format = 'JPEG'
ims.quality = 95
r.resolution_x, r.resolution_y, r.resolution_percentage = 1280, 720, 100
r.filepath = os.path.join(out, "img_####")
r.use_file_extension = True
r.use_overwrite = False          # ne recalcule pas une image existante
r.use_placeholder = False
try:
    sc.eevee.taa_render_samples = 12
except Exception:
    pass

bpy.ops.render.render(animation=True)
print("IMAGES_OK", len([f for f in os.listdir(out) if f.endswith(".jpg")]))
