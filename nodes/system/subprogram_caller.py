import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... tree_info import getSubprogramNetworks, getNodeByIdentifier, getNetworkByIdentifier
from ... utils.enum_items import enumItemsFromDicts

class SubprogramCaller(bpy.types.Node, AnimationNode):
    bl_idname = "an_SubprogramCaller"
    bl_label = "Subprogram Caller"

    def subprogramIdentifierChanged(self, context):
        self.updateSockets()

    subprogramIdentifier = StringProperty(name = "Subprogram Identifier", default = "", update = subprogramIdentifierChanged)

    def draw(self, layout):
        networks = getSubprogramNetworks()
        network = self.subprogramNetwork

        layout.separator()
        col = layout.column()
        col.scale_y = 1.6
        if len(networks) == 0:
            self.functionOperator(col, "createNewGroup", text = "Group", icon = "PLUS")
        else:
            text, icon = (network.name, "GROUP_VERTEX") if network else ("Choose", "TRIA_RIGHT")
            props = col.operator("an.change_subprogram", text = text, icon = icon)
            props.nodeIdentifier = self.identifier
        layout.separator()

    def updateSockets(self):
        subprogram = self.subprogramNode
        if subprogram is None: self.clearSockets()
        else: subprogram.getSocketData().apply(self)

    @property
    def subprogramNode(self):
        try: return getNodeByIdentifier(self.subprogramIdentifier)
        except: return None

    @property
    def subprogramNetwork(self):
        return getNetworkByIdentifier(self.subprogramIdentifier)

    def createNewGroup(self):
        bpy.ops.node.add_and_link_node(type = "an_GroupInput")
        inputNode = self.nodeTree.nodes[-1]
        inputNode.location.x -= 200
        inputNode.location.y += 40
        self.subprogramIdentifier = inputNode.identifier
        bpy.ops.node.add_and_link_node(type = "an_GroupOutput")
        outputNode = self.nodeTree.nodes[-1]
        outputNode.location.x += 60
        outputNode.location.y += 40
        outputNode.groupInputIdentifier = inputNode.identifier
        inputNode.select = True
        bpy.ops.node.translate_attach("INVOKE_DEFAULT")

@enumItemsFromDicts
def getSubprogramItems(self, context):
    itemDict = []
    for network in getSubprogramNetworks():
        itemDict.append({
            "id" : network.identifier,
            "name" : network.name,
            "description" : network.description})
    return itemDict

class ChangeSubprogram(bpy.types.Operator):
    bl_idname = "an.change_subprogram"
    bl_label = "Change Subprogram"
    bl_description = "Change Subprogram"

    nodeIdentifier = StringProperty()
    subprogram = EnumProperty(name = "Subprogram", items = getSubprogramItems)

    @classmethod
    def poll(cls, context):
        networks = getSubprogramNetworks()
        return len(networks) > 0

    def invoke(self, context, event):
        node = getNodeByIdentifier(self.nodeIdentifier)
        if node.subprogramIdentifier != "":
            self.subprogram = node.subprogramIdentifier
        return context.window_manager.invoke_props_dialog(self, width = 400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "subprogram")

    def execute(self, context):
        node = getNodeByIdentifier(self.nodeIdentifier)
        node.subprogramIdentifier = self.subprogram
        return {"FINISHED"}
