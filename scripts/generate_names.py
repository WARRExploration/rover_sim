from PIL import Image, ImageDraw, ImageFont
from lxml import etree
from shutil import copy2
import os
import copy

def create_name_texture(name, path):

    font_size = 80
    size = (600, 300)
    # base image
    # Gazebo doesn't support transparent textures :(
    img = Image.new('RGBA', size, (255,255,255,255))

    # get a font
    fnt = ImageFont.truetype('../resources/names/DejaVuSans-Bold.ttf', font_size)
    # get a drawing context
    d = ImageDraw.Draw(img)

    # draw a blue frame
    # color from warr logo
    margin = 15
    width = 10
    d.rectangle((margin, margin, size[0]-margin, size[1]-margin), fill=(102,163,215,255))
    d.rectangle(((margin+width), (margin+width), size[0]-(margin+width), size[1]-(margin+width)), fill=(255,255,255,255))
    
    # draw the name
    ts = d.textsize(name, fnt)
    y_correction=0.875 # font not centered vertically
    d.text(( (img.size[0]-ts[0])/2, (img.size[1]-ts[1])/2 * y_correction), name, font=fnt, fill=(0,101,189,255))

    #img.show() 
    img.save(path)
    return



def create_mesh(file,path):
    with open(file) as f:
        newText=f.read().replace('<init_from>texture_default.png</init_from>',
                                '<init_from>../textures/texture_name.png</init_from>')

    with open(path, "w") as f:
        f.write(newText)
    return



def create_model_config(name, path):
    config = etree.Element('model')

    name_e = etree.Element('name')
    name_e.text = name

    version = etree.Element('version')
    version.text = '1.0'

    sdf = etree.Element('sdf')
    sdf.set('version', '1.6')
    sdf.text = 'model.sdf'

    config.append(name_e)
    config.append(version)
    config.append(sdf)

    tree = etree.ElementTree(config)
    tree.write(path, pretty_print=True, encoding='utf8', xml_declaration=True)
    #print(etree.tostring(config, pretty_print=True, encoding='utf8', xml_declaration=True))
    return



def create_model_sdf(name, pose_s, path, path_visual):
    sdf = etree.Element('sdf')
    sdf.set('version', '1.6')

    model = etree.Element('model')
    model.set('name', name)

    pose = etree.Element('pose')
    pose.text = pose_s

    static = etree.Element('static')
    static.text = 'true'

    link = etree.Element('link')
    link.set('name', 'link')


    visual = etree.Element('visual')
    visual.set('name', 'visual')
    geometry = etree.Element('geometry')

    mesh = etree.Element('mesh')
    uri = etree.Element('uri')
    uri.text = path_visual
    
    mesh.append(uri)
    geometry.append(mesh)
    visual.append(geometry)


    link.append(visual)
    
    model.append(link)
    
    model.append(pose)
    model.append(static)
    model.append(link)

    sdf.append(model)


    tree = etree.ElementTree(sdf)
    tree.write(path, pretty_print=True, encoding='utf8', xml_declaration=True)
    #print(etree.tostring(sdf, pretty_print=True, encoding='utf8', xml_declaration=True))
    return





def create_all(name, pose):
    # in 'roversim/src/scripts/names''

    os.system('mkdir -p ' + '../models/names/' + name + '/textures'
                    + ' ' + '../models/names/' + name + '/meshes')

    create_name_texture(name,       '../models/names/' + name + '/textures/texture_name.png')
    
    create_mesh('../resources/names/name_default.dae', 
                                    '../models/names/' + name + '/meshes/mesh_name.dae')

    create_model_config(name,       '../models/names/' + name + '/model.config')

    create_model_sdf(name, pose,
        path=                       '../models/names/' + name + '/model.sdf',
        path_visual=    'model://rover_sim/models/names/' + name + '/meshes/mesh_name.dae')



def create_logo(name, pose):
    create_all(name, pose)
    copy2(      '../resources/names/Exploration_logo.png', 
                '../models/names/' + name + '/textures/texture_name.png')
    create_mesh('../resources/names/exp_logo.dae', 
                '../models/names/' + name + '/meshes/mesh_name.dae')



create_logo('Logo', '10 10 -10 0 0 0')
create_all("Alexandra", '10 7.5 -13 0 0 0')
create_all("Markus", '10 7.5 -16 0 0 0')
create_all("Stannis", '10 12.5 -13 0 0 0')