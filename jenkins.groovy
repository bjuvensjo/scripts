#!/usr/bin/env groovy

import groovy.json.JsonOutput
import groovy.json.JsonSlurper

URL.metaClass.post = { Map requestProperties, String body ->
    HttpURLConnection con = delegate.openConnection()
    con.setAllowUserInteraction(true)
    con.setDoInput(true)
    con.setDoOutput(true)
    con.setConnectTimeout(12000)
    con.setDefaultUseCaches(false)
    con.setReadTimeout(12000)
    con.setRequestMethod("POST")
    requestProperties?.each { k, v ->
        con.setRequestProperty(k, v)
    }
    if (body) {
        con.getOutputStream().withWriter("UTF-8") { w ->
            w.write(body)
        }
    }
    con.getResponseCode()
    String responseBody
    con.getInputStream().withReader("UTF-8") { r ->
        responseBody = r.readLines().join("\n")
    }
    [responseCode: con.getResponseCode(), headers: con.getHeaderFields(), body: responseBody]
}

String jenkinsUrl = "http://10.46.64.51:8080"

jobs = {
    def map = new JsonSlurper().parseText("$jenkinsUrl/api/json?pretty=true&tree=jobs[url]".toURL().getText())
    map = map.jobs.collect() { job ->
        job.url
    }
    JsonOutput.prettyPrint(JsonOutput.toJson(map))
}

statuses = {
    def map = new JsonSlurper().parseText("$jenkinsUrl/api/json?pretty=true&tree=jobs[url,color]".toURL().getText())
    map = map.jobs.inject([failed: [], success: []]) { result, job -> 
        if (job.color == "red") {
            result.failed << job.url
        } else {
            result.success << job.url
        }
        result
    }
    JsonOutput.prettyPrint(JsonOutput.toJson(map))
}

create = { String jobName, String configXml -> 
    "$jenkinsUrl/createItem?name=$jobName".toURL().post(["Content-Type": "application/xml"], configXml).responseCode
}

update = { String jobName, String configXml ->
    "$jenkinsUrl/job/$jobName/config.xml".toURL().post(["Content-Type": "application/xml"], configXml).responseCode
}

addToView = { String jobName, String view ->
    "$jenkinsUrl/view/$view/addJobToView?name=$jobName".toURL().post([:], "").responseCode
}

delete = { String jobName ->
    "$jenkinsUrl/job/$jobName/doDelete".toURL().post([:], "").responseCode
}

// Can be called without param from the root of a cloned stash repository
build = { String jobName ->
    jobName = jobName ?: name()
    "$jenkinsUrl/job/$jobName/build".toURL().post([:], "").responseCode
}

// Returns 'standard' name based on stash project name, repository name and current git branch
// Must be called from the root of a cloned stash (git) repository
name = {
    new File(".git/config").findResult { line ->
        def m = line =~ /.*url = .*\/stash\/scm\/([^\/]+)\/(.*).git/
        if (m.matches()) {
            m[0][1].toUpperCase() + "_" + m[0][2] + "_" + new File(".git/HEAD").text.trim().replaceAll(".*/", "")
        }
    }    
}

