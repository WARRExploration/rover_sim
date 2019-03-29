from PIL import Image, ImageDraw, ImageFont
from lxml import etree
from shutil import copy2
import os
import copy

scale_factor = [0.21, 0.21, 0.297]


def create_texture(i, path):
    tag_number = i

    number_y = -5
    number_size = 75

    box_y = number_y + number_size + 5
    box_size = (190, 50)
    circle_number = 4
    circle_size = 35
    circle_dist = box_size[0] / 4

    ar_y = box_y + box_size[1] + 10
    ar_size = 150

    size = (210, 297)


    img = Image.new('RGBA', size, (255,255,255,255))

    # get a font
    fnt = ImageFont.truetype('DejaVuSans-Bold.ttf', number_size)
    # get a drawing context
    d = ImageDraw.Draw(img)

    # decimal number
    ts = d.textsize(str(tag_number), fnt)[0]
    d.text(((img.size[0]-ts)/2, number_y), str(tag_number), font=fnt, fill=(0,0,0,255))

    # binary circle counter
    d.rectangle(((img.size[0]-box_size[0])/2, box_y, (img.size[0]+box_size[0])/2, box_y + box_size[1]), fill=(0,200,50,255))
    for i in range(circle_number):
        if(tag_number & (1 << i)):
            d.ellipse(( img.size[0]/2+((circle_number-1)/2.-i)*circle_dist - circle_size/2, box_y+(box_size[1]-circle_size)/2, 
                        img.size[0]/2+((circle_number-1)/2.-i)*circle_dist + circle_size/2, box_y+(box_size[1]+circle_size)/2), fill=(0,50,200,255))


    # ar tag
    os.system('cd textures; rosrun ar_track_alvar createMarker ' + str(tag_number))

    ar_tag = Image.open('textures/MarkerData_' + str(tag_number) + '.png').resize((ar_size,ar_size), Image.NEAREST)
    img.paste(ar_tag, ((size[0]-ar_size)/2, ar_y))


    #img.show() 
    img.save(path)
    return



def create_mesh(i, path):
    with open('marker.dae') as f:
        newText=f.read().replace('<init_from>texture_marker.png</init_from>',
                                '<init_from>../textures/texture_marker' + str(i) + '.png</init_from>')

    with open(path, "w") as f:
        f.write(newText)
    return



def create_mesh_coll(i, path):
    with open('marker_coll.dae') as f:
        newText=f.read().replace('<init_from>texture_marker.png</init_from>',
                                '<init_from>../textures/texture_marker' + str(i) + '.png</init_from>')

    with open(path, "w") as f:
        f.write(newText)
    return



def create_model_config(i, path):
    config = etree.Element('model')

    name = etree.Element('name')
    name.text = 'L' + str(i)

    version = etree.Element('version')
    version.text = '1.0'

    sdf = etree.Element('sdf')
    sdf.set('version', '1.6')
    sdf.text = 'model.sdf'

    config.append(name)
    config.append(version)
    config.append(sdf)

    tree = etree.ElementTree(config)
    tree.write(path, pretty_print=True, encoding='utf8', xml_declaration=True)
    #print(etree.tostring(config, pretty_print=True, encoding='utf8', xml_declaration=True))
    return



def create_model_sdf(i, pose_s, path_visual, path_collision, path):
    sdf = etree.Element('sdf')
    sdf.set('version', '1.6')

    model = etree.Element('model')
    model.set('name', 'L' + str(i))

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
    
    scale = etree.Element('scale')
    scale.text = ' '.join(list(map(str, scale_factor)))

    mesh.append(uri)
    mesh.append(scale)
    geometry.append(mesh)
    visual.append(geometry)


    collision = etree.Element('collision')
    collision.set('name', 'collision')
    geometry = etree.Element('geometry')

    mesh = etree.Element('mesh')
    uri = etree.Element('uri')
    uri.text = path_collision
    
    scale = etree.Element('scale')
    scale.text = ' '.join(list(map(str, scale_factor)))

    mesh.append(uri)
    mesh.append(scale)
    geometry.append(mesh)
    collision.append(geometry)


    link.append(visual)
    link.append(collision)
    
    model.append(link)
    
    model.append(pose)
    model.append(static)
    model.append(link)

    sdf.append(model)


    tree = etree.ElementTree(sdf)
    tree.write(path, pretty_print=True, encoding='utf8', xml_declaration=True)
    #print(etree.tostring(sdf, pretty_print=True, encoding='utf8', xml_declaration=True))
    return





def create_all(i, pose):
    # in 'roversim/src/scripts/landmarks''

    os.system('mkdir -p ' + '../../models/landmarks/L' + str(i) + '/textures'
                    + ' ' + '../../models/landmarks/L' + str(i) + '/meshes')

    create_texture(i,       '../../models/landmarks/L' + str(i) + '/textures/texture_marker' + str(i) + '.png')
    
    create_mesh(i,          '../../models/landmarks/L' + str(i) + '/meshes/marker' + str(i) + '.dae')

    create_mesh_coll(i,     '../../models/landmarks/L' + str(i) + '/meshes/marker_coll.dae')

    create_model_config(i,  '../../models/landmarks/L' + str(i) + '/model.config')

    create_model_sdf(i, pose,
        path_visual=    'model://rover_sim/models/landmarks/L' + str(i) + '/meshes/marker' + str(i) + '.dae',
        path_collision= 'model://rover_sim/models/landmarks/L' + str(i) + '/meshes/marker_coll.dae',
        path=           '../../models/landmarks/L' + str(i) + '/model.sdf')



#for i in range(1, 13):
 #   create_texture(i)
  #  create_model(i)

create_all(8, '0 0 0 0 0 0')