from mojo.subscriber import (Subscriber, registerGlyphEditorSubscriber,
                             registerSubscriberEvent)
from mojo.UI import getDefault

# originally written by Connor Davenport: https://gist.github.com/connordavenport/ea50758429974d12df3d5c114d9d491b

KEY = "com.adbac.customMetricsGuides"

'''
start up script to draw custom metric guides in the
glyph view using info stored in the font lib.
'''


class CustomMetricsGuidesSubscriber(Subscriber):

    debug = True

    def build(self):
                
        glyphEditor = self.getGlyphEditor()
        self.container = glyphEditor.extensionContainer(
            identifier=KEY,
            location="background",
            clear=True
        )
        self.glyph = glyphEditor.getGlyph()
        self.leftMargin = self.glyph.leftMargin
        self.rightMargin = self.glyph.rightMargin

        self.merzMetrics = {}

    def started(self):
        self.drawCustomMetrics(self.glyph.font)
        
    def destroy(self):
        self.container.clearSublayers()

    def glyphEditorDidSetGlyph(self, info):
        self.glyph = info["glyph"]
        font = self.glyph.font
        self.drawCustomMetrics(font)

    def drawCustomMetrics(self, font):
        # based on benedikt bramböck's `ShowVMetrics` tool
        self.container.clearSublayers()

        border = getDefault("glyphViewVerticalPadding") * 2
        fontsize = getDefault("textFontSize")

        metricsStrokeColor = getDefault("glyphViewFontMetricsStrokeColor")
        metricsTextColor = getDefault("glyphViewMetricsTitlesColor")

        self.merzMetrics = {}

        customMetrics = {}
        for name, value in font.lib.get(KEY, {}).items():
            if value in customMetrics:
                customMetrics[value].append(name)
            else:
                customMetrics[value] = [name]
        
        for value, names in customMetrics.items():

            displayName = f"{', '.join(names)} ({value})"
            value = int(float(value))

            # is there a better way to get the adjusted xPos??

            # off = font.lib.get('com.typemytype.robofont.italicSlantOffset', 0)
            # x = y = math.radians(-font.info.italicAngle or 0)
            # matrix = transform.Identity.skew(x=x, y=y)
            # t = transform.Transform()
            # oX, oY = (0,0)
            # t = t.translate(oX, oY)
            # t = t.transform(matrix)
            # t = t.translate(-oX, -oY)
            # trans = tuple(t)
            # ot = transform.Transform(*trans)
            # n = ot.transformPoint((self.glyph.width + off, value))

            self.merzMetrics[tuple(names)] = dict(
                line = self.container.appendLineSublayer(
                    startPoint=(-border, value),
                    endPoint=(self.glyph.width + border, value),
                    strokeWidth=0.5,
                    strokeColor=metricsStrokeColor,
                ),
                text = self.container.appendTextLineSublayer(
                    # position=(n[0], value),
                    position=(self.glyph.width, value),
                    offset=(20, 4),
                    size=(20, 20),
                    weight="medium",
                    pointSize=fontsize,
                    text=displayName,
                    fillColor=metricsTextColor,
                    horizontalAlignment="left",
                    verticalAlignment="bottom",
                )
            )

    def customMetricsDataDidChange(self, info):
        self.drawCustomMetrics(self.glyph.font)

    glyphEditorGlyphDidChangeContoursDelay = 0.01

    def glyphEditorGlyphDidChangeContours(self, info):
        if self.glyph.leftMargin != self.leftMargin or self.glyph.rightMargin != self.rightMargin:
            newTitleX = self.glyph.width
            newLineEndX = (self.glyph.width + border)*2
            for names, metrics in self.merzMetrics.items():
                y = metrics["line"].getEndPoint()[1]
                metrics["line"].setEndPoint((newLineEndX, y))
                y = metrics["text"].getPosition()[1]
                metrics["text"].setPosition((newTitleX, y))
        else:
            self.leftMargin = self.glyph.leftMargin
            self.rightMargin = self.glyph.rightMargin


def subscriberInfoExtractor(subscriber, info):
    info["old"] = None
    info["new"] = None
    for lowLevelEvent in info["lowLevelEvents"]:
        info["old"] = lowLevelEvent["old"]
        info["new"] = lowLevelEvent["new"]


if __name__ == "__main__":
    registerSubscriberEvent(
        subscriberEventName=f"{KEY}.changed",
        methodName="customMetricsDataDidChange",
        lowLevelEventNames=[f"{KEY}.changed"],
        eventInfoExtractionFunction=subscriberInfoExtractor,
        dispatcher="roboFont",
        documentation="Send when the custom metrics lib key did change parameters.",
        delay=0,
        debug=True,
    )
    registerGlyphEditorSubscriber(CustomMetricsGuidesSubscriber)