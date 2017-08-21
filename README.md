# blender_save_object_keyframes

Provide function set to export keyframes or positions of objects.

![screenshot.png](https://github.com/Drunkar/blender_save_object_keyframes/blob/images/screenshot.png?raw=true)


## Features
- Save object keyframes
- Save material keyframes
- Save seletion positions
- Save vertices positions of mesh


## Feature 1: Save object keyframes

Save keyframes of object, which matched a keyword as CSV.

- location: 3D View > Objet > Animation
- shortcut: `ctrl+alt+K`

### output csv format:


　|　
:--|:--
column1|object_id
column2|frame
column3|location_0
column4|location_1
column5|location_2
column6|rotation_euler_0
column7|rotation_euler_1
column8|rotation_euler_2
column9|sale_0
column10|scale_1
column11|scale_2


### input parameters:

name|type|description
:--|:--|:--
id key|string|Regular expresson to specify objects.
start frame|integer| Start frame to specify the target term.
end frame|integer| End frame to specify the target term.
export file name|string|Output CSV file name. Output csv directory is the same as .blend file.


## Feature 2: Save material keyframes

Save keyframes of object's active material, which matched a keyword as CSV.

- location: 3D View > Objet > Animation

### output csv format:


　|　
:--|:--
column1|object_id
column2|frame
column3|diffuse_color_r
column4|diffuse_color_g
column5|diffuse_color_b
column6|specular_color_r
column7|specular_color_g
column8|specular_color_b
column9|emit
column10|ambient
column11|translucency


### input parameters:

name|type|description
:--|:--|:--
id key|string|Regular expresson to specify objects.
start frame|integer| Start frame to specify the target term.
end frame|integer| End frame to specify the target term.
export file name|string|Output CSV file name. Output csv directory is the same as .blend file.


## Feature 3: Save seletion positions

Save selected objects' current positions as CSV.

- location: 3D View > Objet > Animation


## Feature 4: Save vertices positions of mesh

Save vertices' positions of active mesh.

- location: 3D View > Objet > Animation
