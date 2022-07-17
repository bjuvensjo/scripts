from unittest.mock import patch, mock_open, call

import pytest
from pytest import raises

from vang.maven.get_dependants import do_get_dependants, get_dependants, parse_args

dependency_tree_file_content = r"""[INFO] Scanning for projects...
[WARNING] 
[WARNING] Some problems were encountered while building the effective model for myorg.maven:envconfig-maven-plugin:maven-plugin:1.1
[WARNING] 'build.plugins.plugin.version' for org.apache.maven.plugins:maven-plugin-plugin is missing. @ line 47, column 21
[WARNING] 
[WARNING] It is highly recommended to fix these problems because they threaten the stability of your build.
[WARNING] 
[WARNING] For this reason, future Maven versions might no longer support building such malformed projects.
[WARNING] 
[INFO] ------------------------------------------------------------------------
[INFO] Reactor Build Order:
[INFO] 
[INFO] common.cache                                                       [jar]
[INFO] common.event                                                       [jar]
[INFO] ws                                                                 [pom]
[INFO] 
[INFO] ---------------------< myorg:common.cache >---------------------
[INFO] Building common.cache 1.0.7                                     [35/127]
[INFO] --------------------------------[ jar ]---------------------------------
[WARNING] The POM for myorg:es-maven-plugin:jar:2.0.0-SNAPSHOT is missing, no dependency information available
[WARNING] Failed to retrieve plugin descriptor for myorg:es-maven-plugin:2.0.0-SNAPSHOT: Plugin myorg:es-maven-plugin:2.0.0-SNAPSHOT or one of its dependencies could not be resolved: Could not find artifact myorg:es-maven-plugin:jar:2.0.0-SNAPSHOT
[INFO] 
[INFO] --- maven-dependency-plugin:2.8:tree (default-cli) @ common.cache ---
[INFO] myorg:common.cache:jar:1.0.7
[INFO] +- myorg.spring:bundle-support:jar:1.1:compile
[INFO] |  \- org.slf4j:slf4j-api:jar:1.7.5:compile
[INFO] +- com.hazelcast:hazelcast:jar:3.4:compile
[INFO] |  +- net.sourceforge.findbugs:annotations:jar:1.3.2:compile
[INFO] |  \- com.eclipsesource.minimal-json:minimal-json:jar:0.9.1:compile
[INFO] +- net.sf.ehcache:ehcache:jar:2.7.4:compile
[INFO] +- org.apache.camel:camel-core:jar:2.16.0:compile
[INFO] |  +- com.sun.xml.bind:jaxb-core:jar:2.2.11:compile
[INFO] |  \- com.sun.xml.bind:jaxb-impl:jar:2.2.11:compile
[INFO] +- org.springframework:spring-beans:jar:4.2.2.RELEASE:compile
[INFO] +- org.springframework:spring-context:jar:4.2.2.RELEASE:compile
[INFO] |  +- org.springframework:spring-aop:jar:4.2.2.RELEASE:compile
[INFO] |  |  \- aopalliance:aopalliance:jar:1.0:compile
[INFO] |  \- org.springframework:spring-expression:jar:4.2.2.RELEASE:compile
[INFO] +- org.springframework:spring-core:jar:4.2.2.RELEASE:compile
[INFO] |  \- commons-logging:commons-logging:jar:1.2:compile
[INFO] +- org.springframework:spring-test:jar:4.2.2.RELEASE:test
[INFO] +- ch.qos.logback:logback-classic:jar:1.0.13:compile
[INFO] |  \- ch.qos.logback:logback-core:jar:1.0.13:compile
[INFO] +- junit:junit:jar:4.12:test
[INFO] |  \- org.hamcrest:hamcrest-core:jar:1.3:test
[INFO] \- org.mockito:mockito-core:jar:1.9.5:test
[INFO]    \- org.objenesis:objenesis:jar:1.0:test
[INFO] 
[INFO] ---------------------< myorg:common.event >---------------------
[INFO] Building common.event 1.0.15                                   [101/127]
[INFO] --------------------------------[ jar ]---------------------------------
[WARNING] The POM for myorg:es-maven-plugin:jar:2.0.0-SNAPSHOT is missing, no dependency information available
[WARNING] Failed to retrieve plugin descriptor for myorg:es-maven-plugin:2.0.0-SNAPSHOT: Plugin myorg:es-maven-plugin:2.0.0-SNAPSHOT or one of its dependencies could not be resolved: Could not find artifact myorg:es-maven-plugin:jar:2.0.0-SNAPSHOT
[INFO] 
[INFO] --- maven-dependency-plugin:2.8:tree (default-cli) @ common.event ---
[INFO] myorg:common.event:jar:1.0.15
[INFO] +- org.apache.camel:camel-core:jar:2.16.0:compile
[INFO] |  +- org.slf4j:slf4j-api:jar:1.6.6:compile
[INFO] |  +- com.sun.xml.bind:jaxb-core:jar:2.2.11:compile
[INFO] |  \- com.sun.xml.bind:jaxb-impl:jar:2.2.11:compile
[INFO] +- ch.qos.logback:logback-classic:jar:1.0.13:compile
[INFO] |  \- ch.qos.logback:logback-core:jar:1.0.13:compile
[INFO] +- junit:junit:jar:4.11:test
[INFO] |  \- org.hamcrest:hamcrest-core:jar:1.3:test
[INFO] \- org.mockito:mockito-core:jar:1.9.5:test
[INFO]    \- org.objenesis:objenesis:jar:1.0:test
[INFO] 
[INFO] ----------------------------< my.group:ws >-----------------------------
[INFO] Building ws 1.0.0-SNAPSHOT                                     [127/127]
[INFO] --------------------------------[ pom ]---------------------------------
[INFO] 
[INFO] --- maven-dependency-plugin:2.8:tree (default-cli) @ ws ---
[INFO] my.group:ws:pom:1.0.0-SNAPSHOT
[INFO] ------------------------------------------------------------------------
[INFO] Reactor Summary:
[INFO] 
[INFO] common.cache 1.0.7 ................................. SUCCESS [  0.037 s]
[INFO] common.event 1.0.15 ................................ SUCCESS [  0.035 s]
[INFO] ws 1.0.0-SNAPSHOT .................................. SUCCESS [  0.002 s]
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  7.287 s
[INFO] Finished at: 2019-10-28T16:31:09+01:00
[INFO] ------------------------------------------------------------------------
"""


