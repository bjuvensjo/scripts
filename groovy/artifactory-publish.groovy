#!/usr/bin/env groovy

@Grab(group='org.slf4j', module='slf4j-api', version='1.7.25')
@Grab(group='ch.qos.logback', module='logback-classic', version='1.2.3')
import groovy.util.FileNameByRegexFinder
import groovy.util.logging.Slf4j
import java.security.MessageDigest

@Slf4j
class Artifactory {
    static int TIMEOUT = 60000
    String urlRestApi = "http://cuso.edb.se/artifactory"

    static {
        URL.metaClass.put = { Map requestProperties, File file ->
            HttpURLConnection con = delegate.openConnection()
            con.setAllowUserInteraction(true)
            con.setDoInput(true)
            con.setDoOutput(true)
            con.setConnectTimeout(TIMEOUT)
            con.setDefaultUseCaches(false)
            con.setReadTimeout(TIMEOUT)
            con.setRequestMethod("PUT")
            requestProperties?.each { k, v ->
                con.setRequestProperty(k, v)
            }

            con.getOutputStream().write(file.getBytes())

            String responseCode = con.getResponseCode()
            String responseBody
            con.getInputStream().withReader("UTF-8") { r ->
                responseBody = r.readLines().join("\n")
            }
            [responseCode: responseCode, headers: con.getHeaderFields(), body: responseBody]
        }
    }

    String generateCheckSum(File file, String algorithm) {
        MessageDigest md = MessageDigest.getInstance(algorithm)

        InputStream is = file.newInputStream()
        byte[] dataBytes = new byte[1024]
        int n = 0
        while ((n = is.read(dataBytes)) != -1) {
            md.update(dataBytes, 0, n)
        }

        byte[] buffer = md.digest()

        // Convert the byte to hex format
        StringBuffer sb = new StringBuffer("")
        for (int i = 0; i < buffer.length; i++) {
            sb.append(Integer.toString((buffer[i] & 0xff) + 0x100, 16).substring(1))
        }

        sb.toString()
    }

    Map<String, String> getRequestProperties(String username, String password, File file) {
        [
                'Content-Type'     : 'application/json',
                'Authorization'    : "Basic ${"$username:$password".bytes.encodeBase64().toString()}".toString(),
                'X-Checksum-Sha1'  : generateCheckSum(file, "SHA-1"),
                'X-Checksum-Sha256': generateCheckSum(file, "SHA-256"), // Not yet supported, see https://www.jfrog.com/jira/browse/RTFACT-6962
                "X-Checksum-Md5"   : generateCheckSum(file, "MD5")
        ]
    }

    Map publishMavenArtifact(File workDir, String username, String password) {
        boolean inRepository = false
        File pomFile = new File(workDir, "pom.xml")
        if (!pomFile.exists()) {
            String fileName = new FileNameByRegexFinder().getFileNames(workDir.path, ".*pom").findResult { fileName ->
                fileName
            }

            if (fileName) {
                pomFile = new File(fileName)
                inRepository = true
            }
        }
        def pom = new XmlSlurper().parse(pomFile)

        String groupId = pom.groupId.text() ?: pom.parent.groupId.text()
        String artifactId = pom.artifactId
        String version = pom.version.text() ?: pom.parent.version.text()
        String packaging = pom.packaging
        String artifactoryRepository

        if (version =~ /(?i).*SNAPSHOT.*/) {
            artifactoryRepository = "z-snapshot"
        } else {
            if (groupId.startsWith("com.evry")) {
                artifactoryRepository = "z-release"
            } else {
                artifactoryRepository = "ext-release-local"
            }
        }

        String artifactPath = "$urlRestApi/$artifactoryRepository/${groupId.replaceAll("\\.", "/")}/$artifactId/$version"

        String pomUrl = "${artifactPath}/${artifactId}-${version}.pom"
        log.info("pomFile: {}", pomFile.path)
        log.info("pomUrl: {}", pomUrl)
        Map pomResponse = pomUrl.toURL().put(getRequestProperties(username, password, pomFile), pomFile)
        log.info("pomResponse: {}", pomResponse)        

        if (packaging == "jar" || packaging == "maven-plugin") {
            File jarFile = inRepository ? new File(workDir, "${artifactId}-${version}.jar") : new File(workDir, "target/${artifactId}-${version}.jar")
            String jarUrl = "${artifactPath}/${jarFile.name}"
            log.info("jarFile: {}", jarFile.path)
            log.info("jarUrl: {}", jarUrl)
            Map jarResponse = jarUrl.toURL().put(getRequestProperties(username, password, jarFile), jarFile)
            log.info("jarResponse: {}", jarResponse)        
        }
    }
}

File workDir = new File(args ? args[0] : ".")
String username = System.getenv("U") ?: System.console().readLine("Artifactory username: ")
def password = System.getenv("P") ?: System.console().readPassword("Artifactory password: ")

new Artifactory().publishMavenArtifact(workDir, username, new String(password))
