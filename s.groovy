#!/usr/bin/env groovy

// Usage: s -rsr createTransfer deleteStandingTransfer

def splitCamelCase = { s ->
    s.split("(?=[A-Z.])")
}

def createRow  = { closure, values, delimiter ->
    values.collect({ it.startsWith("-") ? it.drop(1) : splitCamelCase(it).collect(closure).join(delimiter)}
).join(" ")}

def rows = [
    createRow({it}, args, ""),
    createRow({it.capitalize()}, args, ""),
    createRow({it.toLowerCase()}, args, ""),
    createRow({it.toUpperCase()}, args, ""),
    createRow({it.toLowerCase()}, args, "_"),
    createRow({it.toUpperCase()}, args, "_"),
    createRow({it.toLowerCase()}, args, "-"),
    createRow({it.toUpperCase()}, args, "-")
].join("\n")

println rows