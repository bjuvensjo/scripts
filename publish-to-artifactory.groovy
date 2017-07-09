#!/usr/bin/env groovy

@Grab(group='org.slf4j', module='slf4j-api', version='1.7.25')
@Grab(group='ch.qos.logback', module='logback-classic', version='1.2.3')
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
        File pomFile = new File(workDir, "pom.xml")
        def pom = new XmlSlurper().parse(pomFile)

        String groupId = pom.groupId.text()
        String artifactId = pom.artifactId
        String version = pom.version
        String artifactoryRepository

        if (version =~ /(?i).*SNAPSHOT.*/) {
            artifactoryRepository = "lhb-snapshot"
        } else {
            if (groupId.startsWith("com.evry")) {
                artifactoryRepository = "lhb-release"
            } else {
                artifactoryRepository = "ext-release-local"
            }
        }

        String artifactPath = "$urlRestApi/$artifactoryRepository/${(groupId ?: pom.parent.groupId.text()).replaceAll("\\.", "/")}/$artifactId/$version"

        File jarFile = new File(workDir, "target/${artifactId}-${version}.jar")
        String pomUrl = "${artifactPath}/${jarFile.name.replace(".jar", ".pom")}"
        log.info("pomFile: {}", pomFile.path)
        log.info("pomUrl: {}", pomUrl)
        Map pomResponse = pomUrl.toURL().put(getRequestProperties(username, password, pomFile), pomFile)
        log.info("pomResponseCode: {}", pomResponse.responseCode)        

        String jarUrl
        if (jarFile.exists()) {
            jarUrl = "${artifactPath}/${jarFile.name}"
            log.info("jarFile: {}", jarFile.path)
            log.info("jarUrl: {}", jarUrl)
            Map jarResponse = jarUrl.toURL().put(getRequestProperties(username, password, jarFile), jarFile)
            log.info("jarResponseCode: {}", jarResponse.responseCode)        
        }

        [pomUrl: pomUrl, jarUrl: jarUrl]
    }
}

File workDir = new File(args ? args[0] : ".")
String username = System.getProperty("username") ?: System.console().readLine("Artifactory username: ")
def password = System.getProperty("password") ?: System.console().readPassword("Artifactory password: ")

new Artifactory().publishMavenArtifact(workDir, username, new String(password))