@pytest.mark.parametrize(
    "dependency, expected",
    [
        (
            "org.apache.camel:camel-core:jar:2.16.0:compile",
            {
                "org.apache.camel:camel-core:jar:2.16.0:compile": {
                    "direct": {
                        "myorg:common.cache:jar:1.0.7",
                        "myorg:common.event:jar:1.0.15",
                    },
                    "transitive": set(),
                }
            },
        ),
        (
            "camel-core",
            {
                "org.apache.camel:camel-core:jar:2.16.0:compile": {
                    "direct": {
                        "myorg:common.cache:jar:1.0.7",
                        "myorg:common.event:jar:1.0.15",
                    },
                    "transitive": set(),
                }
            },
        ),
        (
            "spring-beans",
            {
                "org.springframework:spring-beans:jar:4.2.2.RELEASE:compile": {
                    "direct": {
                        "myorg:common.cache:jar:1.0.7",
                    },
                    "transitive": set(),
                }
            },
        ),
        (
            "junit",
            {
                "junit:junit:jar:4.11:test": {
                    "direct": {"myorg:common.event:jar:1.0.15"},
                    "transitive": set(),
                },
                "junit:junit:jar:4.12:test": {
                    "direct": {"myorg:common.cache:jar:1.0.7"},
                    "transitive": set(),
                },
            },
        ),
        (
            "logback",
            {
                "ch.qos.logback:logback-classic:jar:1.0.13:compile": {
                    "direct": {
                        "myorg:common.cache:jar:1.0.7",
                        "myorg:common.event:jar:1.0.15",
                    },
                    "transitive": set(),
                },
                "ch.qos.logback:logback-core:jar:1.0.13:compile": {
                    "direct": set(),
                    "transitive": {
                        "myorg:common.cache:jar:1.0.7",
                        "myorg:common.event:jar:1.0.15",
                    },
                },
            },
        ),
        (
            "foo",
            {},
        ),
    ],
)
def test_do_get_dependants(dependency, expected):
    with patch(
        "builtins.open", mock_open(read_data=dependency_tree_file_content), create=True
    ):
        dependants = do_get_dependants("dependency_tree_file", dependency)
        assert dependants == expected


