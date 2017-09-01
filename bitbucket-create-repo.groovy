#!/usr/bin/env groovy

String ENCODING = "UTF-8"
int TIMEOUT = 12000       

URL.metaClass.post = { Map requestProperties, String body ->
    HttpURLConnection con = delegate.openConnection()
    con.setAllowUserInteraction(true)
    con.setDoInput(true)
    con.setDoOutput(true)
    con.setConnectTimeout(TIMEOUT)
    con.setDefaultUseCaches(false)
    con.setReadTimeout(TIMEOUT)
    con.setRequestMethod("POST")
    requestProperties.requestProperties.each { k, v ->
        con.setRequestProperty(k, v)
    }
    con.getOutputStream().withWriter(ENCODING) { w ->
        w.write(body)
    }
    con.getResponseCode()
    String responseBody
    con.getInputStream().withReader(ENCODING) { r ->
        responseBody = r.readLines().join("\n")
    }
    [responseCode: con.getResponseCode(), headers: con.getHeaderFields(), body: responseBody]
}

String projectKey
String repoName
String username
String password

if (args.length == 0) {
    projectKey = System.getProperty("projectKey") ?: System.console().readLine("ProjectKey: ")
    repoName = System.getProperty("repoName") ?: System.console().readLine("RepoName: ")
    username = System.getProperty("username") ?: System.console().readLine("Username: ")
    password = System.getProperty("password") ?: new String(System.console().readPassword("Password: "))
}

if (args.length == 4) {
    projectKey = args[0]
    repoName = args[1]
    username = args[2]
    password = args[3]
}

String urlRestApi = "http://cuso.edb.se/stash/rest/api/1.0"
String uri = "projects/${projectKey}/repos"
Map<String, Map<String, String>> requestProperties = [requestProperties: ['Content-Type': 'application/json', 'Authorization': "Basic ${"$username:$password".bytes.encodeBase64().toString()}".toString()]]
String body = "{\"name\": \"${repoName}\", \"scmId\": \"git\", \"forkable\": true}"

def result = "$urlRestApi/$uri".toURL().post(requestProperties, body)
println result
