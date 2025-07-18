from zoo.libs.hive.library.tools.markingmenus.menus import defaultguidemenu


class FootGuideMenu(defaultguidemenu.BaseHiveGuideMM):
    id = "hiveFootGuideMenu"

    def execute(self, layout, arguments):
        layout = super(FootGuideMenu, self).execute(layout, arguments)
        if layout is None:
            return layout
        acceptedComponents = ("legcomponent", "quadLeg")
        genericLayout = layout["items"]["generic"]
        insertIndex = 0
        for index, item in enumerate(genericLayout):
            if item.get("id", "") == "hiveGuideAutoAlign":
                insertIndex = index
                break

        for comp, nodes in arguments.get("componentToNodes", {}).items():
            if comp.componentType not in acceptedComponents:
                continue
            genericLayout.insert(
                insertIndex,
                {"type": "command", "id": "hiveFootGuideAlign", "arguments": arguments},
            )

            layout["items"]["generic"].insert(
                insertIndex + 1,
                {
                    "type": "separator",
                },
            )
            break
        return layout


class WristGuideMenu(defaultguidemenu.BaseHiveGuideMM):
    id = "hiveWristGuideMenu"

    def execute(self, layout, arguments):
        layout = super(WristGuideMenu, self).execute(layout, arguments)
        if layout is None:
            return layout
        acceptedComponents = ("armcomponent", )
        genericLayout = layout["items"]["generic"]
        insertIndex = 0
        for index, item in enumerate(genericLayout):
            if item.get("id", "") == "hiveGuideAutoAlign":
                insertIndex = index
                break

        for comp, nodes in arguments.get("componentToNodes", {}).items():
            if comp.componentType not in acceptedComponents:
                continue
            genericLayout.insert(
                insertIndex,
                {"type": "command", "id": "hiveWristGuideAlign", "arguments": arguments},
            )

            layout["items"]["generic"].insert(
                insertIndex + 1,
                {
                    "type": "separator",
                },
            )
            break
        return layout
