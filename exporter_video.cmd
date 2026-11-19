@echo off
rem Exporte l'animation en video MP4 (double-clic pour relancer).
rem Etape 1 : Blender calcule les images. Etape 2 : ffmpeg les assemble.
cd /d "%~dp0"
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b "usine-bauxite-alumine-animation.blend" --python "exporter_video.py" > "%TEMP%\usine-export.log" 2>&1
"%LOCALAPPDATA%\Microsoft\WinGet\Links\ffmpeg.exe" -y -framerate 24 -i "%TEMP%\usine-bauxite-images\img_%%04d.jpg" -c:v libx264 -pix_fmt yuv420p -crf 18 -movflags +faststart "simulation-bauxite-alumine.mp4" >> "%TEMP%\usine-export.log" 2>&1
echo EXPORT_TERMINE %ERRORLEVEL% >> "%TEMP%\usine-export.log"
