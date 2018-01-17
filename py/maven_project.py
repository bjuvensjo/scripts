#!/usr/bin/env python3

""" Makes Maven project. """

from os import makedirs

from os.path import normpath

POM_TEMPLATE = """<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
   <modelVersion>4.0.0</modelVersion>
   <groupId>###group_id###</groupId>
   <artifactId>###artifact_id###</artifactId>
   <version>###version###</version>
   <name>${project.groupId}:${project.artifactId}</name>
   <description>${project.artifactId}</description>
   <packaging>###packaging###</packaging>
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


def get_pom(group_id, artifact_id, version, packaging):
    """ Returns pom content. """
    return POM_TEMPLATE \
        .replace('###group_id###', group_id) \
        .replace('###artifact_id###', artifact_id) \
        .replace('###version###', version) \
        .replace('###packaging###', packaging)


def make_dirs(output_dir, group_id, artifact_id, packaging):
    """ Make standard dirs of Maven project. """
    makedirs(output_dir)
    if packaging in ['jar', 'war']:
        package_path = normpath('/'.join(group_id.split('.') + artifact_id.split('.')))
        for p in ['{}/src/main/java/{}', '{}/src/main/resources/{}', '{}/src/test/java/{}', '{}/src/test/resources/{}']:
            makedirs(normpath(p.format(output_dir, package_path)))
        if packaging in ['war']:
            makedirs(normpath('{}/src/main/webapp'.format(output_dir)))


def make_project(output_dir, group_id, artifact_id, version, packaging):
    """ Makes Maven project. """
    make_dirs(output_dir, group_id, artifact_id, packaging)
    pom = get_pom(group_id, artifact_id, version, packaging)
    with open(normpath('{}/pom.xml'.format(output_dir)), 'wt', encoding='utf-8') as pom_file:
        pom_file.write(pom)


def main():
    group_id = str(input('groupId (default mygroup): ') or 'mygroup')
    artifact_id = str(input('artifactId (default slask): ') or 'slask')
    version = str(input('version (default 1.0.0-SNAPSHOT): ') or '1.0.0-SNAPSHOT')
    packaging = str(input('packaging (default jar): ') or 'jar')
    output_dir = normpath('/'.join(artifact_id.split('.')))
    make_project(output_dir, group_id, artifact_id, version, packaging)


if __name__ == '__main__':
    main()