def test_get_dependants():
    with patch(
        "vang.maven.get_dependants.do_get_dependants",
        return_value={
            "ch.qos.logback:logback-classic:jar:1.0.13:compile": {
                "direct": {
                    "myorg:common.cache:jar:1.0.7",
                    "myorg:common.event:jar:1.0.15",
                },
                "transitive": set(),
            },
            "ch.qos.logback:logback-core:jar:1.0.13:compile": {
                "direct": set(),
                "transitive": {
                    "myorg:common.cache:jar:1.0.7",
                    "myorg:common.event:jar:1.0.15",
                },
            },
        },
    ):

        with patch("vang.maven.get_dependants.pprint") as mock_print:
            get_dependants("dependency_tree_file", "dependency", False, False)
            assert mock_print.mock_calls == [
                call(
                    {
                        "ch.qos.logback:logback-classic:jar:1.0.13:compile": {
                            "direct": {
                                "myorg:common.cache:jar:1.0.7",
                                "myorg:common.event:jar:1.0.15",
                            },
                            "transitive": set(),
                        },
                        "ch.qos.logback:logback-core:jar:1.0.13:compile": {
                            "direct": set(),
                            "transitive": {
                                "myorg:common.cache:jar:1.0.7",
                                "myorg:common.event:jar:1.0.15",
                            },
                        },
                    }
                )
            ]

        with patch("vang.maven.get_dependants.pprint") as mock_print:
            get_dependants("dependency_tree_file", "dependency", True, False)
            assert mock_print.mock_calls == [
                call(
                    {
                        "ch.qos.logback:logback-classic:jar:1.0.13:compile": {
                            "myorg:common.cache:jar:1.0.7",
                            "myorg:common.event:jar:1.0.15",
                        },
                        "ch.qos.logback:logback-core:jar:1.0.13:compile": set(),
                    }
                )
            ]

        with patch("vang.maven.get_dependants.pprint") as mock_print:
            get_dependants("dependency_tree_file", "dependency", False, True)
            assert mock_print.mock_calls == [
                call(
                    {
                        "ch.qos.logback:logback-classic:jar:1.0.13:compile": set(),
                        "ch.qos.logback:logback-core:jar:1.0.13:compile": {
                            "myorg:common.cache:jar:1.0.7",
                            "myorg:common.event:jar:1.0.15",
                        },
                    }
                )
            ]


@pytest.mark.parametrize(
    "args",
    [
        "",
        "foo",
        "-d -t",
        "foo bar -d -t",
    ],
)
def test_parse_args_raises(args):
    with raises(SystemExit):
        parse_args(args.split(" ") if args else args)


@pytest.mark.parametrize(
    "args, expected",
    [
        [
            "dtf d",
            {
                "dependency_tree_file": "dtf",
                "dependency": "d",
                "only_direct": False,
                "only_transitive": False,
            },
        ],
        [
            "dtf d -d",
            {
                "dependency_tree_file": "dtf",
                "dependency": "d",
                "only_direct": True,
                "only_transitive": False,
            },
        ],
        [
            "dtf d -t",
            {
                "dependency_tree_file": "dtf",
                "dependency": "d",
                "only_direct": False,
                "only_transitive": True,
            },
        ],
    ],
)
def test_parse_args_valid(args, expected):
    assert parse_args(args.split(" ") if args else "").__dict__ == expected
