#!/usr/bin/env groovy

class Shell {
    private static final boolean WINDOWS = System.properties['os.name'].toLowerCase().contains('windows')

    ShellResult execute(String command, File workingDir) {
        String output = ''

        Process process = new ProcessBuilder(addShellPrefix(command))
        .directory(workingDir)
        .redirectErrorStream(true)
        .start()

        process.inputStream.eachLine { line ->
            output += (line + '\n')
        }

        process.waitFor()

        return new ShellResult(
        command: command, 
        workingDir: workingDir,
        output: output.trim(),
        exitValue:process.exitValue()
        )
    }

    private String[] addShellPrefix(String command) {
        if (WINDOWS) {
            return ['cmd', '/C', command]
        }
        return [System.getenv()['SHELL'] ?: 'sh', '-c', command]
    }
}

class ShellResult {
    String command
    File workingDir
    String output
    int exitValue    
}

def getOriginalVersion = { pomPath ->
    def pom = new XmlSlurper().parse(pomPath)    
    pom.version.toString()
}

def getReleaseVersion = { originalVersion ->
    def matcher = (originalVersion =~ /([0-9]+\.[0-9]+\.[0-9]+).*/)
    if (!matcher.matches()) {
        throw new RuntimeException("Can not getReleaseVersion")
    }
    matcher[0][1]
}

def getReleaseCandidateReleaseVersion = { releaseCandidateVersion ->
    def matcher = (releaseCandidateVersion =~ /([0-9]+\.[0-9]+\.[0-9]+-rc[0-9]+)-SNAPSHOT/)
    if (!matcher.matches()) {
        throw new RuntimeException("Can not getReleaseCandidateReleaseVersion")
    }
    "${matcher[0][1]}"
}    


def getReleaseCandidateVersion = { originalVersion ->
    def matcher = (originalVersion =~ /([0-9]+\.[0-9]+\.[0-9]+)-rc([0-9]+)-SNAPSHOT/)
    def count = 1
    if (matcher.matches()) {
        "${matcher[0][1]}-rc${Integer.parseInt(matcher[0][2]) + 1}-SNAPSHOT"
    } else {
        "${getReleaseVersion(originalVersion)}-rc1-SNAPSHOT"
    }
}    

def getBumpVersion = { version ->
    def matcher = (version =~ /([0-9]+\.[0-9]+\.[0-9]+)-rc([0-9]+).*/)
    if (matcher.matches()) {
        "${matcher[0][1]}-rc${Integer.parseInt(matcher[0][2]) + 1}-SNAPSHOT"
    } else {
        matcher = (version =~ /([0-9]+\.[0-9]+\.)([0-9]+).*/)
        if (!matcher.matches()) {
            throw new RuntimeException("Can not getBumpVersion")
        }
        "${matcher[0][1]}${Integer.parseInt(matcher[0][2]) + 1}-SNAPSHOT"
    }
}

def updateToVersion = { pomPath, version ->
    File pomFile = new File(pomPath)
    
    String xml = pomFile.text

    int startIndex = xml.indexOf("<version>") + "<version>".length()
    int endIndex = xml.indexOf("</version>")

    String updatedXml = xml.substring(0, startIndex) + version + xml.substring(endIndex)

    pomFile.text = updatedXml
}

def execute = { command ->
    ShellResult shellResult = new Shell().execute(command, new File("."))
    if (shellResult.exitValue != 0) {
        throw new RuntimeException("Can not execute: ${command} (${shellResult.output})")
    }
    println "#" * 50
    println "> ${shellResult.command}"
    println shellResult.output
    println "#" * 50    
}

def isReleaseCandidate = { version ->
    def matcher = (version =~ /([0-9]+\.[0-9]+\.[0-9]+)-rc([0-9]+)-SNAPSHOT/)
    return matcher.matches()
}


