import os
import ntpath
import urllib.request
import bpy
import tempfile


bl_info = {
    "name": "Import URL as Image",
    "description": "Imports an image URL into your scene.",
    "category": "Import-Export",
    "author": "Alana Gilston",
    "version": (2, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Properties panel > Tools > Import URL as Image",
    "warning": "",
    "wiki_url": "",
    "support": "COMMUNITY"
}


def get_file(url, temp_file):
    try:
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')

        file = open(temp_file, "wb")
        file.write(urllib.request.urlopen(request).read())
        file.close()

        img = bpy.data.images.load(temp_file)
        img.pack()
        os.remove(temp_file)
    except Exception as e:
        raise NameError("Cannot load image: {0}".format(e))


class ImportPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    file_path: bpy.props.StringProperty(
        name="Temp file path",
        subtype="FILE_PATH",
        default=tempfile.gettempdir()
    )

    def draw(self, context):
        self.layout.prop(self, "file_path")


class ImportButton(bpy.types.Operator):
    bl_idname = "object.import_url_as_image"
    bl_label = "Import"
    bl_description = "Import valid URL as image"
    bl_options = {"REGISTER", "UNDO"}

    url: bpy.props.StringProperty(
        name="URL",
        description="URL to import",
        default="http://"
    )

    def invoke(self, context, event):
        self.url = "http://"
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        basename = os.path.basename(self.url)
        temp_file = os.path.join(
            context.preferences.addons[__name__].preferences.file_path,
            basename
        )
        self.report({"INFO"}, "Importing %s" % basename)
        get_file(self.url, temp_file)
        return {"FINISHED"}


class VIEW3D_PT_ImportUrl(bpy.types.Panel):
    bl_label = "Import URL as Image"
    bl_idname = "VIEW3D_PT_import_url_as_image"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Import/Export"

    def draw(self, context):
        col = self.layout.column(align=True)
        col.operator(ImportButton.bl_idname)


def register():
    bpy.utils.register_class(ImportPreferences)
    bpy.utils.register_class(ImportButton)
    bpy.utils.register_class(VIEW3D_PT_ImportUrl)


def unregister():
    bpy.utils.unregister_class(ImportPreferences)
    bpy.utils.unregister_class(ImportButton)
    bpy.utils.unregister_class(VIEW3D_PT_ImportUrl)


if __name__ == "__main__":
    register()
