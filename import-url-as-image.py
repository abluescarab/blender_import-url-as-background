import os
import ntpath
import urllib.request
import bpy
import tempfile


bl_info = {
    "name": "Import URL as Image",
    "description": "Imports an image URL into your scene.",
    "category": "Import-Export",
    "author": "abluescarab",
    "version": (3, 1),
    "blender": (2, 80, 0),
    "location": "View 3D > Properties panel > Import/Export > Import URL as Image",
    "warning": "",
    "wiki_url": "",
    "support": "COMMUNITY"
}


def add_to_collection(collection_name):
    if collection_name in bpy.data.collections:
        collection = bpy.data.collections[collection_name]
    else:
        collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(collection)

    (bpy.context.window.view_layer.layer_collection.children[collection_name]
        .exclude) = False

    return collection


def get_file(url, temp_file, empty_name, collection):
    try:
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')

        read_request = urllib.request.urlopen(request).read()

        file = open(temp_file, "wb")
        file.write(read_request)
        file.close()

        img = bpy.data.images.load(temp_file)
        img.pack()
        os.remove(temp_file)

        img_empty = bpy.data.objects.new(empty_name, None)

        if collection:
            collection.objects.link(img_empty)
        else:
            bpy.context.scene.collection.objects.link(img_empty)

        img_empty.empty_display_type = "IMAGE"
        img_empty.data = img

        # deselect all objects and select new empty
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = img_empty
        img_empty.select_set(True)
    except Exception as e:
        raise NameError("Cannot load image: {0}".format(e))


class ImportProperties(bpy.types.PropertyGroup):
    temp_path: bpy.props.StringProperty(
        name="Temporary File Path",
        subtype="DIR_PATH",
        description="Temporary file storage path",
        default=tempfile.gettempdir()
    )

    add_to_collection: bpy.props.BoolProperty(
        name="Add to Collection",
        description="Add to a collection or place in the scene directly",
        default=True
    )

    collection_name: bpy.props.StringProperty(
        name="Collection",
        subtype="NONE",
        description="Collection to add to",
        default="Imported Images"
    )


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
        if not self.url or self.url == "http://":
            self.report({"ERROR"}, "Failed to import: no URL provided")
        else:
            tool = context.scene.import_url_as_image_tool
            basename = os.path.basename(self.url)

            temp_file = os.path.join(tool.temp_path, basename)
            collection_name = tool.collection_name

            self.report({"INFO"}, "Importing %s" % basename)

            collection = (add_to_collection(collection_name)
                            if tool.add_to_collection
                            else None)

            get_file(self.url, temp_file, basename, collection)

        return {"FINISHED"}


class VIEW3D_PT_ImportUrl(bpy.types.Panel):
    bl_label = "Import URL as Image"
    bl_idname = "VIEW3D_PT_import_url_as_image"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Import/Export"

    def draw(self, context):
        tool = context.scene.import_url_as_image_tool
        col = self.layout.column(align=True)

        row = col.row(align=True)
        row.operator(ImportButton.bl_idname)

        col.separator()

        row = col.row(align=True)
        row.prop(tool, "add_to_collection")

        row = col.row(align=True)
        row.prop(tool, "collection_name", text="")
        row.active = tool.add_to_collection

        col.separator()

        row = col.row(align=True)
        row.label(text="Temporary File Path:")

        row = col.row(align=True)
        row.prop(tool, "temp_path", text="")


classes = (
    ImportProperties,
    ImportButton,
    VIEW3D_PT_ImportUrl
)


def register():
    from bpy.utils import register_class
    for cl in classes:
        register_class(cl)

    bpy.types.Scene.import_url_as_image_tool = (
        bpy.props.PointerProperty(type=ImportProperties)
    )


def unregister():
    from bpy.utils import unregister_class
    for cl in reversed(classes):
        unregister_class(cl)

    del bpy.types.Scene.import_url_as_image_tool


if __name__ == "__main__":
    register()
