import ezui
from mojo.events import postEvent
from mojo.roboFont import CurrentFont

KEY = "com.adbac.customMetricsGuides"


class SettingsWindowController(ezui.WindowController):

    def build(self):
        content = """
        |--------------| @table
        |              |
        |--------------|
        > (+-)    @addRemoveButton
        """

        self.f = CurrentFont()

        tableItems=[
            dict(
                name=name,
                value=value,
            ) for name, value in self.f.lib.get(KEY, {}).items()
        ]

        descriptionData=dict(
            table=dict(
                width=300,
                height=200,
                items=tableItems,
                drawFocusRing=False,
                allowsMultipleSelection=False,
                allowsEmptySelection=False,
                columnDescriptions=[
                    dict(
                        identifier="name",
                        title="Name",
                        editable=True
                    ),
                    dict(
                        identifier="value",
                        title="Y Value",
                        editable=True,
                        cellDescription=dict(
                            valueType="integer",
                            cellClassArguments=dict(
                                continuous=True,
                            )
                        )
                    ),
                ]
            )
        )

        self.w = ezui.EZPanel(
            title="Custom Metrics Guides - Settings",
            content=content,
            controller=self,
            descriptionData=descriptionData,
        )

    def started(self):
        self.w.open()

    def addRemoveButtonAddCallback(self, sender):
        table = self.w.getItem("table")
        data = self.f.lib.get(KEY, {})
        name = "New Guide"
        baseName = name
        counter = 1
        while name in data:
            name = f"{baseName} {counter}"
            counter += 1
        item = table.makeItem(
            name=name,
            value=0,
        )
        table.appendItems([item])
        self.saveData()
        postEvent(f"{KEY}.changed", old=None, new=(name, 0))

    def addRemoveButtonRemoveCallback(self, sender):
        table = self.w.getItem("table")
        removedItem = table.getSelectedItems()[0]
        removedData = (removedItem["name"], removedItem["value"])
        table.removeSelectedItems()
        self.saveData()
        postEvent(f"{KEY}.changed", old=removedData, new=None)

    def tableEditCallback(self, sender):
        table = self.w.getItem("table")
        data = self.f.lib[KEY]
        editedItem = sender.getSelectedItems()[0]
        editedData = (editedItem["name"], editedItem["value"])
        editedIndex = sender.getSelectedIndexes()[0]
        uneditedData = list(data.items())[editedIndex]
        for i, name in enumerate(data.keys()):
            if i == editedIndex:
                continue
            if name == editedItem["name"]:
                table.setitemValue(editedIndex, "name", uneditedData[0])
                break
        self.saveData()
        postEvent(f"{KEY}.changed", old=uneditedData, new=editedData)

    def saveData(self):
        table = self.w.getItem("table")
        data = {item["name"]: item["value"] for item in table.get()}
        self.f.lib[KEY] = data


if CurrentFont() and __name__ == "__main__":
    SettingsWindowController()
