#!/usr/bin/env groovy

@Grab(group='org.slf4j', module='slf4j-api', version='1.7.25')
@Grab(group='ch.qos.logback', module='logback-classic', version='1.2.3')
import groovy.util.logging.Slf4j
import groovy.json.JsonSlurper

import java.util.stream.Collectors

@Slf4j
class Bitbucket {
    String urlRestApi = "http://cuso.edb.se/stash/rest/api/1.0"

    List<String> getCloneUrls(String username, String password, Map<String, Map<String, List<String>>> projects, String branch) {
        projects.keySet().parallelStream()
                .map { projectKey -> getRepos(projectKey, username, password) }
                .flatMap { repos -> repos.parallelStream() }
                .filter { repo -> !isExcluded(repo.name, projects[repo.project.key].excludes) }
                .filter { repo -> isIncluded(repo.name, projects[repo.project.key].includes) }
                .filter { repo -> !branch || hasBranch(repo.name, branch, getBranches(repo, username, password, branch))}
                .map { repo -> repo.links.clone[0].href }
                .collect(Collectors.toList())
    }

    List<Map> getRepos(String projectKey, String username, String password) {
        new JsonSlurper().parseText("$urlRestApi/projects/$projectKey/repos?limit=1000".toURL().getText(getRequestProperties(username, password))).values
    }

    Map getBranches(Map repo, String username, String password, String branch) {
        new JsonSlurper().parseText("$urlRestApi/projects/${repo.project.key}/repos/${repo.name}/branches?filterText=$branch".toURL().getText(getRequestProperties(username, password)))
    }

    Map<String, Map<String, String>> getRequestProperties(String username, String password) {
        [requestProperties: ['Content-Type': 'application/json', 'Authorization': "Basic ${"$username:$password".bytes.encodeBase64().toString()}".toString()]]
    }

    boolean hasBranch(String repositoryName, String branch, Map branches) {
        boolean has = branches.size > 0 && branches.values.find {
            it.displayId == branch
        }
        if (has) {
            log.info("Included repository {} since it has branch {}", repositoryName, branch)
        } else {
            log.info("Excluded repository {} since it has no branch {}", repositoryName, branch)
        }
        has
    }

    boolean isExcluded(String repositoryName, List<String> excludes) {
        boolean is =  excludes && hasMatch(repositoryName, excludes)
        if (is) {
            log.info("Excluded repository {} since it matches excludes {}", repositoryName, excludes)
        }
        is
    }

    boolean isIncluded(String repositoryName, List<String> includes) {
        boolean is = !includes || hasMatch(repositoryName, includes)
        if (is) {
            log.info("Included repository {} since it matches includes {}", repositoryName, includes)
        }
        is
    }

    boolean hasMatch(String name, List<String> regexps) {
        regexps.stream().filter({ regexp -> (name =~ regexp).matches() }).findFirst().present
    }

    void createCloneScript(String username, String password, File configurationFile, File outputFile) {
        log.info("Configuration file: {}", configurationFile)
        log.info("Output file: {}", outputFile)
        def configuration = new JsonSlurper().parse(configurationFile)
        List<String> cloneUrls = getCloneUrls(username, password, configuration.projects, configuration.branch)
        def commands = cloneUrls.inject("") { cmds, cloneUrl ->
            def m = cloneUrl =~ /.*\/(.*)\/(.*)\.git$/
            cmds + "git clone ${cloneUrl} ${m[0][1]}${File.separator}${m[0][2].replaceAll("\\.", File.separator)}\n"
        }
        log.info("$outputFile content:\n{}", commands)
        outputFile.setText(commands, "UTF-8")
        outputFile.setExecutable(true)
    }
}

String username
String password
String configurationFileName

if (args.length == 0) {
    username = System.getProperty("username") ?: System.console().readLine("Bitbucket username: ")
    password = System.getProperty("password") ?: new String(System.console().readPassword("Bitbucket password: "))
    configurationFileName = System.getProperty("configurationFile") ?: System.console().readLine("configuration file (default ./clone.json): ") ?: "./clone.json"
}

if (args.length == 3) {
    username = args[0]
    password = args[1]
    configurationFileName = args[2]
}

/*
***** Configuration file examples *****

* Example 1 (Includes all repositores in projects ZAUTO and ZCOMM) *

{
  "projects": {
    "ZAUTO": {
    },
    "ZCOMM": {
    }    
  } 
}


* Example 2 (Includes the repositores in project ZCOMM that is specified in includes and not in excludes and that has a master branch)*

{
  "projects": {
    "ZCOMM": {
      "includes": [
        "bean-names",
        "common.*"
      ],
      "excludes": [
      ]
    }
  },
  "branch": "master" 
}
 */

new Bitbucket().createCloneScript(
    username, 
    password, 
    new File(configurationFileName), 
    new File("clone.${System.properties['os.name'].toLowerCase().contains('windows') ? "cmd" : "sh"}")
) 
