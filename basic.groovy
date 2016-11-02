#!/usr/bin/env groovy

String username=args[0]
String password=args[1]
String authorization = java.util.Base64.getEncoder().encodeToString((username + ":" + password).getBytes());

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

ShellResult shellResult = new Shell().execute("echo -n Authorization: Basic " + authorization + " | pbcopy", new File("."))

println "'Authorization: Basic $authorization' copied to clipboard"