// Must be called from the root of a cloned stash repository
createFromTemplate = {
    def template = '''<?xml version='1.0' encoding='UTF-8'?>
<maven2-moduleset plugin="maven-plugin@2.13">
    <actions/>
    <description>##name##</description>
    <keepDependencies>false</keepDependencies>
    <properties>
        <jenkins.plugins.maveninfo.config.MavenInfoJobConfig plugin="maven-info@0.2.0">
            <mainModulePattern></mainModulePattern>
            <dependenciesPattern></dependenciesPattern>
            <assignName>false</assignName>
            <nameTemplate></nameTemplate>
            <assignDescription>false</assignDescription>
            <descriptionTemplate></descriptionTemplate>
        </jenkins.plugins.maveninfo.config.MavenInfoJobConfig>
        <hudson.plugins.buildblocker.BuildBlockerProperty plugin="build-blocker-plugin@1.7.3">
            <useBuildBlocker>false</useBuildBlocker>
            <blockLevel>GLOBAL</blockLevel>
            <scanQueueFor>DISABLED</scanQueueFor>
            <blockingJobs></blockingJobs>
        </hudson.plugins.buildblocker.BuildBlockerProperty>
        <org.jenkinsci.plugins.authorizeproject.AuthorizeProjectProperty plugin="authorize-project@1.2.2">
            <strategy class="org.jenkinsci.plugins.authorizeproject.strategy.SpecificUsersAuthorizationStrategy">
                <userid>SVC-stashuser</userid>
                <noNeedReauthentication>true</noNeedReauthentication>
            </strategy>
        </org.jenkinsci.plugins.authorizeproject.AuthorizeProjectProperty>
        <jenkins.model.BuildDiscarderProperty>
            <strategy class="hudson.tasks.LogRotator">
                <daysToKeep>-1</daysToKeep>
                <numToKeep>5</numToKeep>
                <artifactDaysToKeep>-1</artifactDaysToKeep>
                <artifactNumToKeep>-1</artifactNumToKeep>
            </strategy>
        </jenkins.model.BuildDiscarderProperty>
    </properties>
    <scm class="hudson.plugins.git.GitSCM" plugin="git@3.0.0">
        <configVersion>2</configVersion>
        <userRemoteConfigs>
            <hudson.plugins.git.UserRemoteConfig>
                <name>##repository##</name>
                <url>http://cuso.edb.se/stash/scm/##projectKey##/##repository##.git</url>
                <credentialsId>400cfd20-65b7-4c7b-9120-bfb52ad2cdcc</credentialsId>
            </hudson.plugins.git.UserRemoteConfig>
        </userRemoteConfigs>
        <branches>
            <hudson.plugins.git.BranchSpec>
                <name>##refSpec##</name>
            </hudson.plugins.git.BranchSpec>
        </branches>
        <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
        <browser class="hudson.plugins.git.browser.Stash">
            <url>http://cuso.edb.se/stash/projects/##projectKey##/repos/##repository##/</url>
        </browser>
        <submoduleCfg class="list"/>
        <extensions>
            <hudson.plugins.git.extensions.impl.CleanCheckout/>
        </extensions>
    </scm>
    <assignedNode>LH</assignedNode>
    <canRoam>false</canRoam>
    <disabled>false</disabled>
    <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
    <blockBuildWhenUpstreamBuilding>true</blockBuildWhenUpstreamBuilding>
    <jdk>jdk1.8.102</jdk>
    <triggers>
        <hudson.triggers.TimerTrigger>
            <spec>NEVER</spec>
        </hudson.triggers.TimerTrigger>
        <hudson.triggers.SCMTrigger>
            <spec>H 0 1 1 0</spec>
            <ignorePostCommitHooks>false</ignorePostCommitHooks>
        </hudson.triggers.SCMTrigger>
    </triggers>
    <concurrentBuild>false</concurrentBuild>
    <rootModule>
        <groupId>com.evry.finance.loanprocess.lhb</groupId>
        <artifactId>##repository##</artifactId>
    </rootModule>
    <goals>##mvnGoals##</goals>
    <defaultGoals>generate-resources</defaultGoals>
    <mavenName>Maven 3.3.9</mavenName>
    <aggregatorStyleBuild>true</aggregatorStyleBuild>
    <incrementalBuild>false</incrementalBuild>
    <ignoreUpstremChanges>false</ignoreUpstremChanges>
    <ignoreUnsuccessfulUpstreams>false</ignoreUnsuccessfulUpstreams>
    <archivingDisabled>true</archivingDisabled>
    <siteArchivingDisabled>false</siteArchivingDisabled>
    <fingerprintingDisabled>false</fingerprintingDisabled>
    <resolveDependencies>true</resolveDependencies>
    <processPlugins>true</processPlugins>
    <mavenValidationLevel>-1</mavenValidationLevel>
    <runHeadless>false</runHeadless>
    <disableTriggerDownstreamProjects>false</disableTriggerDownstreamProjects>
    <blockTriggerWhenBuilding>true</blockTriggerWhenBuilding>
    <settings class="jenkins.mvn.FilePathSettingsProvider">
        <path>/opt/cuso/jenkins/cuso-tools/lhb/settings.xml</path>
    </settings>
    <globalSettings class="jenkins.mvn.DefaultGlobalSettingsProvider"/>
    <reporters>
        <hudson.maven.reporters.MavenMailer>
            <recipients></recipients>
            <dontNotifyEveryUnstableBuild>false</dontNotifyEveryUnstableBuild>
            <sendToIndividuals>true</sendToIndividuals>
            <perModuleEmail>true</perModuleEmail>
        </hudson.maven.reporters.MavenMailer>
    </reporters>
    <publishers>
        <org.jfrog.hudson.ArtifactoryRedeployPublisher plugin="artifactory@2.6.0">
            <evenIfUnstable>false</evenIfUnstable>
            <details>
                <artifactoryName>JFrog</artifactoryName>
                <artifactoryUrl>http://cuso.edb.se/artifactory</artifactoryUrl>
                <deployReleaseRepository>
                    <keyFromText></keyFromText>
                    <keyFromSelect>lhb-release</keyFromSelect>
                    <dynamicMode>false</dynamicMode>
                </deployReleaseRepository>
                <deploySnapshotRepository>
                    <keyFromText></keyFromText>
                    <keyFromSelect>lhb-snapshot</keyFromSelect>
                    <dynamicMode>false</dynamicMode>
                </deploySnapshotRepository>
                <stagingPlugin>
                    <pluginName>None</pluginName>
                </stagingPlugin>
                <userPluginKey>None</userPluginKey>
            </details>
            <deployArtifacts>true</deployArtifacts>
            <artifactDeploymentPatterns>
                <includePatterns></includePatterns>
                <excludePatterns></excludePatterns>
            </artifactDeploymentPatterns>
            <deployerCredentialsConfig>
                <credentials>
                    <username></username>
                    <password></password>
                </credentials>
                <credentialsId></credentialsId>
                <overridingCredentials>false</overridingCredentials>
            </deployerCredentialsConfig>
            <includeEnvVars>false</includeEnvVars>
            <envVarsPatterns>
                <includePatterns></includePatterns>
                <excludePatterns>*password*,*secret*,*key*</excludePatterns>
            </envVarsPatterns>
            <runChecks>false</runChecks>
            <violationRecipients></violationRecipients>
            <includePublishArtifacts>false</includePublishArtifacts>
            <passIdentifiedDownstream>false</passIdentifiedDownstream>
            <scopes></scopes>
            <licenseAutoDiscovery>true</licenseAutoDiscovery>
            <disableLicenseAutoDiscovery>false</disableLicenseAutoDiscovery>
            <discardOldBuilds>false</discardOldBuilds>
            <discardBuildArtifacts>true</discardBuildArtifacts>
            <matrixParams></matrixParams>
            <enableIssueTrackerIntegration>false</enableIssueTrackerIntegration>
            <allowPromotionOfNonStagedBuilds>false</allowPromotionOfNonStagedBuilds>
            <allowBintrayPushOfNonStageBuilds>false</allowBintrayPushOfNonStageBuilds>
            <filterExcludedArtifactsFromBuild>true</filterExcludedArtifactsFromBuild>
            <recordAllDependencies>false</recordAllDependencies>
            <defaultPromotionTargetRepository></defaultPromotionTargetRepository>
            <deployBuildInfo>true</deployBuildInfo>
            <aggregateBuildIssues>false</aggregateBuildIssues>
            <blackDuckRunChecks>false</blackDuckRunChecks>
            <blackDuckAppName></blackDuckAppName>
            <blackDuckAppVersion></blackDuckAppVersion>
            <blackDuckReportRecipients></blackDuckReportRecipients>
            <blackDuckScopes></blackDuckScopes>
            <blackDuckIncludePublishedArtifacts>false</blackDuckIncludePublishedArtifacts>
            <autoCreateMissingComponentRequests>true</autoCreateMissingComponentRequests>
            <autoDiscardStaleComponentRequests>true</autoDiscardStaleComponentRequests>
        </org.jfrog.hudson.ArtifactoryRedeployPublisher>
\t\t<hudson.plugins.jacoco.JacocoPublisher plugin="jacoco@2.2.0">
            <execPattern>**/**.exec</execPattern>
            <classPattern>**/classes</classPattern>
            <sourcePattern>**/src/main/java</sourcePattern>
            <inclusionPattern></inclusionPattern>
\t\t\t<exclusionPattern></exclusionPattern>
\t\t\t<skipCopyOfSrcFiles>false</skipCopyOfSrcFiles>
\t\t\t<minimumInstructionCoverage>0</minimumInstructionCoverage>
\t\t\t<minimumBranchCoverage>0</minimumBranchCoverage>
\t\t\t<minimumComplexityCoverage>0</minimumComplexityCoverage>
\t\t\t<minimumLineCoverage>10</minimumLineCoverage>
\t\t\t<minimumMethodCoverage>0</minimumMethodCoverage>
\t\t\t<minimumClassCoverage>0</minimumClassCoverage>
\t\t\t<maximumInstructionCoverage>0</maximumInstructionCoverage>
\t\t\t<maximumBranchCoverage>0</maximumBranchCoverage>
\t\t\t<maximumComplexityCoverage>0</maximumComplexityCoverage>
\t\t\t<maximumLineCoverage>30</maximumLineCoverage>
\t\t\t<maximumMethodCoverage>0</maximumMethodCoverage>
\t\t\t<maximumClassCoverage>0</maximumClassCoverage>
\t\t\t<changeBuildStatus>false</changeBuildStatus>
\t\t\t<deltaInstructionCoverage>0</deltaInstructionCoverage>
\t\t\t<deltaBranchCoverage>0</deltaBranchCoverage>
\t\t\t<deltaComplexityCoverage>0</deltaComplexityCoverage>
\t\t\t<deltaLineCoverage>0</deltaLineCoverage>
\t\t\t<deltaMethodCoverage>0</deltaMethodCoverage>
\t\t\t<deltaClassCoverage>0</deltaClassCoverage>
\t\t\t<buildOverBuild>false</buildOverBuild>
\t\t</hudson.plugins.jacoco.JacocoPublisher>
    </publishers>
    <buildWrappers>
        <hudson.plugins.ws__cleanup.PreBuildCleanup plugin="ws-cleanup@0.30">
            <deleteDirs>false</deleteDirs>
            <cleanupParameter></cleanupParameter>
            <externalDelete></externalDelete>
        </hudson.plugins.ws__cleanup.PreBuildCleanup>
    </buildWrappers>
    <prebuilders>
        <hudson.tasks.Shell>
            <command>mvn org.apache.maven.plugins:maven-dependency-plugin:2.8:list -DincludeParents=true -s /opt/cuso/jenkins/cuso-tools/lhb/settings.xml
            </command>
        </hudson.tasks.Shell>
\t\t<hudson.tasks.Shell>
      <command>echo BRANCH_NAME=`expr &quot;$GIT_BRANCH&quot; : &apos;.*\\/\\(.*\\)&apos;` &gt; propsfile
echo REPO_NAME=`expr &quot;$GIT_URL&quot; : &apos;.*\\/\\(.*\\)\\.git&apos;` &gt;&gt; propsfile</command>
    </hudson.tasks.Shell>
    <EnvInjectBuilder plugin="envinject@1.92.1">
      <info>
        <propertiesFilePath>propsfile</propertiesFilePath>
      </info>
    </EnvInjectBuilder>
    </prebuilders>
    <postbuilders>
\t<org.jenkinsci.plugins.conditionalbuildstep.singlestep.SingleConditionalBuilder plugin="conditional-buildstep@1.3.3">
        <condition class="org.jenkins_ci.plugins.run_condition.core.FileExistsCondition" plugin="run-condition@1.0">
        <file>src/main/java</file>
        <baseDir class="org.jenkins_ci.plugins.run_condition.common.BaseDirectory$Workspace"/>
      </condition>
      <buildStep class="hudson.plugins.sonar.SonarRunnerBuilder" plugin="sonar@2.2.1">
\t    <installationName>SonarServer</installationName>
        <project></project>
        <properties># Required metadata
# Required metadata
sonar.projectKey=$REPO_NAME
sonar.projectName=$REPO_NAME
sonar.projectVersion=1.0
sonar.branch=$BRANCH_NAME

# Comma-separated paths to directories with sources (required)
sonar.sources=src/main/java

#sonar.coverage.exclusions=**/*Spec.js ,**/main.js
sonar.java.binaries=target/classes
#sonar.jacoco.reportMissing.force.zero=true


#sonar.jdbc.dialect=mssql

sonar.jacoco.reportPaths=target/jacoco.exe

# java version used by source files:
sonar.java.source=1.8

sonar.surefire.reportsPath=target/surefire-reports

sonar.dynamicAnalysis=reuseReports
sonar.java.coveragePlugin=jacoco

# Language
sonar.language=java

# Encoding of sources files
sonar.sourceEncoding=UTF-8</properties>
        <javaOpts></javaOpts>
        <jdk>jdk1.8.102</jdk>
        <task></task>
      </buildStep>
      <runner class="org.jenkins_ci.plugins.run_condition.BuildStepRunner$Fail" plugin="run-condition@1.0"/>
    </org.jenkinsci.plugins.conditionalbuildstep.singlestep.SingleConditionalBuilder>
\t</postbuilders>
    <runPostStepsIfResult>
        <name>SUCCESS</name>
        <ordinal>0</ordinal>
        <color>BLUE</color>
        <completeBuild>true</completeBuild>
    </runPostStepsIfResult>
</maven2-moduleset>
'''
    String name = name()
    String configXml = [
        "##projectKey##": name.split("_")[0],
        "##repository##": name.split("_")[1],
        "##refSpec##": name.split("_")[2],
        "##name##": name,
        "##mvnGoals##": "clean org.jacoco:jacoco-maven-plugin:prepare-agent install"
    ].inject(template) { result, key, value ->        
        result.replaceAll(key, value)
    }

    create(name, configXml)
}

// ********************************************************************************

if (args.length < 1) {
    println "Usage: jenkins <command> <params>, where command are a closure name and params are the params to this closure (See the content of this script file for details)."
    System.exit(-1)
}

def command = args[0]
def params = args.length > 1 ? args[1..args.length - 1] : null

def result = invokeMethod("$command", params)
println result
result


