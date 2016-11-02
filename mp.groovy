#!/usr/bin/env groovy

import groovy.io.FileType
import java.util.regex.Matcher

String groupId = System.console().readLine 'groupId (default com.bjuvensjo.github): '
String artifactId = System.console().readLine 'artifactId (default slask): '
String version = System.console().readLine 'version (default 1.0.0-SNAPSHOT): '

if (groupId.trim() == "") {
    groupId = "com.bjuvensjo.github"
}
if (artifactId.trim() == "") {
    artifactId = "slask"
}
if (version.trim() == "") {
    version = "1.0.0-SNAPSHOT"
}

String sourceDir = "."
String outputDir = artifactId

String encoding = 'UTF-8'

File sourceFile = new File(sourceDir)
File outputFile = new File(outputDir)

def template = '''<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>###groupId###</groupId>
    <artifactId>###artifactId###</artifactId>
    <version>###version###</version>
    <name>${project.groupId}:${project.artifactId}</name>
    <description>${project.artifactId}</description>    
    <packaging>jar</packaging>
    <properties>
        <maven.compiler.source>1.8</maven.compiler.source>
        <maven.compiler.target>1.8</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.3</version>
                <configuration>
                    <source>${maven.compiler.source}</source>
                    <target>${maven.compiler.target}</target>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-enforcer-plugin</artifactId>
                <version>1.3.1</version>
                <executions>
                    <execution>
                        <id>enforce-java</id>
                        <goals>
                            <goal>enforce</goal>
                        </goals>
                        <configuration>
                            <rules>
                                <requireJavaVersion>
                                    <version>${maven.compiler.target}</version>
                                </requireJavaVersion>
                            </rules>
                        </configuration>
                    </execution>
                </executions>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-javadoc-plugin</artifactId>
                <version>2.10.3</version>
                <configuration>
                    <show>protected</show>
                    <nohelp>true</nohelp>
                </configuration>
                <executions>
                    <execution>
                        <goals>
                            <goal>jar</goal>
                        </goals>
                    </execution>
                </executions>                
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-source-plugin</artifactId>
                <version>2.4</version>
                <executions>
                    <execution>
                        <goals>
                            <goal>jar</goal>
                        </goals>
                    </execution>
                </executions>                
            </plugin>
        </plugins>
    </build>    
</project>
'''

String pomContent = template
    .replaceAll("###groupId###", groupId)
    .replaceAll("###artifactId###", artifactId)
    .replaceAll("###version###", version)

//println pomContent

outputFile.mkdirs()

new File(outputFile, "pom.xml").setText(pomContent, encoding)

String packagePath = groupId.replaceAll("\\.", "/")
new File(outputFile, "src/main/java/$packagePath").mkdirs()
new File(outputFile, "src/main/resources/$packagePath").mkdirs()
new File(outputFile, "src/test/java/$packagePath").mkdirs()
new File(outputFile, "src/test/resources/$packagePath").mkdirs()
    

