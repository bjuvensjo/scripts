#!/usr/bin/env groovy

String ENCODING = "UTF-8"
int TIMEOUT = 12000

URL.metaClass.put = { Map requestProperties, String body ->
    println body
    HttpURLConnection con = delegate.openConnection()
    con.setAllowUserInteraction(true)
    con.setDoInput(true)
    con.setDoOutput(true)
    con.setConnectTimeout(TIMEOUT)
    con.setDefaultUseCaches(false)
    con.setReadTimeout(TIMEOUT)
    con.setRequestMethod("PUT")
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

String branch = "master"
String username
String password

if (args.length == 0) {
    branch = System.getProperty("branch") ?: System.console().readLine("Branch: ")
    username = System.getProperty("username") ?: System.console().readLine("Username: ")
    password = System.getProperty("password") ?: new String(System.console().readPassword("Password: "))
}

if (args.length == 3) {
    branch = args[0]
    username = args[1]
    password = args[2]
}

String urlRestApi = "http://cuso.edb.se/stash/rest/api/1.0"
def uri = new File(".git/config").findResult { line ->
    def m = line =~ /.*url = .*\/stash\/scm\/([^\/]+)\/(.*).git/
    if (m.matches()) {
        "projects/" + m[0][1] + "/repos/" + m[0][2] + "/branches/default"
    }
}

Map<String, Map<String, String>> requestProperties = [requestProperties: ['Content-Type': 'application/json', 'Authorization': "Basic ${"$username:$password".bytes.encodeBase64().toString()}".toString()]]

"$urlRestApi/$uri".toURL().put(requestProperties, "{\"id\": \"refs/heads/$branch\" }")
