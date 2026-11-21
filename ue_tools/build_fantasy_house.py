# FantasyWorld - procedural medieval cottage test for Unreal Engine 5.9
# Run in Unreal Editor Python console: exec(open(r"F:/GitHub/new-3d-game/ue_tools/build_fantasy_house.py", encoding="utf-8").read())
# Builds in the currently open level. Save a NEW level first to protect ThirdPersonExampleMap.
import unreal
import math
import random

random.seed(17)
editor = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
meshes = {
    "cube": unreal.load_asset("/Engine/BasicShapes/Cube.Cube"),
    "cylinder": unreal.load_asset("/Engine/BasicShapes/Cylinder.Cylinder"),
    "cone": unreal.load_asset("/Engine/BasicShapes/Cone.Cone"),
}
def mat(name, color, roughness=0.86, metallic=0.0):
    path = "/Game/FantasyHouse/Materials"
    unreal.EditorAssetLibrary.make_directory(path)
    full = path + "/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        return unreal.load_asset(full)
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    m = asset_tools.create_asset(name, path, unreal.Material, unreal.MaterialFactoryNew())
    unreal.MaterialEditingLibrary.set_material_property(m, unreal.MaterialProperty.MP_BASE_COLOR, unreal.LinearColor(*color, 1.0)) if False else None
    # Use material instance parameters via a material graph constant-vector node.
    node = unreal.MaterialEditingLibrary.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -400, 0)
    node.set_editor_property("parameter_name", "Color")
    node.set_editor_property("default_value", unreal.LinearColor(*color, 1.0))
    unreal.MaterialEditingLibrary.connect_material_property(node, "", unreal.MaterialProperty.MP_BASE_COLOR)
    r = unreal.MaterialEditingLibrary.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -400, 240)
    r.set_editor_property("parameter_name", "Roughness")
    r.set_editor_property("default_value", roughness)
    unreal.MaterialEditingLibrary.connect_material_property(r, "", unreal.MaterialProperty.MP_ROUGHNESS)
    unreal.MaterialEditingLibrary.recompile_material(m)
    unreal.EditorAssetLibrary.save_loaded_asset(m)
    return m

stone = mat("M_WeatheredStone", (0.31,0.30,0.27))
stone2 = mat("M_DarkStone", (0.19,0.19,0.18))
timber = mat("M_OldTimber", (0.16,0.085,0.044))
timber2 = mat("M_WarmTimber", (0.25,0.14,0.072))
roof = mat("M_RoofSlate", (0.105,0.13,0.15))
roof2 = mat("M_RoofSlateAlt", (0.15,0.17,0.18))
glass = mat("M_AmberGlass", (0.92,0.52,0.13))
door = mat("M_Door", (0.12,0.055,0.027))
metal = mat("M_Iron", (0.055,0.058,0.061), 0.4, 0.65)
moss = mat("M_Moss", (0.10,0.19,0.09))
ground = mat("M_Dirt", (0.20,0.17,0.12))

def piece(name, pos, scale, material, mesh="cube", rotation=(0,0,0)):
    actor = editor.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*pos), unreal.Rotator(*rotation))
    actor.set_actor_label("FH_" + name)
    comp = actor.static_mesh_component
    comp.set_static_mesh(meshes[mesh])
    comp.set_material(0, material)
    # BasicShapes Cube is 100cm wide
    actor.set_actor_scale3d(unreal.Vector(*scale))
    return actor

# Dimensions in centimeters: 820 x 620, ground level z=0.
# Keep house at origin; separate level strongly recommended.
piece("Foundation", (0,0,35), (8.8,6.8,0.7), stone2)
piece("Ground", (0,0,-25), (18,16,0.45), ground)
# Stone masonry walls, with front entrance opening.
for x in (-350,350):
    piece("SideWall", (x,0,210), (1.2,6.2,3.4), stone)
