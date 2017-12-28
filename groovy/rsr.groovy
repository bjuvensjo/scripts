#!/usr/bin/env groovy

import groovy.io.FileType
import java.util.regex.Matcher
import java.util.regex.Pattern

def usage = {
    println "usage: rsr [-r] oldValue newValue"
    System.exit(0)
}

String oldValue
String newValue

if (args.length == 2) {
    oldValue = Pattern.quote(args[0])
    newValue = Matcher.quoteReplacement(args[1])
} else if (args.length == 3) {
    if (args[0] == "-r") {
        oldValue = args[0]
        newValue = args[1]
    } else {
        usage()
    }
} else {
    usage()
}

File sourceDir = new File('.')

String encoding = 'UTF-8'

def move
move = { root, dir ->
    String oldRelativePath = dir.canonicalPath.replaceAll(Pattern.quote(root.canonicalPath), '')
    String newRelativePath = oldRelativePath.replaceAll(oldValue, newValue)

    File newDir = new File(root, newRelativePath)
    if (oldRelativePath != newRelativePath) {
        dir.renameTo(newDir)        
    }

    newDir.eachDir({ subDir ->
        if (!(subDir.name =~ /.git/)) {
            move(root, subDir)
        }
    })

    newDir.eachFile(FileType.FILES, { file ->
        boolean contentChanged = false

        String tmpName = "rsr-tmp"
        File tmpFile = new File(file.parentFile, tmpName)
        tmpFile.withWriter(encoding, { w ->
            file.eachLine(encoding, { line ->
                String newLine = line.replaceAll(oldValue, newValue)
                contentChanged = contentChanged || line != newLine                
                newLine += '\n'
                w << newLine
            })
        })
        
        if (contentChanged) {
            tmpFile.renameTo(file)                
        } else {
            tmpFile.delete()
        }

        String oldName = file.name
        String newName = file.name.replaceAll(oldValue, newValue)        
        if (oldName != newName) {
            file.renameTo(new File(file.parentFile, newName))
        }
    })
}

move(sourceDir, sourceDir)
