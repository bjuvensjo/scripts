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

    String oldRelativePath = dir.canonicalPath.replaceAll(root.canonicalPath, '')

    String newRelativePath = oldRelativePath.replaceAll(oldValue, newValue)

    File newDir = new File(root, newRelativePath)

    dir.renameTo(newDir)

    newDir.eachDir({ subDir ->
        if (!(subDir.name =~ /.git/)) {
            move(root, subDir)
        }
    })

    newDir.eachFile(FileType.FILES, { file ->
        String newName = file.name.replaceAll(oldValue, newValue)
        File newFile = new File(file.parentFile, newName)
        File newFileBackup = new File(file.parentFile, newName + '.backup')
        
        file.renameTo(newFileBackup)

        newFile.withWriter(encoding, { w ->
            newFileBackup.eachLine(encoding, { line ->
                def newLine = line.replaceAll(oldValue, newValue)
                newLine += '\n'
                w << newLine
            })
        })

        newFileBackup.delete()
    })
}

move(sourceDir, sourceDir)
