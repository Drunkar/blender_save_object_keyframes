# blender_save_object_keyframes

Provide function set to export keyframes or positions of objects.

![screenshot.png](https://github.com/Drunkar/blender_save_object_keyframes/blob/images/screenshot.png?raw=true)


## Features
- Save keyframes
- Save seletion positions
- Save vertices positions of mesh


## Feature 1: Save keyframes

Save keyframes of object, which matched a keyword as CSV.

- location: 3D View > Objet > Animation
- shortcut: `ctrl+alt+K`

parameters:

name|type|description
:--|:--|:--
id key|string|Regular expresson to specify objects.
start frame|integer| Start frame to specify the target term.
end frame|integer| End frame to specify the target term.
export file name|string|Output CSV file name. Output csv directory is the same as .blend file.


## Feature 2: Save seletion positions

Save selected objects' current positions as CSV.

- location: 3D View > Objet > Animation


## Feature 3: Save vertices positions of mesh

Save vertices' positions of active mesh.

- location: 3D View > Objet > Animation
