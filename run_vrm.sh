conda activate paint
blender -b -P dp.py
blender -b -P seg_fine.py
python concat.py

python req_txt2img.py

python restore.py
python Tile.py
python Sres.py

blender -P render_vrm.py