def releaseTag = { pomPath ->
    String originalVersion = getOriginalVersion(pomPath)
    String releaseVersion = getReleaseVersion(originalVersion)
    String bumpVersion = getBumpVersion(originalVersion)

    println("originalVersion = $originalVersion")
    println("releaseVersion = $releaseVersion")
    println("bumpVersion = $bumpVersion")

    updateToVersion(pomPath, releaseVersion)    
    execute("mvn clean install")
    execute("git commit -am $releaseVersion")
    execute("git tag -a $releaseVersion -m $releaseVersion")
    execute("git push origin $releaseVersion")
    if (!isReleaseCandidate(originalVersion)) {
        updateToVersion(pomPath, bumpVersion)
        execute("mvn clean install")    
        execute("git commit -am $bumpVersion")
    }
    execute("git push")
}

def releaseCandidateTag = { pomPath ->
    String releaseCandidateVersion = getOriginalVersion(pomPath)
    if (releaseCandidateVersion.indexOf("rc") == -1) {
        println "You are not in a release branch"
        System.exit(-1)
    }

    String releaseCandidateReleaseVersion = getReleaseCandidateReleaseVersion(releaseCandidateVersion)    
    String bumpVersion = getBumpVersion(releaseCandidateVersion)
    
    println("releaseCandidateVersion = $releaseCandidateVersion")
    println("releaseCandidateReleaseVersion = $releaseCandidateReleaseVersion")
    println("bumpVersion = $bumpVersion")

    updateToVersion(pomPath, releaseCandidateReleaseVersion)    
    execute("mvn clean install")
    execute("git commit -am $releaseCandidateReleaseVersion")
    execute("git tag -a $releaseCandidateReleaseVersion -m $releaseCandidateReleaseVersion")
    execute("git push origin $releaseCandidateReleaseVersion")
    
    updateToVersion(pomPath, bumpVersion)
    execute("mvn clean install")    
    execute("git commit -am $bumpVersion")
    execute("git push")
}

def releaseBranch = { pomPath ->
    String originalVersion = getOriginalVersion(pomPath)
    String releaseCandidateVersion = getReleaseCandidateVersion(originalVersion)
    String releaseVersion = getReleaseVersion(originalVersion)    
    String bumpVersion = getBumpVersion(originalVersion)

    println("originalVersion = $originalVersion")
    println("releaseCandidateVersion = $releaseCandidateVersion")
    println("releaseVersion = $releaseVersion")
    println("bumpVersion = $bumpVersion")

    execute("git checkout -b release/$releaseVersion")
    updateToVersion(pomPath, releaseCandidateVersion)    
    execute("mvn clean install")
    execute("git commit -am $releaseCandidateVersion")
    execute("git push origin")

    execute("git checkout develop")
    execute("git merge release/$releaseVersion")
    updateToVersion(pomPath, bumpVersion)
    execute("mvn clean install")    
    execute("git commit -am $bumpVersion")
    execute("git push")    
}

def hotfixBranch = { pomPath ->
    execute("git checkout master")
    
    String originalVersion = getOriginalVersion(pomPath)
    String hotfixVersion = getReleaseCandidateVersion(getReleaseVersion(getBumpVersion(originalVersion)))

    println("originalVersion = $originalVersion")
    println("hotfixVersion = $hotfixVersion")

    execute("git checkout -b hotfix-$hotfixVersion")
    updateToVersion(pomPath, hotfixVersion)    
    execute("mvn clean install")
    execute("git commit -am $hotfixVersion")
    // execute("git push -u origin $hotfixVersion")
}


String thePomPath = "./pom.xml"

// println(getReleaseVersion(getReleaseCandidateVersion(getOriginalVersion(thePomPath))))
//println(getReleaseCandidateReleaseVersion(getReleaseCandidateVersion(getOriginalVersion(thePomPath))))

switch (args[0]) {
    case "branch":
        releaseBranch(thePomPath)
        break 
    case "hotfix":
        hotfixBranch(thePomPath)
        break       
    case "rcTag":
        releaseCandidateTag(thePomPath)
        break       
    case "tag":
        releaseTag(thePomPath)            
        break
    default:
        println "Usage: release tag|branch|rcTag"
} 