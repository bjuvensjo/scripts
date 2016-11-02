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

String artifactId = new XmlSlurper().parse("./pom.xml").artifactId

ShellResult shellResult = new Shell().execute("echo -n " + artifactId + " | pbcopy", new File("."))

println "'$artifactId' copied to clipboard"
