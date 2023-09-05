conda activate paint
blender -b -P dp.py
blender -b -P seg_fine.py
python concat.py

python req_txt2img.py

python restore.py
python Tile.py
python Sres.py

blender -P render.py
python inpaint_from_side.py
python Sres_inpaint.py
python brinting.py
blender -P render_inpaint.py
python inpaint_fusion.py
python Tex_Remap.py
python Tex_tile.py
python Tex_sres.py
blender -P render_remap.py