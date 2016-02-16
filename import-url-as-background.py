bl_info = {
    "name": "Import URL as Background",
    "description": "Imports an image URL as a background in your scene.",
    "category": "Import-Export",
    "author": "Alana Gilston",
    "version": (1, 0),
    "blender": (2, 76, 0),
    "location": "View3D > Properties panel > Background Images > Import URL",
    "warning": "",
    "wiki_url": "",
    "support": "COMMUNITY"
}

import bpy, urllib.request, ntpath, os
from bpy.props import *

image_url = "http://"
button_text = "Import URL"

def run(url):
    try:
        temp_file = os.path.dirname(os.path.dirname(__file__)) + "\\" + ntpath.basename(url)
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')
        download_file(request, temp_file)
        img = bpy.data.images.load(temp_file)
        img.pack()
        os.remove(temp_file)
    except Exception as e:
        raise NameError("Cannot load image: {0}".format(e))

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            space_data = area.spaces.active
            space_data.show_background_images = True
            background = space_data.background_images.new()
            background.image = img
            background.show_background_image = True
            break

def download_file(url, path):
    f = open(path, "wb")
    f.write(urllib.request.urlopen(url).read())
    f.close()
    
class DialogOperator(bpy.types.Operator):
    bl_idname = "object.dialog_operator"
    bl_label = button_text
    
    url = StringProperty(name="URL")
    
    def execute(self, context):
        message = "%s" % (self.url)
        self.report({'INFO'}, message)
        run(self.url)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        self.url = image_url
        return context.window_manager.invoke_props_dialog(self)
    
def import_url_as_background(self, context):
    layout = self.layout
    layout.operator("object.dialog_operator")
    
def register():
    bpy.utils.register_class(DialogOperator)
    bpy.types.VIEW3D_PT_background_image.prepend(import_url_as_background)
    
def unregister():
    bpy.utils.unregister_class(DialogOperator)
    bpy.types.VIEW3D_PT_background_image.remove(import_url_as_background)
    
def load():
    bpy.ops.object.dialog_operator('INVOKE_DEFAULT')

if __name__ == "__main__":
    register()