piece("BackWall", (0,275,210), (7.0,0.7,3.4), stone)
for x in (-260,260):
    piece("FrontPier", (x,-275,210), (1.8,0.7,3.4), stone)
piece("DoorLintel", (0,-275,375), (3.4,0.75,0.6), stone)
piece("FrontDoor", (0,-316,165), (1.65,0.18,2.75), door)
# Timber frame and visible beams.
for x in (-380,-200,0,200,380):
    for y in (-305,305):
        piece("VerticalOakPost", (x,y,260), (0.22,0.25,4.6), timber)
for y in (-305,305):
    for z in (110,450):
        piece("HorizontalOakBeam", (0,y,z), (8.0,0.27,0.24), timber)
for x in (-380,380):
    piece("SideEave", (x,0,465), (0.24,6.8,0.24), timber)
# Roof: two pitched planes along Y axis. Roof ridge z 780, eaves z 450.
# Rotating a 100cm cube about Y creates roof slope along X.
roof_angle = 42
for side in (-1,1):
    piece("RoofPlane", (side*195,0,625), (5.25,7.5,0.18), roof, rotation=(0,side*-roof_angle,0))
    # Rows of individually staggered slate tiles add readable depth.
    for row in range(7):
        x = side*(55 + row*54)
        z = 765 - row*48
        for col in range(12):
            y = -345 + col*63 + (row%2)*25
            piece("RoofTile", (x,y,z+14), (0.80,0.69,0.065), roof2 if (row+col)%5 else roof, rotation=(0,side*-roof_angle,0))
# Gable timber trim
piece("RidgeCap", (0,0,805), (0.22,7.8,0.16), timber)
for y in (-345,345):
    for side in (-1,1):
        piece("GableRafter", (side*188,y,620), (5.3,0.22,0.18), timber, rotation=(0,side*-roof_angle,0))
# Doors and wrought iron bands
for z in (100,170,240):
    piece("DoorIronBand", (0,-331,z), (1.6,0.07,0.075), metal)
piece("DoorHandle", (55,-346,165), (0.09,0.10,0.20), metal)
# Windows as layered inset details; glass panels on facade
for x in (-245,245):
    piece("WindowGlass", (x,-319,270), (1.15,0.08,1.35), glass)
    for dx in (-65,65):
        piece("WindowSideTrim", (x+dx,-336,270), (0.15,0.17,1.60), timber)
    for dz in (-77,77):
        piece("WindowTopBottom", (x,-337,270+dz), (1.48,0.17,0.16), timber)
    piece("WindowCrossV", (x,-341,270), (0.10,0.15,1.45), timber)
    piece("WindowCrossH", (x,-343,270), (1.30,0.15,0.10), timber)
    piece("WindowSill", (x,-347,185), (1.7,0.34,0.14), stone2)
# Chimney and cap
piece("Chimney", (225,115,780), (1.05,0.95,3.2), stone2)
piece("ChimneyCap", (225,115,955), (1.35,1.22,0.20), stone)
# Stone doorstep and path
piece("Step", (0,-395,40), (2.7,1.2,0.3), stone2)
for i in range(8):
    piece("PathStone", (random.uniform(-30,30),-510-i*95,2), (random.uniform(1.3,2.0),0.65,0.08), stone)
# Extra foundation rocks and moss at corners
for i in range(28):
    x = random.choice((-1,1))*random.uniform(320,440)
    y = random.uniform(-330,330)
    piece("LooseStone", (x,y,random.uniform(15,30)), (random.uniform(.35,.8),random.uniform(.35,.7),random.uniform(.25,.5)), stone2)
for i in range(18):
    x = random.choice((-1,1))*random.uniform(340,430)
    y = random.uniform(-330,330)
    piece("MossPatch", (x,y,random.uniform(40,85)), (random.uniform(.25,.6),.12,.16), moss)
unreal.log("Fantasy house test created. Save your level. All actors prefixed FH_.")
