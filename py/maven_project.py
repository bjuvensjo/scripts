#!/usr/bin/env python3

from os import makedirs

POM_TEMPLATE = """<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
   <modelVersion>4.0.0</modelVersion>
   <groupId>###group_id###</groupId>
   <artifactId>###artifact_id###</artifactId>
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
       </plugins>
   </build>
</project>
"""


def get_pom(group_id, artifact_id, version):
    return POM_TEMPLATE \
        .replace('###group_id###', group_id) \
        .replace('###artifact_id###', artifact_id) \
        .replace('###version###', version)


def make_dirs(output_dir, group_id, artifact_id):
    package_path = '/'.join(group_id.split('.') + artifact_id.split('.'))
    makedirs('{}/src/main/java/{}'.format(output_dir, package_path))
    makedirs('{}/src/main/resources/{}'.format(output_dir, package_path))
    makedirs('{}/src/test/java/{}'.format(output_dir, package_path))
    makedirs('{}/src/test/resources/{}'.format(output_dir, package_path))


def make_project(output_dir, group_id, artifact_id, version):
    make_dirs(output_dir, group_id, artifact_id)
    pom = get_pom(group_id, artifact_id, version)
    with open('{}/pom.xml'.format(output_dir), 'wt', encoding='utf-8') as pom_file:
        pom_file.write(pom)


if __name__ == '__main__':
    group_id = str(input('groupId (default mygroup): ') or 'mygroup')
    artifact_id = str(input('artifactId (default slask): ') or 'slask')
    version = str(input('version (default 1.0.0-SNAPSHOT): ') or '1.0.0-SNAPSHOT')
    output_dir = '/'.join(artifact_id.split('.'))

    make_project(output_dir, group_id, artifact_id, version)
