#!/usr/bin/env groovy

import groovy.io.FileType
import java.util.regex.Matcher

String groupId = System.console().readLine 'groupId (default mygroup): '
String artifactId = System.console().readLine 'artifactId (default ws): '
String version = System.console().readLine 'version (default 1.0.0-SNAPSHOT): '
String sourceDir = System.console().readLine 'sourceDir: (default .)'
String outputDir = System.console().readLine 'outputDir: (default ./ws)'

if (groupId.trim() == "") {
    groupId = "mygroup"
}
if (artifactId.trim() == "") {
    artifactId = "ws"
}
if (version.trim() == "") {
    version = "1.0.0-SNAPSHOT"
}
if (sourceDir.trim() == "") {
    sourceDir = "."
}
if (outputDir.trim() == "") {
    outputDir = "./ws"
}

Path path = new Path()
String encoding = 'UTF-8'

String modules = ""
int indent = 8

File sourceFile = new File(sourceDir)
File outputFile = new File(outputDir)

def create
create = { root ->
    root.eachDir({ subDir ->
        if (!(subDir.name =~ /.git/)) {
            create(subDir)
        }
    })

    File pom = new File(root, "pom.xml")
    File src = new File(root, "src")
    if (pom.exists() && !(pom.parentFile.name == "template")) {
        def rootNode = new XmlSlurper().parse(pom)        
        def relativePath = path.getRelativePath(outputFile.absolutePath, pom.parentFile.absolutePath)
        modules +=  "\n" + (" " * indent) + "<module>${relativePath}</module>"
    }    
}

create(sourceFile);


def template = '''<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>###groupId###</groupId>
    <artifactId>###artifactId###</artifactId>
    <version>###version###</version>
    <packaging>pom</packaging>
    <modules>###modules###
    </modules>
</project>
'''

String pomContent = template
    .replaceAll("###groupId###", groupId)
    .replaceAll("###artifactId###", artifactId)
    .replaceAll("###version###", version)    
    .replaceAll("###modules###", modules)

println pomContent

outputFile.mkdirs()

new File(outputFile, "pom.xml").setText(pomContent, encoding)


class Path {

    String getNormalizedCanonicalPath(File file) {
        String platformSpecificCanonicalPath = file.canonicalPath

        return getNormalizedPath(platformSpecificCanonicalPath)
    }

    String getNormalizedPath(String path) {
        return path.replaceAll(Matcher.quoteReplacement('\\'), '/').replaceFirst('.*:', '')
    }

    String getRelativePath(String fromDirAbsolutePath, String toDirAbsolutePath) {
        String fromDirNormalizedPath = getNormalizedPath(fromDirAbsolutePath)
        String toDirNormalizedPath = getNormalizedPath(toDirAbsolutePath)

        int equalStartPathLength = getEqualStartPathLength(fromDirNormalizedPath, toDirNormalizedPath)

        String specificFromDirSubPath = fromDirNormalizedPath.substring(equalStartPathLength)

        String relativeUpNavigation = getRelativeUpNavigation(specificFromDirSubPath)

        String specificToDirSubPath = toDirNormalizedPath.substring(equalStartPathLength)

        String relativePath = relativeUpNavigation + specificToDirSubPath

        relativePath = relativePath.replaceAll('/./', '/')

        return relativePath
    }

    private int getEqualStartPathLength(String from, String to) {
        int index = from.indexOf('/')
        int previousIndex = 0;
        while (index != -1 && index < to.length() && from.substring(0, index + 1).equals(to.substring(0, index + 1))) {
            previousIndex = index
            index = from.indexOf('/', index + 1)
        }
        return previousIndex + 1
    }

    private String getRelativeUpNavigation(String subPath) {
        int nbOfParents = getNumberOfParents(subPath)
        
        return '../' * nbOfParents
    }

    private int getNumberOfParents(String path) {
        def matcher = (path =~ /\//)
    
        return  matcher.getCount() + 1
    }
}
    
